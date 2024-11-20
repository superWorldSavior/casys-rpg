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
        self.max_tokens = 1000
        self.temperature = 0.3

    def _encode_image(self, image_path: str) -> str:
        """Convert image to base64 string"""
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
        """
        Multimodal analysis using gpt-4o-mini for combined chapter detection and content analysis
        Returns: (formatted_blocks, current_chapter_info, is_chapter_complete)
        """
        try:
            logger.info(f"Processing page {page_num} with gpt-4o-mini multimodal analysis")
            
            system_prompt = """You are a multimodal content analyzer specialized in book content analysis. 
            Analyze the provided content following these guidelines:

            1. Chapter Analysis:
               - Identify chapter boundaries and structure
               - Determine if this is the start, continuation, or end of a chapter
               - Extract chapter titles when present

            2. Content Processing:
               - Analyze both text and images together for complete context
               - Identify visual-textual relationships
               - Maintain natural content flow and hierarchy

            3. Use standard markdown formatting:
               - # for chapter titles
               - ## for section headers
               - Regular paragraphs with no special markup
               - Lists with - or 1. 
               - > for quotes or special text

            Respond with structured output:
            1. CHAPTER_STATUS: [NEW/CONTINUE/END]
            2. CHAPTER_TITLE: [title if new chapter]
            3. CONTENT: [formatted content in markdown]"""

            # Prepare multimodal content
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add context from current chapter if exists
            if current_chapter:
                messages.append({
                    "role": "user",
                    "content": f"Current chapter context: {current_chapter['title']}\nContinuing from previous page..."
                })

            # Process images if available
            if images:
                page_images = [img for img in images if img.page_number == page_num]
                for img in page_images:
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
                                    "type": "image",
                                    "image_url": f"data:image/png;base64,{image_data}"
                                }
                            ]
                        })

            # Add text content
            messages.append({
                "role": "user",
                "content": f"Page {page_num} content:\n\n{page_text}"
            })

            # Get AI analysis
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
            formatted_blocks = []
            content_lines = []

            # Extract chapter information and content
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.upper().startswith("CHAPTER_STATUS:"):
                    chapter_status = line.split(":", 1)[1].strip().upper()
                elif line.upper().startswith("CHAPTER_TITLE:"):
                    chapter_title = line.split(":", 1)[1].strip()
                elif line.upper().startswith("CONTENT:"):
                    continue  # Skip the content marker
                else:
                    content_lines.append(line)

            # Process content into formatted blocks
            current_format = TextFormatting.PARAGRAPH
            metadata = {"indentation_level": 0, "formatting": [], "context": ""}

            for line in content_lines:
                # Markdown parsing
                if line.startswith('# '):
                    current_format = TextFormatting.HEADER
                    line = line[2:].strip()
                    metadata = {"context": "chapter_title"}
                elif line.startswith('## '):
                    current_format = TextFormatting.SUBHEADER
                    line = line[3:].strip()
                    metadata = {"context": "section_title"}
                elif line.startswith(('- ', '* ')):
                    current_format = TextFormatting.LIST_ITEM
                    line = line[2:].strip()
                    metadata = {"context": "list", "indentation_level": 1}
                elif line.startswith('> '):
                    current_format = TextFormatting.QUOTE
                    line = line[2:].strip()
                    metadata = {"context": "quote"}
                elif re.match(r'^\d+\. ', line):
                    current_format = TextFormatting.LIST_ITEM
                    line = re.sub(r'^\d+\. ', '', line).strip()
                    metadata = {"context": "numbered_list", "indentation_level": 1}
                else:
                    current_format = TextFormatting.PARAGRAPH
                    metadata = {"context": "body", "indentation_level": 0}

                formatted_blocks.append(FormattedText(
                    text=line,
                    format_type=current_format,
                    metadata=metadata.copy()
                ))

            # Determine chapter status
            is_chapter_complete = chapter_status == "END"
            new_chapter_info = None

            if chapter_status == "NEW":
                new_chapter_info = {
                    "title": chapter_title,
                    "start_page": page_num
                }
            elif chapter_status == "CONTINUE" and current_chapter:
                new_chapter_info = current_chapter

            return formatted_blocks, new_chapter_info, is_chapter_complete

        except Exception as e:
            logger.error(f"Error in gpt-4o-mini analysis for page {page_num}: {e}")
            return [FormattedText(
                text=page_text,
                format_type=TextFormatting.PARAGRAPH,
                metadata={"context": "error_fallback"}
            )], current_chapter, False
