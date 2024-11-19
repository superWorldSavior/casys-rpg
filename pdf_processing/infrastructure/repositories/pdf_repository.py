"""Implementation of PDF repository."""
from typing import List, Optional
from ...domain.ports import PDFRepository
from ...domain.entities import Section, PDFImage, ProcessedPDF
import os
import json

class FilePDFRepository(PDFRepository):
    """File system implementation of PDF repository."""
    
    def __init__(self, base_dir: str = "sections"):
        self.base_dir = base_dir

    async def save_section(self, section: Section) -> None:
        """Save section content to file."""
        try:
            os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
            with open(section.file_path, 'w', encoding='utf-8') as f:
                if section.title:
                    f.write(f"# {section.title}\n\n")
                f.write(section.content)
        except Exception as e:
            raise Exception(f"Failed to save section: {str(e)}")

    async def save_image(self, image: PDFImage) -> None:
        """Save image metadata."""
        try:
            metadata_dir = os.path.join(self.base_dir, image.pdf_name, "metadata")
            os.makedirs(metadata_dir, exist_ok=True)
            
            metadata_path = os.path.join(metadata_dir, "images.json")
            existing_images = []
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    existing_images = json.load(f)
            
            image_data = {
                "page_number": image.page_number,
                "path": image.image_path,
                "width": image.width,
                "height": image.height,
                "section_number": image.section_number
            }
            
            existing_images.append(image_data)
            
            with open(metadata_path, 'w') as f:
                json.dump(existing_images, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save image metadata: {str(e)}")

    async def save_metadata(self, processed_pdf: ProcessedPDF) -> None:
        """Save PDF processing metadata."""
        try:
            metadata_dir = os.path.join(self.base_dir, processed_pdf.pdf_name, "metadata")
            os.makedirs(metadata_dir, exist_ok=True)
            
            metadata = {
                "pdf_name": processed_pdf.pdf_name,
                "total_sections": len(processed_pdf.sections),
                "total_images": len(processed_pdf.images),
                "processing_status": processed_pdf.progress.status.value,
                "base_path": processed_pdf.base_path
            }
            
            metadata_path = os.path.join(metadata_dir, "processing.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save PDF metadata: {str(e)}")
