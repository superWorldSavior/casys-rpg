import os
import json
from typing import List
from ..domain.ports import PDFRepository
from ..domain.entities import Section, PDFImage, ProcessedPDF, ProcessingStatus

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
        # Create metadata directory
        metadata_dir = os.path.join(
            processed_pdf.base_path,
            processed_pdf.pdf_name,
            'metadata'
        )
        os.makedirs(metadata_dir, exist_ok=True)

        # Prepare sections metadata
        sections_metadata = [
            {
                'section_number': section.number,
                'file_path': os.path.relpath(section.file_path, processed_pdf.base_path),
                'pdf_name': section.pdf_name,
                'page_number': section.page_number
            }
            for section in processed_pdf.sections
        ]

        # Save sections metadata
        sections_metadata_path = os.path.join(metadata_dir, 'sections.json')
        with open(sections_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(sections_metadata, f, ensure_ascii=False, indent=2)

        # Save progress metadata
        progress_metadata = {
            'status': processed_pdf.progress.status.value,
            'current_page': processed_pdf.progress.current_page,
            'total_pages': processed_pdf.progress.total_pages,
            'processed_sections': processed_pdf.progress.processed_sections,
            'processed_images': processed_pdf.progress.processed_images,
            'error_message': processed_pdf.progress.error_message
        }
        
        progress_metadata_path = os.path.join(metadata_dir, 'progress.json')
        with open(progress_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(progress_metadata, f, ensure_ascii=False, indent=2)

    async def get_processing_status(self, pdf_name: str, base_path: str) -> dict:
        progress_path = os.path.join(base_path, pdf_name, 'metadata', 'progress.json')
        try:
            with open(progress_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'status': ProcessingStatus.NOT_STARTED.value,
                'current_page': 0,
                'total_pages': 0,
                'processed_sections': 0,
                'processed_images': 0,
                'error_message': None
            }
