from typing import List, Dict
import fitz  # PyMuPDF
import logging
import os
import json
import asyncio
from ..domain.entities import Section, ProcessedPDF, ProcessingProgress, FormattedText, TextFormatting, ProcessingStatus
from .ai_processor import AIProcessor
from .file_system_processor import FileSystemProcessor
from .section_processor import SectionProcessor
from .image_processor import ImageProcessor

logger = logging.getLogger(__name__)

class MuPDFProcessor:
    def __init__(self):
        self.ai_processor = AIProcessor()
        self.file_system_processor = FileSystemProcessor()
        self.section_processor = SectionProcessor()
        self.image_processor = ImageProcessor()

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections and images from a PDF."""
        logger.info(f"Starting PDF processing for: {pdf_path}")

        # Create folder structure for the processed PDF
        pdf_folder_name = self.file_system_processor.get_pdf_folder_name(pdf_path)
        paths = self.file_system_processor.create_book_structure(base_output_dir, pdf_folder_name)
        histoire_dir = paths["histoire_dir"]
        sections_dir = os.path.join(base_output_dir, pdf_folder_name, "sections")
        os.makedirs(sections_dir, exist_ok=True)
        
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING, total_pages=len(doc))
            sections = []
            pre_sections = []
            numbered_sections = []

            # Process all pages
            all_pages = [
                {"text": doc[page_num].get_text(sort=True), "num": page_num + 1}
                for page_num in range(len(doc))
            ]
            
            # Process pages with AI
            processed_pages = await self.ai_processor.process_pages_concurrently(all_pages)
            
            current_section = []
            current_section_num = 0
            current_chapter_num = 1
            in_numbered_section = False
            
            for page_blocks in processed_pages:
                for block in page_blocks:
                    # Check for numbered sections first (e.g., "1.", "2.", etc.)
                    is_numbered = block.metadata.get("is_numbered_section", False)
                    section_number = block.metadata.get("section_number")
                    
                    if is_numbered and section_number is not None:
                        if current_section:
                            # Save previous section
                            section = self.section_processor.save_section(
                                current_section_num if in_numbered_section else current_chapter_num,
                                current_section,
                                sections_dir if in_numbered_section else histoire_dir,
                                pdf_folder_name,
                                is_chapter=not in_numbered_section
                            )
                            if in_numbered_section:
                                numbered_sections.append(section)
                            else:
                                pre_sections.append(section)
                                current_chapter_num += 1
                            current_section = []
                        
                        current_section_num = section_number
                        current_section = [block]
                        in_numbered_section = True
                        continue

                    # Check for chapter headers and rules sections
                    if block.metadata.get("is_chapter") or block.metadata.get("is_rules_section"):
                        if current_section:
                            # Save previous section
                            section = self.section_processor.save_section(
                                current_section_num if in_numbered_section else current_chapter_num,
                                current_section,
                                sections_dir if in_numbered_section else histoire_dir,
                                pdf_folder_name,
                                is_chapter=not in_numbered_section
                            )
                            if in_numbered_section:
                                numbered_sections.append(section)
                            else:
                                pre_sections.append(section)
                            current_section = []
                            if not in_numbered_section:
                                current_chapter_num += 1
                        
                        # Start new chapter/rules section
                        current_section = [block]
                        in_numbered_section = False
                    else:
                        current_section.append(block)
            
            # Save any remaining content
            if current_section:
                section = self.section_processor.save_section(
                    current_section_num if in_numbered_section else current_chapter_num,
                    current_section,
                    sections_dir if in_numbered_section else histoire_dir,
                    pdf_folder_name,
                    is_chapter=not in_numbered_section
                )
                if in_numbered_section:
                    numbered_sections.append(section)
                else:
                    pre_sections.append(section)
            
            # Combine all sections
            sections = pre_sections + numbered_sections
            progress.processed_sections = len(sections)
            
            # Process images
            logger.info("Extracting images...")
            images = self.image_processor.extract_images(
                pdf_path, paths["images_dir"], paths["metadata_dir"], pdf_folder_name, sections
            )
            progress.processed_images = len(images)

            # Generate metadata files
            self._save_metadata_files(
                sections=sections,
                images=images,
                pdf_folder_name=pdf_folder_name,
                base_output_dir=base_output_dir,
                metadata_dir=paths["metadata_dir"],
                pre_sections=pre_sections,
                numbered_sections=numbered_sections,
                progress=progress
            )

            # Update progress and return the processed data
            progress.status = ProcessingStatus.COMPLETED
            logger.info(f"Processing completed: {len(sections)} sections, {len(images)} images.")
            return ProcessedPDF(
                sections=sections,
                images=images,
                progress=progress,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir
            )

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise

    def _save_metadata_files(self, sections, images, pdf_folder_name, base_output_dir, metadata_dir,
                           pre_sections, numbered_sections, progress):
        """Save all metadata files."""
        try:
            # Save book metadata
            book_metadata = {
                "title": pdf_folder_name,
                "total_sections": len(sections),
                "total_images": len(images),
                "sections": [{
                    "number": section.number,
                    "page_number": section.page_number,
                    "title": section.title,
                    "file_path": os.path.relpath(section.file_path, base_output_dir),
                    "is_chapter": section.is_chapter,
                    "chapter_number": section.chapter_number
                } for section in sections],
                "base_path": base_output_dir,
                "processing_status": ProcessingStatus.COMPLETED.value
            }
            
            with open(os.path.join(metadata_dir, "book.json"), 'w', encoding='utf-8') as f:
                json.dump(book_metadata, f, indent=2, ensure_ascii=False)

            # Save sections metadata as a list
            sections_metadata = [{
                "section_number": section.number,
                "chapter_number": section.chapter_number,
                "file_path": os.path.relpath(section.file_path, base_output_dir),
                "pdf_name": section.pdf_name,
                "page_number": section.page_number,
                "is_chapter": section.is_chapter,
                "title": section.title
            } for section in sections]
            
            with open(os.path.join(metadata_dir, "sections.json"), 'w', encoding='utf-8') as f:
                json.dump(sections_metadata, f, indent=2, ensure_ascii=False)

            # Save progress metadata
            progress_metadata = {
                "status": progress.status.value,
                "current_page": progress.current_page,
                "total_pages": progress.total_pages,
                "processed_sections": progress.processed_sections,
                "processed_images": progress.processed_images,
                "error_message": progress.error_message,
                "section_counts": {
                    "total": len(sections),
                    "pre_sections": len(pre_sections),
                    "numbered_sections": len(numbered_sections)
                }
            }
            
            with open(os.path.join(metadata_dir, "progress.json"), 'w', encoding='utf-8') as f:
                json.dump(progress_metadata, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error saving metadata files: {e}")
            raise