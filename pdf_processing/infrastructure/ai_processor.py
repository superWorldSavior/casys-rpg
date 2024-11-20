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
            Analyze the provided content following these strict guidelines:

            1. Layout Analysis:
               - Identify page structure and content organization
               - Detect headers, subheaders, paragraphs, and lists
               - Analyze text alignment and indentation
               - Identify visual elements and their relationship to text
               - Preserve whitespace and formatting

            2. Chapter Analysis:
               - Identify clear chapter boundaries
               - Look for explicit chapter markers (numbers, titles)
               - Analyze content transitions and thematic shifts
               - Consider both textual and visual context for boundaries
               - Track narrative progression and topic changes

            3. Content Processing:
               - Maintain hierarchical structure
               - Preserve original formatting style
               - Keep paragraph breaks and indentation
               - Handle lists and enumerations properly
               - Respect content flow and organization

            4. Markdown Formatting Rules:
               - # Chapter Title (only for main chapter titles)
               - ## Section Headers (for major sections)
               - ### Subsection Headers (for minor sections)
               - Regular paragraphs with blank lines between
               - Lists with proper indentation:
                 - Unordered lists with -
                 - Ordered lists with numbers
               - > for quotes or special text
               - Preserve line breaks for readability

            Provide structured output in this exact format:
            CHAPTER_STATUS: [NEW/CONTINUE/END]
            CHAPTER_TITLE: [title if new chapter]
            LAYOUT_INFO: [description of page layout and structure]
            CONTENT:
            [formatted content in markdown]"""

            # Prepare multimodal content
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add context from current chapter if exists
            if current_chapter:
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Current chapter context:\nTitle: {current_chapter['title']}\nStarting from page: {current_chapter['start_page']}\nContinuing analysis from previous page..."
                        }
                    ]
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

            # Add text content with layout context
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Page {page_num} content for analysis:\n\n{page_text}"
                    }
                ]
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
            layout_info = None
            formatted_blocks = []
            content_lines = []
            current_section = None

            # Extract metadata and content
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.upper().startswith("CHAPTER_STATUS:"):
                    chapter_status = line.split(":", 1)[1].strip().upper()
                elif line.upper().startswith("CHAPTER_TITLE:"):
                    chapter_title = line.split(":", 1)[1].strip()
                elif line.upper().startswith("LAYOUT_INFO:"):
                    layout_info = line.split(":", 1)[1].strip()
                elif line.upper().startswith("CONTENT:"):
                    continue
                else:
                    content_lines.append(line)

            # Process content into formatted blocks
            current_format = TextFormatting.PARAGRAPH
            metadata = {
                "indentation_level": 0,
                "formatting": [],
                "context": "",
                "layout_info": layout_info
            }

            for line in content_lines:
                # Markdown parsing with enhanced formatting
                if line.startswith('# '):
                    current_format = TextFormatting.HEADER
                    line = line[2:].strip()
                    metadata = {"context": "chapter_title", "layout_info": layout_info}
                elif line.startswith('## '):
                    current_format = TextFormatting.SUBHEADER
                    line = line[3:].strip()
                    metadata = {"context": "section_title", "layout_info": layout_info}
                elif line.startswith('### '):
                    current_format = TextFormatting.SUBHEADER
                    line = line[4:].strip()
                    metadata = {"context": "subsection_title", "layout_info": layout_info}
                elif line.startswith(('- ', '* ')):
                    current_format = TextFormatting.LIST_ITEM
                    line = line[2:].strip()
                    metadata = {
                        "context": "list",
                        "indentation_level": len(re.match(r'^\s*', line).group()),
                        "layout_info": layout_info
                    }
                elif line.startswith('> '):
                    current_format = TextFormatting.QUOTE
                    line = line[2:].strip()
                    metadata = {"context": "quote", "layout_info": layout_info}
                elif re.match(r'^\d+\. ', line):
                    current_format = TextFormatting.LIST_ITEM
                    line = re.sub(r'^\d+\. ', '', line).strip()
                    metadata = {
                        "context": "numbered_list",
                        "indentation_level": len(re.match(r'^\s*', line).group()),
                        "layout_info": layout_info
                    }
                else:
                    current_format = TextFormatting.PARAGRAPH
                    metadata = {
                        "context": "body",
                        "indentation_level": len(re.match(r'^\s*', line).group()),
                        "layout_info": layout_info
                    }

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
                    "start_page": page_num,
                    "layout_info": layout_info
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
