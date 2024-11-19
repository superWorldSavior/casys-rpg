"""PDF Processor adapter implementing the PDFProcessor port."""
import os
import re
import fitz
import tempfile
import shutil
from PyPDF2 import PdfReader
from typing import List, Optional, Dict, Tuple, Set
from ...domain.ports import PDFProcessor
from ...domain.entities import (
    Section, PDFImage, ProcessedPDF,
    ProcessingStatus, ProcessingProgress,
    TextFormatting, FormattedText
)
from ..analyzers.text_analyzer import TextAnalyzer
from ..analyzers.image_analyzer import ImageAnalyzer

class MuPDFProcessorAdapter(PDFProcessor):
    """Adapter for MuPDF implementation of PDF processing."""
    
    def __init__(self, text_analyzer: TextAnalyzer, image_analyzer: ImageAnalyzer):
        self.text_analyzer = text_analyzer
        self.image_analyzer = image_analyzer
        self.processed_sections: Set[str] = set()
        self.processed_images: Set[str] = set()

    def _get_pdf_folder_name(self, pdf_path: str) -> str:
        base_name = os.path.basename(pdf_path)
        folder_name = os.path.splitext(base_name)[0]
        folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
        return folder_name

    def _create_book_structure(self, base_output_dir: str, pdf_folder_name: str) -> Dict[str, str]:
        """Create the book directory structure and return paths"""
        book_dir = os.path.join(base_output_dir, pdf_folder_name)
        sections_dir = os.path.join(book_dir, "sections")
        images_dir = os.path.join(book_dir, "images")
        metadata_dir = os.path.join(book_dir, "metadata")
        histoire_dir = os.path.join(book_dir, "histoire")

        for directory in [book_dir, sections_dir, images_dir, metadata_dir, histoire_dir]:
            os.makedirs(directory, exist_ok=True)

        return {
            "book_dir": book_dir,
            "sections_dir": sections_dir,
            "images_dir": images_dir,
            "metadata_dir": metadata_dir,
            "histoire_dir": histoire_dir
        }

    def _get_content_hash(self, content: str) -> str:
        """Generate a unique hash for content to prevent duplicates"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()

    def _save_section_content(self, section: Section):
        """Save section content to file with proper formatting and atomic write"""
        # Generate content hash
        content_hash = self._get_content_hash(section.content)
        
        # Check if this content has already been processed
        if content_hash in self.processed_sections:
            print(f"Skipping duplicate content for section {section.number}")
            return
        
        # Prepare the content
        formatted_content = []
        for fmt_text in section.formatted_content:
            if fmt_text.format_type == TextFormatting.HEADER:
                if not re.match(r'^\s*\d+\s*$', fmt_text.text.strip()):
                    formatted_content.append(f"\n## {fmt_text.text}\n")
            elif fmt_text.format_type == TextFormatting.SUBHEADER:
                formatted_content.append(f"\n### {fmt_text.text}\n")
            elif fmt_text.format_type == TextFormatting.LIST_ITEM:
                formatted_content.append(f"- {fmt_text.text}\n")
            elif fmt_text.format_type == TextFormatting.CODE:
                formatted_content.append(f"\n```\n{fmt_text.text}\n```\n")
            elif fmt_text.format_type == TextFormatting.QUOTE:
                formatted_content.append(f"\n> {fmt_text.text}\n")
            else:
                formatted_content.append(f"\n{fmt_text.text}\n")

        # Create content with title
        full_content = []
        if section.title:
            full_content.append(f"# {section.title}\n\n")
        full_content.append("".join(formatted_content).strip() + "\n")
        
        # Create temporary file
        os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
        temp_path = f"{section.file_path}.tmp"
        
        try:
            # Write to temporary file
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write("".join(full_content))
            
            # Atomic rename
            shutil.move(temp_path, section.file_path)
            
            # Mark as processed
            self.processed_sections.add(content_hash)
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from PDF using MuPDF."""
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        sections_dir = paths["sections_dir"]
        histoire_dir = paths["histoire_dir"]

        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        sections = []

        try:
            reader = PdfReader(pdf_path)
            progress.total_pages = len(reader.pages)
            progress.status = ProcessingStatus.EXTRACTING_SECTIONS

            # First pass: collect pre-section content
            pre_section_content = []
            first_section_page = None

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text:
                    continue

                page_lines = []
                lines = text.splitlines()

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Check for standalone section number
                    chapter_num, _ = self.text_analyzer.detect_chapter(line)
                    if chapter_num is not None:
                        first_section_page = page_num
                        break

                    page_lines.append(line)

                if first_section_page is not None:
                    break

                if page_lines:
                    pre_section_content.append("\n".join(page_lines))

            # Process pre-section content
            if pre_section_content:
                content = "\n".join(pre_section_content)
                formatted_blocks = self.text_analyzer.process_text_block(content, is_pre_section=True)

                # Use AI to detect chapter breaks
                current_chapter = []
                chapter_count = 0

                for block in formatted_blocks:
                    is_chapter, title = await self.text_analyzer.detect_chapter_with_ai(block.text)

                    if is_chapter and current_chapter:
                        # Save current chapter
                        chapter_count += 1
                        file_path = os.path.join(histoire_dir, f"{chapter_count}.md")

                        sections.append(
                            Section(
                                number=chapter_count,
                                content="\n".join(text.text for text in current_chapter),
                                page_number=1,
                                file_path=file_path,
                                pdf_name=pdf_folder_name,
                                title=title,
                                formatted_content=current_chapter,
                                is_chapter=True,
                                chapter_number=chapter_count
                            )
                        )
                        self._save_section_content(sections[-1])
                        current_chapter = []

                    current_chapter.append(block)

                # Save last chapter if exists
                if current_chapter:
                    chapter_count += 1
                    file_path = os.path.join(histoire_dir, f"{chapter_count}.md")

                    sections.append(
                        Section(
                            number=chapter_count,
                            content="\n".join(text.text for text in current_chapter),
                            page_number=1,
                            file_path=file_path,
                            pdf_name=pdf_folder_name,
                            title=None,
                            formatted_content=current_chapter,
                            is_chapter=True,
                            chapter_number=chapter_count
                        )
                    )
                    self._save_section_content(sections[-1])

            # Process numbered sections
            current_section = None
            current_text = []
            current_page = first_section_page or 0

            for page_num in range(current_page, len(reader.pages)):
                page = reader.pages[page_num]
                progress.current_page = page_num + 1

                try:
                    text = page.extract_text()
                    if not text:
                        continue

                    lines = text.splitlines()
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue

                        chapter_num, _ = self.text_analyzer.detect_chapter(line)
                        if chapter_num is not None:
                            # Save previous section if exists
                            if current_section is not None and current_text:
                                file_path = os.path.join(sections_dir, f"{current_section}.md")
                                formatted_content = self.text_analyzer.process_text_block("\n".join(current_text))

                                sections.append(
                                    Section(
                                        number=len(sections),
                                        content="\n".join(current_text),
                                        page_number=page_num + 1,
                                        file_path=file_path,
                                        pdf_name=pdf_folder_name,
                                        title=None,
                                        formatted_content=formatted_content,
                                        is_chapter=True,
                                        chapter_number=current_section
                                    )
                                )
                                self._save_section_content(sections[-1])
                                progress.processed_sections += 1

                            # Start new section
                            current_section = chapter_num
                            current_text = []
                        else:
                            current_text.append(line)

                except Exception as e:
                    print(f"Error processing page {page_num + 1}: {e}")

            # Save last section if exists
            if current_section is not None and current_text:
                file_path = os.path.join(sections_dir, f"{current_section}.md")
                formatted_content = self.text_analyzer.process_text_block("\n".join(current_text))

                sections.append(
                    Section(
                        number=len(sections),
                        content="\n".join(current_text),
                        page_number=progress.current_page,
                        file_path=file_path,
                        pdf_name=pdf_folder_name,
                        title=None,
                        formatted_content=formatted_content,
                        is_chapter=True,
                        chapter_number=current_section
                    )
                )
                self._save_section_content(sections[-1])
                progress.processed_sections += 1

            progress.status = ProcessingStatus.COMPLETED
            return ProcessedPDF(
                sections=sections,
                images=[],  # Will be populated by extract_images
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )

        except Exception as e:
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            raise

    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        """Extract images from PDF using MuPDF."""
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        images_dir = paths["images_dir"]
        images = []

        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()

                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Generate image path and hash for deduplication
                        image_hash = self._get_content_hash(str(image_bytes))
                        if image_hash in self.processed_images:
                            continue
                        
                        # Generate image path
                        image_filename = f"page_{page_num + 1}_img_{img_idx + 1}.png"
                        image_path = os.path.join(images_dir, image_filename)
                        
                        # Process and save image
                        pdf_image = self.image_analyzer.process_image(
                            image_bytes, page_num + 1, pdf_folder_name, image_path
                        )
                        images.append(pdf_image)
                        self.processed_images.add(image_hash)
                        
                    except Exception as e:
                        print(f"Error extracting image {img_idx + 1} from page {page_num + 1}: {e}")

            return images

        except Exception as e:
            print(f"Error extracting images from PDF: {e}")
            raise
        finally:
            if 'doc' in locals():
                doc.close()
