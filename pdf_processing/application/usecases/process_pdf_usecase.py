"""Core PDF processing use case implementation."""
from typing import Protocol
from ...domain.entities import ProcessedPDF, ProcessingStatus
from ...domain.ports import PDFProcessor, PDFRepository, ProcessPDFUseCasePort

class ProcessPDFUseCase(ProcessPDFUseCasePort):
    """Use case for processing PDF files."""
    
    def __init__(
        self,
        pdf_processor: PDFProcessor,
        pdf_repository: PDFRepository
    ):
        self.pdf_processor = pdf_processor
        self.pdf_repository = pdf_repository
    
    async def execute(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Execute the PDF processing use case."""
        try:
            # Extract content from PDF
            processed_pdf = await self.pdf_processor.extract_sections(pdf_path, base_output_dir)
            
            # Extract and process images
            processed_pdf.images = await self.pdf_processor.extract_images(pdf_path, base_output_dir)
            
            # Save all content
            for section in processed_pdf.sections:
                await self.pdf_repository.save_section(section)
            
            for image in processed_pdf.images:
                await self.pdf_repository.save_image(image)
            
            # Save overall metadata
            await self.pdf_repository.save_metadata(processed_pdf)
            
            return processed_pdf
            
        except Exception as e:
            # Update processing status to failed if we have a processed_pdf
            if 'processed_pdf' in locals():
                processed_pdf.progress.status = ProcessingStatus.FAILED
                processed_pdf.progress.error_message = str(e)
                await self.pdf_repository.save_metadata(processed_pdf)
            raise
