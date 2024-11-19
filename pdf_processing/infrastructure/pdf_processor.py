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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.text_processor = TextFormatProcessor()
        self.chapter_processor = ChapterProcessor()
        self.file_system_processor = FileSystemProcessor()
        self.ai_processor = AIProcessor()
        self.image_processor = ImageProcessor()

    async def process_pre_section_pages(self, pages: List[Dict[str, any]], progress: ProcessingProgress) -> List[List[FormattedText]]:
        """Process pre-section pages sequentially using AI model"""
        progress.status = ProcessingStatus.PROCESSING_PRE_SECTIONS
        logger.info("Starting sequential pre-section processing with AI model")
        
        results = []
        try:
            for page in pages:
                logger.info(f"Processing pre-section page {page['num']}")
                # Process each page sequentially with AI
                response = await self.ai_processor.analyze_page_content(page['text'], page['num'])
                results.append(response)
                logger.info(f"Successfully processed pre-section page {page['num']}")
            return results
        except Exception as e:
            logger.error(f"Error in pre-section pages processing: {e}")
            raise

    def process_numbered_section_page(self, text: str, page_num: int) -> List[FormattedText]:
        """Process a single numbered section page using text processor without AI"""
        try:
            # Use text_processor directly without any AI processing or batching
            lines = text.splitlines()
            formatted_blocks = []
            
            for line in lines:
                if line.strip():
                    block = self.text_processor.process_text_block(line, is_pre_section=False)
                    formatted_blocks.extend(block)
                    
            logger.info(f"Successfully processed numbered section page {page_num} with {len(formatted_blocks)} blocks")
            return formatted_blocks
        except Exception as e:
            logger.error(f"Error processing numbered section page {page_num}: {e}")
            raise

    async def save_current_section(self, current_section: int, current_blocks: List[FormattedText],
                                 page_num: int, sections_dir: str, pdf_folder_name: str,
                                 sections: List[Section], progress: ProcessingProgress,
                                 is_chapter: bool = False, title: Optional[str] = None) -> bool:
        """Save current section with proper formatting and naming conventions"""
        try:
            if current_section is not None and current_blocks:
                # Determine section filename based on type
                if is_chapter:
                    filename = f"chapitre_{current_section}.md"
                    section_title = title if title else f"Chapitre {current_section}"
                else:
                    filename = f"{current_section}.md"
                    section_title = f"Section {current_section}"

                section_path = os.path.join(sections_dir, filename)
                
                # Create sections directory if needed
                os.makedirs(os.path.dirname(section_path), exist_ok=True)
                logger.info(f"Section directory ensured: {os.path.dirname(section_path)}")
                
                # Create section with proper metadata
                section = Section(
                    number=current_section,
                    content="\n".join(block.text for block in current_blocks),
                    page_number=page_num,
                    file_path=section_path,
                    pdf_name=pdf_folder_name,
                    title=section_title,
                    formatted_content=current_blocks,
                    is_chapter=is_chapter,
                    chapter_number=current_section
                )

                # Save section and update progress
                sections.append(section)
                self.file_system_processor.save_section_content(section)
                progress.processed_sections += 1
                
                section_type = "chapter" if is_chapter else "numbered section"
                logger.info(f"Successfully saved {section_type} {current_section} at page {page_num}")
                return True

        except Exception as e:
            logger.error(f"Error saving section {current_section}: {e}")
            raise

        return False

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from the PDF with distinct processing workflows"""
        pdf_folder_name = self.file_system_processor.get_pdf_folder_name(pdf_path)
        paths = self.file_system_processor.create_book_structure(base_output_dir, pdf_folder_name)
        sections_dir = paths["sections_dir"]
        histoire_dir = paths["histoire_dir"]
        images_dir = paths["images_dir"]
        metadata_dir = paths["metadata_dir"]

        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        sections = []
        images = []

        try:
            # Open PDF with both PyMuPDF and PyPDF2 for different processing needs
            doc = fitz.open(pdf_path)
            reader = PdfReader(pdf_path)
            progress.total_pages = len(reader.pages)
            logger.info(f"Processing PDF with {progress.total_pages} pages")

            # First workflow: Find first numbered section
            progress.status = ProcessingStatus.ANALYZING_STRUCTURE
            first_section_page = None
            pre_section_pages = []

            # Collect pre-section pages
            for page_num in range(len(doc)):
                progress.current_page = page_num + 1
                page = doc[page_num]
                text = page.get_text()

                if not text.strip():
                    logger.info(f"Skipping empty page {page_num + 1}")
                    continue

                # Check each line for numbered section start
                found_section = False
                for line in text.splitlines():
                    chapter_num, _ = self.chapter_processor.detect_chapter(line.strip())
                    if chapter_num is not None:
                        first_section_page = page_num
                        found_section = True
                        logger.info(f"Found first numbered section at page {page_num + 1}, section {chapter_num}")
                        break

                if found_section:
                    break

                # Add page to pre-section batch if no numbered section found
                logger.info(f"Adding page {page_num + 1} to pre-sections")
                pre_section_pages.append({
                    'text': text,
                    'num': page_num + 1
                })

            # Second workflow: Process pre-section content with AI
            pre_section_content = []
            if pre_section_pages:
                pre_section_content = await self.process_pre_section_pages(
                    pre_section_pages,
                    progress
                )

            # Process pre-section content into chapters
            if pre_section_content:
                current_chapter: List[FormattedText] = []
                chapter_count = 0

                for page_blocks in pre_section_content:
                    for block in page_blocks:
                        is_chapter, title = await self.ai_processor.detect_chapter_with_ai(block.text)

                        if is_chapter and current_chapter:
                            # Save current chapter
                            chapter_count += 1
                            file_path = os.path.join(histoire_dir, f"{chapter_count}.md")
                            
                            await self.save_current_section(
                                current_section=chapter_count,
                                current_blocks=current_chapter,
                                page_num=progress.current_page,
                                sections_dir=histoire_dir,
                                pdf_folder_name=pdf_folder_name,
                                sections=sections,
                                progress=progress,
                                is_chapter=True,
                                title=title
                            )
                            current_chapter = []

                        current_chapter.append(block)

                # Save last chapter if exists
                if current_chapter:
                    chapter_count += 1
                    file_path = os.path.join(histoire_dir, f"{chapter_count}.md")
                    
                    await self.save_current_section(
                        current_section=chapter_count,
                        current_blocks=current_chapter,
                        page_num=progress.current_page,
                        sections_dir=histoire_dir,
                        pdf_folder_name=pdf_folder_name,
                        sections=sections,
                        progress=progress,
                        is_chapter=True,
                        title=None
                    )

            # Third workflow: Process numbered sections without AI
            if first_section_page is not None:
                progress.status = ProcessingStatus.PROCESSING_NUMBERED_SECTIONS
                current_section = None
                current_blocks: List[FormattedText] = []
                last_section_number = 0

                # Process one page at a time sequentially
                for page_num in range(first_section_page, len(doc)):
                    progress.current_page = page_num + 1
                    try:
                        page = doc[page_num]
                        text = page.get_text()
                        
                        if not text.strip():
                            logger.info(f"Skipping empty page {page_num + 1}")
                            continue

                        logger.info(f"Processing numbered section page {page_num + 1}")
                        
                        # Process each line to check for section numbers
                        lines = text.splitlines()
                        line_blocks: List[FormattedText] = []
                        
                        for line in lines:
                            if not line.strip():
                                continue
                                
                            chapter_num, _ = self.chapter_processor.detect_chapter(line.strip())
                            
                            if chapter_num is not None:
                                # Validate section number sequence
                                if chapter_num <= last_section_number:
                                    logger.warning(f"Non-sequential section number detected: {chapter_num} after {last_section_number}")
                                else:
                                    last_section_number = chapter_num

                                # Save previous section if exists
                                if current_section is not None and current_blocks:
                                    await self.save_current_section(
                                        current_section=current_section,
                                        current_blocks=current_blocks,
                                        page_num=page_num,
                                        sections_dir=sections_dir,
                                        pdf_folder_name=pdf_folder_name,
                                        sections=sections,
                                        progress=progress,
                                        is_chapter=False
                                    )
                                
                                # Start new section
                                current_section = chapter_num
                                current_blocks = []
                                logger.info(f"Starting new numbered section {chapter_num} on page {page_num + 1}")
                            else:
                                # Process the line without AI
                                block = self.text_processor.process_text_block(line, is_pre_section=False)
                                line_blocks.extend(block)
                        
                        # Add processed lines to current section
                        if current_section is not None:
                            current_blocks.extend(line_blocks)

                    except Exception as e:
                        logger.error(f"Error processing page {page_num + 1}: {e}")
                        raise

                # Save the last section if exists
                if current_section is not None and current_blocks:
                    await self.save_current_section(
                        current_section=current_section,
                        current_blocks=current_blocks,
                        page_num=progress.current_page,
                        sections_dir=sections_dir,
                        pdf_folder_name=pdf_folder_name,
                        sections=sections,
                        progress=progress,
                        is_chapter=False
                    )

            # Fourth workflow: Process images
            progress.status = ProcessingStatus.EXTRACTING_IMAGES
            images = self.image_processor.extract_images(
                pdf_path, images_dir, metadata_dir, pdf_folder_name, sections)
            progress.processed_images = len(images)

            progress.status = ProcessingStatus.COMPLETED
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
            if 'doc' in locals():
                doc.close()
            return ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )

    async def extract_images(
            self,
            pdf_path: str,
            base_output_dir: str = "sections",
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