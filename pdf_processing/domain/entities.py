from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class ProcessingStatus(Enum):
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    EXTRACTING_SECTIONS = "extracting_sections"
    EXTRACTING_IMAGES = "extracting_images"
    SAVING_METADATA = "saving_metadata"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProcessingProgress:
    status: ProcessingStatus
    current_page: int = 0
    total_pages: int = 0
    error_message: Optional[str] = None
    processed_sections: int = 0
    processed_images: int = 0

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
    progress: ProcessingProgress = field(default_factory=lambda: ProcessingProgress(status=ProcessingStatus.NOT_STARTED))
