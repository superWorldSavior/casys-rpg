import os
from typing import List, Optional, Dict, Tuple
import logging
from PyPDF2 import PdfReader
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

    async def extract_sections(self, pdf_path: str,
                             base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from the PDF with enhanced formatting detection"""
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
            reader = PdfReader(pdf_path)
            progress.total_pages = len(reader.pages)
            progress.status = ProcessingStatus.EXTRACTING_SECTIONS

            # Process pre-section content page by page
            pre_section_pages: List[List[FormattedText]] = []
            first_section_page = None

            # First pass: Identify where numbered sections begin
            for page_num, page in enumerate(reader.pages):
                progress.current_page = page_num + 1
                text = page.extract_text()
                
                if not text:
                    continue

                # Check for standalone section number
                lines = text.splitlines()
                for line in lines:
                    chapter_num, _ = self.chapter_processor.detect_chapter(line.strip())
                    if chapter_num is not None:
                        first_section_page = page_num
                        break

                if first_section_page is not None:
                    break

                # Process page content using AI for pre-sections
                formatted_blocks = await self.ai_processor.analyze_page_content(text, page_num + 1)
                if formatted_blocks:
                    pre_section_pages.append(formatted_blocks)

            # Process pre-section pages into chapters
            if pre_section_pages:
                current_chapter: List[FormattedText] = []
                chapter_count = 0

                for page_blocks in pre_section_pages:
                    for block in page_blocks:
                        is_chapter, title = await self.ai_processor.detect_chapter_with_ai(
                            block.text)

                        if is_chapter and current_chapter:
                            # Save current chapter
                            chapter_count += 1
                            file_path = os.path.join(histoire_dir,
                                                   f"{chapter_count}.md")
                            
                            sections.append(
                                Section(number=chapter_count,
                                       content="\n".join(
                                           block.text for block in current_chapter),
                                       page_number=progress.current_page,
                                       file_path=file_path,
                                       pdf_name=pdf_folder_name,
                                       title=title,
                                       formatted_content=current_chapter,
                                       is_chapter=True,
                                       chapter_number=chapter_count))
                            self.file_system_processor.save_section_content(sections[-1])
                            current_chapter = []

                        current_chapter.append(block)

                # Save last chapter if exists
                if current_chapter:
                    chapter_count += 1
                    file_path = os.path.join(histoire_dir,
                                           f"{chapter_count}.md")
                    
                    sections.append(
                        Section(number=chapter_count,
                               content="\n".join(block.text for block in current_chapter),
                               page_number=progress.current_page,
                               file_path=file_path,
                               pdf_name=pdf_folder_name,
                               title=None,
                               formatted_content=current_chapter,
                               is_chapter=True,
                               chapter_number=chapter_count))
                    self.file_system_processor.save_section_content(sections[-1])

            # Process numbered sections
            if first_section_page is not None:
                current_section = None
                current_blocks: List[FormattedText] = []

                for page_num in range(first_section_page, len(reader.pages)):
                    progress.current_page = page_num + 1
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        
                        if not text:
                            continue

                        # Process page content using AI
                        formatted_blocks = await self.ai_processor.analyze_page_content(text, page_num + 1)

                        for block in formatted_blocks:
                            chapter_num, _ = self.chapter_processor.detect_chapter(block.text.strip())
                            
                            if chapter_num is not None:
                                # Save previous section if exists
                                if current_section is not None and current_blocks:
                                    file_path = os.path.join(sections_dir,
                                                           f"{current_section}.md")
                                    
                                    sections.append(
                                        Section(number=len(sections),
                                               content="\n".join(
                                                   block.text for block in current_blocks),
                                               page_number=page_num + 1,
                                               file_path=file_path,
                                               pdf_name=pdf_folder_name,
                                               title=None,
                                               formatted_content=current_blocks,
                                               is_chapter=True,
                                               chapter_number=current_section))
                                    self.file_system_processor.save_section_content(sections[-1])
                                    progress.processed_sections += 1
                                    current_blocks = []

                                current_section = chapter_num
                            else:
                                current_blocks.append(block)

                    except Exception as e:
                        logger.error(f"Error processing page {page_num + 1}: {e}")

                # Save the last section if exists
                if current_section is not None and current_blocks:
                    file_path = os.path.join(sections_dir,
                                           f"{current_section}.md")
                    
                    sections.append(
                        Section(number=len(sections),
                               content="\n".join(
                                   block.text for block in current_blocks),
                               page_number=progress.current_page,
                               file_path=file_path,
                               pdf_name=pdf_folder_name,
                               title=None,
                               formatted_content=current_blocks,
                               is_chapter=True,
                               chapter_number=current_section))
                    self.file_system_processor.save_section_content(sections[-1])
                    progress.processed_sections += 1

            # Extract images
            progress.status = ProcessingStatus.EXTRACTING_IMAGES
            images = self.image_processor.extract_images(
                pdf_path, images_dir, metadata_dir, pdf_folder_name, sections)

            progress.status = ProcessingStatus.COMPLETED
            return ProcessedPDF(sections=sections,
                              images=images,
                              pdf_name=pdf_folder_name,
                              base_path=base_output_dir,
                              progress=progress)

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            return ProcessedPDF(sections=sections,
                              images=images,
                              pdf_name=pdf_folder_name,
                              base_path=base_output_dir,
                              progress=progress)

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
