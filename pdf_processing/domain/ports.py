"""Domain ports (interfaces) for PDF processing."""
from typing import Protocol, List, Optional, Any
from .entities import Section, PDFImage, ProcessedPDF

class PDFRepository(Protocol):
    """Repository interface for PDF-related data."""

    async def save_section(self, section: Section) -> None:
        """Save a section to storage."""
        ...

    async def save_image(self, image: PDFImage) -> None:
        """Save image metadata to storage."""
        ...

    async def save_metadata(self, processed_pdf: ProcessedPDF) -> None:
        """Save PDF processing metadata."""
        ...

    def format_to_markdown(self, formatted_blocks: Any) -> str:
        """Format blocks to markdown."""
        ...

class PDFProcessor(Protocol):
    """Interface for PDF processing operations."""

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from a PDF file."""
        ...

    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        """Extract images from a PDF file."""
        ...

class TextAnalyzer(Protocol):
    """Interface for text analysis operations."""


    async def detect_chapter_with_ai(self, text: str) -> tuple[bool, Optional[str]]:
        """Detect if text represents a chapter using AI."""
        return False, None


    def detect_formatting(self, text: str, is_pre_section: bool = False) -> str:
        """Detect text formatting type."""
        return ""  # Return empty string as default

class ImageAnalyzer(Protocol):
    """Interface for image analysis operations."""


    def process_image(self, image_data: bytes, page_number: int, pdf_name: str, output_path: str) -> PDFImage:
        """Process image data into a PDFImage entity."""
        raise NotImplementedError

class ProcessPDFUseCasePort(Protocol):
    """Interface for PDF processing use case."""

    async def execute(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Execute the PDF processing use case."""
        raise NotImplementedError
