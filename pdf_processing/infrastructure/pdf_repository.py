import os
import json
from typing import List
from datetime import datetime
from ..domain.ports import PDFRepository
from ..domain.entities import Section, PDFImage, ProcessedPDF, PDFMetadata

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
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        metadata = {
            'pdf_info': {
                'title': processed_pdf.metadata.title if processed_pdf.metadata else None,
                'author': processed_pdf.metadata.author if processed_pdf.metadata else None,
                'subject': processed_pdf.metadata.subject if processed_pdf.metadata else None,
                'keywords': processed_pdf.metadata.keywords if processed_pdf.metadata else None,
                'creator': processed_pdf.metadata.creator if processed_pdf.metadata else None,
                'producer': processed_pdf.metadata.producer if processed_pdf.metadata else None,
                'creation_date': processed_pdf.metadata.creation_date if processed_pdf.metadata else None,
                'modification_date': processed_pdf.metadata.modification_date if processed_pdf.metadata else None,
                'page_count': processed_pdf.metadata.page_count if processed_pdf.metadata else None,
                'file_size': processed_pdf.metadata.file_size if processed_pdf.metadata else None,
                'pdf_version': processed_pdf.metadata.pdf_version if processed_pdf.metadata else None,
                'is_encrypted': processed_pdf.metadata.is_encrypted if processed_pdf.metadata else None,
                'page_dimensions': processed_pdf.metadata.page_dimensions if processed_pdf.metadata else None
            },
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
            json.dump(metadata, f, ensure_ascii=False, indent=4, default=datetime_handler)
