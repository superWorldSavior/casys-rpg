import asyncio
import os
import json
import logging
from ..domain.ports import PDFProcessor, PDFRepository
from ..domain.entities import ProcessedPDF

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self, processor: PDFProcessor, repository: PDFRepository):
        self.processor = processor
        self.repository = repository

    async def process_pdf(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        try:
            logger.info(f"Starting PDF processing for: {pdf_path}")
            processed_pdf = await self.processor.extract_sections(pdf_path, base_output_dir)

            pdf_folder_name = processed_pdf.pdf_name
            metadata_dir = os.path.join(base_output_dir, pdf_folder_name, "metadata")
            os.makedirs(metadata_dir, exist_ok=True)

            for section in processed_pdf.sections:
                try:
                    await self.repository.save_section(section)
                except Exception as e:
                    logger.error(f"Error saving section {section.number}: {e}")
                    raise

            for image in processed_pdf.images:
                try:
                    await self.repository.save_image(image)
                except Exception as e:
                    logger.error(f"Error saving image metadata: {e}")
                    raise

            book_metadata = {
                "title": pdf_folder_name,
                "total_sections": len(processed_pdf.sections),
                "total_images": len(processed_pdf.images),
                "sections": [{
                    "number": section.number,
                    "page_number": section.page_number,
                    "file_path": section.file_path
                } for section in processed_pdf.sections],
                "base_path": base_output_dir,
                "processing_status": "completed"
            }

            metadata_path = os.path.join(metadata_dir, "book.json")
            with open(metadata_path, 'w') as f:
                json.dump(book_metadata, f, indent=2)

            await self.repository.save_metadata(processed_pdf)
            logger.info(f"Successfully completed processing PDF: {pdf_path}")

            return processed_pdf
        except Exception as e:
            logger.error(f"Error in PDF processing service: {e}")
            if 'processed_pdf' in locals():
                processed_pdf.progress.error_message = str(e)
                try:
                    await self.repository.save_metadata(processed_pdf)
                except Exception as save_error:
                    logger.error(f"Error saving error state metadata: {save_error}")
            raise