import asyncio
from ..domain.ports import PDFProcessor, PDFRepository
from ..domain.entities import ProcessedPDF

class PDFService:
    def __init__(self, processor: PDFProcessor, repository: PDFRepository):
        self.processor = processor
        self.repository = repository

    async def process_pdf(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        # Process the PDF and get all sections and images
        processed_pdf = await self.processor.extract_sections(pdf_path, base_output_dir)

        # Save sections
        for section in processed_pdf.sections:
            await self.repository.save_section(section)

        # Save images (actual image files are saved during processing)
        for image in processed_pdf.images:
            await self.repository.save_image(image)

        # Save metadata
        await self.repository.save_metadata(processed_pdf)

        return processed_pdf
