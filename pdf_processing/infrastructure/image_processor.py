import os
import fitz
import json
import logging
from typing import List, Optional
from ..domain.entities import Section, PDFImage

logger = logging.getLogger(__name__)

class ImageProcessor:
    def extract_images(
            self,
            doc_path: str,
            images_dir: str,
            metadata_dir: str,
            pdf_name: str,
            sections: Optional[List[Section]] = None) -> List[PDFImage]:
        """Extract images from the PDF with section information using PyMuPDF"""
        images = []
        images_metadata = []
        doc = None

        try:
            doc = fitz.open(doc_path)
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(metadata_dir, exist_ok=True)

            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)

                # Find corresponding section for this page
                section_number = None
                if sections:
                    for section in sections:
                        if section.page_number <= page_num + 1:
                            section_number = section.chapter_number

                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]

                        # Save as PNG
                        image_filename = f"page_{page_num + 1}_img_{img_idx + 1}.png"
                        image_path = os.path.join(images_dir, image_filename)

                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)

                        # Create PDFImage object
                        image_data = PDFImage(
                            page_number=page_num + 1,
                            image_path=image_path,
                            pdf_name=pdf_name,
                            width=img[2],
                            height=img[3],
                            section_number=section_number
                        )
                        images.append(image_data)

                        # Collect metadata
                        images_metadata.append({
                            "page_number": page_num + 1,
                            "image_path": image_path,
                            "width": img[2],
                            "height": img[3],
                            "filename": image_filename,
                            "section_number": section_number
                        })

                    except Exception as e:
                        logger.error(f"Error extracting image {img_idx} from page {page_num + 1}: {e}")
                        continue

            # Save all image metadata to a single file
            metadata_path = os.path.join(metadata_dir, "images.json")
            with open(metadata_path, 'w') as f:
                json.dump({
                    "pdf_name": pdf_name,
                    "total_images": len(images_metadata),
                    "images": images_metadata
                }, f, indent=2)

            logger.info(f"Successfully extracted {len(images)} images from PDF")
            return images

        except Exception as e:
            logger.error(f"Error processing PDF for images: {e}")
            return images
        finally:
            if doc:
                doc.close()
