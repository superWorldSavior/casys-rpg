import os
import fitz  # PyMuPDF
import re
import json
from typing import List, Optional, Dict, Tuple
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfReader
from ..domain.ports import PDFProcessor
from ..domain.entities import (
    Section, PDFImage, ProcessedPDF, ProcessingStatus, 
    ProcessingProgress, TextFormatting, FormattedText
)

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.chapter_patterns = [
            r'^(?:chapter|section)\s*(\d+)(?:[.:]\s*|\s+)(.*)$',
            r'^\s*(\d+)(?:[.:]\s*|\s+)(.*)$',
            r'^\s*part\s+(\d+)(?:[.:]\s*|\s+)(.*)$',
        ]
        self.header_patterns = [
            r'^[A-Z][^a-z]{0,2}[A-Z].*$',  # All caps or nearly all caps
            r'^[A-Z][a-zA-Z\s]{0,50}$',     # Title case, not too long
        ]
        self.numerical_start_pattern = r'^\s*\d+\.?\s*$'  # Matches standalone numbers

    def _get_pdf_folder_name(self, pdf_path: str) -> str:
        base_name = os.path.basename(pdf_path)
        folder_name = os.path.splitext(base_name)[0]
        folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
        return folder_name

    def _create_book_structure(self, base_output_dir: str, pdf_folder_name: str) -> Dict[str, str]:
        """Create the book directory structure and return paths"""
        book_dir = os.path.join(base_output_dir, pdf_folder_name)
        sections_dir = os.path.join(book_dir, "sections")
        images_dir = os.path.join(book_dir, "images")
        metadata_dir = os.path.join(book_dir, "metadata")

        for directory in [book_dir, sections_dir, images_dir, metadata_dir]:
            os.makedirs(directory, exist_ok=True)

        return {
            "book_dir": book_dir,
            "sections_dir": sections_dir,
            "images_dir": images_dir,
            "metadata_dir": metadata_dir
        }

    def _detect_chapter(self, text: str) -> Tuple[Optional[int], Optional[str]]:
        """Detect if text is a chapter header and return chapter number and title"""
        text = text.strip()
        for pattern in self.chapter_patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                try:
                    chapter_num = int(match.group(1))
                    title = match.group(2).strip() if len(match.groups()) > 1 else ""
                    return chapter_num, title
                except ValueError:
                    continue
        return None, None

    def _is_standalone_number(self, text: str) -> bool:
        """Check if the text is just a standalone number (possibly with a period)"""
        return bool(re.match(self.numerical_start_pattern, text))

    def _detect_formatting(self, text: str, is_pre_section: bool = False) -> TextFormatting:
        """Detect the formatting type of a text line"""
        text = text.strip()
        
        # Empty line
        if not text:
            return TextFormatting.PARAGRAPH

        # Skip standalone numbers in pre-section content
        if is_pre_section and self._is_standalone_number(text):
            return TextFormatting.PARAGRAPH

        # Check for headers
        chapter_num, _ = self._detect_chapter(text)
        if chapter_num is not None:
            return TextFormatting.HEADER

        # Check for all caps headers
        if any(re.match(pattern, text) for pattern in self.header_patterns):
            return TextFormatting.HEADER

        # Check for list items
        if re.match(r'^\s*[-•*]\s+', text) or re.match(r'^\s*\d+\.\s+.+', text):
            return TextFormatting.LIST_ITEM

        # Check for code blocks (indented text)
        if text.startswith('    ') or text.startswith('\t'):
            return TextFormatting.CODE

        # Check for quotes
        if text.startswith('>') or (text.startswith('"') and text.endswith('"')):
            return TextFormatting.QUOTE

        # Check for subheaders (shorter lines with title case)
        if len(text) < 100 and text.istitle():
            return TextFormatting.SUBHEADER

        return TextFormatting.PARAGRAPH

    def _process_text_block(self, text: str, is_pre_section: bool = False) -> List[FormattedText]:
        """Process a block of text and return formatted text segments"""
        formatted_texts = []
        paragraphs = text.split('\n\n')
        
        current_list_items = []
        current_paragraph = []
        
        for line in text.splitlines():
            line = line.strip()
            if not line:
                if current_paragraph:
                    formatted_texts.append(FormattedText(
                        text='\n'.join(current_paragraph),
                        format_type=TextFormatting.PARAGRAPH
                    ))
                    current_paragraph = []
                continue
            
            # For pre-section content, check if it's actually a section marker
            if is_pre_section:
                chapter_num, _ = self._detect_chapter(line)
                if chapter_num is not None or self._is_standalone_number(line):
                    continue
            
            format_type = self._detect_formatting(line, is_pre_section)
            
            # Handle list items specially
            if format_type == TextFormatting.LIST_ITEM:
                if current_paragraph:
                    formatted_texts.append(FormattedText(
                        text='\n'.join(current_paragraph),
                        format_type=TextFormatting.PARAGRAPH
                    ))
                    current_paragraph = []
                current_list_items.append(line)
            else:
                if current_list_items:
                    formatted_texts.append(FormattedText(
                        text='\n'.join(current_list_items),
                        format_type=TextFormatting.LIST_ITEM
                    ))
                    current_list_items = []
                
                if format_type in [TextFormatting.HEADER, TextFormatting.SUBHEADER]:
                    if current_paragraph:
                        formatted_texts.append(FormattedText(
                            text='\n'.join(current_paragraph),
                            format_type=TextFormatting.PARAGRAPH
                        ))
                        current_paragraph = []
                    formatted_texts.append(FormattedText(
                        text=line,
                        format_type=format_type
                    ))
                else:
                    current_paragraph.append(line)
        
        # Add any remaining content
        if current_list_items:
            formatted_texts.append(FormattedText(
                text='\n'.join(current_list_items),
                format_type=TextFormatting.LIST_ITEM
            ))
        if current_paragraph:
            formatted_texts.append(FormattedText(
                text='\n'.join(current_paragraph),
                format_type=TextFormatting.PARAGRAPH
            ))
        
        return formatted_texts

    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        """Extract images from the PDF"""
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        images_dir = paths["images_dir"]
        metadata_dir = paths["metadata_dir"]

        images = []
        images_metadata = []

        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_img = doc.extract_image(xref)
                        image_bytes = base_img["image"]
                        
                        image = Image.open(io.BytesIO(image_bytes))
                        width, height = image.size
                        
                        image_filename = f"page_{page_num + 1}_img_{img_idx + 1}.png"
                        image_path = os.path.join(images_dir, image_filename)
                        image.save(image_path)

                        image_data = PDFImage(
                            page_number=page_num + 1,
                            image_path=image_path,
                            pdf_name=pdf_folder_name,
                            width=width,
                            height=height
                        )
                        images.append(image_data)
                        
                        images_metadata.append({
                            "page_number": page_num + 1,
                            "image_path": image_path,
                            "width": width,
                            "height": height,
                            "filename": image_filename
                        })
                    except Exception as e:
                        print(f"Error extracting image {img_idx} from page {page_num + 1}: {e}")
                        continue
            
            doc.close()

            metadata_path = os.path.join(metadata_dir, "images.json")
            with open(metadata_path, 'w') as f:
                json.dump(images_metadata, f, indent=2)

        except Exception as e:
            print(f"Error processing PDF for images: {e}")

        return images

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        sections_dir = paths["sections_dir"]
        
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        
        try:
            reader = PdfReader(pdf_path)
            progress.total_pages = len(reader.pages)
            progress.status = ProcessingStatus.EXTRACTING_SECTIONS
            
            sections = []
            current_section: Optional[int] = None
            current_text: str = ""
            current_page: int = 0
            pre_section_content: str = ""
            current_chapter: Optional[int] = None
            current_title: Optional[str] = None
            
            # First pass: collect all section markers
            section_markers = []
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    lines = text.splitlines()
                    for line in lines:
                        chapter_num, title = self._detect_chapter(line)
                        if chapter_num is not None:
                            section_markers.append((chapter_num, title, page_num))
            
            # Second pass: process content with known section boundaries
            for page_num, page in enumerate(reader.pages):
                progress.current_page = page_num + 1
                try:
                    text = page.extract_text()
                    if text:
                        # Check if this page starts a new section
                        next_section = None
                        for marker_num, marker_title, marker_page in section_markers:
                            if marker_page == page_num:
                                if current_section is not None:
                                    # Save current section
                                    file_path = os.path.join(sections_dir, f"{current_section}.md")
                                    formatted_content = self._process_text_block(current_text)
                                    sections.append(Section(
                                        number=current_section,
                                        content=current_text,
                                        page_number=current_page + 1,
                                        file_path=file_path,
                                        pdf_name=pdf_folder_name,
                                        title=current_title,
                                        formatted_content=formatted_content,
                                        is_chapter=True,
                                        chapter_number=current_chapter
                                    ))
                                    progress.processed_sections += 1
                                
                                current_section = len(sections) + 1
                                current_text = ""
                                current_page = page_num
                                current_chapter = marker_num
                                current_title = marker_title
                                next_section = marker_num
                                break
                        
                        # Process page content
                        lines = text.splitlines()
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Skip section marker lines
                            chapter_num, _ = self._detect_chapter(line)
                            if chapter_num == next_section:
                                continue
                            
                            if current_section is not None:
                                current_text += line + "\n"
                            else:
                                pre_section_content += line + "\n"
                
                except Exception as e:
                    print(f"Error processing page {page_num + 1}: {e}")
                    continue

            # Save last section
            if current_section is not None:
                file_path = os.path.join(sections_dir, f"{current_section}.md")
                formatted_content = self._process_text_block(current_text)
                sections.append(Section(
                    number=current_section,
                    content=current_text,
                    page_number=current_page + 1,
                    file_path=file_path,
                    pdf_name=pdf_folder_name,
                    title=current_title,
                    formatted_content=formatted_content,
                    is_chapter=True,
                    chapter_number=current_chapter
                ))
                progress.processed_sections += 1

            # Save pre-section content if exists
            if pre_section_content.strip():
                file_path = os.path.join(sections_dir, "0.md")
                formatted_content = self._process_text_block(pre_section_content, is_pre_section=True)
                if formatted_content:  # Only save if there's actual content
                    sections.append(Section(
                        number=0,
                        content=pre_section_content,
                        page_number=1,
                        file_path=file_path,
                        pdf_name=pdf_folder_name,
                        title="Introduction",
                        formatted_content=formatted_content,
                        is_chapter=False,
                        chapter_number=None
                    ))
                    progress.processed_sections += 1

            # Extract images
            progress.status = ProcessingStatus.EXTRACTING_IMAGES
            images = await self.extract_images(pdf_path, base_output_dir)
            
            # Save sections content with proper markdown formatting
            progress.status = ProcessingStatus.SAVING_METADATA
            for section in sections:
                os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
                formatted_content = []
                
                # Add title with proper formatting
                if section.is_chapter:
                    if section.title:
                        formatted_content.append(f"# Chapter {section.chapter_number}: {section.title}\n")
                    else:
                        formatted_content.append(f"# Chapter {section.chapter_number}\n")
                else:
                    formatted_content.append("# Introduction\n")
                
                # Add formatted content with proper spacing
                for fmt_text in section.formatted_content:
                    if fmt_text.format_type == TextFormatting.HEADER:
                        formatted_content.append(f"\n## {fmt_text.text}\n")
                    elif fmt_text.format_type == TextFormatting.SUBHEADER:
                        formatted_content.append(f"\n### {fmt_text.text}\n")
                    elif fmt_text.format_type == TextFormatting.LIST_ITEM:
                        items = fmt_text.text.split('\n')
                        formatted_content.append("\n" + "\n".join([f"- {item.lstrip('- ').lstrip('* ').lstrip('• ')}" for item in items]) + "\n")
                    elif fmt_text.format_type == TextFormatting.CODE:
                        formatted_content.append(f"\n```\n{fmt_text.text}\n```\n")
                    elif fmt_text.format_type == TextFormatting.QUOTE:
                        formatted_content.append(f"\n> {fmt_text.text}\n")
                    else:
                        formatted_content.append(f"\n{fmt_text.text}\n")
                
                with open(section.file_path, 'w', encoding='utf-8') as f:
                    f.write("".join(formatted_content))

            progress.status = ProcessingStatus.COMPLETED
            return ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )
        except Exception as e:
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            print(f"Error processing PDF: {e}")
            raise
