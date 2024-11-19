"""API Controllers for PDF processing."""
import logging
from typing import Dict, Any
from ...application.services.pdf_service import PDFService
from ...application.dto.pdf_dto import PDFProcessingRequest, PDFProcessingResponse
from ...domain.entities import ProcessingStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFController:
    """Controller for PDF processing endpoints."""
    
    def __init__(self, pdf_service: PDFService):
        self.pdf_service = pdf_service
    
    async def process_pdf(self, pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """Process a PDF file and return the processing result."""
        try:
            logger.info(f"Received request to process PDF: {pdf_path}")
            request = PDFProcessingRequest(pdf_path=pdf_path, output_directory=output_dir)
            result = await self.pdf_service.process_pdf(request.pdf_path, request.output_directory)
            
            response = {
                "status": result.progress.status.value,
                "pdf_name": result.pdf_name,
                "total_sections": len(result.sections),
                "total_images": len(result.images),
                "base_path": result.base_path
            }
            
            logger.info(f"Successfully processed PDF: {pdf_path}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}", exc_info=True)
            return {
                "status": ProcessingStatus.FAILED.value,
                "error": str(e),
                "pdf_name": pdf_path,
                "total_sections": 0,
                "total_images": 0,
                "base_path": output_dir
            }
