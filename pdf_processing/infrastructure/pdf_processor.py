import os
from typing import List, Optional, Tuple
import fitz  # PyMuPDF
import json
from datetime import datetime
from ..domain.ports import PDFProcessor
from ..domain.entities import Section, PDFImage, ProcessedPDF, PDFMetadata

class MuPDFProcessor(PDFProcessor):
    def _extract_metadata(self, pdf_path: str) -> PDFMetadata:
        """Extract metadata from PDF file."""
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata if doc else {}
            
            # Get page dimensions for all pages
            page_dimensions = [(page.rect.width, page.rect.height) for page in doc]

            def parse_pdf_date(date_str: Optional[str]) -> Optional[datetime]:
                """Parse PDF date string to datetime object."""
                if not date_str:
                    return None
                try:
                    # Handle different date formats
                    if isinstance(date_str, str):
                        # Remove timezone info and 'D:' prefix if present
                        date_str = date_str.replace('D:', '')[:14]
                        return datetime.strptime(date_str, '%Y%m%d%H%M%S')
                    return None
                except ValueError:
                    return None

            # Extract PDF version
            pdf_version = f"{doc.get_pdf_version():.1f}"

            pdf_metadata = PDFMetadata(
                title=metadata.get('title'),
                author=metadata.get('author'),
                subject=metadata.get('subject'),
                keywords=metadata.get('keywords'),
                creator=metadata.get('creator'),
                producer=metadata.get('producer'),
                creation_date=parse_pdf_date(metadata.get('creationDate')),
                modification_date=parse_pdf_date(metadata.get('modDate')),
                page_count=len(doc),
                file_size=os.path.getsize(pdf_path),
                pdf_version=pdf_version,
                is_encrypted=doc.is_encrypted,
                page_dimensions=page_dimensions
            )
            doc.close()
            return pdf_metadata
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            # Return minimal metadata in case of error
            return PDFMetadata(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                creator=None,
                producer=None,
                creation_date=None,
                modification_date=None,
                page_count=0,
                file_size=os.path.getsize(pdf_path),
                pdf_version="1.0",
                is_encrypted=False,
                page_dimensions=[]
            )

    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        """Extract images from PDF file."""
        images = []
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        image_dir = os.path.join(base_output_dir, pdf_name, "images")
        os.makedirs(image_dir, exist_ok=True)

        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc):
                img_list = page.get_images()
                for img_idx, img in enumerate(img_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Create image file name
                        image_path = os.path.join(image_dir, f"page_{page_num + 1}_img_{img_idx + 1}.png")
                        
                        # Save image
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        # Add to images list
                        images.append(PDFImage(
                            page_number=page_num + 1,
                            image_path=image_path,
                            pdf_name=pdf_name
                        ))
                    except Exception as e:
                        print(f"Error extracting image {img_idx} from page {page_num + 1}: {e}")
                        continue
            doc.close()
        except Exception as e:
            print(f"Error processing PDF images: {e}")
        
        return images

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        """Extract sections from PDF file."""
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = os.path.join(base_output_dir, pdf_name)
        os.makedirs(output_dir, exist_ok=True)

        sections = []
        current_section = []
        current_section_num = 1
        current_page_num = 1

        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    current_section.append(text)
                    
                    # Create a new section after collecting enough text or at the end
                    if len(''.join(current_section)) >= 1000 or page_num == len(doc) - 1:
                        section_path = os.path.join(output_dir, f"section_{current_section_num}.md")
                        sections.append(Section(
                            number=current_section_num,
                            content=''.join(current_section),
                            page_number=current_page_num,
                            file_path=section_path,
                            pdf_name=pdf_name
                        ))
                        current_section = []
                        current_section_num += 1
                        current_page_num = page_num + 2  # Next page number
            
            # Extract metadata and images
            metadata = self._extract_metadata(pdf_path)
            images = await self.extract_images(pdf_path, base_output_dir)
            
            doc.close()
            
            return ProcessedPDF(
                sections=sections,
                images=images,
                pdf_name=pdf_name,
                base_path=base_output_dir,
                metadata=metadata
            )
        except Exception as e:
            print(f"Error processing PDF: {e}")
            raise
