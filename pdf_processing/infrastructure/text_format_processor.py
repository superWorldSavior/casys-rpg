import re
from ..domain.entities import TextFormatting, FormattedText
from typing import List, Dict, Any

class TextFormatProcessor:
    def __init__(self):
        self.header_patterns = [
            r'^[A-Z][^a-z]{0,2}[A-Z].*$',  # All caps or nearly all caps
            r'^[A-Z][a-zA-Z\s]{0,50}$',  # Title case, not too long
        ]

    def is_centered_text(self, text: str, line_spacing: float = None) -> bool:
        text = text.strip()
        if not text:
            return False

        # Skip long paragraphs
        if len(text) > 100:
            return False

        # Enhanced centered text indicators for pre-section content
        indicators = [
            text.isupper() and len(text) < 60,  # All uppercase, reasonably short
            text.istitle() and len(text.split()) <= 7,  # Short title case phrases
            text.startswith('    ') or text.startswith('\t'),  # Indentation
            text.startswith('*') and text.endswith('*'),  # Asterisk wrapping
            bool(re.match(r'^[-—=]{3,}$', text)),  # Horizontal rules
            bool(re.match(r'^[A-Z][^.!?]*(?:[.!?]|\s)*$', text) and len(text) < 60),  # Short complete sentence
            bool(re.match(r'^(?:by|written by|translated by)\s+[A-Z][a-zA-Z\s.]+$', text, re.I)),  # Author attribution
            bool(re.match(r'^[A-Z\s]+$', text) and len(text) < 50),  # All caps short text
            bool(re.match(r'^Chapter\s+[IVXLCDM]+|[0-9]+', text, re.I))  # Chapter headings
        ]

        return any(indicators)

    def detect_format_type(self, text: str, is_pre_section: bool = False) -> TextFormatting:
        """Detect the format type of a text block with enhanced pre-section support."""
        text = text.strip()

        if not text:
            return TextFormatting.PARAGRAPH

        # Check for horizontal rules
        if re.match(r'^[-—=*]{3,}$', text):
            return TextFormatting.HEADER

        # Enhanced centered text detection for pre-sections
        if is_pre_section and self.is_centered_text(text):
            # Check for main title or chapter header indicators
            if text.isupper() or (text.istitle() and len(text.split()) <= 5) or re.match(r'^Chapter\s+[IVXLCDM]+|[0-9]+', text, re.I):
                return TextFormatting.CENTERED_HEADER
            return TextFormatting.SUBHEADER

        # Check for headers
        if any(re.match(pattern, text) for pattern in self.header_patterns):
            return TextFormatting.HEADER

        # Check for list items
        if re.match(r'^\s*[-•*]\s+', text) or re.match(r'^\s*\d+\.\s+.+', text):
            return TextFormatting.LIST_ITEM

        # Check for code blocks
        if text.startswith('    ') or text.startswith('\t'):
            return TextFormatting.CODE

        # Check for quotes
        if text.startswith('>') or (text.startswith('"') and text.endswith('"')):
            return TextFormatting.QUOTE

        return TextFormatting.PARAGRAPH

    def analyze_formatting(self, text: str, is_pre_section: bool = False) -> Dict[str, Any]:
        """Analyze text formatting attributes with enhanced pre-section support."""
        metadata = {
            "is_centered": self.is_centered_text(text),
            "is_capitalized": text.isupper(),
            "is_title_case": text.istitle(),
            "indentation": len(text) - len(text.lstrip()),
            "line_length": len(text),
            "is_pre_section": is_pre_section
        }

        # Enhanced list detection
        if re.match(r'^\s*[-•*]\s+', text):
            metadata["list_type"] = "bullet"
        elif re.match(r'^\s*\d+\.\s+', text):
            metadata["list_type"] = "numbered"
        elif re.match(r'^\s*[a-z]\)\s+', text):
            metadata["list_type"] = "alphabetical"
        
        # Detect special formatting
        metadata["formatting"] = []
        if '*' in text:
            metadata["formatting"].append("emphasis")
        if '__' in text or text.isupper():
            metadata["formatting"].append("strong")
        if '`' in text:
            metadata["formatting"].append("code")
            
        return metadata

    def process_text_block(self, text: str, is_pre_section: bool = False) -> List[FormattedText]:
        formatted_texts = []
        current_format = None
        current_text = []

        for line in text.splitlines():
            line = line.strip()
            if not line:
                if current_text:
                    formatted_texts.append(
                        FormattedText(
                            text="\n".join(current_text),
                            format_type=current_format or TextFormatting.PARAGRAPH,
                            metadata=self.analyze_formatting("\n".join(current_text), is_pre_section)
                        )
                    )
                    current_text = []
                    current_format = None
                continue

            format_type = self.detect_format_type(line, is_pre_section)

            # Always start a new block for headers, subheaders, and centered headers
            if (format_type != current_format or 
                format_type in [TextFormatting.HEADER, TextFormatting.SUBHEADER, TextFormatting.CENTERED_HEADER]):
                if current_text:
                    formatted_texts.append(
                        FormattedText(
                            text="\n".join(current_text),
                            format_type=current_format or TextFormatting.PARAGRAPH,
                            metadata=self.analyze_formatting("\n".join(current_text), is_pre_section)
                        )
                    )
                    current_text = []
                current_format = format_type

            current_text.append(line)

        if current_text:
            formatted_texts.append(
                FormattedText(
                    text="\n".join(current_text),
                    format_type=current_format or TextFormatting.PARAGRAPH,
                    metadata=self.analyze_formatting("\n".join(current_text), is_pre_section)
                )
            )

        return formatted_texts
