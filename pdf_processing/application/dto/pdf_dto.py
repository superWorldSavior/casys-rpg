"""Data Transfer Objects for PDF processing."""
from dataclasses import dataclass
from typing import List, Optional
from ...domain.entities import ProcessingStatus

@dataclass
class PDFProcessingRequest:
    """DTO for PDF processing request."""
    pdf_path: str
    output_directory: str
    options: Optional[dict] = None

@dataclass
class PDFProcessingResponse:
    """DTO for PDF processing response."""
    status: ProcessingStatus
    pdf_name: str
    total_sections: int
    total_images: int
    base_path: str
    error_message: Optional[str] = None
