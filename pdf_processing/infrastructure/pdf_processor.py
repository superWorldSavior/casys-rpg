"""PDF Processor implementation with multimodal chapter analysis"""
import os
import re
import json
import logging
from typing import List, Optional, Dict, Tuple
import fitz  # PyMuPDF
from ..domain.ports import PDFProcessor
from ..domain.entities import (Section, ProcessedPDF, PDFImage,
                           ProcessingStatus, ProcessingProgress, 
                           TextFormatting, FormattedText)
from .file_system_processor import FileSystemProcessor
from .ai_processor import AIProcessor

logger = logging.getLogger(__name__)

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.file_system_processor = FileSystemProcessor()
        self.ai_processor = AIProcessor()
        self.max_content_length = 4000

    async def get_section_count(self, doc: fitz.Document) -> Tuple[int, int, int]:
        """Get section counts using multimodal analysis"""
        logger.info("Starting section count analysis using multimodal processing")
        total_sections = 0
        pre_sections = 0
        numbered_sections = 0
        current_chapter = None
        
        try:
            # Extract images for multimodal analysis
            images = self.extract_images(doc.name)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                # Use multimodal analysis for chapter detection
                blocks, new_chapter_info, is_chapter_complete = await self.ai_processor.analyze_page_with_chapters(
                    text, page_num + 1, images, current_chapter
                )
                
                if new_chapter_info and new_chapter_info != current_chapter:
                    pre_sections += 1
                    current_chapter = new_chapter_info
                    logger.info(f"Detected chapter at page {page_num + 1}: {new_chapter_info.get('title')}")
                
                # Check for numbered sections
                if re.search(r'^\s*\d+\s*[.:)]', text, re.MULTILINE):
                    numbered_sections += 1
                    logger.debug(f"Detected numbered section at page {page_num + 1}")

            total_sections = pre_sections + numbered_sections
            logger.info(f"Section analysis complete - Total: {total_sections}, "
                       f"Pre-sections: {pre_sections}, Numbered: {numbered_sections}")
            
            return total_sections, pre_sections, numbered_sections
            
        except Exception as e:
            logger.error(f"Error in section counting: {e}")
            return 0, 0, 0

    async def process_first_section(
        self, 
        doc: fitz.Document,
        histoire_dir: str,
        pdf_folder_name: str
    ) -> List[Section]:
        """Process first section with multimodal analysis"""
        logger.info("Starting first section processing with multimodal analysis")
        sections = []
        current_chapter = None
        current_blocks = []
        
        try:
            # Get images for multimodal analysis
            images = self.extract_images(doc.name)
            
            # Process pages until first numbered section
            for page_num in range(len(doc)):
                logger.info(f"Processing page {page_num + 1}")
                page = doc[page_num]
                text = page.get_text("text")
                
                if not text.strip():
                    logger.debug(f"Skipping empty page {page_num + 1}")
                    continue

                # Check for numbered section
                if re.search(r'^\s*\d+\s*[.:)]', text, re.MULTILINE):
                    logger.info(f"Found numbered section at page {page_num + 1}, stopping pre-section processing")
                    break

                # Perform multimodal analysis
                blocks, new_chapter_info, is_chapter_complete = await self.ai_processor.analyze_page_with_chapters(
                    text,
                    page_num + 1,
                    images,
                    current_chapter
                )

                # Handle chapter transitions
                if new_chapter_info and new_chapter_info != current_chapter:
                    logger.info(f"New chapter detected: {new_chapter_info.get('title')}")
                    if current_chapter and current_blocks:
                        section = await self.save_section(
                            section_num=len(sections) + 1,
                            blocks=current_blocks,
                            page_num=page_num,
                            output_dir=histoire_dir,
                            pdf_folder_name=pdf_folder_name,
                            title=current_chapter.get("title")
                        )
                        sections.append(section)
                        current_blocks = []
                    
                    current_chapter = new_chapter_info

                current_blocks.extend(blocks)

                if is_chapter_complete and current_chapter and current_blocks:
                    logger.info(f"Chapter complete: {current_chapter.get('title')}")
                    section = await self.save_section(
                        section_num=len(sections) + 1,
                        blocks=current_blocks,
                        page_num=page_num + 1,
                        output_dir=histoire_dir,
                        pdf_folder_name=pdf_folder_name,
                        title=current_chapter.get("title")
                    )
                    sections.append(section)
                    current_blocks = []
                    current_chapter = None

            # Handle remaining content
            if current_blocks:
                section = await self.save_section(
                    section_num=len(sections) + 1,
                    blocks=current_blocks,
                    page_num=len(doc),
                    output_dir=histoire_dir,
                    pdf_folder_name=pdf_folder_name,
                    title=current_chapter.get("title") if current_chapter else None
                )
                sections.append(section)

        except Exception as e:
            logger.error(f"Error in first section processing: {e}")
            raise

        return sections

    def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        """Extract images from PDF using MuPDF"""
        images = []
        doc = None
        try:
            logger.info(f"Extracting images from {pdf_path}")
            doc = fitz.open(pdf_path)
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            # Setup directories
            book_dir = os.path.join(base_output_dir, pdf_name)
            images_dir = os.path.join(book_dir, "images")
            metadata_dir = os.path.join(book_dir, "metadata")
            
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(metadata_dir, exist_ok=True)
            
            images_metadata = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        image_filename = f"page_{page_num + 1}_img_{img_idx + 1}.png"
                        image_path = os.path.join(images_dir, image_filename)
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        image_metadata = {
                            "page_number": page_num + 1,
                            "image_number": img_idx + 1,
                            "file_path": image_path,
                            "pdf_name": pdf_name
                        }
                        
                        images_metadata.append(image_metadata)
                        images.append(PDFImage(
                            page_number=page_num + 1,
                            image_path=image_path,
                            pdf_name=pdf_name,
                            width=img[2],
                            height=img[3]
                        ))
                        
                    except Exception as img_error:
                        logger.error(f"Error extracting image {img_idx} from page {page_num + 1}: {img_error}")
                        continue
            
            # Save metadata
            metadata_path = os.path.join(metadata_dir, "images.json")
            with open(metadata_path, "w") as f:
                json.dump({
                    "pdf_name": pdf_name,
                    "total_images": len(images_metadata),
                    "images": images_metadata
                }, f, indent=2)
            
            logger.info(f"Extracted {len(images)} images from PDF")
            return images
            
        except Exception as e:
            logger.error(f"Error in image extraction: {e}")
            return []
        finally:
            if doc:
                doc.close()

    async def save_section(
        self,
        section_num: int,
        blocks: List[FormattedText],
        page_num: int,
        output_dir: str,
        pdf_folder_name: str,
        title: Optional[str] = None
    ) -> Section:
        """Save section with simplified file naming"""
        try:
            # Use simple chapitre_X.md naming
            filename = f"chapitre_{section_num}.md"
            section_path = os.path.join(output_dir, filename)
            
            logger.info(f"Saving section {section_num} to {section_path}")
            
            # Create section object
            section = Section(
                number=section_num,
                content="",  # Content will be generated from blocks
                page_number=page_num,
                file_path=section_path,
                pdf_name=pdf_folder_name,
                title=title,
                formatted_content=blocks,
                is_chapter=True,
                chapter_number=section_num
            )
            
            # Save content using file system processor
            self.file_system_processor.save_section_content(section)
            
            return section
            
        except Exception as e:
            logger.error(f"Error saving section {section_num}: {e}")
            raise

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections with multimodal analysis"""
        pdf_folder_name = self.file_system_processor.get_pdf_folder_name(pdf_path)
        paths = self.file_system_processor.create_book_structure(base_output_dir, pdf_folder_name)
        sections = []
        images = []
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        doc = None

        try:
            logger.info(f"Processing PDF: {pdf_path}")
            doc = fitz.open(pdf_path)
            
            # Get accurate section counts using multimodal analysis
            total_sections, pre_sections, numbered_sections = await self.get_section_count(doc)
            progress.total_pages = len(doc)
            
            logger.info(f"Document analysis complete: {progress.total_pages} pages, "
                       f"{total_sections} total sections")
            
            # Process first section
            progress.status = ProcessingStatus.PROCESSING_PRE_SECTIONS
            sections = await self.process_first_section(
                doc,
                paths["histoire_dir"],
                pdf_folder_name
            )
            
            # Extract images
            progress.status = ProcessingStatus.EXTRACTING_IMAGES
            images = self.extract_images(pdf_path, base_output_dir)
            progress.processed_images = len(images)
            
            # Update progress
            progress.status = ProcessingStatus.COMPLETED
            progress.processed_sections = len(sections)
            
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
            return ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )
        finally:
            if doc:
                doc.close()