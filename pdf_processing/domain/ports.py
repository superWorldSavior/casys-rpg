from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Section, PDFImage, ProcessedPDF

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

class PDFProcessor(ABC):
    @abstractmethod
    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        pass

    @abstractmethod
    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        pass
