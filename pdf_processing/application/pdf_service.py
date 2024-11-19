import os
import json
from typing import Optional
from ..domain.ports import PDFProcessor, PDFRepository, AIContentAnalyzer, TextFormatDetector
from ..domain.entities import ProcessedPDF
from ..infrastructure.logging_config import StructuredLogger
from .validation import validate_pdf_processing_request, validate_processing_status, PDFValidationError

class PDFService:
    def __init__(
        self,
        processor: PDFProcessor,
        repository: PDFRepository,
        ai_analyzer: Optional[AIContentAnalyzer] = None,
        text_detector: Optional[TextFormatDetector] = None
    ):
        self.processor = processor
        self.repository = repository
        self.ai_analyzer = ai_analyzer
        self.text_detector = text_detector
        self.logger = StructuredLogger("PDFService")
    
    async def process_pdf(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        try:
            # Validate input
            self.logger.info("Validating PDF processing request", {
                "pdf_path": pdf_path,
                "base_output_dir": base_output_dir
            })
            
            errors = validate_pdf_processing_request(pdf_path, base_output_dir)
            if errors:
                raise PDFValidationError(errors)
            
            # Process the PDF
            self.logger.info("Starting PDF processing", {"pdf_path": pdf_path})
            processed_pdf = await self.processor.extract_sections(pdf_path, base_output_dir)
            
            # Create metadata directory
            pdf_folder_name = processed_pdf.pdf_name
            metadata_dir = os.path.join(base_output_dir, pdf_folder_name, "metadata")
            os.makedirs(metadata_dir, exist_ok=True)
            
            # Save sections
            self.logger.info("Saving sections", {"count": len(processed_pdf.sections)})
            for section in processed_pdf.sections:
                await self.repository.save_section(section)
            
            # Save images
            self.logger.info("Saving images", {"count": len(processed_pdf.images)})
            for image in processed_pdf.images:
                await self.repository.save_image(image)
            
            # Prepare and save book metadata
            book_metadata = {
                "title": pdf_folder_name,
                "total_sections": len(processed_pdf.sections),
                "total_images": len(processed_pdf.images),
                "sections": [{
                    "number": section.number,
                    "page_number": section.page_number,
                    "file_path": section.file_path
                } for section in processed_pdf.sections],
                "base_path": base_output_dir
            }
            
            metadata_path = os.path.join(metadata_dir, "book.json")
            with open(metadata_path, 'w') as f:
                json.dump(book_metadata, f, indent=2)
            
            # Save metadata to repository
            await self.repository.save_metadata(processed_pdf)
            
            self.logger.info("PDF processing completed successfully", {
                "pdf_name": pdf_folder_name,
                "total_sections": len(processed_pdf.sections),
                "total_images": len(processed_pdf.images)
            })
            
            return processed_pdf
            
        except PDFValidationError as e:
            self.logger.error("Validation error in PDF processing", e)
            raise
        except Exception as e:
            self.logger.error("Error processing PDF", e, {
                "pdf_path": pdf_path,
                "base_output_dir": base_output_dir
            })
            raise
    
    async def get_processing_status(self, pdf_name: str, base_path: str) -> dict:
        try:
            status = await self.repository.get_processing_status(pdf_name, base_path)
            
            # Validate status
            errors = validate_processing_status(status)
            if errors:
                raise PDFValidationError(errors)
            
            return status
        except Exception as e:
            self.logger.error("Error getting processing status", e, {
                "pdf_name": pdf_name,
                "base_path": base_path
            })
            raise
