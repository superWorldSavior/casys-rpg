import logging
from typing import List
from ..domain.entities import Section, FormattedText, TextFormatting
import os

logger = logging.getLogger(__name__)

class SectionProcessor:
    def __init__(self):
        self.text_formatting = TextFormatting

    def save_section(self, section_num: int, blocks: List[FormattedText], output_dir: str, 
                    pdf_name: str, is_chapter: bool = False) -> Section:
        """Save a section to a file with proper formatting."""
        try:
            file_path = os.path.join(output_dir, f"{section_num}.md")
            content = []
            
            # Process blocks to maintain formatting
            for block in blocks:
                if block.format_type == TextFormatting.HEADER:
                    # Check if header should have # prefix
                    if block.metadata.get("should_prefix_header", False):
                        content.append(f"# {block.text}")
                    else:
                        content.append(block.text)
                elif block.format_type == TextFormatting.SUBHEADER:
                    content.append(f"## {block.text}")
                elif block.format_type == TextFormatting.LIST_ITEM:
                    indent = "  " * block.metadata.get("indentation_level", 0)
                    content.append(f"{indent}- {block.text}")
                elif block.format_type == TextFormatting.QUOTE:
                    content.append(f"> {block.text}")
                elif block.format_type == TextFormatting.CODE:
                    content.append(f"```\n{block.text}\n```")
                else:  # PARAGRAPH
                    content.append(block.text)
            
            formatted_content = "\n\n".join(content)
            page_number = blocks[0].metadata.get("page_number", 0) if blocks else 0
            
            os.makedirs(output_dir, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(formatted_content)
            
            logger.info(f"Saved {'chapter' if is_chapter else 'section'} {section_num} to {file_path}")
            return Section(
                number=section_num,
                content=formatted_content,
                page_number=page_number,
                file_path=file_path,
                pdf_name=pdf_name,
                is_chapter=is_chapter,
                formatted_content=blocks
            )
        except Exception as e:
            logger.error(f"Error saving section {section_num}: {e}")
            raise
