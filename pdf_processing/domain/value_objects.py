"""Value objects for the PDF processing domain."""
from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class PageContent:
    """Represents the content of a page in a PDF."""
    page_number: int
    text: str
    images: List['ImageMetadata']

@dataclass(frozen=True)
class ImageMetadata:
    """Metadata for an image extracted from a PDF."""
    width: int
    height: int
    format: str
    location: str
