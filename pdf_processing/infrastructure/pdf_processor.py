import fitz  # PyMuPDF
import logging
import os
from typing import List, Dict

from ..domain.entities import Section, ProcessedPDF, ProcessingProgress, ProcessingStatus
from .ai_processor import AIProcessor
from .section_processor import SectionProcessor
from .file_system_processor import FileSystemProcessor
from .image_processor import ImageProcessor
from ..domain.ports import PDFProcessor, PDFRepository

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MuPDFProcessor(PDFProcessor):
    def __init__(self, repository: PDFRepository):
        self.repository = repository
        self.ai_processor = AIProcessor()
        self.file_system_processor = FileSystemProcessor()
        self.image_processor = ImageProcessor()

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        logger.info(f"Starting PDF processing for: {pdf_path}")

        pdf_folder_name = self.file_system_processor.get_pdf_folder_name(pdf_path)
        paths = self.file_system_processor.create_book_structure(base_output_dir, pdf_folder_name)
        histoire_dir = paths["histoire_dir"]
        images_dir = paths["images_dir"]
        metadata_dir = paths["metadata_dir"]

        try:
            doc = fitz.open(pdf_path)
            progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING, total_pages=len(doc))
            sections = []
            content_buffer = ""
            current_chapter_number = 0

            # Extract pages with text
            pages = SectionProcessor.extract_text_from_pdf(pdf_path)

            # Find the page where section 1 starts
            section_one_page = SectionProcessor.find_section(pages, section_number=1)
            if section_one_page:
                logger.info(f"Section 1 found on page {section_one_page}. Stopping extraction before this page.")

            for page in pages:
                page_num = page["num"]
                page_text = page["text"]

                if not page_text:
                    logger.warning(f"Page {page_num} is empty. Skipping...")
                    continue

                logger.debug(f"Processing page {page_num}")

                # Stop extraction before the section 1 page
                if section_one_page and page_num >= section_one_page:
                    logger.info(f"Stopping extraction before page {page_num} (section 1 detected).")
                    break

                # Detect new chapter titles
                is_new_chapter, chapter_title = await self.ai_processor.detect_chapter_with_ai(page_text)

                if is_new_chapter:
                    # Save current chapter content
                    if content_buffer.strip():
                        current_chapter_number += 1
                        self._save_chapter(
                            current_chapter_number, content_buffer.strip(), page_num, histoire_dir, pdf_folder_name, sections, progress
                        )
                    content_buffer = ""  # Reset buffer for new chapter

                # Add page content to buffer
                markdown_content = await self.ai_processor.analyze_multimodal_page({
                    "text": page_text,
                    "num": page_num,
                    "image_path": None
                })
                if markdown_content:
                    content_buffer += markdown_content + "\n"

            # Save the final chapter content if not empty
            if content_buffer.strip():
                current_chapter_number += 1
                self._save_chapter(
                    current_chapter_number, content_buffer.strip(), page_num, histoire_dir, pdf_folder_name, sections, progress
                )

            # Extract images
            logger.info("Extracting images...")
            images = self.image_processor.extract_images(pdf_path, images_dir, metadata_dir, pdf_folder_name, sections)
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
            logger.info(f"PDF processing completed: {len(sections)} sections, {len(images)} images.")
            return processed_pdf

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            raise

    def _save_chapter(
        self, chapter_number: int, content: str, page_num: int, histoire_dir: str, pdf_name: str, sections: List[Section], progress: ProcessingProgress
    ):
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
        section_file_path = os.path.join(histoire_dir, f"chapter_{chapter_number}.md")
        section = Section(
            number=chapter_number,
            content=content,
            page_number=page_num,
            file_path=section_file_path,
            pdf_name=pdf_name,
            is_chapter=True
        )
        self.repository.save_section(section)
        sections.append(section)
        progress.processed_sections += 1
        logger.info(f"Chapter {chapter_number} saved.")