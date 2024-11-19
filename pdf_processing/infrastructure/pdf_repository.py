import os
import json
import logging
from typing import List
from ..domain.ports import PDFRepository
from ..domain.entities import Section, PDFImage, ProcessedPDF, ProcessingStatus

logger = logging.getLogger(__name__)

class FileSystemPDFRepository(PDFRepository):
    async def save_section(self, section: Section) -> None:
        """Save a section with proper validation and error handling"""
        try:
            # Verify file path exists
            section_dir = os.path.dirname(section.file_path)
            if not os.path.exists(section_dir):
                os.makedirs(section_dir, exist_ok=True)
                logger.info(f"Created section directory: {section_dir}")

            # Save section with proper formatting
            with open(section.file_path, "w", encoding="utf-8") as f:
                f.write(f"# Section {section.number}\n\n")
                if section.title:
                    f.write(f"## {section.title}\n\n")
                f.write(section.content.strip())
            
            logger.info(f"Successfully saved section {section.number} to {section.file_path}")
        except Exception as e:
            logger.error(f"Error saving section {section.number}: {e}")
            raise

    async def save_image(self, image: PDFImage) -> None:
        """Save image metadata with proper directory validation"""
        try:
            image_dir = os.path.dirname(image.image_path)
            os.makedirs(image_dir, exist_ok=True)
            logger.info(f"Image directory validated: {image_dir}")
            # The actual image saving is handled by the processor
        except Exception as e:
            logger.error(f"Error preparing image directory for {image.image_path}: {e}")
            raise

    async def save_metadata(self, processed_pdf: ProcessedPDF) -> None:
        """Save metadata with comprehensive validation and section tracking"""
        try:
            # Create metadata directory
            metadata_dir = os.path.join(
                processed_pdf.base_path,
                processed_pdf.pdf_name,
                'metadata'
            )
            os.makedirs(metadata_dir, exist_ok=True)
            logger.info(f"Created metadata directory: {metadata_dir}")

            # Validate sections
            if not processed_pdf.sections:
                logger.warning(f"No sections found for PDF: {processed_pdf.pdf_name}")
            
            # Track section numbers for validation
            section_numbers = set()
            pre_section_count = 0
            numbered_section_count = 0

            # Prepare comprehensive sections metadata
            sections_metadata = []
            for section in processed_pdf.sections:
                # Validate section number uniqueness
                if section.number in section_numbers:
                    logger.warning(f"Duplicate section number found: {section.number}")
                section_numbers.add(section.number)

                # Count section types
                if section.is_chapter:
                    pre_section_count += 1
                else:
                    numbered_section_count += 1

                # Create section metadata
                section_metadata = {
                    'section_number': section.number,
                    'chapter_number': section.chapter_number,
                    'file_path': os.path.relpath(section.file_path, processed_pdf.base_path),
                    'pdf_name': section.pdf_name,
                    'page_number': section.page_number,
                    'is_chapter': section.is_chapter,
                    'title': section.title
                }
                sections_metadata.append(section_metadata)

            # Save sections metadata with stats
            sections_metadata_with_stats = {
                'sections': sections_metadata,
                'total_sections': len(processed_pdf.sections),
                'pre_section_count': pre_section_count,
                'numbered_section_count': numbered_section_count
            }
            
            sections_metadata_path = os.path.join(metadata_dir, 'sections.json')
            with open(sections_metadata_path, 'w', encoding='utf-8') as f:
                json.dump(sections_metadata_with_stats, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved sections metadata: {len(sections_metadata)} sections")

            # Save progress metadata
            progress_metadata = {
                'status': processed_pdf.progress.status.value,
                'current_page': processed_pdf.progress.current_page,
                'total_pages': processed_pdf.progress.total_pages,
                'processed_sections': processed_pdf.progress.processed_sections,
                'processed_images': processed_pdf.progress.processed_images,
                'error_message': processed_pdf.progress.error_message,
                'section_counts': {
                    'total': len(processed_pdf.sections),
                    'pre_sections': pre_section_count,
                    'numbered_sections': numbered_section_count
                }
            }
            
            progress_metadata_path = os.path.join(metadata_dir, 'progress.json')
            with open(progress_metadata_path, 'w', encoding='utf-8') as f:
                json.dump(progress_metadata, f, ensure_ascii=False, indent=2)
            logger.info("Saved progress metadata with section counts")

        except Exception as e:
            logger.error(f"Error saving metadata for {processed_pdf.pdf_name}: {e}")
            raise

    async def get_processing_status(self, pdf_name: str, base_path: str) -> dict:
        """Get processing status with proper error handling"""
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
