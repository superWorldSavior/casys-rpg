# Enhanced PDF processor with proper Vision API model and improved error handling
import os
import fitz  # PyMuPDF
import re
import json
import base64
import io
import tempfile
from typing import List, Optional, Dict, Any
from PIL import Image
from openai import AsyncOpenAI
from ..domain.ports import PDFProcessor
from ..domain.entities import (
    Section, PDFImage, ProcessedPDF, ProcessingStatus, 
    ProcessingProgress, TextFormatting, FormattedText
)

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.chapter_pattern = r'^\s*(\d+)\s*$'
        self.header_patterns = [
            r'^[A-Z][^a-z]{0,2}[A-Z].*$',  # All caps or nearly all caps
            r'^[A-Z][a-zA-Z\s]{0,50}$',     # Title case, not too long
            r'^(?:CHAPTER|Chapter)\s+\d+.*$',  # Chapter headings
            r'^#\s+.*$',  # Markdown-style headers
            r'^.*(?:RULES|INTRODUCTION|EQUIPMENT).*$'  # Special section headers
        ]
        self.pre_section_markers = [
            "INTRODUCTION",
            "COMBAT RULES",
            "GAME RULES",
            "EQUIPMENT"
        ]
        self.openai_client = AsyncOpenAI()

    async def _analyze_page_with_vision(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extract text with formatting using Vision API with fallback to PyMuPDF"""
        try:
            # Extract text blocks with formatting
            blocks = []
            text_page = page.get_textpage()
            text_dict = text_page.extractDICT()
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                text = span.get("text", "").strip()
                                if text:
                                    format_type = self._detect_formatting(text)
                                    blocks.append({
                                        "text": text,
                                        "format_type": format_type
                                    })
            
            if not blocks:
                # Try Vision API for better formatting detection
                try:
                    # Convert page to PNG using PyMuPDF's built-in rendering
                    zoom = 2.0
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    img_data = bytes(pix.samples)
                    img = Image.frombytes("RGB", [pix.width, pix.height], img_data)
                    
                    # Save to temporary PNG file
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        img.save(tmp.name, format='PNG', quality=95)
                        with open(tmp.name, "rb") as image_file:
                            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    
                    os.unlink(tmp.name)
                    
                    # Call Vision API with latest model version
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """Analyze this page layout and formatting:
1. Identify text blocks and their formatting (headers, paragraphs, lists)
2. Detect chapter or section breaks
3. Find pre-section content like Introduction, Rules, Equipment
Return the analysis as structured text blocks with formatting information."""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    }
                                }
                            ]
                        }],
                        max_tokens=4096
                    )
                    
                    if response.choices and response.choices[0].message.content:
                        vision_blocks = self._process_vision_response(response.choices[0].message.content)
                        if vision_blocks:
                            blocks = vision_blocks
                            
                except Exception as e:
                    print(f"Vision API analysis failed: {e}")
                    # Fall back to basic text extraction if Vision API fails
                    text = text_page.extractText()
                    if text.strip():
                        blocks.append({
                            "text": text.strip(),
                            "format_type": self._detect_formatting(text.strip())
                        })
            
            return blocks
            
        except Exception as e:
            print(f"Page analysis failed: {e}")
            return []

    def _process_vision_response(self, content: str) -> List[Dict[str, Any]]:
        """Process Vision API response into structured format"""
        blocks = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                format_type = self._detect_formatting(line)
                blocks.append({
                    "text": line,
                    "format_type": format_type
                })
        return blocks

    def _detect_formatting(self, text: str) -> TextFormatting:
        """Enhanced formatting detection with improved pattern matching"""
        text = text.strip()
        if not text:
            return TextFormatting.PARAGRAPH

        # Check for pre-section markers first
        if any(marker.lower() in text.lower() for marker in self.pre_section_markers):
            return TextFormatting.HEADER

        # Check for headers
        if any(re.match(pattern, text, re.IGNORECASE) for pattern in self.header_patterns):
            return TextFormatting.HEADER

        # Check for subheaders
        if text.isupper() and len(text.split()) <= 4:
            return TextFormatting.SUBHEADER

        # Check for list items
        if re.match(r'^\s*[-•*]\s+', text) or re.match(r'^\s*\d+\.\s+.+', text):
            return TextFormatting.LIST_ITEM

        # Check for quotes
        if text.startswith('>') or (text.startswith('"') and text.endswith('"')):
            return TextFormatting.QUOTE

        # Check for code blocks
        if text.startswith(('    ', '\t')) or all(line.startswith(('    ', '\t')) for line in text.split('\n')):
            return TextFormatting.CODE

        return TextFormatting.PARAGRAPH

    def _save_section_content(self, section: Section) -> None:
        """Save section content with enhanced formatting"""
        os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
        formatted_content = []
        
        if section.title:
            formatted_content.append(f"# {section.title}\n")

        for fmt_text in section.formatted_content:
            if fmt_text.format_type == TextFormatting.HEADER:
                formatted_content.append(f"\n## {fmt_text.text}\n")
            elif fmt_text.format_type == TextFormatting.SUBHEADER:
                formatted_content.append(f"\n### {fmt_text.text}\n")
            elif fmt_text.format_type == TextFormatting.LIST_ITEM:
                formatted_content.append(f"- {fmt_text.text}\n")
            elif fmt_text.format_type == TextFormatting.CODE:
                formatted_content.append(f"\n```\n{fmt_text.text}\n```\n")
            elif fmt_text.format_type == TextFormatting.QUOTE:
                formatted_content.append(f"\n> {fmt_text.text}\n")
            else:
                formatted_content.append(f"\n{fmt_text.text}\n")

        with open(section.file_path, 'w', encoding='utf-8') as f:
            f.write("".join(formatted_content).strip() + "\n")

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections with enhanced pre-section detection"""
        pdf_folder_name = os.path.splitext(os.path.basename(pdf_path))[0]
        book_dir = os.path.join(base_output_dir, pdf_folder_name)
        sections_dir = os.path.join(book_dir, "sections")
        histoire_dir = os.path.join(book_dir, "histoire")
        metadata_dir = os.path.join(book_dir, "metadata")
        
        os.makedirs(sections_dir, exist_ok=True)
        os.makedirs(histoire_dir, exist_ok=True)
        os.makedirs(metadata_dir, exist_ok=True)
        
        sections: List[Section] = []
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        
        try:
            doc = fitz.open(pdf_path)
            progress.total_pages = len(doc)
            progress.status = ProcessingStatus.EXTRACTING_SECTIONS
            
            # First pass: Process pre-sections
            current_chapter = []
            chapter_count = 0
            first_section_page = None
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                progress.current_page = page_num + 1
                
                # Check for numbered section start
                text_page = page.get_textpage()
                text = text_page.extractText()
                if re.search(r'^\s*\d+\s*$', text, re.MULTILINE):
                    first_section_page = page_num
                    break
                
                # Process pre-section content
                blocks = await self._analyze_page_with_vision(page)
                formatted_texts = []
                
                for block in blocks:
                    formatted_texts.append(FormattedText(
                        text=block["text"],
                        format_type=TextFormatting(block["format_type"])
                    ))
                
                # Detect chapter breaks and save content
                if formatted_texts and formatted_texts[0].format_type == TextFormatting.HEADER:
                    if current_chapter:
                        chapter_count += 1
                        file_path = os.path.join(histoire_dir, f"{chapter_count}.md")
                        
                        section = Section(
                            number=chapter_count,
                            content="\n".join(text.text for text in current_chapter),
                            page_number=page_num,
                            file_path=file_path,
                            pdf_name=pdf_folder_name,
                            title=current_chapter[0].text if current_chapter else None,
                            formatted_content=current_chapter,
                            is_chapter=True,
                            chapter_number=chapter_count
                        )
                        self._save_section_content(section)
                        sections.append(section)
                        progress.processed_sections += 1
                        current_chapter = []
                
                current_chapter.extend(formatted_texts)
            
            # Save last pre-section chapter if exists
            if current_chapter:
                chapter_count += 1
                file_path = os.path.join(histoire_dir, f"{chapter_count}.md")
                
                section = Section(
                    number=chapter_count,
                    content="\n".join(text.text for text in current_chapter),
                    page_number=chapter_count,
                    file_path=file_path,
                    pdf_name=pdf_folder_name,
                    title=current_chapter[0].text if current_chapter else None,
                    formatted_content=current_chapter,
                    is_chapter=True,
                    chapter_number=chapter_count
                )
                self._save_section_content(section)
                sections.append(section)
                progress.processed_sections += 1
            
            # Second pass: Process numbered sections
            if first_section_page is not None:
                current_section_texts = []
                current_section_num = None
                
                for page_num in range(first_section_page, len(doc)):
                    page = doc[page_num]
                    text_page = page.get_textpage()
                    text = text_page.extractText()
                    
                    # Look for section numbers
                    number_matches = list(re.finditer(r'^\s*(\d+)\s*$', text, re.MULTILINE))
                    
                    for match in number_matches:
                        section_num = int(match.group(1))
                        
                        # Save previous section if exists
                        if current_section_texts and current_section_num is not None:
                            file_path = os.path.join(sections_dir, f"{current_section_num}.md")
                            formatted_texts = []
                            for text_block in current_section_texts:
                                format_type = self._detect_formatting(text_block)
                                formatted_texts.append(FormattedText(
                                    text=text_block,
                                    format_type=format_type
                                ))
                            
                            section = Section(
                                number=len(sections),
                                content="\n".join(current_section_texts),
                                page_number=page_num + 1,
                                file_path=file_path,
                                pdf_name=pdf_folder_name,
                                formatted_content=formatted_texts,
                                is_chapter=True,
                                chapter_number=current_section_num
                            )
                            self._save_section_content(section)
                            sections.append(section)
                            progress.processed_sections += 1
                            current_section_texts = []
                        
                        current_section_num = section_num
                        start_pos = match.end()
                        # Get text until next section number or end of page
                        next_match = next((m for m in number_matches if m.start() > start_pos), None)
                        end_pos = next_match.start() if next_match else len(text)
                        section_text = text[start_pos:end_pos].strip()
                        if section_text:
                            current_section_texts.append(section_text)
                    
                    # If we're in a section but didn't find a new number, add all text
                    if not number_matches and current_section_num is not None:
                        current_section_texts.append(text.strip())
                
                # Save the last section if we have one
                if current_section_texts and current_section_num is not None:
                    file_path = os.path.join(sections_dir, f"{current_section_num}.md")
                    formatted_texts = []
                    for text_block in current_section_texts:
                        format_type = self._detect_formatting(text_block)
                        formatted_texts.append(FormattedText(
                            text=text_block,
                            format_type=format_type
                        ))
                    
                    section = Section(
                        number=len(sections),
                        content="\n".join(current_section_texts),
                        page_number=len(doc),
                        file_path=file_path,
                        pdf_name=pdf_folder_name,
                        formatted_content=formatted_texts,
                        is_chapter=True,
                        chapter_number=current_section_num
                    )
                    self._save_section_content(section)
                    sections.append(section)
                    progress.processed_sections += 1
            
            # Save metadata
            book_metadata = {
                "title": pdf_folder_name,
                "total_sections": len(sections),
                "total_images": 0,
                "sections": [{
                    "number": section.number,
                    "page_number": section.page_number,
                    "file_path": section.file_path,
                    "title": section.title,
                    "is_chapter": section.is_chapter,
                    "chapter_number": section.chapter_number
                } for section in sections],
                "base_path": base_output_dir
            }
            
            with open(os.path.join(metadata_dir, "book.json"), 'w', encoding='utf-8') as f:
                json.dump(book_metadata, f, indent=2, ensure_ascii=False)
            
            doc.close()
            progress.status = ProcessingStatus.COMPLETED
            
            return ProcessedPDF(
                sections=sections,
                images=[],  # Images will be handled separately
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )
            
        except Exception as e:
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            raise

    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections", sections: Optional[List[Section]] = None) -> List[PDFImage]:
        """Extract images with enhanced section mapping"""
        pdf_folder_name = os.path.splitext(os.path.basename(pdf_path))[0]
        book_dir = os.path.join(base_output_dir, pdf_folder_name)
        images_dir = os.path.join(book_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        images: List[PDFImage] = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                # Find corresponding section
                section_number = None
                if sections:
                    for section in sections:
                        if section.page_number <= page_num + 1:
                            section_number = section.chapter_number
                
                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_img = doc.extract_image(xref)
                        image_bytes = base_img["image"]
                        
                        image = Image.open(io.BytesIO(image_bytes))
                        width, height = image.size
                        
                        image_filename = f"page_{page_num + 1}_img_{img_idx + 1}.png"
                        image_path = os.path.join(images_dir, image_filename)
                        
                        # Save image
                        image.save(image_path)
                        
                        image_data = PDFImage(
                            page_number=page_num + 1,
                            image_path=image_path,
                            pdf_name=pdf_folder_name,
                            width=width,
                            height=height,
                            section_number=section_number
                        )
                        images.append(image_data)
                        
                    except Exception as e:
                        print(f"Error extracting image {img_idx} from page {page_num + 1}: {e}")
                        continue
            
            doc.close()
            return images
            
        except Exception as e:
            print(f"Error processing PDF for images: {e}")
            return []
