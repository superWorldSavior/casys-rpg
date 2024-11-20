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

    async def analyze_page_content(self, page_text: str, page_num: int, images: Optional[List[PDFImage]] = None) -> List[FormattedText]:
        """Analyze page content using multimodal analysis with gpt-4o-mini"""
        try:
            logger.info(f"Processing page {page_num} with multimodal gpt-4o-mini analysis")
            
            # Prepare system message with explicit multimodal focus
            system_prompt = """You are an expert document analyzer specialized in multimodal book content processing.
            Analyze both text and images together to understand the complete document structure.
            Tasks:
            1. Identify structural elements (headers, subheaders, paragraphs)
            2. Recognize visual-textual relationships
            3. Determine semantic importance of content
            4. Apply appropriate formatting and hierarchy
            
            Return structured markdown with clear semantic formatting."""

            # Initialize messages array with system prompt
            messages = [{"role": "system", "content": system_prompt}]
            
            # Process text content
            text_content = f"""Page {page_num} Content Analysis:
            
            Text Content:
            {page_text}"""
            
            # Add image analysis if available
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

            # Add text analysis request
            messages.append({"role": "user", "content": text_content})

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

            # Parse the response into formatted blocks with enhanced structure detection
            blocks = []
            current_format = TextFormatting.PARAGRAPH
            current_metadata = {"indentation_level": 0, "formatting": [], "context": ""}

            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Enhanced format detection with context preservation
                if re.match(r'^#{1,2}\s+', line):
                    level = len(re.match(r'^#+', line).group())
                    current_format = TextFormatting.HEADER if level == 1 else TextFormatting.SUBHEADER
                    line = re.sub(r'^#+\s+', '', line)
                    current_metadata["context"] = "heading"
                elif line.startswith(('- ', '* ', '• ')):
                    current_format = TextFormatting.LIST_ITEM
                    line = re.sub(r'^[- *•]\s+', '', line)
                    current_metadata["indentation_level"] = 1
                    current_metadata["context"] = "list"
                elif line.startswith('> '):
                    current_format = TextFormatting.QUOTE
                    line = line[2:]
                    current_metadata["context"] = "quote"
                elif re.match(r'^\d+\.\s+', line):
                    current_format = TextFormatting.LIST_ITEM
                    line = re.sub(r'^\d+\.\s+', '', line)
                    current_metadata["indentation_level"] = 1
                    current_metadata["context"] = "numbered_list"
                else:
                    current_format = TextFormatting.PARAGRAPH
                    current_metadata["indentation_level"] = 0
                    current_metadata["context"] = "body"

                blocks.append(FormattedText(
                    text=line,
                    format_type=current_format,
                    metadata=current_metadata.copy()
                ))

            return blocks

        except Exception as e:
            logger.error(f"Error in gpt-4o-mini multimodal analysis for page {page_num}: {e}")
            # Fallback to basic formatting
            return [FormattedText(
                text=page_text,
                format_type=TextFormatting.PARAGRAPH,
                metadata={"indentation_level": 0, "formatting": [], "context": "fallback"}
            )]

    async def detect_chapter_with_ai(self, text: str, associated_image: Optional[PDFImage] = None) -> Tuple[bool, Optional[str]]:
        """Detect chapter breaks using multimodal gpt-4o-mini analysis"""
        try:
            # Enhanced system prompt for chapter detection
            system_prompt = """You are a specialized AI trained to identify chapter breaks in books using multimodal analysis.
            Consider both textual and visual indicators:
            1. Chapter numbers and titles (explicit markers)
            2. Visual layout and formatting (implicit markers)
            3. Content transitions and thematic shifts
            4. Image placement and relevance to chapter boundaries
            
            Respond with:
            - CHAPTER: YES/NO
            - TITLE: [extracted title if found]
            - CONFIDENCE: HIGH/MEDIUM/LOW"""

            # Prepare messages array
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add image analysis if available
            if associated_image:
                image_data = self._encode_image(associated_image.image_path)
                if image_data:
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Visual content for chapter analysis:"
                            },
                            {
                                "type": "image",
                                "image_url": f"data:image/png;base64,{image_data}"
                            }
                        ]
                    })

            # Add text analysis request
            content_prompt = f"""Analyze for chapter indicators:
            {text}"""
            messages.append({"role": "user", "content": content_prompt})

            # Get AI analysis
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=200
            )

            content = response.choices[0].message.content
            if not content:
                return False, None

            # Enhanced response parsing
            is_chapter = False
            title = None
            confidence = "LOW"

            # Parse structured response
            for line in content.lower().split('\n'):
                if 'chapter:' in line:
                    is_chapter = 'yes' in line
                elif 'title:' in line:
                    title_match = re.search(r'title:\s*(.+)', line, re.IGNORECASE)
                    if title_match:
                        title = title_match.group(1).strip()
                elif 'confidence:' in line:
                    confidence = line.split(':')[1].strip().upper()

            # Only accept chapter detection with medium or high confidence
            if confidence == "LOW":
                is_chapter = False

            # Fallback title extraction if needed
            if is_chapter and not title:
                # Look for capitalized lines that might be titles
                title_candidates = [line.strip() for line in text.split('\n')
                                 if line.strip() and line.strip()[0].isupper()]
                if title_candidates:
                    title = title_candidates[0]

            return is_chapter, title

        except Exception as e:
            logger.error(f"Error in gpt-4o-mini chapter detection: {e}")
            return False, None
