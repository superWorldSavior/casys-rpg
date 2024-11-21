"""Domain ports (interfaces) for PDF processing."""
from typing import Protocol
from typing import List, Optional, Protocol
from .entities import Section, PDFImage, ProcessedPDF

class PDFRepository(Protocol):
    """Repository interface for PDF-related data."""


    async def save_section(self, section: Section) -> None:
        """Save a section to storage."""
        pass


    async def save_image(self, image: PDFImage) -> None:
        """Save image metadata to storage."""
        pass


    async def save_metadata(self, processed_pdf: ProcessedPDF) -> None:
        """Save PDF processing metadata."""
        pass

    def format_to_markdown(self, formatted_blocks):
        pass


class PDFProcessor(Protocol):
    """Interface for PDF processing operations."""


    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from a PDF file."""
        pass


    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        """Extract images from a PDF file."""
        pass

class TextAnalyzer(Protocol):
    """Interface for text analysis operations."""


    async def detect_chapter_with_ai(self, text: str) -> tuple[bool, Optional[str]]:
        """Detect if text represents a chapter using AI."""
        pass


    def detect_formatting(self, text: str, is_pre_section: bool = False) -> str:
        """Detect text formatting type."""
        pass

class ImageAnalyzer(Protocol):
    """Interface for image analysis operations."""


    def process_image(self, image_data: bytes, page_number: int, pdf_name: str, output_path: str) -> PDFImage:
        """Process image data into a PDFImage entity."""
        pass

class ProcessPDFUseCasePort(Protocol):
    """Interface for PDF processing use case."""

    async def execute(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Execute the PDF processing use case."""
        pass
