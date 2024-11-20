import json
import re
import base64
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

    def _encode_image(self, image_path: str) -> Optional[str]:
        """Convert image to base64 string with error handling"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return None

    async def analyze_page_with_chapters(
        self,
        page_text: str,
        page_num: int,
        images: Optional[List[PDFImage]] = None,
        current_chapter: Optional[Dict] = None
    ) -> Tuple[List[FormattedText], Optional[Dict], bool]:
        """Multimodal analysis using gpt-4o-mini for combined chapter detection and content analysis"""
        try:
            logger.info(f"Starting multimodal analysis for page {page_num}")
            
            system_prompt = """Analyze the provided document content to:
1. Identify natural chapter boundaries and transitions
2. Understand page layout and content organization
3. Process visual elements and their context
4. Determine content hierarchy and relationships

Provide structured output as:
CHAPTER_STATUS: [NEW/CONTINUE/END]
CHAPTER_TITLE: [if new chapter detected]
LAYOUT_INFO: [structural description]
CONTENT:
[processed content with preserved formatting]"""

            messages = [{"role": "system", "content": system_prompt}]

            # Add context from current chapter if exists
            if current_chapter:
                logger.debug(f"Adding context from chapter: {current_chapter.get('title')}")
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Current chapter context:\nTitle: {current_chapter['title']}\nStarting from page: {current_chapter['start_page']}"
                        }
                    ]
                })

            # Process images with error handling
            if images:
                page_images = [img for img in images if img.page_number == page_num]
                logger.info(f"Processing {len(page_images)} images for page {page_num}")
                
                for img in page_images:
                    try:
                        image_data = self._encode_image(img.image_path)
                        if image_data:
                            messages.append({
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Visual content from page {page_num}:"
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{image_data}",
                                            "detail": "auto"
                                        }
                                    }
                                ]
                            })
                            logger.debug(f"Successfully added image from page {page_num}")
                    except Exception as img_error:
                        logger.error(f"Error processing image on page {page_num}: {img_error}")
                        continue

            # Add text content
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Analyze page {page_num} content:\n\n{page_text}"
                    }
                ]
            })

            # Get AI analysis
            logger.info(f"Sending request to GPT-4o-mini for page {page_num}")
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from AI model")

            # Parse the response
            lines = content.split('\n')
            chapter_status = None
            chapter_title = None
            layout_info = None
            formatted_blocks = []
            content_lines = []

            # Extract metadata and content
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.upper().startswith("CHAPTER_STATUS:"):
                    chapter_status = line.split(":", 1)[1].strip().upper()
                    logger.debug(f"Detected chapter status: {chapter_status}")
                elif line.upper().startswith("CHAPTER_TITLE:"):
                    chapter_title = line.split(":", 1)[1].strip()
                    logger.debug(f"Detected chapter title: {chapter_title}")
                elif line.upper().startswith("LAYOUT_INFO:"):
                    layout_info = line.split(":", 1)[1].strip()
                    logger.debug(f"Detected layout info: {layout_info}")
                elif line.upper().startswith("CONTENT:"):
                    continue
                else:
                    content_lines.append(line)

            # Process content preserving AI's formatting
            current_format = TextFormatting.PARAGRAPH
            metadata = {
                "layout_info": layout_info,
                "context": "body"
            }

            for line in content_lines:
                if line.startswith('#'):
                    level = len(re.match(r'^#+', line).group())
                    current_format = TextFormatting.HEADER if level == 1 else TextFormatting.SUBHEADER
                    line = line.lstrip('#').strip()
                    metadata = {"context": "title", "layout_info": layout_info}
                elif line.startswith(('- ', '* ')):
                    current_format = TextFormatting.LIST_ITEM
                    line = line[2:].strip()
                    metadata = {"context": "list", "layout_info": layout_info}
                elif line.startswith('> '):
                    current_format = TextFormatting.QUOTE
                    line = line[2:].strip()
                    metadata = {"context": "quote", "layout_info": layout_info}
                elif re.match(r'^\d+[.)] ', line):
                    current_format = TextFormatting.LIST_ITEM
                    line = re.sub(r'^\d+[.)] ', '', line).strip()
                    metadata = {"context": "numbered_list", "layout_info": layout_info}
                else:
                    current_format = TextFormatting.PARAGRAPH
                    metadata = {"context": "body", "layout_info": layout_info}

                formatted_blocks.append(
                    FormattedText(
                        text=line,
                        format_type=current_format,
                        metadata=metadata.copy()
                    )
                )

            # Determine chapter status
            is_chapter_complete = chapter_status == "END"
            new_chapter_info = None

            if chapter_status == "NEW":
                new_chapter_info = {
                    "title": chapter_title,
                    "start_page": page_num,
                    "layout_info": layout_info
                }
                logger.info(f"New chapter detected: {chapter_title}")
            elif chapter_status == "CONTINUE" and current_chapter:
                new_chapter_info = current_chapter
                logger.debug(f"Continuing chapter: {current_chapter.get('title')}")

            return formatted_blocks, new_chapter_info, is_chapter_complete

        except Exception as e:
            logger.error(f"Error in gpt-4o-mini analysis for page {page_num}: {e}")
            # Fallback to text-only analysis
            logger.info(f"Falling back to text-only analysis for page {page_num}")
            return [
                FormattedText(
                    text=page_text,
                    format_type=TextFormatting.PARAGRAPH,
                    metadata={"context": "error_fallback", "error": str(e)}
                )
            ], current_chapter, False