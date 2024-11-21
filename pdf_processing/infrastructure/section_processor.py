import logging
import re
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
            previous_format = None
            previous_context = None
            in_combat_rules = False
            in_list = False
            list_indent_level = 0
            
            for block in blocks:
                # Determine block context and format
                current_context = block.metadata.get("context")
                current_format = block.format_type
                text = block.text.strip()
                
                if not text:
                    continue

                # Detect combat rules section
                if "COMBAT RULES" in text.upper():
                    in_combat_rules = True
                    if content:  # Add extra spacing before combat rules
                        content.append("")
                    content.append("# COMBAT RULES")
                    content.append("")  # Extra spacing after header
                    previous_format = current_format
                    previous_context = current_context
                    continue

                # Handle context transitions
                if previous_context != current_context and previous_context is not None:
                    content.append("")

                # Process block based on format type
                if current_format == TextFormatting.HEADER:
                    # Add spacing before headers if needed
                    if content and not content[-1].isspace():
                        content.append("")
                    in_list = False
                    # Don't add section numbers as headers
                    if not re.match(r'^\d+\.?\s*$', text):
                        if block.metadata.get("should_prefix_header", True):
                            content.append(f"# {text}")
                        else:
                            content.append(text)
                    content.append("")  # Add spacing after header

                elif current_format == TextFormatting.SUBHEADER:
                    # Add spacing before subheaders
                    if content and not content[-1].isspace():
                        content.append("")
                    in_list = False
                    if block.metadata.get("should_prefix_header", True):
                        content.append(f"## {text}")
                    else:
                        content.append(text)
                    content.append("")  # Add spacing after subheader

                elif current_format == TextFormatting.LIST_ITEM:
                    # Calculate indentation
                    raw_indent = block.metadata.get("indentation_level", 0)
                    indent_level = raw_indent // 4  # Normalize indentation
                    indent = "  " * indent_level
                    
                    # Handle list start or context change
                    if not in_list or previous_context != current_context:
                        content.append("")  # Add spacing before list
                        in_list = True
                        list_indent_level = indent_level
                    elif indent_level < list_indent_level:  # New list level
                        content.append("")
                        list_indent_level = indent_level
                    
                    # Choose list marker based on context
                    if in_combat_rules or current_context == "combat_rules":
                        marker = "* "  # Use asterisk for combat rules
                    else:
                        marker = "- "  # Use hyphen for other sections
                        
                    content.append(f"{indent}{marker}{text}")

                elif current_format == TextFormatting.QUOTE:
                    if in_list:
                        content.append("")
                        in_list = False
                    content.append(f"> {text}")

                elif current_format == TextFormatting.CODE:
                    if in_list:
                        content.append("")
                        in_list = False
                    content.append("```")
                    content.append(text)
                    content.append("```")

                else:  # PARAGRAPH
                    if in_list:
                        content.append("")
                        in_list = False
                    # Clean up whitespace while preserving intentional line breaks
                    formatted_text = re.sub(r'\s+', ' ', text).strip()
                    if formatted_text:
                        content.append(formatted_text)

                previous_format = current_format
                previous_context = current_context
            
            # Join content with proper spacing
            formatted_content = "\n".join(content).strip()
            # Clean up multiple blank lines
            formatted_content = re.sub(r'\n{3,}', '\n\n', formatted_content)
            formatted_content += "\n"  # Ensure file ends with newline
            
            # Get page number from first block's metadata
            page_number = blocks[0].metadata.get("page_number", 0) if blocks else 0
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Write formatted content to file
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
