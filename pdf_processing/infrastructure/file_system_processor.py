import os
import re
from typing import Dict
from ..domain.entities import Section, TextFormatting

class FileSystemProcessor:
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
        os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
        formatted_content = []

        # Add formatted content without section numbers in titles
        for fmt_text in section.formatted_content:
            if fmt_text.format_type == TextFormatting.HEADER:
                # Skip if it's just a number
                if not re.match(r'^\s*\d+\s*$', fmt_text.text.strip()):
                    formatted_content.append(f"\n## {fmt_text.text}\n")
            elif fmt_text.format_type == TextFormatting.SUBHEADER:
                formatted_content.append(f"\n### {fmt_text.text}\n")
            elif fmt_text.format_type == TextFormatting.LIST_ITEM:
                formatted_content.append(f"- {fmt_text.text}\n")
            elif fmt_text.format_type == TextFormatting.CODE:
                formatted_content.append(f"\n```\n{fmt_text.text}\n```\n")
            elif fmt_text.format_type == TextFormatting.QUOTE:
                formatted_content.append(f"\n> {fmt_text.text}\n")
            else:
                formatted_content.append(f"\n{fmt_text.text}\n")

        with open(section.file_path, 'w', encoding='utf-8') as f:
            # Add title if present, otherwise skip section number
            if section.title:
                f.write(f"# {section.title}\n\n")
            f.write("".join(formatted_content).strip() + "\n")
