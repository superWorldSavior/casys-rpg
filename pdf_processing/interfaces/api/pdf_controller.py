"""API Controllers for PDF processing."""
from typing import Dict, Any
from ...application.pdf_service import PDFService
from ...application.dto.pdf_dto import PDFProcessingRequest, PDFProcessingResponse

class PDFController:
    """Controller for PDF processing endpoints."""
    
    def __init__(self, pdf_service: PDFService):
        self.pdf_service = pdf_service
    
    async def process_pdf(self, pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """Process a PDF file and return the processing result."""
        request = PDFProcessingRequest(pdf_path=pdf_path, output_directory=output_dir)
        result = await self.pdf_service.process_pdf(request.pdf_path, request.output_directory)
        
        return {
            "status": result.progress.status.value,
            "pdf_name": result.pdf_name,
            "total_sections": len(result.sections),
            "total_images": len(result.images),
            "base_path": result.base_path
        }
