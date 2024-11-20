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
        try:
            base_name = os.path.basename(pdf_path)
            folder_name = os.path.splitext(base_name)[0]
            folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
            logger.debug(f"Sanitized folder name: {folder_name}")
            return folder_name
        except Exception as e:
            logger.error(f"Error creating folder name from {pdf_path}: {e}")
            raise

    def create_book_structure(self, base_output_dir: str, pdf_folder_name: str) -> Dict[str, str]:
        """Create book directory structure at correct level"""
        logger.info(f"Creating book structure for {pdf_folder_name}")
        
        try:
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

        except Exception as e:
            logger.error(f"Error creating book structure for {pdf_folder_name}: {e}")
            raise

    def save_section_content(self, section: Section):
        """Save section content preserving AI-generated formatting"""
        try:
            logger.info(f"Saving section {section.number} to {section.file_path}")
            
            # Ensure directory exists
            dir_path = os.path.dirname(section.file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logger.debug(f"Created section directory: {dir_path}")

            formatted_content = []
            current_context = None

            # Process each block preserving AI formatting
            for fmt_text in section.formatted_content:
                try:
                    if not isinstance(fmt_text, FormattedText):
                        logger.warning(f"Invalid format block in section {section.number}")
                        continue

                    text_content = fmt_text.text.strip()
                    if not text_content:
                        continue

                    # Add spacing between different contexts
                    if fmt_text.metadata.get("context") != current_context:
                        formatted_content.append("")
                        current_context = fmt_text.metadata.get("context")

                    # Preserve original formatting
                    if fmt_text.format_type == self.text_formatting.HEADER:
                        formatted_content.append(f"# {text_content}")
                    elif fmt_text.format_type == self.text_formatting.SUBHEADER:
                        formatted_content.append(f"## {text_content}")
                    elif fmt_text.format_type == self.text_formatting.LIST_ITEM:
                        indent = "  " * fmt_text.metadata.get("indentation_level", 0)
                        if fmt_text.metadata.get("context") == "numbered_list":
                            formatted_content.append(f"{indent}1. {text_content}")
                        else:
                            formatted_content.append(f"{indent}- {text_content}")
                    elif fmt_text.format_type == self.text_formatting.QUOTE:
                        formatted_content.append(f"> {text_content}")
                    elif fmt_text.format_type == self.text_formatting.CODE:
                        formatted_content.append(f"```\n{text_content}\n```")
                    else:  # PARAGRAPH
                        formatted_content.append(text_content)

                except Exception as block_error:
                    logger.error(f"Error processing block in section {section.number}: {block_error}")
                    continue

            # Write content preserving formatting
            content = "\n".join(formatted_content).strip() + "\n"
            
            try:
                with open(section.file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Successfully saved section {section.number} to {section.file_path}")
            except Exception as write_error:
                logger.error(f"Error writing section {section.number}: {write_error}")
                raise

        except Exception as e:
            logger.error(f"Error saving section {section.number}: {e}")
            raise
