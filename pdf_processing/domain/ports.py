from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from .entities import Section, PDFImage, ProcessedPDF, FormattedText

class PDFRepository(ABC):
    @abstractmethod
    async def save_section(self, section: Section) -> None:
        pass
    
    @abstractmethod
    async def save_image(self, image: PDFImage) -> None:
        pass
    
    @abstractmethod
    async def save_metadata(self, processed_pdf: ProcessedPDF) -> None:
        pass

    @abstractmethod
    async def get_processing_status(self, pdf_name: str, base_path: str) -> dict:
        pass

class PDFProcessor(ABC):
    @abstractmethod
    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        pass

    @abstractmethod
    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections", sections: Optional[List[Section]] = None) -> List[PDFImage]:
        pass

class TextFormatDetector(ABC):
    @abstractmethod
    async def detect_chapter(self, text: str) -> Tuple[Optional[int], Optional[str]]:
        pass

    @abstractmethod
    async def detect_formatting(self, text: str, is_pre_section: bool = False) -> FormattedText:
        pass

class AIContentAnalyzer(ABC):
    @abstractmethod
    async def analyze_chapter_break(self, text: str) -> Tuple[bool, Optional[str]]:
        """Analyze text to determine if it represents a chapter break and extract title"""
        pass

class PDFStorage(ABC):
    @abstractmethod
    async def save_file(self, content: bytes, path: str) -> None:
        pass

    @abstractmethod
    async def load_file(self, path: str) -> bytes:
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> None:
        pass
