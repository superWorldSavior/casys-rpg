import os
from typing import List, Optional, Dict, Tuple
import logging
import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import asyncio
from ..domain.ports import PDFProcessor
from ..domain.entities import (Section, ProcessedPDF, PDFImage,
                             ProcessingStatus, ProcessingProgress, 
                             TextFormatting, FormattedText)
from .text_format_processor import TextFormatProcessor
from .file_system_processor import FileSystemProcessor
from .ai_processor import AIProcessor
import json
import re

logger = logging.getLogger(__name__)

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.text_processor = TextFormatProcessor()
        self.file_system_processor = FileSystemProcessor()
        self.ai_processor = AIProcessor()
        self.max_content_length = 4000

    async def get_section_count(self, doc: fitz.Document) -> Tuple[int, int, int]:
        """Get accurate section counts using PyMuPDF"""
        logger.info("Analyzing document structure for section counting")
        total_sections = 0
        pre_sections = 0
        numbered_sections = 0
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                # Use AI to detect chapter boundaries
                is_chapter_start, chapter_title = await self.ai_processor.detect_chapter_with_ai(text)
                if is_chapter_start:
                    pre_sections += 1
                    logger.info(f"Detected chapter boundary at page {page_num + 1}: {chapter_title}")
                
                # Look for numbered sections with enhanced detection
                if re.search(r'^\s*\d+\s*[.:)]', text, re.MULTILINE):
                    numbered_sections += 1
                    logger.info(f"Detected numbered section at page {page_num + 1}")
            
            total_sections = pre_sections + numbered_sections
            logger.info(f"Section count analysis complete - Total: {total_sections}, "
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
        """Process first section with improved chapter boundary detection and logging"""
        logger.info("Starting first section processing with enhanced boundary detection")
        sections = []
        current_chapter = None
        current_blocks = []
        page_context = ""
        
        try:
            # Get images for multimodal analysis
            logger.info("Extracting images for multimodal analysis")
            base_dir = os.path.dirname(os.path.dirname(histoire_dir))
            images = self.extract_images(
                pdf_path=doc.name,
                base_output_dir=base_dir
            )

            # Process pages until first numbered section is found
            for page_num in range(len(doc)):
                logger.info(f"Processing page {page_num + 1}")
                page = doc[page_num]
                try:
                    text = page.get_text("text")
                    if not text.strip():
                        logger.debug(f"Skipping empty page {page_num + 1}")
                        continue

                    # Check for numbered section with enhanced detection
                    if re.search(r'^\s*\d+\s*[.:)]', text, re.MULTILINE):
                        logger.info(f"Found numbered section at page {page_num + 1}, stopping pre-section processing")
                        break

                    # Manage content length
                    if len(page_context + text) > self.max_content_length:
                        text = text[:self.max_content_length - len(page_context)]
                        logger.debug(f"Truncated page {page_num + 1} content to fit length limit")
                    
                    page_context += text

                    # Enhanced multimodal analysis with detailed logging
                    logger.info(f"Performing multimodal analysis for page {page_num + 1}")
                    page_blocks, new_chapter_info, is_chapter_complete = await self.ai_processor.analyze_page_with_chapters(
                        text,
                        page_num + 1,
                        images,
                        current_chapter
                    )

                    # Handle chapter boundaries with improved logging
                    if new_chapter_info and new_chapter_info != current_chapter:
                        logger.info(f"Detected new chapter boundary: {new_chapter_info.get('title')}")
                        if current_chapter and current_blocks:
                            section = await self.save_section(
                                section_num=len(sections) + 1,
                                blocks=current_blocks,
                                page_num=page_num,
                                output_dir=histoire_dir,
                                pdf_folder_name=pdf_folder_name,
                                is_chapter=True,
                                title=current_chapter.get("title")
                            )
                            sections.append(section)
                            logger.info(f"Saved chapter: {current_chapter.get('title')}")
                            current_blocks = []
                            page_context = text
                        
                        current_chapter = new_chapter_info
                        logger.info(f"Started new chapter: {current_chapter.get('title')}")

                    # Accumulate content
                    current_blocks.extend(page_blocks)

                    # Handle chapter completion
                    if is_chapter_complete and current_chapter and current_blocks:
                        logger.info(f"Chapter complete: {current_chapter.get('title')}")
                        section = await self.save_section(
                            section_num=len(sections) + 1,
                            blocks=current_blocks,
                            page_num=page_num + 1,
                            output_dir=histoire_dir,
                            pdf_folder_name=pdf_folder_name,
                            is_chapter=True,
                            title=current_chapter.get("title")
                        )
                        sections.append(section)

                except Exception as page_error:
                    logger.error(f"Error processing page {page_num + 1}: {page_error}")
                    continue

            # Handle remaining content
            if current_blocks and not sections:
                logger.info("Saving accumulated content as final section")
                section = await self.save_section(
                    section_num=1,
                    blocks=current_blocks,
                    page_num=len(doc),
                    output_dir=histoire_dir,
                    pdf_folder_name=pdf_folder_name,
                    is_chapter=True,
                    title=current_chapter.get("title") if current_chapter else "Chapter 1"
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
            doc = fitz.open(pdf_path)
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            images_dir = os.path.join(base_output_dir, pdf_name, "images")
            metadata_dir = os.path.join(base_output_dir, pdf_name, "metadata")
            
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
                        
                        # Save as PNG
                        image_filename = f"image_{page_num + 1}_{img_idx + 1}.png"
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
            
            # Save all metadata to a single file
            metadata_path = os.path.join(metadata_dir, "images.json")
            with open(metadata_path, "w") as meta_file:
                json.dump({
                    "pdf_name": pdf_name,
                    "total_images": len(images_metadata),
                    "images": images_metadata
                }, meta_file, indent=2)
                
            return images
            
        except Exception as e:
            logger.error(f"Error in image extraction: {e}")
            return []
        finally:
            if doc:
                doc.close()

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections with enhanced counting and logging"""
        pdf_folder_name = self.file_system_processor.get_pdf_folder_name(pdf_path)
        paths = self.file_system_processor.create_book_structure(base_output_dir, pdf_folder_name)
        sections = []
        images = []
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        doc = None

        try:
            logger.info(f"Opening PDF: {pdf_path}")
            doc = fitz.open(pdf_path)
            
            # Get accurate section counts
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
            logger.info(f"Extracted {len(images)} images")

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

    async def save_section(self, section_num: int, blocks: List[FormattedText],
                          page_num: int, output_dir: str, pdf_folder_name: str,
                          is_chapter: bool = False, title: Optional[str] = None) -> Section:
        """Save a section with proper formatting and metadata"""
        try:
            # Create chapter directory
            chapter_dir = os.path.join(output_dir, f"chapter_{section_num}")
            os.makedirs(chapter_dir, exist_ok=True)

            # Prepare filenames
            content_filename = "content.md"
            section_path = os.path.join(chapter_dir, content_filename)

            # Format content with proper markdown structure
            formatted_content = []
            if title:
                formatted_content.append(f"# {title}\n")

            current_context = None
            for block in blocks:
                # Add spacing between different contexts
                if block.metadata.get("context") != current_context:
                    formatted_content.append("")
                    current_context = block.metadata.get("context")

                # Format based on block type
                if not isinstance(block, FormattedText):
                    continue

                text = block.text.strip()
                if not text:
                    continue

                if block.format_type == TextFormatting.HEADER:
                    formatted_content.append(f"# {text}\n")
                elif block.format_type == TextFormatting.SUBHEADER:
                    formatted_content.append(f"## {text}\n")
                elif block.format_type == TextFormatting.LIST_ITEM:
                    indent = "  " * block.metadata.get("indentation_level", 0)
                    if block.metadata.get("context") == "numbered_list":
                        formatted_content.append(f"{indent}1. {text}")
                    else:
                        formatted_content.append(f"{indent}- {text}")
                elif block.format_type == TextFormatting.QUOTE:
                    formatted_content.append(f"> {text}")
                else:
                    formatted_content.append(text)

            # Write content to file
            with open(section_path, "w", encoding="utf-8") as f:
                f.write("\n".join(formatted_content))

            # Create section object
            section = Section(
                number=section_num,
                content="\n".join(formatted_content),
                page_number=page_num,
                file_path=section_path,
                pdf_name=pdf_folder_name,
                title=title or f"Chapter {section_num}",
                formatted_content=blocks,
                is_chapter=True,
                chapter_number=section_num
            )

            return section

        except Exception as e:
            logger.error(f"Error saving section {section_num}: {e}")
            raise