import asyncio
import os
import json
from typing import List, Dict
from ..domain.ports import PDFProcessor, PDFRepository
from ..domain.entities import ProcessedPDF, ProcessingStatus

class PDFService:
    def __init__(self, processor: PDFProcessor, repository: PDFRepository):
        self.processor = processor
        self.repository = repository
        self._processing_queue = asyncio.Queue()
        self._is_processing = False

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

        # Save images metadata (already saved by processor in images.json)
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
                "file_path": section.file_path
            } for section in processed_pdf.sections],
            "base_path": base_output_dir
        }

        metadata_path = os.path.join(metadata_dir, "book.json")
        with open(metadata_path, 'w') as f:
            json.dump(book_metadata, f, indent=2)

        # Save metadata to repository
        await self.repository.save_metadata(processed_pdf)

        return processed_pdf

    def process_pdf_sync(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Synchronous version of process_pdf"""
        return asyncio.run(self.process_pdf(pdf_path, base_output_dir))

    async def add_to_queue(self, pdf_path: str, base_output_dir: str = "sections") -> None:
        """Add a PDF to the processing queue"""
        await self._processing_queue.put((pdf_path, base_output_dir))
        if not self._is_processing:
            asyncio.create_task(self._process_queue())

    async def _process_queue(self) -> None:
        """Process PDFs in the queue sequentially"""
        self._is_processing = True
        try:
            while not self._processing_queue.empty():
                pdf_path, base_output_dir = await self._processing_queue.get()
                try:
                    await self.process_pdf(pdf_path, base_output_dir)
                except Exception as e:
                    print(f"Error processing {pdf_path}: {e}")
                finally:
                    self._processing_queue.task_done()
        finally:
            self._is_processing = False

    async def get_queue_status(self) -> Dict:
        """Get the current status of the processing queue"""
        return {
            "queue_size": self._processing_queue.qsize(),
            "is_processing": self._is_processing
        }
