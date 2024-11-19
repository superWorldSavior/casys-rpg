import json
from typing import Dict
from ...domain.entities import Section, ProcessedPDF, TextFormatting
from ...domain.analyzers import MetadataAnalyzer
from ...domain.ports import DirectoryManager
from ...infrastructure.logging_config import StructuredLogger

class FileSystemMetadataAnalyzer(MetadataAnalyzer):
    def __init__(self, directory_manager: DirectoryManager):
        self.logger = StructuredLogger("MetadataAnalyzer")
        self.directory_manager = directory_manager

    async def extract_metadata(self, processed_pdf: ProcessedPDF) -> dict:
        """Extract and structure metadata from processed PDF"""
        try:
            # Ensure metadata directory exists
            metadata_dir = await self.directory_manager.get_metadata_directory(
                processed_pdf.base_path,
                processed_pdf.pdf_name
            )
            
            sections_metadata = []
            for section in processed_pdf.sections:
                section_metadata = await self.analyze_section_metadata(section)
                sections_metadata.append(section_metadata)

            # Structure the complete metadata
            metadata = {
                "title": processed_pdf.pdf_name,
                "total_sections": len(processed_pdf.sections),
                "total_images": len(processed_pdf.images),
                "sections": sections_metadata,
                "images": [{
                    "page_number": img.page_number,
                    "path": img.image_path,
                    "width": img.width,
                    "height": img.height,
                    "section_number": img.section_number
                } for img in processed_pdf.images],
                "progress": {
                    "status": processed_pdf.progress.status.value,
                    "current_page": processed_pdf.progress.current_page,
                    "total_pages": processed_pdf.progress.total_pages,
                    "processed_sections": processed_pdf.progress.processed_sections,
                    "processed_images": processed_pdf.progress.processed_images
                }
            }

            # Save metadata to file
            metadata_path = f"{metadata_dir}/book.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.logger.info("Metadata extracted and saved", {
                "metadata_path": metadata_path,
                "total_sections": len(sections_metadata)
            })

            return metadata

        except Exception as e:
            self.logger.error("Error extracting metadata", e)
            raise

    async def analyze_section_metadata(self, section: Section) -> dict:
        """Analyze and extract metadata for a specific section"""
        try:
            # Count different formatting types
            format_counts = {format_type: 0 for format_type in TextFormatting}
            for block in section.formatted_content:
                format_counts[block.format_type] += 1

            # Create section metadata with all required fields
            metadata = {
                "number": section.number,
                "page_number": section.page_number,
                "file_path": section.file_path,
                "is_chapter": section.is_chapter,
                "chapter_number": section.chapter_number if section.is_chapter else None,
                "title": section.title,
                "formatting": {
                    "total_blocks": len(section.formatted_content),
                    "format_distribution": {
                        format_type.value: count
                        for format_type, count in format_counts.items()
                        if count > 0
                    }
                }
            }

            return metadata

        except Exception as e:
            self.logger.error(f"Error analyzing metadata for section {section.number}", e)
            raise
