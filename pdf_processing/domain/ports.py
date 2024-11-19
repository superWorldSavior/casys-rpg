"""Domain ports (interfaces) for PDF processing."""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Section, PDFImage, ProcessedPDF

class PDFRepository(ABC):
    """Repository interface for PDF-related data."""
    
    @abstractmethod
    async def save_section(self, section: Section) -> None:
        """Save a section to storage."""
        pass
    
    @abstractmethod
    async def save_image(self, image: PDFImage) -> None:
        """Save image metadata to storage."""
        pass
    
    @abstractmethod
    async def save_metadata(self, processed_pdf: ProcessedPDF) -> None:
        """Save PDF processing metadata."""
        pass

class PDFProcessor(ABC):
    """Interface for PDF processing operations."""
    
    @abstractmethod
    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from a PDF file."""
        pass

    @abstractmethod
    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        """Extract images from a PDF file."""
        pass

class TextAnalyzer(ABC):
    """Interface for text analysis operations."""
    
    @abstractmethod
    async def detect_chapter_with_ai(self, text: str) -> tuple[bool, Optional[str]]:
        """Detect if text represents a chapter using AI."""
        pass
    
    @abstractmethod
    def detect_formatting(self, text: str, is_pre_section: bool = False) -> str:
        """Detect text formatting type."""
        pass

class ImageAnalyzer(ABC):
    """Interface for image analysis operations."""
    
    @abstractmethod
    def process_image(self, image_data: bytes, page_number: int, pdf_name: str, output_path: str) -> PDFImage:
        """Process image data into a PDFImage entity."""
        pass
