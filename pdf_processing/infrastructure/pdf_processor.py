import os
import fitz  # PyMuPDF
import re
import json
from typing import List, Optional, Dict, Tuple
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfReader
from ..domain.ports import PDFProcessor
from ..domain.entities import (Section, PDFImage, ProcessedPDF,
                             ProcessingStatus, ProcessingProgress,
                             TextFormatting, FormattedText)
from .logging_config import StructuredLogger
from .adapters.openai_adapter import OpenAIAnalyzer
from .adapters.text_formatting_adapter import RegexTextFormatDetector

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.text_detector = RegexTextFormatDetector()
        self.ai_analyzer = OpenAIAnalyzer()
        self.logger = StructuredLogger("PDFProcessor")

    def _get_pdf_folder_name(self, pdf_path: str) -> str:
        base_name = os.path.basename(pdf_path)
        folder_name = os.path.splitext(base_name)[0]
        folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
        return folder_name

    def _create_book_structure(self, base_output_dir: str,
                             pdf_folder_name: str) -> Dict[str, str]:
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

    async def _process_text_block(self, text: str, is_pre_section: bool = False) -> List[FormattedText]:
        """Process a block of text and return formatted text segments"""
        formatted_texts = []
        lines = text.splitlines()
        current_block = []
        current_format = None

        for line in lines:
            line = line.strip()
            if not line:
                if current_block:
                    formatted_text = await self.text_detector.detect_formatting(
                        "\n".join(current_block),
                        is_pre_section=is_pre_section
                    )
                    formatted_texts.append(formatted_text)
                    current_block = []
                    current_format = None
                continue

            # Get format for current line
            formatted_line = await self.text_detector.detect_formatting(
                line,
                is_pre_section=is_pre_section
            )

            # Start new block if format changes or if it's a header/subheader
            if (formatted_line.format_type != current_format or 
                formatted_line.format_type in [TextFormatting.HEADER, TextFormatting.SUBHEADER]):
                if current_block:
                    formatted_text = await self.text_detector.detect_formatting(
                        "\n".join(current_block),
                        is_pre_section=is_pre_section
                    )
                    formatted_texts.append(formatted_text)
                    current_block = []
                current_format = formatted_line.format_type

            current_block.append(line)

        # Add remaining block
        if current_block:
            formatted_text = await self.text_detector.detect_formatting(
                "\n".join(current_block),
                is_pre_section=is_pre_section
            )
            formatted_texts.append(formatted_text)

        return formatted_texts

    def _save_section_content(self, section: Section):
        """Save section content to file with proper formatting"""
        os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
        formatted_content = []

        # Add formatted content
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

        with open(section.file_path, 'w', encoding='utf-8') as f:
            if section.title:
                f.write(f"# {section.title}\n\n")
            f.write("".join(formatted_content).strip() + "\n")

    async def extract_sections(self, pdf_path: str,
                             base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from PDF with enhanced formatting detection"""
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        sections = []
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)

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

                lines = text.splitlines()
                page_lines = []

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Check for standalone section number
                    chapter_num, _ = await self.text_detector.detect_chapter(line)
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
                formatted_blocks = await self._process_text_block(content, is_pre_section=True)

                # Use AI to detect chapter breaks
                current_chapter = []
                chapter_count = 0

                for block in formatted_blocks:
                    is_chapter, title = await self.ai_analyzer.analyze_chapter_break(block.text)

                    if is_chapter and current_chapter:
                        # Save current chapter
                        chapter_count += 1
                        file_path = os.path.join(paths["histoire_dir"], f"{chapter_count}.md")

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
                    file_path = os.path.join(paths["histoire_dir"], f"{chapter_count}.md")

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
            progress.status = ProcessingStatus.EXTRACTING_SECTIONS
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

                        chapter_num, _ = await self.text_detector.detect_chapter(line)
                        if chapter_num is not None:
                            # Save previous section if exists
                            if current_section is not None and current_text:
                                file_path = os.path.join(paths["sections_dir"], f"{current_section}.md")
                                formatted_content = await self._process_text_block("\n".join(current_text))

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
                    self.logger.error(f"Error processing page {page_num + 1}", e)
                    continue

            # Save last section if exists
            if current_section is not None and current_text:
                file_path = os.path.join(paths["sections_dir"], f"{current_section}.md")
                formatted_content = await self._process_text_block("\n".join(current_text))

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

            # Extract images
            progress.status = ProcessingStatus.EXTRACTING_IMAGES
            images = await self.extract_images(pdf_path, base_output_dir, sections)

            progress.status = ProcessingStatus.COMPLETED
            return ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )

        except Exception as e:
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            raise

    async def extract_images(self, pdf_path: str,
                           base_output_dir: str = "sections",
                           sections: Optional[List[Section]] = None) -> List[PDFImage]:
        """Extract images from PDF with section information"""
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        images = []
        images_metadata = []

        try:
            doc = fitz.open(pdf_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()

                # Find corresponding section
                section_number = None
                if sections:
                    for section in sections:
                        if section.page_number <= page_num + 1:
                            section_number = section.chapter_number

                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_img = doc.extract_image(xref)
                        image_bytes = base_img["image"]

                        image = Image.open(io.BytesIO(image_bytes))
                        width, height = image.size

                        image_filename = f"page_{page_num + 1}_img_{img_idx + 1}.png"
                        image_path = os.path.join(paths["images_dir"], image_filename)
                        image.save(image_path)

                        image_data = PDFImage(
                            page_number=page_num + 1,
                            image_path=image_path,
                            pdf_name=pdf_folder_name,
                            width=width,
                            height=height,
                            section_number=section_number
                        )
                        images.append(image_data)

                        images_metadata.append({
                            "page_number": page_num + 1,
                            "image_path": image_path,
                            "width": width,
                            "height": height,
                            "filename": image_filename,
                            "section_number": section_number
                        })

                    except Exception as e:
                        self.logger.error(f"Error extracting image {img_idx} from page {page_num + 1}", e)
                        continue

            doc.close()

            # Save images metadata
            metadata_path = os.path.join(paths["metadata_dir"], "images.json")
            with open(metadata_path, 'w') as f:
                json.dump(images_metadata, f, indent=2)

        except Exception as e:
            self.logger.error("Error processing PDF for images", e)

        return images
