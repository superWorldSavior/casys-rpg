import asyncio
import os
import json
from ..domain.ports import PDFProcessor, PDFRepository
from ..domain.entities import ProcessedPDF

class PDFService:
    def __init__(self, processor: PDFProcessor, repository: PDFRepository):
        self.processor = processor
        self.repository = repository

    async def process_pdf(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        # Process the PDF and get all sections and images
        processed_pdf = await self.processor.extract_sections(pdf_path, base_output_dir)

        # Create metadata directory
        pdf_folder_name = processed_pdf.pdf_name
        metadata_dir = os.path.join(base_output_dir, pdf_folder_name, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)

        # Save sections
        for section in processed_pdf.sections:
            await self.repository.save_section(section)

        # Save images metadata
        for image in processed_pdf.images:
            await self.repository.save_image(image)

        # Save book metadata
        book_metadata = {
            "title": pdf_folder_name,
            "total_sections": len(processed_pdf.sections),
            "total_images": len(processed_pdf.images),
            "sections": [{
                "number": section.number,
                "page_number": section.page_number,
                "file_path": section.file_path,
                "title": section.title,
                "is_chapter": section.is_chapter,
                "chapter_number": section.chapter_number
            } for section in processed_pdf.sections],
            "base_path": base_output_dir
        }

        metadata_path = os.path.join(metadata_dir, "book.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(book_metadata, f, indent=2, ensure_ascii=False)

        # Save metadata to repository
        await self.repository.save_metadata(processed_pdf)

        return processed_pdf

    def process_pdf_sync(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Synchronous version of process_pdf"""
        return asyncio.run(self.process_pdf(pdf_path, base_output_dir))
