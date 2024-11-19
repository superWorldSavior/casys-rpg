"""Image analysis functionality."""
import os
from typing import List
from PIL import Image
import io
from ...domain.entities import PDFImage

class ImageAnalyzer:
    """Analyzes and processes images from PDFs."""
    
    def process_image(self, image_data: bytes, page_number: int, pdf_name: str, output_path: str) -> PDFImage:
        """Process PDF image data into PDFImage entity."""
        try:
            # Create image from bytes
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size

            # Save image
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(image_data)

            return PDFImage(
                page_number=page_number,
                image_path=output_path,
                pdf_name=pdf_name,
                width=width,
                height=height
            )
        except Exception as e:
            print(f"Error processing image: {e}")
            raise
