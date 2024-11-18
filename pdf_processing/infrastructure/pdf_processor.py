import os
import fitz  # PyMuPDF
import re
import json
from typing import List, Optional, Dict, Any, Tuple
from PIL import Image
import io
from ..domain.ports import PDFProcessor
from ..domain.entities import (
    Section, PDFImage, ProcessedPDF, ProcessingStatus, 
    ProcessingProgress, TextFormatting, FormattedText
)

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.chapter_pattern = r'^\s*(\d+)\s*$'
        self.pre_section_titles = ['Introduction', 'Preface', 'Game Rules']
        self.list_pattern = r'^(?:•|\d+\.)\s+'

    def _get_text_properties(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text properties including font and positioning"""
        properties = {
            'font_size': 0,
            'font_name': '',
            'is_bold': False,
            'is_italic': False,
            'is_centered': False,
            'top_margin': 0,
            'bottom_margin': 0,
            'alignment': 'left'
        }
        
        try:
            # Process spans for font information
            spans = block.get('spans', [])
            if spans:
                for span in spans:
                    size = span.get('size', 0)
                    if size > properties['font_size']:
                        properties['font_size'] = size
                    
                    font = span.get('font', '').lower()
                    properties['is_bold'] = properties['is_bold'] or 'bold' in font
                    properties['is_italic'] = properties['is_italic'] or 'italic' in font
            
            # Process block position
            bbox = block.get('bbox', (0, 0, 0, 0))
            if len(bbox) == 4:
                page_width = 612  # Standard letter width in points
                text_width = bbox[2] - bbox[0]
                left_margin = bbox[0]
                right_margin = page_width - bbox[2]
                
                # Enhanced center detection with dynamic threshold
                margin_threshold = min(30, page_width * 0.05)  # Points or 5% of page width
                if abs(left_margin - right_margin) < margin_threshold:
                    properties['alignment'] = 'center'
                    properties['is_centered'] = True
            
            properties['top_margin'] = bbox[1]
            properties['bottom_margin'] = bbox[3]
            
        except Exception as e:
            print(f"Error extracting text properties: {e}")
        
        return properties

    def _detect_formatting(self, text: str, properties: Dict[str, Any]) -> TextFormatting:
        """Enhanced formatting detection with improved rules"""
        text = text.strip()
        if not text:
            return TextFormatting.PARAGRAPH

        # Pre-section titles detection
        if text in self.pre_section_titles and properties['font_size'] >= 14:
            return TextFormatting.HEADER

        # Headers detection based on font size and style
        if properties['font_size'] >= 18 or (properties['is_bold'] and len(text.split()) <= 5):
            return TextFormatting.HEADER
        elif properties['font_size'] >= 14 and (properties['is_bold'] or properties.get('is_centered')):
            return TextFormatting.SUBHEADER

        # List items detection
        if re.match(self.list_pattern, text):
            return TextFormatting.LIST_ITEM

        # Quotes detection
        if (text.startswith('>') or (text.startswith('"') and text.endswith('"'))) and len(text.split()) > 1:
            return TextFormatting.QUOTE

        return TextFormatting.PARAGRAPH

    def _process_text_block(self, block: Dict[str, Any]) -> Optional[FormattedText]:
        """Process a text block with enhanced formatting"""
        text = block.get('text', '').strip()
        if not text:
            return None
            
        properties = self._get_text_properties(block)
        format_type = self._detect_formatting(text, properties)
        
        # Clean up text content
        text = re.sub(r'\s+', ' ', text).strip()
        
        return FormattedText(
            text=text,
            format_type=format_type,
            metadata=properties
        )

    def _extract_blocks_from_page(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extract and sort text blocks"""
        try:
            text_page = page.get_textpage()
            dict_data = text_page.extractDICT()
            
            blocks = [
                block for block in dict_data.get("blocks", [])
                if block.get("type") == 0 and block.get("bbox")
            ]
            
            # Sort blocks by vertical position first, then horizontal
            blocks.sort(key=lambda b: (round(b["bbox"][1]), b["bbox"][0]))
            
            return blocks
            
        except Exception as e:
            print(f"Error extracting blocks from page: {e}")
            return []

    def _format_text(self, fmt_text: FormattedText, skip_header: bool = False) -> str:
        """Format text content with improved markdown syntax"""
        text = fmt_text.text.strip()
        
        if fmt_text.format_type == TextFormatting.HEADER and not skip_header:
            return f"# {text}\n\n"
        elif fmt_text.format_type == TextFormatting.SUBHEADER:
            return f"### {text}\n\n"
        elif fmt_text.format_type == TextFormatting.LIST_ITEM:
            match = re.match(self.list_pattern, text)
            if match:
                list_content = text[match.end():].strip()
                if text.startswith('•'):
                    return f"- {list_content}\n"
                elif re.match(r'^\d+\.', text):
                    return f"{text}\n"
            return f"- {text}\n"
        elif fmt_text.format_type == TextFormatting.QUOTE:
            return f"> {text}\n\n"
        else:  # Paragraph
            if fmt_text.metadata.get('is_centered'):
                return f"<div align='center'>{text}</div>\n\n"
            return f"{text}\n\n"

    def _process_section_content(self, content: List[FormattedText]) -> List[FormattedText]:
        """Process and clean section content"""
        if not content:
            return []
        
        # Remove duplicate content
        seen = set()
        unique_content = []
        for fmt_text in content:
            text_hash = hash(fmt_text.text.strip())
            if text_hash not in seen:
                seen.add(text_hash)
                unique_content.append(fmt_text)
        return unique_content

    def _save_section_content(self, section: Section) -> None:
        """Save formatted section content"""
        os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
        
        # Process and format content
        content = self._process_section_content(section.formatted_content)
        formatted_lines = []
        
        # Add section title
        if section.title:
            formatted_lines.append(f"# {section.title}\n\n")
        
        # Format remaining content
        for fmt_text in content:
            # Skip chapter numbers in numbered sections
            if section.is_chapter and re.match(self.chapter_pattern, fmt_text.text.strip()):
                continue
            formatted_lines.append(self._format_text(fmt_text))
        
        # Write content to file
        with open(section.file_path, 'w', encoding='utf-8') as f:
            f.write("".join(formatted_lines).strip() + "\n")

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections with enhanced pre-section and chapter handling"""
        pdf_folder_name = os.path.splitext(os.path.basename(pdf_path))[0]
        pdf_folder_name = re.sub(r'[^\w\s-]', '_', pdf_folder_name)
        
        paths = {
            "sections_dir": os.path.join(base_output_dir, pdf_folder_name, "sections"),
            "histoire_dir": os.path.join(base_output_dir, pdf_folder_name, "histoire"),
            "images_dir": os.path.join(base_output_dir, pdf_folder_name, "images"),
            "metadata_dir": os.path.join(base_output_dir, pdf_folder_name, "metadata"),
        }
        
        for directory in paths.values():
            os.makedirs(directory, exist_ok=True)
        
        sections = []
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)
        doc = None
        
        try:
            doc = fitz.open(pdf_path)
            progress.total_pages = len(doc)
            progress.status = ProcessingStatus.EXTRACTING_SECTIONS
            
            # Process pre-sections first
            current_pre_section = None
            current_content = []
            pre_section_number = 0
            page_num = 0
            
            # Find and process pre-sections
            while page_num < len(doc):
                progress.current_page = page_num + 1
                page = doc[page_num]
                blocks = self._extract_blocks_from_page(page)
                
                for block in blocks:
                    fmt_text = self._process_text_block(block)
                    if not fmt_text:
                        continue
                    
                    # Check for numbered section start
                    if re.match(self.chapter_pattern, fmt_text.text.strip()):
                        # Save current pre-section if exists
                        if current_pre_section and current_content:
                            file_path = os.path.join(
                                paths["histoire_dir"],
                                f"{current_pre_section.lower().replace(' ', '_')}.md"
                            )
                            sections.append(Section(
                                number=pre_section_number,
                                content="\n".join(text.text for text in current_content),
                                page_number=page_num,
                                file_path=file_path,
                                pdf_name=pdf_folder_name,
                                title=current_pre_section,
                                formatted_content=current_content,
                                is_chapter=False
                            ))
                            self._save_section_content(sections[-1])
                            progress.processed_sections += 1
                        page_num -= 1  # Go back one page to process the chapter
                        break
                    
                    # Check for pre-section titles
                    if fmt_text.text in self.pre_section_titles:
                        if current_pre_section and current_content:
                            file_path = os.path.join(
                                paths["histoire_dir"],
                                f"{current_pre_section.lower().replace(' ', '_')}.md"
                            )
                            sections.append(Section(
                                number=pre_section_number,
                                content="\n".join(text.text for text in current_content),
                                page_number=page_num,
                                file_path=file_path,
                                pdf_name=pdf_folder_name,
                                title=current_pre_section,
                                formatted_content=current_content,
                                is_chapter=False
                            ))
                            self._save_section_content(sections[-1])
                            progress.processed_sections += 1
                            pre_section_number += 1
                        
                        current_pre_section = fmt_text.text
                        current_content = [fmt_text]
                    elif current_pre_section:
                        current_content.append(fmt_text)
                
                if not re.match(self.chapter_pattern, fmt_text.text.strip() if fmt_text else ""):
                    page_num += 1
                else:
                    break
            
            # Process numbered sections
            current_section = None
            current_content = []
            
            while page_num < len(doc):
                progress.current_page = page_num + 1
                page = doc[page_num]
                blocks = self._extract_blocks_from_page(page)
                
                for block in blocks:
                    fmt_text = self._process_text_block(block)
                    if not fmt_text:
                        continue
                    
                    # Check for new numbered section
                    match = re.match(self.chapter_pattern, fmt_text.text.strip())
                    if match:
                        if current_section and current_content:
                            file_path = os.path.join(
                                paths["sections_dir"],
                                f"{current_section['chapter']}.md"
                            )
                            sections.append(Section(
                                number=current_section['number'],
                                content="\n".join(text.text for text in current_content),
                                page_number=current_section['page'],
                                file_path=file_path,
                                pdf_name=pdf_folder_name,
                                title=f"Chapter {current_section['chapter']}",
                                formatted_content=current_content,
                                is_chapter=True,
                                chapter_number=current_section['chapter']
                            ))
                            self._save_section_content(sections[-1])
                            progress.processed_sections += 1
                        
                        # Start new section
                        chapter_num = int(match.group(1))
                        current_section = {
                            'number': len(sections),
                            'chapter': chapter_num,
                            'page': page_num + 1
                        }
                        current_content = []
                    
                    current_content.append(fmt_text)
                
                page_num += 1
            
            # Save last section if exists
            if current_section and current_content:
                file_path = os.path.join(
                    paths["sections_dir"],
                    f"{current_section['chapter']}.md"
                )
                sections.append(Section(
                    number=current_section['number'],
                    content="\n".join(text.text for text in current_content),
                    page_number=current_section['page'],
                    file_path=file_path,
                    pdf_name=pdf_folder_name,
                    title=f"Chapter {current_section['chapter']}",
                    formatted_content=current_content,
                    is_chapter=True,
                    chapter_number=current_section['chapter']
                ))
                self._save_section_content(sections[-1])
                progress.processed_sections += 1
            
            progress.status = ProcessingStatus.COMPLETED
            
            # Extract images
            images = await self.extract_images(pdf_path, base_output_dir)
            
            return ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            return ProcessedPDF(
                sections=[],
                images=[],
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )
        finally:
            if doc:
                doc.close()

    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        """Extract images from PDF with enhanced handling"""
        pdf_folder_name = os.path.splitext(os.path.basename(pdf_path))[0]
        pdf_folder_name = re.sub(r'[^\w\s-]', '_', pdf_folder_name)
        
        paths = {
            "images_dir": os.path.join(base_output_dir, pdf_folder_name, "images"),
            "metadata_dir": os.path.join(base_output_dir, pdf_folder_name, "metadata"),
        }
        
        for directory in paths.values():
            os.makedirs(directory, exist_ok=True)
        
        images = []
        images_metadata = []
        doc = None
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_idx, img_info in enumerate(image_list):
                    try:
                        xref = img_info[0]
                        base_image = doc.extract_image(xref)
                        
                        if not base_image:
                            continue
                        
                        image_bytes = base_image["image"]
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Save image with original format
                        image_filename = f"image_{page_num + 1}_{img_idx + 1}.{base_image['ext']}"
                        image_path = os.path.join(paths["images_dir"], image_filename)
                        
                        with open(image_path, 'wb') as img_file:
                            img_file.write(image_bytes)
                        
                        pdf_image = PDFImage(
                            page_number=page_num + 1,
                            image_path=image_path,
                            pdf_name=pdf_folder_name,
                            width=image.width,
                            height=image.height
                        )
                        
                        images.append(pdf_image)
                        images_metadata.append({
                            "page_number": page_num + 1,
                            "image_path": image_path,
                            "width": image.width,
                            "height": image.height
                        })
                        
                    except Exception as e:
                        print(f"Error processing image {img_idx} on page {page_num + 1}: {e}")
            
            # Save metadata
            metadata_path = os.path.join(paths["metadata_dir"], "images.json")
            with open(metadata_path, 'w') as f:
                json.dump(images_metadata, f, indent=2)
            
            return images
            
        except Exception as e:
            print(f"Error extracting images: {e}")
            raise
        
        finally:
            if doc:
                doc.close()
