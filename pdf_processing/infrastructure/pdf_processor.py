import os
import fitz  # PyMuPDF
import re
from typing import List, Optional
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfReader
from ..domain.ports import PDFProcessor
from ..domain.entities import Section, PDFImage, ProcessedPDF
from openai import OpenAI

class MuPDFProcessor(PDFProcessor):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_pdf_folder_name(self, pdf_path: str) -> str:
        base_name = os.path.basename(pdf_path)
        folder_name = os.path.splitext(base_name)[0]
        folder_name = re.sub(r'[^\w\s-]', '_', folder_name)
        return folder_name

    async def extract_images(self, pdf_path: str, base_output_dir: str = "sections") -> List[PDFImage]:
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        images_dir = os.path.join(base_output_dir, pdf_folder_name, "images")
        os.makedirs(images_dir, exist_ok=True)

        images = []
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
                        
                        # Save image using PIL
                        image = Image.open(io.BytesIO(image_bytes))
                        image_filename = f"page_{page_num + 1}_img_{img_idx + 1}.png"
                        image_path = os.path.join(images_dir, image_filename)
                        image.save(image_path)

                        images.append(PDFImage(
                            page_number=page_num + 1,
                            image_path=image_path,
                            pdf_name=pdf_folder_name
                        ))
                    except Exception as e:
                        print(f"Error extracting image {img_idx} from page {page_num + 1}: {e}")
                        continue
            
            doc.close()
        except Exception as e:
            print(f"Error processing PDF for images: {e}")

        return images

    async def extract_sections(self, pdf_path: str, base_output_dir: str = "sections") -> ProcessedPDF:
        pdf_folder_name = self._get_pdf_folder_name(pdf_path)
        output_dir = os.path.join(base_output_dir, pdf_folder_name)
        os.makedirs(output_dir, exist_ok=True)

        reader = PdfReader(pdf_path)
        sections = []
        current_section = None
        current_text = ""

        def process_section_text(text: str) -> str:
            try:
                completion = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that formats text for gamebooks."},
                        {"role": "user", "content": f"Here is a text extracted from a gamebook:\n\n{text}\n\nIdentify numbers representing chapters that the reader should go to and surround them with [[ ]]. Leave other numbers as they are. Don't Say : Certainly! Here's the formatted text: Or Something else than the text"}
                    ]
                )
                return completion.choices[0].message.content
            except Exception as e:
                print(f"Error processing text with AI: {e}")
                return text

        with ThreadPoolExecutor() as executor:
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        lines = text.splitlines()
                        for line in lines:
                            line = line.strip()
                            if line.isdigit():
                                if current_section is not None:
                                    # Process and save current section
                                    processed_text = process_section_text(current_text)
                                    file_path = os.path.join(output_dir, f"{current_section}.md")
                                    sections.append(Section(
                                        number=current_section,
                                        content=processed_text,
                                        page_number=page_num + 1,
                                        file_path=file_path,
                                        pdf_name=pdf_folder_name
                                    ))
                                
                                current_section = int(line)
                                current_text = ""
                            else:
                                if current_section is not None:
                                    current_text += line + "\n"

                except Exception as e:
                    print(f"Error processing page {page_num + 1}: {e}")

            # Save last section
            if current_section is not None:
                processed_text = process_section_text(current_text)
                file_path = os.path.join(output_dir, f"{current_section}.md")
                sections.append(Section(
                    number=current_section,
                    content=processed_text,
                    page_number=len(reader.pages),
                    file_path=file_path,
                    pdf_name=pdf_folder_name
                ))

        # Extract images
        images = await self.extract_images(pdf_path, base_output_dir)
        
        return ProcessedPDF(
            sections=sections,
            images=images,
            pdf_name=pdf_folder_name,
            base_path=base_output_dir
        )
