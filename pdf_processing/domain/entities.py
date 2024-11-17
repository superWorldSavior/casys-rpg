from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Section:
    number: int
    content: str
    page_number: int
    file_path: str
    pdf_name: str

@dataclass
class PDFImage:
    page_number: int
    image_path: str
    pdf_name: str
    width: int
    height: int
    section_number: Optional[int] = None

@dataclass
class ProcessedPDF:
    sections: List[Section]
    images: List[PDFImage]
    pdf_name: str
    base_path: str
