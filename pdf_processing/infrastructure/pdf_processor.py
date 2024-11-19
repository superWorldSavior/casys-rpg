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
        self.batch_size = 5  # Process 5 pages at a time

    async def process_pre_section_pages(self, pages: List[Dict[str, any]], progress: ProcessingProgress) -> List[List[FormattedText]]:
        """Process multiple pre-section pages concurrently using AI model"""
        progress.status = ProcessingStatus.PROCESSING_PRE_SECTIONS
        logger.info("Starting pre-section processing with AI model")
        
        try:
            results = []
            total_pages = len(pages)
            
            # Process pages in batches
            for i in range(0, total_pages, self.batch_size):
                batch = pages[i:i + self.batch_size]
                batch_tasks = []
                
                for page in batch:
                    # Create task for each page in the batch
                    task = self.ai_processor.analyze_page_content(
                        page['text'],
                        page['num']
                    )
                    batch_tasks.append(task)
                
                # Process batch concurrently
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Handle results and update progress
                for j, result in enumerate(batch_results):
                    current_page = batch[j]
                    try:
                        if isinstance(result, Exception):
                            logger.error(f"Error in AI processing for page {current_page['num']}: {result}")
                            # Fallback to basic text processing
                            fallback_result = self.text_processor.process_text_block(
                                current_page['text'],
                                is_pre_section=True
                            )
                            results.append(fallback_result)
                        else:
                            results.append(result)
                            logger.info(f"Successfully processed pre-section page {current_page['num']}")
                    except Exception as e:
                        logger.error(f"Error processing page {current_page['num']}: {e}")
                        # Ensure we always append something for each page
                        results.append([FormattedText(
                            text=current_page['text'],
                            format_type=TextFormatting.PARAGRAPH,
                            metadata={"error": str(e)}
                        )])
                    
                    # Update progress
                    progress.current_page = current_page['num']
                
                # Log batch completion
                logger.info(f"Completed batch processing: pages {i+1} to {min(i+self.batch_size, total_pages)}")
            
            return results
        except Exception as e:
            logger.error(f"Error in batch processing pre-section pages: {e}")
            raise

    def process_numbered_section_page(self, text: str, page_num: int) -> List[FormattedText]:
        """Process a single numbered section page using direct text formatting without AI"""
        try:
            # Use only text processor for numbered sections
            formatted_blocks = self.text_processor.process_text_block(text, is_pre_section=False)
            logger.info(f"Successfully processed numbered section page {page_num}")
            return formatted_blocks
        except Exception as e:
            logger.error(f"Error processing numbered section page {page_num}: {e}")
            raise

    async def extract_sections(self, pdf_path: str,
                             base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from the PDF with distinct processing workflows"""
        pdf_folder_name = self.file_system_processor.get_pdf_folder_name(pdf_path)
        paths = self.file_system_processor.create_book_structure(base_output_dir,
                                                               pdf_folder_name)
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
                    continue

                # Check for numbered section start
                lines = text.splitlines()
                for line in lines:
                    chapter_num, _ = self.chapter_processor.detect_chapter(line.strip())
                    if chapter_num is not None:
                        first_section_page = page_num
                        break

                if first_section_page is not None:
                    break

                # Add page to pre-section batch
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
                            
                            section = Section(
                                number=chapter_count,
                                content="\n".join(block.text for block in current_chapter),
                                page_number=progress.current_page,
                                file_path=file_path,
                                pdf_name=pdf_folder_name,
                                title=title,
                                formatted_content=current_chapter,
                                is_chapter=True,
                                chapter_number=chapter_count
                            )
                            sections.append(section)
                            self.file_system_processor.save_section_content(section)
                            progress.processed_sections += 1
                            current_chapter = []

                        current_chapter.append(block)

                # Save last chapter if exists
                if current_chapter:
                    chapter_count += 1
                    file_path = os.path.join(histoire_dir, f"{chapter_count}.md")
                    
                    section = Section(
                        number=chapter_count,
                        content="\n".join(block.text for block in current_chapter),
                        page_number=progress.current_page,
                        file_path=file_path,
                        pdf_name=pdf_folder_name,
                        title=None,
                        formatted_content=current_chapter,
                        is_chapter=True,
                        chapter_number=chapter_count
                    )
                    sections.append(section)
                    self.file_system_processor.save_section_content(section)
                    progress.processed_sections += 1

            # Third workflow: Process numbered sections without AI
            if first_section_page is not None:
                progress.status = ProcessingStatus.PROCESSING_NUMBERED_SECTIONS
                current_section = None
                current_blocks: List[FormattedText] = []

                for page_num in range(first_section_page, len(doc)):
                    progress.current_page = page_num + 1
                    try:
                        page = doc[page_num]
                        text = page.get_text()
                        
                        if not text.strip():
                            continue

                        formatted_blocks = self.process_numbered_section_page(text, page_num + 1)
                        
                        for block in formatted_blocks:
                            chapter_num, _ = self.chapter_processor.detect_chapter(block.text)
                            
                            if chapter_num is not None:
                                # Save previous section if exists
                                if current_section is not None and current_blocks:
                                    file_path = os.path.join(sections_dir, f"{current_section}.md")
                                    
                                    section = Section(
                                        number=len(sections),
                                        content="\n".join(block.text for block in current_blocks),
                                        page_number=page_num + 1,
                                        file_path=file_path,
                                        pdf_name=pdf_folder_name,
                                        title=None,
                                        formatted_content=current_blocks,
                                        is_chapter=True,
                                        chapter_number=current_section
                                    )
                                    sections.append(section)
                                    self.file_system_processor.save_section_content(section)
                                    progress.processed_sections += 1
                                    current_blocks = []

                                current_section = chapter_num
                            else:
                                current_blocks.append(block)

                    except Exception as e:
                        logger.error(f"Error processing page {page_num + 1}: {e}")

                # Save the last section if exists
                if current_section is not None and current_blocks:
                    file_path = os.path.join(sections_dir, f"{current_section}.md")
                    
                    section = Section(
                        number=len(sections),
                        content="\n".join(block.text for block in current_blocks),
                        page_number=progress.current_page,
                        file_path=file_path,
                        pdf_name=pdf_folder_name,
                        title=None,
                        formatted_content=current_blocks,
                        is_chapter=True,
                        chapter_number=current_section
                    )
                    sections.append(section)
                    self.file_system_processor.save_section_content(section)
                    progress.processed_sections += 1

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
