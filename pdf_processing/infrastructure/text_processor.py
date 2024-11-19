from typing import List
from ..domain.entities import FormattedText, TextFormatting, ProcessingError
import re

class TextProcessor:
    def __init__(self):
        self.paragraph_min_length = 50

    def process_text_block(self, text: str, is_pre_section: bool = False) -> List[FormattedText]:
        """Process a block of text and return formatted text blocks."""
        try:
            lines = text.splitlines()
            formatted_blocks = []
            current_block = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_block:
                        formatted_blocks.append(self._create_formatted_block(
                            "\n".join(current_block), is_pre_section))
                        current_block = []
                    continue
                
                current_block.append(line)
            
            if current_block:
                formatted_blocks.append(self._create_formatted_block(
                    "\n".join(current_block), is_pre_section))
            
            return formatted_blocks
        except Exception as e:
            raise ProcessingError(f"Error processing text block: {str(e)}")

    def _create_formatted_block(self, text: str, is_pre_section: bool) -> FormattedText:
        """Create a formatted text block with appropriate formatting type."""
        text = text.strip()
        
        # Determine formatting type
        if is_pre_section:
            if len(text) < self.paragraph_min_length:
                return FormattedText(text=text, format_type=TextFormatting.HEADER)
            return FormattedText(text=text, format_type=TextFormatting.PARAGRAPH)
        
        # Check for different formatting types
        if text.startswith(">"):
            return FormattedText(text=text[1:].strip(), format_type=TextFormatting.QUOTE)
        elif text.startswith(("- ", "* ", "• ")):
            return FormattedText(text=text, format_type=TextFormatting.LIST_ITEM)
        elif len(text) < self.paragraph_min_length and text.isupper():
            return FormattedText(text=text, format_type=TextFormatting.HEADER)
        elif len(text) < self.paragraph_min_length:
            return FormattedText(text=text, format_type=TextFormatting.SUBHEADER)
        
        return FormattedText(text=text, format_type=TextFormatting.PARAGRAPH)
