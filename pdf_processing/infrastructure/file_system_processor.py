import os
import re
import logging
from typing import Dict
from ..domain.entities import Section, TextFormatting, FormattedText, ProcessingStatus

logger = logging.getLogger(__name__)

class FileSystemProcessor:
    def __init__(self):
        self.text_formatting = TextFormatting

    def get_pdf_folder_name(self, pdf_path: str) -> str:
        """Get sanitized PDF folder name"""
        base_name = os.path.basename(pdf_path)
        folder_name = os.path.splitext(base_name)[0]
        folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
        return folder_name

    def create_book_structure(self, base_output_dir: str, pdf_folder_name: str) -> Dict[str, str]:
        """Create optimized book directory structure at correct level"""
        logger.info(f"Creating book structure for {pdf_folder_name}")
        
        # Create base book directory
        book_dir = os.path.join(base_output_dir, pdf_folder_name)
        
        # Define all directories at the same level
        directories = {
            "book_dir": book_dir,
            "images_dir": os.path.join(book_dir, "images"),
            "metadata_dir": os.path.join(book_dir, "metadata"),
            "histoire_dir": os.path.join(book_dir, "histoire")
        }

        # Create directories with logging
        for dir_name, dir_path in directories.items():
            try:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    logger.info(f"Created directory: {dir_name} at {dir_path}")
            except Exception as e:
                logger.error(f"Error creating directory {dir_name}: {e}")
                raise

        return directories

    def save_section_content(self, section: Section):
        """Save section content with enhanced formatting and logging"""
        try:
            dir_path = os.path.dirname(section.file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logger.info(f"Created section directory: {dir_path}")

            formatted_content = []
            
            # Add title if present
            if section.title:
                formatted_content.append(f"# {section.title}\n")
                logger.debug(f"Added title: {section.title}")

            current_context = None
            for fmt_text in section.formatted_content:
                if not isinstance(fmt_text, FormattedText):
                    continue

                text_content = fmt_text.text.strip()
                if not text_content:
                    continue

                # Add spacing between different contexts
                if fmt_text.metadata.get("context") != current_context:
                    formatted_content.append("")
                    current_context = fmt_text.metadata.get("context")

                # Format based on block type with proper indentation
                if fmt_text.format_type == self.text_formatting.HEADER:
                    if not re.match(r'^\s*\d+\s*$', text_content):
                        formatted_content.append(f"## {text_content}\n")
                elif fmt_text.format_type == self.text_formatting.SUBHEADER:
                    formatted_content.append(f"### {text_content}\n")
                elif fmt_text.format_type == self.text_formatting.LIST_ITEM:
                    indentation = "  " * fmt_text.metadata.get("indentation_level", 0)
                    if fmt_text.metadata.get("context") == "numbered_list":
                        formatted_content.append(f"{indentation}1. {text_content}")
                    else:
                        formatted_content.append(f"{indentation}- {text_content}")
                elif fmt_text.format_type == self.text_formatting.QUOTE:
                    formatted_content.append(f"> {text_content}")
                elif fmt_text.format_type == self.text_formatting.CODE:
                    formatted_content.append(f"\n```\n{text_content}\n```\n")
                else:  # PARAGRAPH
                    formatted_content.append(text_content)

            content = "\n".join(formatted_content).strip() + "\n"
            
            with open(section.file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                logger.info(f"Successfully saved section {section.number} to {section.file_path}")

        except Exception as e:
            logger.error(f"Error saving section {section.number}: {e}")
            raise
