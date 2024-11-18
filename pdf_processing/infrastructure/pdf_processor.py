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
        # Simplified pattern to match only standalone numbers
        self.chapter_pattern = r'^\s*(\d+)\s*$'
        self.header_patterns = [
            r'^[A-Z][^a-z]{0,2}[A-Z].*$',  # All caps or nearly all caps
            r'^[A-Z][a-zA-Z\s]{0,50}$',     # Title case, not too long
        ]

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
        histoire_dir = os.path.join(book_dir, "histoire")

        for directory in [book_dir, sections_dir, images_dir, metadata_dir, histoire_dir]:
            os.makedirs(directory, exist_ok=True)

        return {
            "book_dir": book_dir,
            "sections_dir": sections_dir,
            "images_dir": images_dir,
            "metadata_dir": metadata_dir,
            "histoire_dir": histoire_dir
        }

    def _detect_chapter(self, text: str) -> Tuple[Optional[int], Optional[str]]:
        """Detect if text is a standalone number"""
        text = text.strip()
        match = re.match(self.chapter_pattern, text)
        if match:
            try:
                chapter_num = int(match.group(1))
                return chapter_num, ""
            except ValueError:
                pass
        return None, None

    def _is_centered_text(self, text: str, line_spacing: Optional[float] = None) -> bool:
        """Enhanced centered text detection"""
        text = text.strip()
        if not text:
            return False
            
        # Skip long paragraphs
        if len(text) > 100:
            return False
            
        # Check for common centered text indicators
        indicators = [
            text.isupper(),  # All uppercase
            text.istitle(),  # Title case
            text.startswith('    ') or text.startswith('\t'),  # Indentation
            text.startswith('*') and text.endswith('*'),  # Asterisk wrapping
            bool(re.match(r'^[-—=]{3,}$', text)),  # Horizontal rules
            bool(re.match(r'^[A-Z][^.!?]*(?:[.!?]|\s)*$', text))  # Single complete sentence starting with capital
        ]
        
        return any(indicators) and len(text.split()) <= 10  # Limit to short phrases

    def _detect_formatting(self, text: str, is_pre_section: bool = False) -> TextFormatting:
        """Enhanced formatting detection"""
        text = text.strip()
        
        if not text:
            return TextFormatting.PARAGRAPH

        # Check for standalone section number
        chapter_num, _ = self._detect_chapter(text)
        if chapter_num is not None and not is_pre_section:
            return TextFormatting.HEADER

        # Enhanced centered text detection for pre-sections
        if is_pre_section and self._is_centered_text(text):
            return TextFormatting.HEADER

        # Check for headers
        if any(re.match(pattern, text) for pattern in self.header_patterns):
            return TextFormatting.HEADER

        # Check for list items
        if re.match(r'^\s*[-•*]\s+', text) or re.match(r'^\s*\d+\.\s+.+', text):
            return TextFormatting.LIST_ITEM

        # Check for code blocks
        if text.startswith('    ') or text.startswith('\t'):
            return TextFormatting.CODE

        # Check for quotes
        if text.startswith('>') or (text.startswith('"') and text.endswith('"')):
            return TextFormatting.QUOTE

        # Check for subheaders in pre-section content
        if is_pre_section and len(text) < 100 and text.istitle():
            return TextFormatting.SUBHEADER

        return TextFormatting.PARAGRAPH

    def _process_text_block(self, text: str, is_pre_section: bool = False) -> List[FormattedText]:
        """Process a block of text and return formatted text segments"""
        formatted_texts = []
        current_format = None
        current_text = []
        
        for line in text.splitlines():
            line = line.strip()
            if not line:
                if current_text:
                    formatted_texts.append(FormattedText(
                        text="\n".join(current_text),
                        format_type=current_format or TextFormatting.PARAGRAPH
                    ))
                    current_text = []
                    current_format = None
                continue

            format_type = self._detect_formatting(line, is_pre_section)
            
            if format_type != current_format or format_type in [TextFormatting.HEADER, TextFormatting.SUBHEADER]:
                if current_text:
                    formatted_texts.append(FormattedText(
                        text="\n".join(current_text),
                        format_type=current_format or TextFormatting.PARAGRAPH
                    ))
                    current_text = []
                current_format = format_type
            
            current_text.append(line)
        
        if current_text:
            formatted_texts.append(FormattedText(
                text="\n".join(current_text),
                format_type=current_format or TextFormatting.PARAGRAPH
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
        """Extract sections from the PDF"""
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        sections_dir = paths["sections_dir"]
        histoire_dir = paths["histoire_dir"]
        
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        sections = []
        
        try:
            reader = PdfReader(pdf_path)
            progress.total_pages = len(reader.pages)
            progress.status = ProcessingStatus.EXTRACTING_SECTIONS
            
            # First pass: collect all content until first standalone number
            pre_section_content = []
            first_section_page = None
            first_section_number = None
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                page_lines = []
                lines = text.splitlines()
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check for standalone section number
                    chapter_num, _ = self._detect_chapter(line)
                    if chapter_num is not None:
                        first_section_page = page_num
                        first_section_number = line
                        break
                    
                    page_lines.append(line)
                
                if first_section_page is not None:
                    break
                
                if page_lines:
                    pre_section_content.append("\n".join(page_lines))
            
            # Save pre-section content
            if pre_section_content:
                content = "\n".join(pre_section_content)
                file_path = os.path.join(histoire_dir, "introduction.md")
                formatted_content = self._process_text_block(content, is_pre_section=True)
                
                sections.append(Section(
                    number=0,
                    content=content,
                    page_number=1,
                    file_path=file_path,
                    pdf_name=pdf_folder_name,
                    title="Introduction",
                    formatted_content=formatted_content,
                    is_chapter=False,
                    chapter_number=None
                ))
                progress.processed_sections += 1
            
            # Second pass: process numbered sections
            current_section = None
            current_text = []
            current_page = first_section_page or 0
            
            # Start with the first section number if we found one
            if first_section_number:
                chapter_num, _ = self._detect_chapter(first_section_number)
                if chapter_num is not None:
                    current_section = {
                        'chapter': chapter_num,
                        'title': "",
                        'page': current_page + 1
                    }
                    current_text = [first_section_number]
            
            # Process remaining pages
            for page_num in range(current_page, len(reader.pages)):
                page = reader.pages[page_num]
                progress.current_page = page_num + 1
                
                try:
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    lines = text.splitlines()
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Skip the first section number we already processed
                        if page_num == first_section_page and line == first_section_number:
                            continue
                        
                        chapter_num, _ = self._detect_chapter(line)
                        if chapter_num is not None:
                            # Save previous section if exists
                            if current_section is not None and current_text:
                                file_path = os.path.join(sections_dir, f"{current_section['chapter']}.md")
                                formatted_content = self._process_text_block("\n".join(current_text))
                                
                                sections.append(Section(
                                    number=len(sections),
                                    content="\n".join(current_text),
                                    page_number=current_section['page'],
                                    file_path=file_path,
                                    pdf_name=pdf_folder_name,
                                    title=current_section['title'],
                                    formatted_content=formatted_content,
                                    is_chapter=True,
                                    chapter_number=current_section['chapter']
                                ))
                                progress.processed_sections += 1
                            
                            # Start new section
                            current_section = {
                                'chapter': chapter_num,
                                'title': "",
                                'page': page_num + 1
                            }
                            current_text = [line]
                        elif current_section is not None:
                            current_text.append(line)
                
                except Exception as e:
                    print(f"Error processing page {page_num + 1}: {e}")
                    continue
            
            # Save last section if exists
            if current_section is not None and current_text:
                file_path = os.path.join(sections_dir, f"{current_section['chapter']}.md")
                formatted_content = self._process_text_block("\n".join(current_text))
                
                sections.append(Section(
                    number=len(sections),
                    content="\n".join(current_text),
                    page_number=current_section['page'],
                    file_path=file_path,
                    pdf_name=pdf_folder_name,
                    title=current_section['title'],
                    formatted_content=formatted_content,
                    is_chapter=True,
                    chapter_number=current_section['chapter']
                ))
                progress.processed_sections += 1
            
            # Save sections with proper markdown formatting
            for section in sections:
                os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
                formatted_content = []
                
                # Add title
                if section.is_chapter:
                    formatted_content.append(f"# {section.chapter_number}\n")
                else:
                    formatted_content.append("# Introduction\n")
                
                # Add formatted content
                for fmt_text in section.formatted_content:
                    if fmt_text.format_type == TextFormatting.HEADER:
                        formatted_content.append(f"\n## {fmt_text.text}\n")
                    elif fmt_text.format_type == TextFormatting.SUBHEADER:
                        formatted_content.append(f"\n### {fmt_text.text}\n")
                    elif fmt_text.format_type == TextFormatting.LIST_ITEM:
                        formatted_content.append(f"\n- {fmt_text.text}\n")
                    elif fmt_text.format_type == TextFormatting.CODE:
                        formatted_content.append(f"\n```\n{fmt_text.text}\n```\n")
                    elif fmt_text.format_type == TextFormatting.QUOTE:
                        formatted_content.append(f"\n> {fmt_text.text}\n")
                    else:
                        formatted_content.append(f"\n{fmt_text.text}\n")
                
                with open(section.file_path, 'w', encoding='utf-8') as f:
                    f.write("".join(formatted_content).strip() + "\n")
            
            # Extract images
            progress.status = ProcessingStatus.EXTRACTING_IMAGES
            images = await self.extract_images(pdf_path, base_output_dir)
            
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
