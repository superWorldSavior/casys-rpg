from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from .entities import Section, FormattedText, ProcessedPDF

class SectionAnalyzer(ABC):
    @abstractmethod
    async def analyze_sections(self, text: str, page_number: int) -> List[Section]:
        """Analyze and extract sections from text content"""
        pass

class PreSectionAnalyzer(ABC):
    @abstractmethod
    async def analyze_pre_sections(self, text: str) -> List[Section]:
        """Analyze and extract pre-sections (content before numbered sections)"""
        pass

    @abstractmethod
    async def is_pre_section_content(self, text: str) -> bool:
        """Determine if the given text is pre-section content"""
        pass

class MetadataAnalyzer(ABC):
    @abstractmethod
    async def extract_metadata(self, processed_pdf: ProcessedPDF) -> dict:
        """Extract and structure metadata from processed PDF"""
        pass

    @abstractmethod
    async def analyze_section_metadata(self, section: Section) -> dict:
        """Analyze and extract metadata for a specific section"""
        pass
