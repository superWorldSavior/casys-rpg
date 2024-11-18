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

    def _is_centered_text(self, text: str, line_spacing: Optional[float] = None) -> bool:
        """Detect if text appears to be centered based on formatting"""
        if not text.strip():
            return False
        if len(text.strip()) > 100:
            return False
        if text.startswith('    ') or text.startswith('\t'):
            return True
        return text.istitle() or text.isupper()

    def _detect_formatting(self, text: str, is_pre_section: bool = False) -> TextFormatting:
        """Detect the formatting type of a text line"""
        text = text.strip()
        
        if not text:
            return TextFormatting.PARAGRAPH

        chapter_num, _ = self._detect_chapter(text)
        if chapter_num is not None and not is_pre_section:
            return TextFormatting.HEADER

        if is_pre_section and self._is_centered_text(text):
            return TextFormatting.HEADER

        if any(re.match(pattern, text) for pattern in self.header_patterns):
            return TextFormatting.HEADER

        if re.match(r'^\s*[-•*]\s+', text) or re.match(r'^\s*\d+\.\s+.+', text):
            return TextFormatting.LIST_ITEM

        if text.startswith('    ') or text.startswith('\t'):
            return TextFormatting.CODE

        if text.startswith('>') or (text.startswith('"') and text.endswith('"')):
            return TextFormatting.QUOTE

        if len(text) < 100 and text.istitle():
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
            
            # First pass: collect pre-section content
            pre_section_content = []
            first_chapter_page = None
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.splitlines()
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if this is a numbered chapter
                    chapter_num, _ = self._detect_chapter(line)
                    if chapter_num is not None:
                        first_chapter_page = page_num
                        break
                
                if first_chapter_page is not None:
                    break
                    
                pre_section_content.append(text)
            
            # Save pre-section content if it exists
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
            current_page = first_chapter_page or 0
            
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
                        
                        chapter_num, title = self._detect_chapter(line)
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
                                'title': title,
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
                    if section.title:
                        formatted_content.append(f"# Chapter {section.chapter_number}: {section.title}\n")
                    else:
                        formatted_content.append(f"# Chapter {section.chapter_number}\n")
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
