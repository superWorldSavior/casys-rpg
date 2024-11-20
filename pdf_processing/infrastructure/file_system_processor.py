import os
import re
from typing import Dict
from ..domain.entities import Section, TextFormatting, FormattedText, ProcessingStatus

class FileSystemProcessor:
    def __init__(self):
        self.text_formatting = TextFormatting  # Store reference to avoid import issues
        
    def get_pdf_folder_name(self, pdf_path: str) -> str:
        base_name = os.path.basename(pdf_path)
        folder_name = os.path.splitext(base_name)[0]
        folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
        return folder_name

    def create_book_structure(self, base_output_dir: str, pdf_folder_name: str) -> Dict[str, str]:
        """Create the book directory structure and return paths"""
        book_dir = os.path.join(base_output_dir, pdf_folder_name)
        sections_dir = os.path.join(book_dir, "sections")
        images_dir = os.path.join(book_dir, "images")
        metadata_dir = os.path.join(book_dir, "metadata")
        histoire_dir = os.path.join(book_dir, "histoire")

        for directory in [book_dir, sections_dir, images_dir, metadata_dir, histoire_dir]:
            os.makedirs(directory, exist_ok=True)

        return {
            "book_dir": book_dir,
            "sections_dir": sections_dir,
            "images_dir": images_dir,
            "metadata_dir": metadata_dir,
            "histoire_dir": histoire_dir
        }

    def save_section_content(self, section: Section):
        """Save section content to file with proper formatting"""
        try:
            os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
            formatted_content = []

            for fmt_text in section.formatted_content:
                if not isinstance(fmt_text, FormattedText):
                    continue

                try:
                    text_content = fmt_text.text.strip()
                    if not text_content:
                        continue

                    if fmt_text.format_type == self.text_formatting.HEADER:
                        # Skip if it's just a number
                        if not re.match(r'^\s*\d+\s*$', text_content):
                            formatted_content.append(f"\n## {text_content}\n")
                    elif fmt_text.format_type == self.text_formatting.SUBHEADER:
                        formatted_content.append(f"\n### {text_content}\n")
                    elif fmt_text.format_type == self.text_formatting.LIST_ITEM:
                        indentation = " " * fmt_text.metadata.get("indentation_level", 0)
                        formatted_content.append(f"{indentation}- {text_content}\n")
                    elif fmt_text.format_type == self.text_formatting.CODE:
                        formatted_content.append(f"\n```\n{text_content}\n```\n")
                    elif fmt_text.format_type == self.text_formatting.QUOTE:
                        formatted_content.append(f"\n> {text_content}\n")
                    elif fmt_text.format_type == self.text_formatting.PARAGRAPH:
                        # Add blank line before paragraphs for better readability
                        formatted_content.append(f"\n{text_content}\n")
                except (AttributeError, TypeError) as e:
                    # Fallback to paragraph if format_type is invalid
                    formatted_content.append(f"\n{text_content}\n")

            with open(section.file_path, 'w', encoding='utf-8') as f:
                # Add title if present
                if section.title:
                    f.write(f"# {section.title}\n\n")
                f.write("".join(formatted_content).strip() + "\n")
        except Exception as e:
            raise Exception(f"Error saving section {section.number}: {str(e)}")
