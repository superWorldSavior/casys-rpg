import os
import json
import logging
from typing import List
from ..domain.ports import PDFRepository
from ..domain.entities import Section, PDFImage, ProcessedPDF, ProcessingStatus

logger = logging.getLogger(__name__)

class FileSystemPDFRepository(PDFRepository):
    async def save_section(self, section: Section) -> None:
        """Save a section directly using the content from AI."""
        try:
            # Ensure section directory exists
            section_dir = os.path.dirname(section.file_path)
            if not os.path.exists(section_dir):
                os.makedirs(section_dir, exist_ok=True)
                logger.info(f"Created section directory: {section_dir}")

            # Save the section content to a Markdown file
            with open(section.file_path, "w", encoding="utf-8") as f:
                if section.title:
                    f.write(f"# {section.title}\n\n")  # Optionally prepend the title
                f.write(section.content)  # Directly write the content
                logger.debug(f"Section content saved to file: {section.file_path}")

            logger.info(f"Successfully saved section {section.number} to {section.file_path}")
        except Exception as e:
            logger.error(f"Error saving section {section.number}: {e}")
            raise

    async def save_image(self, image: PDFImage) -> None:
        """Save image metadata with proper directory validation."""
        try:
            image_dir = os.path.dirname(image.image_path)
            if not os.path.exists(image_dir):
                os.makedirs(image_dir, exist_ok=True)
                logger.info(f"Created image directory: {image_dir}")
            # Log the image metadata saving
            logger.debug(f"Prepared to save image metadata for {image.image_path}")
        except Exception as e:
            logger.error(f"Error preparing image directory for {image.image_path}: {e}")
            raise

    async def save_metadata(self, processed_pdf: ProcessedPDF) -> None:
        """Save metadata with comprehensive validation and section tracking."""
        try:
            # Create metadata directory
            metadata_dir = os.path.join(
                processed_pdf.base_path,
                processed_pdf.pdf_name,
                'metadata'
            )
            os.makedirs(metadata_dir, exist_ok=True)
            logger.info(f"Created metadata directory: {metadata_dir}")

            # Prepare comprehensive sections metadata
            sections_metadata = [
                {
                    'section_number': section.number,
                    'chapter_number': section.chapter_number,
                    'file_path': os.path.relpath(section.file_path, processed_pdf.base_path),
                    'pdf_name': section.pdf_name,
                    'page_number': section.page_number,
                    'is_chapter': section.is_chapter,
                    'title': section.title
                }
                for section in processed_pdf.sections
            ]

            # Save sections metadata to JSON
            sections_metadata_path = os.path.join(metadata_dir, 'sections.json')
            with open(sections_metadata_path, 'w', encoding='utf-8') as f:
                json.dump({'sections': sections_metadata}, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved sections metadata: {len(sections_metadata)} sections")

            # Save progress metadata
            progress_metadata = {
                'status': processed_pdf.progress.status.value,
                'current_page': processed_pdf.progress.current_page,
                'total_pages': processed_pdf.progress.total_pages,
                'processed_sections': processed_pdf.progress.processed_sections,
                'processed_images': processed_pdf.progress.processed_images,
                'error_message': processed_pdf.progress.error_message,
            }

            progress_metadata_path = os.path.join(metadata_dir, 'progress.json')
            with open(progress_metadata_path, 'w', encoding='utf-8') as f:
                json.dump(progress_metadata, f, ensure_ascii=False, indent=2)
            logger.info("Saved progress metadata with section counts")
        except Exception as e:
            logger.error(f"Error saving metadata for {processed_pdf.pdf_name}: {e}")
            raise

    async def get_processing_status(self, pdf_name: str, base_path: str) -> dict:
        """Get processing status with proper error handling."""
        progress_path = os.path.join(base_path, pdf_name, 'metadata', 'progress.json')
        try:
            with open(progress_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Progress file not found for {pdf_name}")
            return {
                'status': ProcessingStatus.NOT_STARTED.value,
                'current_page': 0,
                'total_pages': 0,
                'processed_sections': 0,
                'processed_images': 0,
                'error_message': None
            }
        except Exception as e:
            logger.error(f"Error reading progress for {pdf_name}: {e}")
            raise
