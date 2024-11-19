"""PDF processor implementation using MuPDF."""
import os
import fitz  # PyMuPDF
import re
import json
from PIL import Image
import io
import logging
from typing import List, Optional, Dict, Tuple
from ..domain.ports import PDFProcessor, TextAnalyzer
from ..domain.entities import (Section, PDFImage, ProcessedPDF,
                             ProcessingStatus, ProcessingProgress,
                             TextFormatting, FormattedText)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MuPDFProcessor(PDFProcessor):
    """MuPDF-based implementation of PDFProcessor."""
    
    def __init__(self):
        self.text_analyzer: Optional[TextAnalyzer] = None

    def _get_pdf_folder_name(self, pdf_path: str) -> str:
        """Get standardized folder name from PDF path."""
        base_name = os.path.basename(pdf_path)
        folder_name = os.path.splitext(base_name)[0]
        folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
        return folder_name

    def _create_book_structure(self, base_output_dir: str,
                             pdf_folder_name: str) -> Dict[str, str]:
        """Create the book directory structure and return paths."""
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

    def _save_section_content(self, section: Section) -> None:
        """Save section content to file with proper formatting."""
        if not section or not section.file_path:
            logger.warning("Invalid section data provided")
            return

        try:
            os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
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

            with open(section.file_path, 'w', encoding='utf-8') as f:
                if section.title:
                    f.write(f"# {section.title}\n\n")
                f.write("".join(formatted_content).strip() + "\n")

        except Exception as e:
            logger.error(f"Error saving section content: {str(e)}", exc_info=True)
            raise

    async def extract_sections(self, pdf_path: str,
                             base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from the PDF with enhanced formatting detection."""
        if not self.text_analyzer:
            raise ValueError("TextAnalyzer not initialized")

        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        sections = []

        try:
            with fitz.open(pdf_path) as doc:
                progress.total_pages = len(doc)
                progress.status = ProcessingStatus.EXTRACTING_SECTIONS
                
                current_section = None
                current_text = []
                
                for page_num in range(len(doc)):
                    progress.current_page = page_num + 1
                    page = doc[page_num]
                    
                    try:
                        text = page.get_text()
                        if not text:
                            continue

                        # Process text using injected text analyzer
                        formatted_blocks = self.text_analyzer.process_text_block(text)
                        
                        for block in formatted_blocks:
                            is_chapter, title = await self.text_analyzer.detect_chapter_with_ai(block.text)
                            
                            if is_chapter:
                                # Save previous section if exists
                                if current_section and current_text:
                                    section = Section(
                                        number=len(sections),
                                        content="\n".join(current_text),
                                        page_number=page_num,
                                        file_path=os.path.join(paths["sections_dir"], f"{len(sections)+1}.md"),
                                        pdf_name=pdf_folder_name,
                                        title=title,
                                        formatted_content=formatted_blocks,
                                        is_chapter=True,
                                        chapter_number=len(sections)+1
                                    )
                                    sections.append(section)
                                    self._save_section_content(section)
                                    progress.processed_sections += 1
                                    current_text = []
                                
                            current_text.append(block.text)
                            
                    except Exception as e:
                        logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                        continue

                # Save last section if exists
                if current_text:
                    section = Section(
                        number=len(sections),
                        content="\n".join(current_text),
                        page_number=progress.current_page,
                        file_path=os.path.join(paths["sections_dir"], f"{len(sections)+1}.md"),
                        pdf_name=pdf_folder_name,
                        title=None,
                        formatted_content=[],
                        is_chapter=True,
                        chapter_number=len(sections)+1
                    )
                    sections.append(section)
                    self._save_section_content(section)
                    progress.processed_sections += 1

                progress.status = ProcessingStatus.COMPLETED
                return ProcessedPDF(
                    sections=sections,
                    images=[],  # Images will be processed separately
                    pdf_name=pdf_folder_name,
                    base_path=base_output_dir,
                    progress=progress
                )

        except Exception as e:
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            logger.error(f"Error extracting sections: {str(e)}", exc_info=True)
            raise

    async def extract_images(self, pdf_path: str,
                           base_output_dir: str = "sections",
                           sections: Optional[List[Section]] = None) -> List[PDFImage]:
        """Extract images from the PDF with section information."""
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        images = []

        try:
            with fitz.open(pdf_path) as doc:
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
                            
                            # Save image
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

                        except Exception as e:
                            logger.error(f"Error extracting image {img_idx} from page {page_num + 1}: {str(e)}")
                            continue

            return images

        except Exception as e:
            logger.error(f"Error extracting images: {str(e)}", exc_info=True)
            raise
