from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class PDFMetadata:
    title: Optional[str]
    author: Optional[str]
    subject: Optional[str]
    keywords: Optional[str]
    creator: Optional[str]
    producer: Optional[str]
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]
    page_count: int
    file_size: int
    pdf_version: str
    is_encrypted: bool
    page_dimensions: List[tuple[float, float]]  # List of (width, height) for each page

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

@dataclass
class ProcessedPDF:
    sections: List[Section]
    images: List[PDFImage]
    pdf_name: str
    base_path: str
    metadata: Optional[PDFMetadata] = None
