import os
import re
import logging
import traceback
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
            logger.debug(f"Sanitized folder name from '{base_name}' to '{folder_name}'")
            return folder_name
        except Exception as e:
            logger.error(f"Error creating folder name from {pdf_path}: {e}\n{traceback.format_exc()}")
            raise

    def create_book_structure(self, base_output_dir: str, pdf_folder_name: str) -> Dict[str, str]:
        """Create flattened book directory structure"""
        logger.info(f"Creating book structure for {pdf_folder_name} in {base_output_dir}")
        
        try:
            # Create base book directory
            book_dir = os.path.join(base_output_dir, pdf_folder_name)
            logger.info(f"Setting up root directory at {book_dir}")
            
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
                    else:
                        logger.debug(f"Directory already exists: {dir_name} at {dir_path}")
                except Exception as e:
                    logger.error(f"Error creating directory {dir_name} at {dir_path}: {e}\n{traceback.format_exc()}")
                    raise

            logger.info(f"Successfully created book structure for {pdf_folder_name}")
            return directories

        except Exception as e:
            logger.error(f"Error creating book structure for {pdf_folder_name}: {e}\n{traceback.format_exc()}")
            raise

    def save_section_content(self, section: Section):
        """Save section content with enhanced formatting and logging"""
        try:
            logger.info(f"Saving section {section.number} to {section.file_path}")
            
            # Ensure directory exists
            dir_path = os.path.dirname(section.file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logger.info(f"Created section directory: {dir_path}")

            formatted_content = []
            current_context = None

            # Process each block preserving AI formatting
            logger.debug(f"Processing {len(section.formatted_content)} formatted blocks for section {section.number}")
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
                        logger.debug(f"Context change in section {section.number}: {current_context}")

                    # Preserve original formatting
                    if fmt_text.format_type == self.text_formatting.HEADER:
                        formatted_content.append(f"# {text_content}")
                        logger.debug(f"Added header: {text_content[:50]}...")
                    elif fmt_text.format_type == self.text_formatting.SUBHEADER:
                        formatted_content.append(f"## {text_content}")
                        logger.debug(f"Added subheader: {text_content[:50]}...")
                    elif fmt_text.format_type == self.text_formatting.LIST_ITEM:
                        indent = "  " * fmt_text.metadata.get("indentation_level", 0)
                        if fmt_text.metadata.get("context") == "numbered_list":
                            formatted_content.append(f"{indent}1. {text_content}")
                            logger.debug(f"Added numbered item: {text_content[:50]}...")
                        else:
                            formatted_content.append(f"{indent}- {text_content}")
                            logger.debug(f"Added bullet item: {text_content[:50]}...")
                    elif fmt_text.format_type == self.text_formatting.QUOTE:
                        formatted_content.append(f"> {text_content}")
                        logger.debug(f"Added quote: {text_content[:50]}...")
                    elif fmt_text.format_type == self.text_formatting.CODE:
                        formatted_content.append(f"```\n{text_content}\n```")
                        logger.debug(f"Added code block: {text_content[:50]}...")
                    else:  # PARAGRAPH
                        formatted_content.append(text_content)
                        logger.debug(f"Added paragraph: {text_content[:50]}...")

                except Exception as block_error:
                    logger.error(f"Error processing block in section {section.number}: {block_error}\n{traceback.format_exc()}")
                    continue

            # Write content preserving formatting
            content = "\n".join(formatted_content).strip() + "\n"
            
            try:
                with open(section.file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Successfully saved section {section.number} ({len(content)} bytes) to {section.file_path}")
            except Exception as write_error:
                logger.error(f"Error writing section {section.number} to {section.file_path}: {write_error}\n{traceback.format_exc()}")
                raise

        except Exception as e:
            logger.error(f"Error saving section {section.number}: {e}\n{traceback.format_exc()}")
            raise
