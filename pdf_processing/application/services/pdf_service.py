"""Application service for PDF processing."""
import os
from typing import Protocol
from ...domain.ports import PDFProcessor, PDFRepository
from ...domain.entities import ProcessedPDF, ProcessingStatus

class PDFService:
    """Service for processing PDF documents."""
    
    def __init__(self, processor: PDFProcessor, repository: PDFRepository):
        """Initialize service with required dependencies."""
        self.processor = processor
        self.repository = repository
    
    async def process_pdf(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Process a PDF file and store its contents."""
        try:
            # Extract content from PDF
            processed_pdf = await self.processor.extract_sections(pdf_path, base_output_dir)
            
            # Extract and process images
            processed_pdf.images = await self.processor.extract_images(pdf_path, base_output_dir)
            
            # Save all content
            for section in processed_pdf.sections:
                await self.repository.save_section(section)
            
            for image in processed_pdf.images:
                await self.repository.save_image(image)
            
            # Save overall metadata
            await self.repository.save_metadata(processed_pdf)
            
            return processed_pdf
            
        except Exception as e:
            # Update processing status to failed
            if processed_pdf:
                processed_pdf.progress.status = ProcessingStatus.FAILED
                processed_pdf.progress.error_message = str(e)
                await self.repository.save_metadata(processed_pdf)
            raise
