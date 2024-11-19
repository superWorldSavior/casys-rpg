import json
import re
import asyncio
from typing import Tuple, Optional, List, Dict
import openai
import logging
from ..domain.entities import FormattedText, TextFormatting

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.model_name = "gpt-4-mini"  # Updated model name
        self.max_concurrent = 3  # Reduced for better stability

    async def process_pages_concurrently(self, pages: List[Dict[str, any]]) -> List[List[FormattedText]]:
        """Process multiple pages concurrently using asyncio.gather()"""
        try:
            results = []
            for i in range(0, len(pages), self.max_concurrent):
                batch = pages[i:i + self.max_concurrent]
                tasks = [
                    self.analyze_page_content(page['text'], page['num'])
                    for page in batch
                ]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing page {batch[j]['num']}: {str(result)}")
                        # Use basic text processing as fallback
                        results.append([
                            FormattedText(
                                text=batch[j]['text'],
                                format_type=TextFormatting.PARAGRAPH,
                                metadata={"error": str(result)}
                            )
                        ])
                    else:
                        results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error in concurrent page processing: {e}")
            raise

    async def detect_chapter_with_ai(self, text: str) -> Tuple[bool, Optional[str]]:
        """Use GPT-4-mini to detect chapter breaks and determine titles"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": """You are a text formatting analyzer specializing in book chapter detection.
                    Given a text block, determine if it represents a chapter break and extract the chapter title.
                    Consider various chapter formats including numbered chapters, roman numerals, and descriptive titles.
                    Respond in JSON format with:
                    {
                        "is_chapter": boolean,
                        "title": string or null,
                        "confidence": float (0-1)
                    }"""
                }, {
                    "role": "user",
                    "content": f"Analyze this text block for chapter characteristics:\n{text}"
                }],
                temperature=0.3
            )

            result = re.sub(r'^```json|```$', '',
                          response.choices[0].message.content.strip())
            result_json = json.loads(result)
            return result_json.get("is_chapter", False), result_json.get("title")
        except Exception as e:
            logger.error(f"Error using GPT-4-mini for chapter detection: {e}")
            return False, None

    async def analyze_page_content(self, page_text: str,
                                 page_num: int) -> List[FormattedText]:
        """Analyze page content using GPT-4-mini with enhanced formatting detection"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": """You are a text formatting analyzer specializing in book content structure.
                    Analyze the given page content and identify text blocks with their formatting attributes.
                    Pay special attention to:
                    - Chapter headers and subheaders
                    - Centered text and special formatting
                    - List items and their hierarchy
                    - Block quotes and code segments
                    
                    Return a JSON array where each object has:
                    {
                        "text": string (the content),
                        "format_type": string (one of: 'header', 'subheader', 'centered_header', 'paragraph', 'list_item', 'quote', 'code'),
                        "metadata": {
                            "indentation_level": int (0-3),
                            "formatting": array of strings ['bold', 'italic', 'underline'],
                            "is_centered": boolean,
                            "is_capitalized": boolean,
                            "list_type": string (optional: 'bullet', 'numbered', 'alphabetical')
                        }
                    }"""
                }, {
                    "role": "user",
                    "content": f"Analyze page {page_num} content:\n{page_text}"
                }],
                temperature=0.3
            )

            result = re.sub(r'^```json|```$', '',
                          response.choices[0].message.content.strip())
            blocks = json.loads(result)
            
            return [
                FormattedText(
                    text=block["text"],
                    format_type=TextFormatting[block.get("format_type", "PARAGRAPH").upper()],
                    metadata={
                        "indentation_level": block.get("metadata", {}).get("indentation_level", 0),
                        "formatting": block.get("metadata", {}).get("formatting", []),
                        "is_centered": block.get("metadata", {}).get("is_centered", False),
                        "is_capitalized": block.get("metadata", {}).get("is_capitalized", False),
                        "list_type": block.get("metadata", {}).get("list_type", None)
                    }
                ) for block in blocks
            ]
        except Exception as e:
            logger.error(f"Error analyzing page {page_num}: {e}")
            return [FormattedText(
                text=page_text,
                format_type=TextFormatting.PARAGRAPH,
                metadata={"error": str(e)}
            )]
