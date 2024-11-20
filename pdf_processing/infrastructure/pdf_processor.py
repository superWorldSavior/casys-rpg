import os
from typing import List, Optional, Dict, Tuple
import logging
import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import asyncio
from ..domain.ports import PDFProcessor
from ..domain.entities import (Section, ProcessedPDF, PDFImage,
                             ProcessingStatus, ProcessingProgress, FormattedText, TextFormatting)
from .text_format_processor import TextFormatProcessor
from .chapter_processor import ChapterProcessor
from .file_system_processor import FileSystemProcessor
from .ai_processor import AIProcessor
from .image_processor import ImageProcessor

logger = logging.getLogger(__name__)

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.text_processor = TextFormatProcessor()
        self.chapter_processor = ChapterProcessor()
        self.file_system_processor = FileSystemProcessor()
        self.ai_processor = AIProcessor()
        self.image_processor = ImageProcessor()

    async def process_pre_sections(self, doc, start_page: int, end_page: int, 
                                 histoire_dir: str, pdf_folder_name: str) -> List[Section]:
        """Process pre-sections using unified AI analysis"""
        logger.info(f"Starting pre-section processing from page {start_page + 1} to {end_page + 1}")
        sections = []
        current_chapter = None
        current_blocks = []
        chapter_count = 0

        try:
            # Get all images for multimodal analysis
            images = self.image_processor.extract_images(
                doc_path=doc.name,
                images_dir=os.path.join(os.path.dirname(histoire_dir), "images"),
                metadata_dir=os.path.join(os.path.dirname(histoire_dir), "metadata"),
                pdf_name=pdf_folder_name
            )

            for page_num in range(start_page, end_page + 1):
                page = doc[page_num]
                try:
                    text = page.get_text("text")
                except AttributeError:
                    logger.warning(f"Could not extract text from page {page_num + 1}")
                    continue

                if not text.strip():
                    logger.info(f"Skipping empty page {page_num + 1}")
                    continue

                # Use new unified analysis
                page_blocks, new_chapter_info, is_chapter_complete = await self.ai_processor.analyze_page_with_chapters(
                    text,
                    page_num + 1,
                    images,
                    current_chapter
                )

                # Handle chapter transitions
                if new_chapter_info and new_chapter_info != current_chapter:
                    if current_chapter and current_blocks:
                        # Save previous chapter
                        chapter_count += 1
                        section = await self.save_section(
                            section_num=chapter_count,
                            blocks=current_blocks,
                            page_num=page_num + 1,
                            output_dir=histoire_dir,
                            pdf_folder_name=pdf_folder_name,
                            is_chapter=True,
                            title=current_chapter.get("title")
                        )
                        sections.append(section)
                        current_blocks = []
                    
                    current_chapter = new_chapter_info

                # Accumulate content
                current_blocks.extend(page_blocks)

                # Save completed chapter
                if is_chapter_complete and current_chapter and current_blocks:
                    chapter_count += 1
                    section = await self.save_section(
                        section_num=chapter_count,
                        blocks=current_blocks,
                        page_num=page_num + 1,
                        output_dir=histoire_dir,
                        pdf_folder_name=pdf_folder_name,
                        is_chapter=True,
                        title=current_chapter.get("title")
                    )
                    sections.append(section)
                    current_blocks = []
                    current_chapter = None

            # Handle any remaining content
            if current_chapter and current_blocks:
                chapter_count += 1
                section = await self.save_section(
                    section_num=chapter_count,
                    blocks=current_blocks,
                    page_num=end_page + 1,
                    output_dir=histoire_dir,
                    pdf_folder_name=pdf_folder_name,
                    is_chapter=True,
                    title=current_chapter.get("title")
                )
                sections.append(section)

        except Exception as e:
            logger.error(f"Error in pre-section processing: {e}")
            raise

        return sections

    async def process_numbered_sections(self, doc, start_page: int,
                                     sections_dir: str, pdf_folder_name: str) -> List[Section]:
        """Process numbered sections without AI"""
        logger.info(f"Starting numbered section processing from page {start_page + 1}")
        sections = []
        current_section = None
        current_blocks: List[FormattedText] = []
        last_section_number = 0

        try:
            for page_num in range(start_page, len(doc)):
                page = doc[page_num]
                try:
                    text = page.get_text("text")
                except AttributeError:
                    logger.warning(f"Could not extract text from page {page_num + 1}")
                    continue

                if not text.strip():
                    logger.info(f"Skipping empty page {page_num + 1}")
                    continue

                logger.info(f"Processing numbered section page {page_num + 1}")
                lines = text.splitlines()
                line_blocks: List[FormattedText] = []

                for line in lines:
                    if not line.strip():
                        continue

                    chapter_num, _ = self.chapter_processor.detect_chapter(line.strip())

                    if chapter_num is not None:
                        if chapter_num <= last_section_number:
                            logger.warning(f"Non-sequential section number detected: {chapter_num} after {last_section_number}")
                        else:
                            last_section_number = chapter_num

                        if current_section is not None and current_blocks:
                            section = await self.save_section(
                                section_num=current_section,
                                blocks=current_blocks,
                                page_num=page_num + 1,
                                output_dir=sections_dir,
                                pdf_folder_name=pdf_folder_name,
                                is_chapter=False
                            )
                            sections.append(section)

                        current_section = chapter_num
                        current_blocks = []
                        logger.info(f"Starting new numbered section {chapter_num} on page {page_num + 1}")
                    else:
                        block = self.text_processor.process_text_block(line, is_pre_section=False)
                        line_blocks.extend(block)

                if current_section is not None:
                    current_blocks.extend(line_blocks)

            if current_section is not None and current_blocks:
                section = await self.save_section(
                    section_num=current_section,
                    blocks=current_blocks,
                    page_num=len(doc),
                    output_dir=sections_dir,
                    pdf_folder_name=pdf_folder_name,
                    is_chapter=False
                )
                sections.append(section)

        except Exception as e:
            logger.error(f"Error in numbered section processing: {e}")
            raise

        return sections

    async def save_section(self, section_num: int, blocks: List[FormattedText],
                          page_num: int, output_dir: str, pdf_folder_name: str,
                          is_chapter: bool = False, title: Optional[str] = None) -> Section:
        """Save a section with proper formatting and naming conventions"""
        try:
            if is_chapter:
                filename = f"chapitre_{section_num}.md"
                section_title = title if title else f"Chapitre {section_num}"
            else:
                filename = f"{section_num}.md"
                section_title = f"Section {section_num}"

            section_path = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(section_path), exist_ok=True)

            section = Section(
                number=section_num,
                content="\n".join(block.text for block in blocks),
                page_number=page_num,
                file_path=section_path,
                pdf_name=pdf_folder_name,
                title=section_title,
                formatted_content=blocks,
                is_chapter=is_chapter,
                chapter_number=section_num
            )

            self.file_system_processor.save_section_content(section)
            section_type = "chapter" if is_chapter else "numbered section"
            logger.info(f"Successfully saved {section_type} {section_num} at page {page_num}")
            return section

        except Exception as e:
            logger.error(f"Error saving section {section_num}: {e}")
            raise

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from the PDF with distinct processing workflows"""
        pdf_folder_name = self.file_system_processor.get_pdf_folder_name(pdf_path)
        paths = self.file_system_processor.create_book_structure(base_output_dir, pdf_folder_name)
        sections = []
        images = []
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        doc = None

        try:
            doc = fitz.open(pdf_path)
            reader = PdfReader(pdf_path)
            progress.total_pages = len(reader.pages)
            logger.info(f"Processing PDF with {progress.total_pages} pages")

            # First workflow: Find first numbered section
            progress.status = ProcessingStatus.ANALYZING_STRUCTURE
            first_section_page = None

            for page_num in range(len(doc)):
                progress.current_page = page_num + 1
                page = doc[page_num]
                try:
                    text = page.get_text("text")
                except AttributeError:
                    continue

                if not text.strip():
                    continue

                for line in text.splitlines():
                    chapter_num, _ = self.chapter_processor.detect_chapter(line.strip())
                    if chapter_num is not None:
                        first_section_page = page_num
                        logger.info(f"Found first numbered section at page {page_num + 1}")
                        break

                if first_section_page is not None:
                    break

            # Second workflow: Process pre-sections with AI
            if first_section_page is None:
                first_section_page = len(doc)
                logger.info("No numbered sections found, processing all pages as pre-sections")

            progress.status = ProcessingStatus.PROCESSING_PRE_SECTIONS
            pre_sections = await self.process_pre_sections(
                doc, 0, first_section_page - 1,
                paths["histoire_dir"], pdf_folder_name
            )
            sections.extend(pre_sections)

            # Third workflow: Process numbered sections without AI
            if first_section_page < len(doc):
                progress.status = ProcessingStatus.PROCESSING_NUMBERED_SECTIONS
                numbered_sections = await self.process_numbered_sections(
                    doc, first_section_page,
                    paths["sections_dir"], pdf_folder_name
                )
                sections.extend(numbered_sections)

            # Fourth workflow: Process images
            progress.status = ProcessingStatus.EXTRACTING_IMAGES
            images = self.image_processor.extract_images(
                pdf_path, paths["images_dir"], paths["metadata_dir"],
                pdf_folder_name, sections
            )
            progress.processed_images = len(images)

            progress.status = ProcessingStatus.COMPLETED
            if doc:
                doc.close()
            return ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            if doc:
                doc.close()
            return ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )

    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections",
                           sections: Optional[List[Section]] = None) -> List[PDFImage]:
        """Extract images from the PDF with section information"""
        pdf_folder_name = self.file_system_processor.get_pdf_folder_name(pdf_path)
        paths = self.file_system_processor.create_book_structure(base_output_dir, pdf_folder_name)
        return self.image_processor.extract_images(
            pdf_path,
            paths["images_dir"],
            paths["metadata_dir"],
            pdf_folder_name,
            sections
        )