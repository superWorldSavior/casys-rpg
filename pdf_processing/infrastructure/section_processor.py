import os
from typing import List, Dict, Optional
from PyPDF2 import PdfReader
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SectionProcessor:
    @staticmethod
    def find_section(pages: List[Dict[str, str]], section_number: int) -> Optional[int]:
        """
        Find the page where a section with the given number starts.

        Args:
            pages (List[Dict[str, str]]): List of pages with text and their page numbers.
            section_number (int): The section number to look for.

        Returns:
            Optional[int]: The page number where the section starts, or None if not found.
        """
        for page in pages:
            page_number = page["num"]
            page_text = page["text"]

            try:
                # Split text into lines
                lines = page_text.splitlines()
                for line in lines:
                    line = line.strip()
                    if line.isdigit() and int(line) == section_number:
                        logger.info(f"Section {section_number} detected on page {page_number}.")
                        return int(page_number)
            except Exception as e:
                logger.error(f"Error processing page {page_number}: {e}")

        logger.info(f"Section {section_number} not found in the document.")
        return None

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, str]]:
        """
        Extract text from a PDF and return a list of pages with their numbers and text.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            List[Dict[str, str]]: List of dictionaries containing page numbers and text.
        """
        pages = []
        try:
            reader = PdfReader(pdf_path)
            for i, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                pages.append({"num": i, "text": text.strip() if text else ""})
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")

        return pages
