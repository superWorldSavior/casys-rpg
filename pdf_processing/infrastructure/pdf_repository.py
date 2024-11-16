import os
import json
from typing import List
from ..domain.ports import PDFRepository
from ..domain.entities import Section, PDFImage, ProcessedPDF

class FileSystemPDFRepository(PDFRepository):
    async def save_section(self, section: Section) -> None:
        os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
        with open(section.file_path, "w", encoding="utf-8") as f:
            f.write(f"# Section {section.number}\n\n")
            f.write(section.content.strip())

    async def save_image(self, image: PDFImage) -> None:
        os.makedirs(os.path.dirname(image.image_path), exist_ok=True)
        # The actual image saving is handled by the processor

    async def save_metadata(self, processed_pdf: ProcessedPDF) -> None:
        metadata = {
            'sections': [
                {
                    'section_number': section.number,
                    'file_path': os.path.relpath(section.file_path, processed_pdf.base_path),
                    'pdf_name': section.pdf_name,
                    'page_number': section.page_number
                }
                for section in processed_pdf.sections
            ],
            'images': [
                {
                    'page_number': img.page_number,
                    'image_path': os.path.relpath(img.image_path, processed_pdf.base_path),
                    'pdf_name': img.pdf_name
                }
                for img in processed_pdf.images
            ]
        }
        
        metadata_path = os.path.join(
            processed_pdf.base_path,
            processed_pdf.pdf_name,
            'section_metadata.json'
        )
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
