import json
import re
import base64
import os
from typing import Tuple, Optional, List, Dict
import openai
import logging
from ..domain.entities import FormattedText, TextFormatting, PDFImage

logger = logging.getLogger(__name__)


class AIProcessor:

    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.model_name = "gpt-4o-mini"
        self.max_tokens = 1500
        self.temperature = 0.3

    def _encode_image(self, image_path: str) -> str:
        """Convert image to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return None

    async def detect_chapter_boundaries(self,
                                        page_texts: List[str]) -> List[Dict]:
        """
        First pass to detect chapter boundaries in the document.
        """
        chapters = []
        current_chapter = None

        logger.info("Starting chapter boundary detection")

        for page_num, text in enumerate(page_texts):
            logger.debug(
                f"Analyzing page {page_num + 1} for chapter boundaries")

            messages = [{
                "role":
                "system",
                "content":
                """You are a book content analyzer specialized in identifying chapter boundaries. Determine if the given page content starts a new chapter, continues an existing chapter, or ends a chapter. Provide the output as:
                    CHAPTER_STATUS: [NEW/CONTINUE/END]
                    CHAPTER_TITLE: [title if new chapter]"""
            }, {
                "role": "user",
                "content": f"Page {page_num + 1} content:\n{text}"
            }]

            try:
                response = await self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens)

                content = response.choices[0].message.content
                if not content:
                    logger.warning(
                        f"Empty response for chapter detection on page {page_num + 1}"
                    )
                    continue

                lines = content.split('\n')
                chapter_status = None
                chapter_title = None

                for line in lines:
                    if line.upper().startswith("CHAPTER_STATUS:"):
                        chapter_status = line.split(":", 1)[1].strip().upper()
                    elif line.upper().startswith("CHAPTER_TITLE:"):
                        chapter_title = line.split(":", 1)[1].strip()

                if chapter_status == "NEW":
                    if current_chapter:
                        # End previous chapter
                        chapters.append(current_chapter)
                        logger.info(
                            f"Ended chapter: {current_chapter['title']} at page {page_num}"
                        )
                    # Start new chapter
                    current_chapter = {
                        "title": chapter_title
                        or f"Chapter starting at page {page_num + 1}",
                        "start_page": page_num + 1,
                        "end_page": None
                    }
                    logger.info(
                        f"Detected new chapter: {current_chapter['title']}")
                elif chapter_status == "END" and current_chapter:
                    current_chapter["end_page"] = page_num + 1
                    chapters.append(current_chapter)
                    logger.info(
                        f"Completed chapter: {current_chapter['title']}")
                    current_chapter = None

            except Exception as e:
                logger.error(
                    f"Error detecting chapter boundaries on page {page_num + 1}: {e}"
                )

        # Handle any open chapter
        if current_chapter:
            current_chapter["end_page"] = len(page_texts)
            chapters.append(current_chapter)
            logger.info(f"Finalized last chapter: {current_chapter['title']}")

        # Write temporary output for chapter boundaries
        temp_output_path = "chapter_boundaries.json"
        with open(temp_output_path, "w") as f:
            json.dump(chapters, f, indent=2)
        logger.info(f"Chapter boundaries written to {temp_output_path}")

        return chapters

    async def analyze_chapter(
            self,
            chapter: Dict,
            page_texts: List[str],
            images: Optional[List[PDFImage]] = None) -> List[FormattedText]:
        """
        Second pass: Analyze a given chapter using multimodal processing.
        """
        logger.info(
            f"Starting multimodal analysis for chapter: {chapter['title']}")
        formatted_blocks = []
        current_chapter = chapter

        for page_num in range(chapter["start_page"] - 1, chapter["end_page"]):
            logger.debug(
                f"Analyzing page {page_num + 1} in chapter: {chapter['title']}"
            )
            text = page_texts[page_num]

            messages = [{
                "role":
                "system",
                "content":
                """You are a book content analyzer specialized in understanding document structure and narrative flow. Analyze the provided content and identify text blocks with formatting attributes."""
            }, {
                "role": "user",
                "content": f"Page {page_num + 1} content:\n\n{text}"
            }]

            # Process a limited number of images for the page
            if images:
                for img in images:
                    if img.page_number == page_num + 1:
                        image_data = self._encode_image(img.image_path)
                        if image_data:
                            messages.append({
                                "role":
                                "user",
                                "content":
                                f"Image data (base64) for page {page_num + 1}: {image_data}"
                            })

            try:
                response = await self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens)

                content = response.choices[0].message.content
                if not content:
                    logger.warning(
                        f"Empty response for multimodal analysis on page {page_num + 1}"
                    )
                    continue

                # Parse and format the response content
                lines = content.split('\n')
                current_format = TextFormatting.PARAGRAPH
                metadata = {"indentation_level": 0, "formatting": []}

                for line in lines:
                    if line.startswith('#'):
                        level = len(re.match(r'^#+', line).group())
                        current_format = TextFormatting.HEADER if level == 1 else TextFormatting.SUBHEADER
                        line = line.lstrip('#').strip()
                    elif line.startswith(('- ', '* ')):
                        current_format = TextFormatting.LIST_ITEM
                        line = line[2:].strip()
                    elif line.startswith('> '):
                        current_format = TextFormatting.QUOTE
                        line = line[2:].strip()
                    elif re.match(r'^\d+[.)] ', line):
                        current_format = TextFormatting.LIST_ITEM
                        line = re.sub(r'^\d+[.)] ', '', line).strip()
                    else:
                        current_format = TextFormatting.PARAGRAPH

                    formatted_blocks.append(
                        FormattedText(text=line,
                                      format_type=current_format,
                                      metadata=metadata.copy()))

            except Exception as e:
                logger.error(
                    f"Error in multimodal analysis for page {page_num + 1}: {e}"
                )

        return formatted_blocks
