import os
from typing import List, Optional, Dict
import logging
import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import asyncio
from ..domain.ports import PDFProcessor
from ..domain.entities import (Section, ProcessedPDF, PDFImage,
                             ProcessingStatus, ProcessingProgress, FormattedText)
from .text_format_processor import TextFormatProcessor
from .file_system_processor import FileSystemProcessor
from .ai_processor import AIProcessor
import json

logger = logging.getLogger(__name__)

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.text_processor = TextFormatProcessor()
        self.file_system_processor = FileSystemProcessor()
        self.ai_processor = AIProcessor()
        self.max_content_length = 4000  # Limit content length for analysis

    def extract_images(self, doc_path: str, images_dir: str, metadata_dir: str,
                      pdf_name: str, sections: Optional[List[Section]] = None,
                      page_limit: Optional[int] = None) -> List[PDFImage]:
        """Extract images from PDF using MuPDF"""
        images = []
        try:
            doc = fitz.open(doc_path)
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(metadata_dir, exist_ok=True)

            max_page = page_limit if page_limit is not None else len(doc)
            
            for page_num in range(max_page):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        image_filename = f"image_{page_num + 1}_{img_idx + 1}.{image_ext}"
                        image_path = os.path.join(images_dir, image_filename)
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                            
                        image_metadata = {
                            "page_number": page_num + 1,
                            "image_number": img_idx + 1,
                            "file_path": image_path,
                            "extension": image_ext,
                            "pdf_name": pdf_name
                        }
                        
                        metadata_filename = f"image_{page_num + 1}_{img_idx + 1}_metadata.json"
                        metadata_path = os.path.join(metadata_dir, metadata_filename)
                        
                        with open(metadata_path, "w") as meta_file:
                            json.dump(image_metadata, meta_file, indent=2)
                            
                        images.append(PDFImage(**image_metadata))
                        
                    except Exception as img_error:
                        logger.error(f"Error extracting image {img_idx} from page {page_num + 1}: {img_error}")
                        continue
                        
            doc.close()
            return images
            
        except Exception as e:
            logger.error(f"Error in image extraction: {e}")
            if 'doc' in locals():
                doc.close()
            return images

    async def process_first_section(self, doc, histoire_dir: str, pdf_folder_name: str) -> List[Section]:
        """Process only the first section using gpt-4o-mini multimodal analysis"""
        logger.info("Starting first section processing")
        sections = []
        current_chapter = None
        current_blocks = []
        page_context = ""

        try:
            # Get images for multimodal analysis
            images = self.extract_images(
                doc_path=doc.name,
                images_dir=os.path.join(os.path.dirname(histoire_dir), "images"),
                metadata_dir=os.path.join(os.path.dirname(histoire_dir), "metadata"),
                pdf_name=pdf_folder_name,
                page_limit=10  # Limit to first 10 pages for first section
            )

            # Process first few pages until we get a complete chapter
            for page_num in range(min(10, len(doc))):
                page = doc[page_num]
                try:
                    text = page.get_text("text")
                    if len(text.strip()) == 0:
                        logger.info(f"Skipping empty page {page_num + 1}")
                        continue

                    # Manage content length
                    if len(page_context + text) > self.max_content_length:
                        text = text[:self.max_content_length - len(page_context)]
                    
                    page_context += text

                    # Use gpt-4o-mini analysis
                    page_blocks, new_chapter_info, is_chapter_complete = await self.ai_processor.analyze_page_with_chapters(
                        text,
                        page_num + 1,
                        images,
                        current_chapter
                    )

                    # Handle chapter information
                    if new_chapter_info and new_chapter_info != current_chapter:
                        # If we have a new chapter and already have content, save the current one
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
                            current_blocks = []
                            page_context = text  # Reset context to current page
                        
                        current_chapter = new_chapter_info
                    
                    # Accumulate content
                    current_blocks.extend(page_blocks)

                    # Save and return if chapter is complete
                    if is_chapter_complete and current_chapter and current_blocks:
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
                        break  # Stop after first complete chapter

                except Exception as page_error:
                    logger.error(f"Error processing page {page_num + 1}: {page_error}")
                    continue

            # If we haven't found a complete chapter but have content, save what we have
            if not sections and current_blocks:
                section = await self.save_section(
                    section_num=1,
                    blocks=current_blocks,
                    page_num=min(10, len(doc)),
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
            metadata_dir = os.path.join(os.path.dirname(output_dir), "metadata")
            os.makedirs(metadata_dir, exist_ok=True)

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
                text = block.text
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

            # Save content
            with open(section_path, "w", encoding="utf-8") as f:
                f.write("\n".join(formatted_content))

            # Save metadata
            metadata = {
                "section_number": section_num,
                "title": section.title,
                "page_number": page_num,
                "is_chapter": True,
                "chapter_number": section_num,
                "content_file": os.path.join(f"chapter_{section_num}", content_filename)
            }
            
            metadata_path = os.path.join(metadata_dir, "book.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    book_metadata = json.load(f)
                if "sections" not in book_metadata:
                    book_metadata["sections"] = []
                book_metadata["sections"].append(metadata)
            else:
                book_metadata = {
                    "title": pdf_folder_name,
                    "sections": [metadata],
                    "processing_status": "completed"
                }
            
            with open(metadata_path, 'w') as f:
                json.dump(book_metadata, f, indent=2)

            logger.info(f"Successfully saved chapter {section_num} with metadata")
            return section

        except Exception as e:
            logger.error(f"Error saving section {section_num}: {e}")
            raise

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract only the first section using gpt-4o-mini analysis"""
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

            # Process only the first section
            progress.status = ProcessingStatus.PROCESSING_PRE_SECTIONS
            sections = await self.process_first_section(
                doc,
                paths["histoire_dir"],
                pdf_folder_name
            )

            # Extract images for the processed section
            progress.status = ProcessingStatus.EXTRACTING_IMAGES
            if sections:
                max_page = sections[0].page_number
                images = self.extract_images(
                    pdf_path,
                    paths["images_dir"],
                    paths["metadata_dir"],
                    pdf_folder_name,
                    sections,
                    page_limit=max_page
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