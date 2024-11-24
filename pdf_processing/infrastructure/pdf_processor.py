import json

import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)
import os
from typing import List, Dict, Union
import fitz

from .rules_processor import RulesProcessor
from ..domain.entities import PDFImage
from ..domain.entities import Section, ProcessedPDF, ProcessingProgress, ProcessingStatus
from .ai_processor import AIProcessor
from .section_processor import SectionProcessor
from .file_system_processor import FileSystemProcessor
from .image_processor import ImageProcessor
from ..domain.ports import PDFProcessor, PDFRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MuPDFProcessor(PDFProcessor):

    def __init__(self, repository: PDFRepository):
        self.repository = repository
        self.ai_processor = AIProcessor()
        self.file_system_processor = FileSystemProcessor()
        self.image_processor = ImageProcessor()
        self.rules_processor = RulesProcessor()

    async def extract_sections(
            self,
            pdf_path: str,
            base_output_dir: str = "sections") -> ProcessedPDF:
        logger.info(f"Starting PDF processing for: {pdf_path}")

        pdf_folder_name = self.file_system_processor.get_pdf_folder_name(
            pdf_path)
        paths = self.file_system_processor.create_book_structure(
            base_output_dir, pdf_folder_name)
        histoire_dir = paths["histoire_dir"]
        images_dir = paths["images_dir"]
        metadata_dir = paths["metadata_dir"]
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING,
                                    total_pages=0)

        try:
            doc = fitz.Document(pdf_path)  # Open PDF document using PyMuPDF
            progress.total_pages = len(doc)
            sections = []
            content_buffer = ""
            current_chapter_number = 0

            # Extract pages with text
            pages = SectionProcessor.extract_text_from_pdf(pdf_path)

            # Find the page where section 1 starts
            section_one_page = SectionProcessor.find_section(pages,
                                                             section_number=1)
            if section_one_page:
                logger.info(
                    f"Section 1 found on page {section_one_page}. Stopping extraction before this page."
                )

            for page in pages:
                page_num = page["num"]
                page_text = page["text"]

                if not page_text:
                    logger.warning(f"Page {page_num} is empty. Skipping...")
                    continue

                logger.debug(f"Processing page {page_num}")

                # Stop extraction before the section 1 page
                if section_one_page and int(page_num) >= section_one_page:
                    logger.info(
                        f"Stopping extraction before page {page_num} (section 1 detected)."
                    )
                    break

                # Detect new chapter titles
                is_new_chapter, chapter_title = await self.ai_processor.detect_chapter_with_ai(
                    page_text)

                if is_new_chapter:
                    # Save current chapter content
                    if content_buffer.strip():
                        current_chapter_number += 1
                        await self._save_chapter(current_chapter_number,
                                                 content_buffer.strip(),
                                                 page_num, histoire_dir,
                                                 pdf_folder_name, sections,
                                                 progress)
                    content_buffer = ""  # Reset buffer for new chapter

                # Add page content to buffer
                markdown_content = await self.ai_processor.analyze_multimodal_page(
                    {
                        "text": page_text,
                        "num": page_num,
                        "image_path": None
                    })
                if markdown_content:
                    content_buffer += markdown_content + "\n"

            # Save the final chapter content if not empty
            if content_buffer.strip():
                current_chapter_number += 1
                await self._save_chapter(current_chapter_number,
                                         content_buffer.strip(), 
                                         page["num"],  # Use the current page number from the page dict
                                         histoire_dir, 
                                         pdf_folder_name,
                                         sections, 
                                         progress)

            # Call RulesProcessor after extracting chapters
            try:
                rules_output_path = os.path.join(metadata_dir, "rules.json")
                rules = await self.rules_processor.process_chapters(
                    [section.to_dict() for section in sections])
                with open(rules_output_path, 'w', encoding='utf-8') as f:
                    json.dump(rules, f, ensure_ascii=False, indent=2)
                logger.info(
                    f"Rules extraction completed and saved to {rules_output_path}"
                )
            except Exception as e:
                logger.error(f"Error in rules extraction: {e}")

            # Extract images
            logger.info("Extracting images...")
            images = self.image_processor.extract_images(
                pdf_path, images_dir, metadata_dir, pdf_folder_name, sections)
            for image in images:
                await self.repository.save_image(image)
            progress.processed_images = len(images)

            # Finalize processing
            processed_pdf = ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress,
            )
            await self.repository.save_metadata(processed_pdf)

            progress.status = ProcessingStatus.COMPLETED
            logger.info(
                f"PDF processing completed: {len(sections)} sections, {len(images)} images."
            )
            return processed_pdf

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            raise

    async def _save_chapter(self, chapter_number: int, content: str,
                            page_num: Union[str, int], histoire_dir: str, pdf_name: str,
                            sections: List[Section],
                            progress: ProcessingProgress):
        """
        Save chapter content to file and update metadata.

        Args:
            chapter_number (int): Chapter number.
            content (str): Chapter content.
            page_num (int): Page number.
            histoire_dir (str): Directory for saving chapters.
            pdf_name (str): PDF file name.
            sections (List[Section]): List of sections.
            progress (ProcessingProgress): Progress tracker.
        """
        section_file_path = os.path.join(histoire_dir,
                                         f"chapter_{chapter_number}.md")
        section = Section(number=chapter_number,
                          content=content,
                          page_number=int(page_num) if isinstance(page_num, str) else page_num,
                          file_path=section_file_path,
                          pdf_name=pdf_name,
                          is_chapter=True)
        await self.repository.save_section(section)
        sections.append(section)
        progress.processed_sections += 1
    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        """Extract images from a PDF file."""
        try:
            pdf_folder_name = self.file_system_processor.get_pdf_folder_name(pdf_path)
            paths = self.file_system_processor.create_book_structure(base_output_dir, pdf_folder_name)
            
            images = self.image_processor.extract_images(
                pdf_path,
                paths["images_dir"],
                paths["metadata_dir"],
                pdf_folder_name
            )
            logger.info(f"Extracted {len(images)} images from PDF")
            return images
        except Exception as e:
            logger.error(f"Error extracting images from PDF: {e}")
            return []
