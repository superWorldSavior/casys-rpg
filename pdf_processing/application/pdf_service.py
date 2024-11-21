import asyncio
import os
import json
import logging
from typing import List
from ..domain.ports import PDFProcessor, PDFRepository
from ..domain.entities import ProcessedPDF, Section, PDFImage, ProcessingProgress, ProcessingStatus

logger = logging.getLogger(__name__)


class PDFService:
    def __init__(self, processor: PDFProcessor, repository: PDFRepository):
        self.processor = processor
        self.repository = repository

    async def process_pdf(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        try:
            logger.info(f"Starting PDF processing for: {pdf_path}")

            # Process the PDF and get sections, images, and metadata
            processed_pdf = await self.processor.extract_sections(pdf_path, base_output_dir)
            metadata_dir = os.path.join(base_output_dir, processed_pdf.pdf_name, "metadata")
            os.makedirs(metadata_dir, exist_ok=True)

            # Save sections
            await self._save_sections(processed_pdf.sections)

            # Save images metadata
            await self._save_images(processed_pdf.images)

            # Save book metadata
            self._save_book_metadata(processed_pdf, base_output_dir)

            logger.info(f"Successfully completed processing PDF: {pdf_path}")
            return processed_pdf
        except Exception as e:
            logger.error(f"Error in PDF processing service: {e}")
            return self._handle_error(e, pdf_path)

    async def _save_sections(self, sections: List[Section]):
        """Save each section's content."""
        for section in sections:
            try:
                await self.repository.save_section(section)
                logger.info(f"Saved section {section.number}: {section.file_path}")
            except Exception as e:
                logger.error(f"Failed to save section {section.number}: {e}")

    async def _save_images(self, images: List[PDFImage]):
        """Save metadata for each image."""
        for image in images:
            try:
                await self.repository.save_image(image)
                logger.info(f"Saved image metadata for {image.image_path}")
            except Exception as e:
                logger.error(f"Failed to save image metadata: {e}")

    def _save_book_metadata(self, processed_pdf: ProcessedPDF, base_output_dir: str):
        """Save metadata for the entire book."""
        pdf_folder_name = processed_pdf.pdf_name
        metadata_dir = os.path.join(base_output_dir, pdf_folder_name, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)

        # Ensure status is always a string
        processing_status = (
            processed_pdf.progress.status.value
            if isinstance(processed_pdf.progress.status, ProcessingStatus)
            else processed_pdf.progress.status
        )

        book_metadata = {
            "title": pdf_folder_name,
            "total_sections": len(processed_pdf.sections),
            "total_images": len(processed_pdf.images),
            "sections": [self._serialize_section_metadata(section) for section in processed_pdf.sections],
            "base_path": base_output_dir,
            "processing_status": processing_status,
            "error_message": processed_pdf.progress.error_message,
        }

        metadata_path = os.path.join(metadata_dir, "book.json")
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(book_metadata, f, indent=2)
            logger.info(f"Saved book metadata to {metadata_path}")
        except Exception as e:
            logger.error(f"Failed to save book metadata: {e}")

    def _serialize_section_metadata(self, section: Section) -> dict:
        """Helper to serialize section metadata."""
        return {
            "number": section.number,
            "page_number": section.page_number,
            "file_path": section.file_path,
            "title": section.title,
        }

    def _handle_error(self, error: Exception, pdf_path: str) -> ProcessedPDF:
        """Handle errors during processing."""
        error_message = str(error)
        logger.error(f"Error while processing {pdf_path}: {error_message}")
        progress = ProcessingProgress(
            status=ProcessingStatus.FAILED,
            error_message=error_message
        )

        return ProcessedPDF(
            sections=[],
            images=[],
            pdf_name=os.path.basename(pdf_path),
            base_path="",
            progress=progress
        )

    def process_pdf_sync(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Synchronous wrapper for process_pdf."""
        try:
            return asyncio.run(self.process_pdf(pdf_path, base_output_dir))
        except RuntimeError as e:
            # Handle potential event loop issues for synchronous calls
            logger.error(f"RuntimeError during synchronous processing: {e}")
            return self._handle_error(e, pdf_path)
