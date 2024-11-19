import os
import fitz  # PyMuPDF
import re
from typing import List, Optional, Dict, Tuple
from PIL import Image
import io
from PyPDF2 import PdfReader
from ..domain.ports import PDFProcessor
from ..domain.entities import (Section, PDFImage, ProcessedPDF,
                             ProcessingStatus, ProcessingProgress)
from .logging_config import StructuredLogger
from .analyzers.section_analyzer import MuPDFSectionAnalyzer
from .analyzers.pre_section_analyzer import MuPDFPreSectionAnalyzer
from .analyzers.metadata_analyzer import FileSystemMetadataAnalyzer

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.section_analyzer = MuPDFSectionAnalyzer()
        self.pre_section_analyzer = MuPDFPreSectionAnalyzer()
        self.metadata_analyzer = FileSystemMetadataAnalyzer()
        self.logger = StructuredLogger("PDFProcessor")

    def _get_pdf_folder_name(self, pdf_path: str) -> str:
        base_name = os.path.basename(pdf_path)
        folder_name = os.path.splitext(base_name)[0]
        folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
        return folder_name

    def _create_book_structure(self, base_output_dir: str,
                             pdf_folder_name: str) -> Dict[str, str]:
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

    async def extract_sections(self, pdf_path: str,
                             base_output_dir: str = "sections") -> ProcessedPDF:
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        sections = []
        progress = ProcessingProgress(status=ProcessingStatus.INITIALIZING)

        try:
            reader = PdfReader(pdf_path)
            progress.total_pages = len(reader.pages)
            progress.status = ProcessingStatus.EXTRACTING_SECTIONS

            # First pass: collect and analyze pre-section content
            pre_section_content = []
            first_section_page = None

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text:
                    continue

                # Check if this is still pre-section content
                if await self.pre_section_analyzer.is_pre_section_content(text):
                    pre_section_content.append(text)
                else:
                    first_section_page = page_num
                    break

            # Process pre-section content if any
            if pre_section_content:
                pre_sections = await self.pre_section_analyzer.analyze_pre_sections(
                    "\n".join(pre_section_content)
                )
                
                # Set file paths for pre-sections
                for section in pre_sections:
                    section.pdf_name = pdf_folder_name
                    section.file_path = os.path.join(
                        paths["histoire_dir"],
                        f"{section.chapter_number}.md"
                    )
                sections.extend(pre_sections)

            # Process numbered sections
            current_page = first_section_page or 0
            for page_num in range(current_page, len(reader.pages)):
                progress.current_page = page_num + 1
                try:
                    text = reader.pages[page_num].extract_text()
                    if not text:
                        continue

                    page_sections = await self.section_analyzer.analyze_sections(text, page_num + 1)
                    
                    # Set file paths and PDF name for sections
                    for section in page_sections:
                        section.pdf_name = pdf_folder_name
                        section.file_path = os.path.join(
                            paths["sections_dir"],
                            f"{section.chapter_number}.md"
                        )
                        sections.append(section)
                        progress.processed_sections += 1

                except Exception as e:
                    self.logger.error(f"Error processing page {page_num + 1}", e)
                    continue

            # Extract images
            progress.status = ProcessingStatus.EXTRACTING_IMAGES
            images = await self.extract_images(pdf_path, base_output_dir, sections)
            progress.processed_images = len(images)

            # Create ProcessedPDF object
            processed_pdf = ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_folder_name,
                base_path=base_output_dir,
                progress=progress
            )

            # Extract and save metadata
            metadata = await self.metadata_analyzer.extract_metadata(processed_pdf)
            metadata_path = os.path.join(paths["metadata_dir"], "book.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            progress.status = ProcessingStatus.COMPLETED
            return processed_pdf

        except Exception as e:
            progress.status = ProcessingStatus.FAILED
            progress.error_message = str(e)
            raise

    async def extract_images(self, pdf_path: str,
                           base_output_dir: str = "sections",
                           sections: Optional[List[Section]] = None) -> List[PDFImage]:
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        paths = self._create_book_structure(base_output_dir, pdf_folder_name)
        images = []

        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()

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
                        image_path = os.path.join(paths["images_dir"], image_filename)
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
                        self.logger.error(f"Error extracting image {img_idx} from page {page_num + 1}", e)
                        continue

            doc.close()

        except Exception as e:
            self.logger.error("Error processing PDF for images", e)

        return images