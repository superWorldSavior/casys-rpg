from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

class ProcessingStatus(Enum):
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    COMPLETED = "completed"
    FAILED = "failed"
    ANALYZING_STRUCTURE = "analyzing_structure"
    PROCESSING_PRE_SECTIONS = "processing_pre_sections"
    PROCESSING_NUMBERED_SECTIONS = "processing_numbered_sections"
    EXTRACTING_IMAGES = "extracting_images"
    SAVING_METADATA = "saving_metadata"

class TextFormatting(Enum):
    HEADER = "header"
    SUBHEADER = "subheader"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    ITEM = "item"  # Ajout du nouveau type
    QUOTE = "quote"
    CODE = "code"


@dataclass
class ProcessingProgress:
    status: ProcessingStatus
    current_page: int = 0
    total_pages: int = 0
    error_message: Optional[str] = None
    processed_sections: int = 0
    processed_images: int = 0

@dataclass
class FormattedText:
    text: str
    format_type: TextFormatting
    metadata: Dict = field(default_factory=dict)

@dataclass
class Section:
    number: int
    content: str
    page_number: int
    file_path: str
    pdf_name: str
    title: Optional[str] = None
    formatted_content: List[FormattedText] = field(default_factory=list)
    is_chapter: bool = False
    chapter_number: Optional[int] = None

    def to_dict(self):
        return {
            "number": self.number,
            "content": self.content,
            "page_number": self.page_number,
            "file_path": self.file_path,
            "pdf_name": self.pdf_name,
            "title": self.title,
            "formatted_content": [ft.__dict__ for ft in self.formatted_content],
            # Assuming FormattedText also needs conversion
            "is_chapter": self.is_chapter,
            "chapter_number": self.chapter_number
        }

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