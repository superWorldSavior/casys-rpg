import os
import json
from typing import Dict
from ...domain.analyzers import MetadataAnalyzer
from ...domain.entities import Section, ProcessedPDF
from ..logging_config import StructuredLogger

class FileSystemMetadataAnalyzer(MetadataAnalyzer):
    def __init__(self):
        self.logger = StructuredLogger("MetadataAnalyzer")

    async def extract_metadata(self, processed_pdf: ProcessedPDF) -> dict:
        try:
            metadata = {
                "title": processed_pdf.pdf_name,
                "total_sections": len(processed_pdf.sections),
                "total_images": len(processed_pdf.images),
                "sections": [
                    await self.analyze_section_metadata(section)
                    for section in processed_pdf.sections
                ],
                "images": [
                    {
                        "page_number": img.page_number,
                        "path": img.image_path,
                        "width": img.width,
                        "height": img.height,
                        "section_number": img.section_number
                    }
                    for img in processed_pdf.images
                ],
                "progress": {
                    "status": processed_pdf.progress.status.value,
                    "current_page": processed_pdf.progress.current_page,
                    "total_pages": processed_pdf.progress.total_pages,
                    "processed_sections": processed_pdf.progress.processed_sections,
                    "processed_images": processed_pdf.progress.processed_images,
                    "error_message": processed_pdf.progress.error_message
                }
            }
            return metadata
            
        except Exception as e:
            self.logger.error("Error extracting metadata", e)
            raise

    async def analyze_section_metadata(self, section: Section) -> dict:
        try:
            return {
                "number": section.number,
                "page_number": section.page_number,
                "file_path": section.file_path,
                "is_chapter": section.is_chapter,
                "chapter_number": section.chapter_number,
                "title": section.title,
                "formatting": [
                    {
                        "type": fmt.format_type.value,
                        "metadata": fmt.metadata
                    }
                    for fmt in section.formatted_content
                ]
            }
        except Exception as e:
            self.logger.error(f"Error analyzing section metadata for section {section.number}", e)
            raise
