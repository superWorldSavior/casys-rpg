import fitz  # PyMuPDF
import logging
import os
from typing import List, Dict

from ..domain.entities import Section, ProcessedPDF, ProcessingProgress, ProcessingStatus
from .ai_processor import AIProcessor
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
            logger.info(f"PDF opened. Total pages: {len(doc)}")

            # Préparer les pages pour analyse
            pages = [{"num": i + 1, "text": doc[i].get_text("text").strip()} for i in range(len(doc))]

            # Trouver la page où commence la section 1
            section_one_page = await self.ai_processor.find_section(pages, section_number=1)
            if section_one_page:
                logger.info(f"Section 1 found on page {section_one_page}. Stopping extraction before this page.")

            for page_num, page in enumerate(pages, start=1):
                page_text = page["text"]

                if not page_text:
                    logger.warning(f"Page {page_num} is empty. Skipping...")
                    continue

                logger.debug(f"Processing page {page_num}")

                # Arrêter l'extraction avant la page de la section 1
                if section_one_page and page_num >= section_one_page:
                    logger.info(f"Stopping extraction before page {page_num} (section 1 detected).")
                    break

                # Analyze page content
                markdown_content = await self.ai_processor.analyze_multimodal_page({
                    "text": page_text,
                    "num": page_num,
                    "image_path": None
                })

                if not markdown_content:
                    logger.warning(f"Skipping page {page_num} due to empty Markdown content.")
                    continue

                # Save the chapter
                section_file_path = os.path.join(histoire_dir, f"chapter_{len(sections) + 1}.md")
                section = Section(
                    number=len(sections) + 1,
                    content=markdown_content,
                    page_number=page_num,
                    file_path=section_file_path,
                    pdf_name=pdf_folder_name,
                    is_chapter=True
                )
                await self.repository.save_section(section)
                sections.append(section)
                progress.processed_sections += 1

            logger.info("Extracting images...")
            images = self.image_processor.extract_images(pdf_path, images_dir, metadata_dir, pdf_folder_name, sections)
            for image in images:
                await self.repository.save_image(image)
            progress.processed_images = len(images)

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