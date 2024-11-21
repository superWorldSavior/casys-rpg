import re
from ..domain.entities import TextFormatting, FormattedText
from typing import List, Dict, Any

class TextFormatProcessor:
    def __init__(self):
        self.header_patterns = [
            r'^[A-Z][^a-z]{0,2}[A-Z].*$',  # All caps or nearly all caps
            r'^[A-Z][a-zA-Z\s]{0,50}$',  # Title case, not too long
        ]
        self.list_patterns = [
            r'^\s*[-•*]\s+',  # Bullet list items
            r'^\s*\d+\.\s+',  # Numbered list items
            r'^\s*[a-z]\)\s+',  # Letter list items
        ]

    def is_centered_text(self, text: str, line_spacing: float = None) -> bool:
        text = text.strip()
        if not text:
            return False

        # Skip long paragraphs
        if len(text) > 100:
            return False

        # Check for common centered text indicators
        indicators = [
            text.isupper(),  # All uppercase
            text.istitle() and len(text.split()) <= 7,  # Short title case phrases
            text.startswith('    ') or text.startswith('\t'),  # Indentation
            text.startswith('*') and text.endswith('*'),  # Asterisk wrapping
            bool(re.match(r'^[-—=]{3,}$', text)),  # Horizontal rules
            bool(re.match(r'^[A-Z][^.!?]*(?:[.!?]|\s)*$', text) and len(text) < 60),  # Short complete sentence
            bool(re.match(r'^(?:by|written by|translated by)\s+[A-Z][a-zA-Z\s.]+$', text, re.I)),  # Author attribution
            bool(re.match(r'^[A-Z\s]+$', text) and len(text) < 50)  # All caps short text
        ]

        return any(indicators)

    def detect_format_type(self, text: str) -> TextFormatting:
        """Detect the format type of a text block without AI assistance."""
        return self.detect_formatting(text, is_pre_section=False)

    def analyze_formatting(self, text: str) -> Dict[str, Any]:
        """Analyze text formatting attributes."""
        text = text.strip()
        metadata = {
            "is_centered": self.is_centered_text(text),
            "is_capitalized": text.isupper(),
            "is_title_case": text.istitle(),
            "indentation": len(text) - len(text.lstrip()),
            "line_length": len(text),
            "context": None,
            "list_type": None,
            "list_marker": None
        }

        # Enhanced list detection
        for pattern in self.list_patterns:
            if match := re.match(pattern, text):
                marker = match.group(0).strip()
                if re.match(r'^\d+\.', marker):
                    metadata["list_type"] = "numbered"
                    metadata["context"] = "numbered_list"
                    metadata["list_marker"] = marker
                elif re.match(r'^[a-z]\)', marker):
                    metadata["list_type"] = "letter"
                    metadata["context"] = "letter_list"
                    metadata["list_marker"] = marker
                else:
                    metadata["list_type"] = "bullet"
                    metadata["context"] = "bullet_list"
                    metadata["list_marker"] = marker
                break
        
        return metadata

    def detect_formatting(self, text: str, is_pre_section: bool = False) -> TextFormatting:
        text = text.strip()

        if not text:
            return TextFormatting.PARAGRAPH

        # Check for horizontal rules
        if re.match(r'^[-—=*]{3,}$', text):
            return TextFormatting.HEADER

        # Enhanced centered text detection for pre-sections
        if is_pre_section and self.is_centered_text(text):
            # Check for main title indicators
            if text.isupper() or (text.istitle() and len(text.split()) <= 5):
                return TextFormatting.HEADER
            return TextFormatting.SUBHEADER

        # Check for headers
        if any(re.match(pattern, text) for pattern in self.header_patterns):
            return TextFormatting.HEADER

        # Enhanced list detection
        for pattern in self.list_patterns:
            if re.match(pattern, text):
                return TextFormatting.LIST_ITEM

        # Check for code blocks
        if text.startswith('    ') or text.startswith('\t'):
            return TextFormatting.CODE

        # Check for quotes
        if text.startswith('>') or (text.startswith('"') and text.endswith('"')):
            return TextFormatting.QUOTE

        return TextFormatting.PARAGRAPH

    def process_text_block(self, text: str, is_pre_section: bool = False) -> List[FormattedText]:
        formatted_texts = []
        current_format = None
        current_text = []
        list_context = None

        for line in text.splitlines():
            line = line.strip()
            if not line:
                if current_text:
                    formatted_texts.append(
                        FormattedText(
                            text="\n".join(current_text),
                            format_type=current_format or TextFormatting.PARAGRAPH,
                            metadata=self.analyze_formatting("\n".join(current_text))
                        )
                    )
                    current_text = []
                    current_format = None
                    list_context = None
                continue

            format_type = self.detect_formatting(line, is_pre_section)
            metadata = self.analyze_formatting(line)

            # Handle list continuity
            if format_type == TextFormatting.LIST_ITEM:
                if list_context != metadata.get("context"):
                    if current_text:
                        formatted_texts.append(
                            FormattedText(
                                text="\n".join(current_text),
                                format_type=current_format or TextFormatting.PARAGRAPH,
                                metadata=self.analyze_formatting("\n".join(current_text))
                            )
                        )
                        current_text = []
                    list_context = metadata.get("context")
                current_format = format_type
                current_text.append(line)
                continue

            # Handle non-list blocks
            if format_type != current_format or format_type in [TextFormatting.HEADER, TextFormatting.SUBHEADER]:
                if current_text:
                    formatted_texts.append(
                        FormattedText(
                            text="\n".join(current_text),
                            format_type=current_format or TextFormatting.PARAGRAPH,
                            metadata=self.analyze_formatting("\n".join(current_text))
                        )
                    )
                    current_text = []
                current_format = format_type
                list_context = None

            current_text.append(line)

        # Add remaining text
        if current_text:
            formatted_texts.append(
                FormattedText(
                    text="\n".join(current_text),
                    format_type=current_format or TextFormatting.PARAGRAPH,
                    metadata=self.analyze_formatting("\n".join(current_text))
                )
            )

        return formatted_texts
