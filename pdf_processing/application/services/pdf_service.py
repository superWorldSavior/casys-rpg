"""Application service for PDF processing."""
import logging
from typing import Optional
from ...domain.ports import ProcessPDFUseCasePort
from ...domain.entities import ProcessedPDF, ProcessingStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessingError(Exception):
    """Custom exception for PDF processing errors."""
    pass

class PDFService:
    """Service for processing PDF documents."""
    
    def __init__(self, process_pdf_usecase: ProcessPDFUseCasePort):
        """Initialize service with required use case."""
        self.process_pdf_usecase = process_pdf_usecase
    
    async def process_pdf(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Process a PDF file using the process PDF use case."""
        try:
            logger.info(f"Starting PDF processing for file: {pdf_path}")
            processed_pdf = await self.process_pdf_usecase.execute(pdf_path, base_output_dir)
            logger.info(f"Successfully processed PDF: {processed_pdf.pdf_name}")
            return processed_pdf
            
        except Exception as e:
            error_msg = f"Error processing PDF {pdf_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise PDFProcessingError(error_msg) from e
