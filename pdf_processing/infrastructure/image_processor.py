import os
import fitz  # PyMuPDF
import io
from typing import List, Optional
from ..domain.entities import Section, PDFImage
from PIL import Image
import json
from typing import List, Optional, Dict
from ..domain.entities import Section, PDFImage

class ImageProcessor:
    def extract_images(
            self,
            doc_path: str,
            images_dir: str,
            metadata_dir: str,
            pdf_name: str,
            sections: Optional[List[Section]] = None) -> List[PDFImage]:
        """Extract images from the PDF with section information"""
        images = []
        images_metadata = []

        try:
            doc = fitz.Document(doc_path)  # Open PDF document using PyMuPDF

            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()

                # Find corresponding section for this page
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
                        image.save(image_path)

                        image_data = PDFImage(
                            page_number=page_num + 1,
                            image_path=image_path,
                            pdf_name=pdf_name,
                            width=width,
                            height=height,
                            section_number=section_number
                        )
                        images.append(image_data)

                        images_metadata.append({
                            "page_number": page_num + 1,
                            "image_path": image_path,
                            "width": width,
                            "height": height,
                            "filename": image_filename,
                            "section_number": section_number
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
