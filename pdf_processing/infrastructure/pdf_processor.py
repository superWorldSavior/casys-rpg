import os
import fitz  # PyMuPDF
import re
import json
from typing import List, Optional, Dict
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfReader
from ..domain.ports import PDFProcessor
from ..domain.entities import Section, PDFImage, ProcessedPDF

class MuPDFProcessor(PDFProcessor):
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

        # Create all directories
        for directory in [book_dir, sections_dir, images_dir, metadata_dir]:
            os.makedirs(directory, exist_ok=True)

        return {
            "book_dir": book_dir,
            "sections_dir": sections_dir,
            "images_dir": images_dir,
            "metadata_dir": metadata_dir
        }

    def _find_section_for_page(self, page_num: int, sections: List[Section]) -> Optional[int]:
        """Find which section a page belongs to"""
        for section in sections:
            if section.page_number == page_num:
                return section.number
        return None

    async def extract_images(self, pdf_path: str, base_output_dir: str, sections: List[Section]) -> List[PDFImage]:
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
                
                section_number = self._find_section_for_page(page_num + 1, sections)
                
                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_img = doc.extract_image(xref)
                        image_bytes = base_img["image"]
                        
                        # Get image dimensions using PIL
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
                            height=height,
                            section_number=section_number
                        )
                        images.append(image_data)
                        
                        # Add to metadata
                        images_metadata.append({
                            "page_number": page_num + 1,
                            "image_path": image_path,
                            "width": width,
                            "height": height,
                            "section_number": section_number,
                            "filename": image_filename
                        })
                    except Exception as e:
                        print(f"Error extracting image {img_idx} from page {page_num + 1}: {e}")
                        continue
            
            doc.close()

            # Save images metadata
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

        reader = PdfReader(pdf_path)
        sections = []
        current_section: Optional[int] = None
        current_text: str = ""
        current_page: int = 0

        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    lines = text.splitlines()
                    for line in lines:
                        line = line.strip()
                        if line.isdigit():
                            if current_section is not None:
                                # Save current section
                                file_path = os.path.join(sections_dir, f"{current_section}.md")
                                sections.append(Section(
                                    number=current_section,
                                    content=current_text,
                                    page_number=current_page + 1,
                                    file_path=file_path,
                                    pdf_name=pdf_folder_name
                                ))
                            
                            current_section = int(line)
                            current_text = ""
                            current_page = page_num
                        else:
                            if current_section is not None:
                                current_text += line + "\n"

            except Exception as e:
                print(f"Error processing page {page_num + 1}: {e}")

        # Save last section
        if current_section is not None:
            file_path = os.path.join(sections_dir, f"{current_section}.md")
            sections.append(Section(
                number=current_section,
                content=current_text,
                page_number=current_page + 1,
                file_path=file_path,
                pdf_name=pdf_folder_name
            ))

        # Extract images after sections to properly associate them
        images = await self.extract_images(pdf_path, base_output_dir, sections)
        
        # Save sections content
        for section in sections:
            os.makedirs(os.path.dirname(section.file_path), exist_ok=True)
            with open(section.file_path, 'w', encoding='utf-8') as f:
                f.write(section.content)

        return ProcessedPDF(
            sections=sections,
            images=images,
            pdf_name=pdf_folder_name,
            base_path=base_output_dir
        )
