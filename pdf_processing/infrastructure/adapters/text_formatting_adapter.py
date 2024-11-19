import re
from typing import Tuple, Optional, List
from ...domain.ports import TextFormatDetector
from ...domain.entities import TextFormatting, FormattedText
from ..logging_config import StructuredLogger

class RegexTextFormatDetector(TextFormatDetector):
    def __init__(self):
        self.chapter_pattern = r'^\s*(\d+)\s*$'
        self.header_patterns = [
            r'^[A-Z][^a-z]{0,2}[A-Z].*$',  # All caps or nearly all caps
            r'^[A-Z][a-zA-Z\s]{0,50}$',     # Title case, not too long
        ]
        self.logger = StructuredLogger("TextFormatDetector")
    
    async def detect_chapter(self, text: str) -> Tuple[Optional[int], Optional[str]]:
        """Detect if text is a standalone number"""
        try:
            text = text.strip()
            match = re.match(self.chapter_pattern, text)
            if match:
                try:
                    chapter_num = int(match.group(1))
                    self.logger.info(f"Chapter number detected: {chapter_num}")
                    return chapter_num, ""
                except ValueError:
                    self.logger.warning(f"Invalid chapter number format: {text}")
            return None, None
        except Exception as e:
            self.logger.error("Error detecting chapter", e)
            return None, None
    
    def _is_centered_text(self, text: str) -> bool:
        """Enhanced centered text detection"""
        if not text or len(text) > 100:
            return False
            
        indicators = [
            text.isupper(),
            text.istitle() and len(text.split()) <= 7,
            text.startswith('    ') or text.startswith('\t'),
            text.startswith('*') and text.endswith('*'),
            bool(re.match(r'^[-—=]{3,}$', text)),
            bool(re.match(r'^[A-Z][^.!?]*(?:[.!?]|\s)*$', text) and len(text) < 60),
            bool(re.match(r'^(?:by|written by|translated by)\s+[A-Z][a-zA-Z\s.]+$', text, re.I)),
            bool(re.match(r'^[A-Z\s]+$', text) and len(text) < 50)
        ]
        
        return any(indicators)
    
    async def detect_formatting(self, text: str, is_pre_section: bool = False) -> FormattedText:
        """Enhanced formatting detection"""
        try:
            text = text.strip()
            if not text:
                return FormattedText(text="", format_type=TextFormatting.PARAGRAPH)
            
            # Check for horizontal rules
            if re.match(r'^[-—=*]{3,}$', text):
                return FormattedText(text=text, format_type=TextFormatting.HEADER)
            
            # Check for standalone section number
            chapter_num, _ = await self.detect_chapter(text)
            if chapter_num is not None and not is_pre_section:
                return FormattedText(text=text, format_type=TextFormatting.HEADER)
            
            # Enhanced centered text detection for pre-sections
            if is_pre_section and self._is_centered_text(text):
                if text.isupper() or (text.istitle() and len(text.split()) <= 5):
                    return FormattedText(text=text, format_type=TextFormatting.HEADER)
                return FormattedText(text=text, format_type=TextFormatting.SUBHEADER)
            
            # Check for headers
            if any(re.match(pattern, text) for pattern in self.header_patterns):
                return FormattedText(text=text, format_type=TextFormatting.HEADER)
            
            # Check for list items
            if re.match(r'^\s*[-•*]\s+', text) or re.match(r'^\s*\d+\.\s+.+', text):
                return FormattedText(text=text, format_type=TextFormatting.LIST_ITEM)
            
            # Check for code blocks
            if text.startswith('    ') or text.startswith('\t'):
                return FormattedText(text=text, format_type=TextFormatting.CODE)
            
            # Check for quotes
            if text.startswith('>') or (text.startswith('"') and text.endswith('"')):
                return FormattedText(text=text, format_type=TextFormatting.QUOTE)
            
            return FormattedText(text=text, format_type=TextFormatting.PARAGRAPH)
            
        except Exception as e:
            self.logger.error("Error detecting formatting", e)
            return FormattedText(text=text, format_type=TextFormatting.PARAGRAPH)
