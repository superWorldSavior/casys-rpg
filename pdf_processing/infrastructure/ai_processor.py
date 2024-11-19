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
        self.model_name = "gpt-3.5-turbo"  # Updated to use gpt-3.5-turbo
        self.max_concurrent = 5

    async def process_pages_concurrently(self, pages: List[Dict[str, any]]) -> List[List[FormattedText]]:
        """Process multiple pages concurrently using asyncio.gather()"""
        try:
            # Create batches of max_concurrent size
            results = []
            for i in range(0, len(pages), self.max_concurrent):
                batch = pages[i:i + self.max_concurrent]
                tasks = [
                    self.analyze_page_content(page['text'], page['num'])
                    for page in batch
                ]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle any exceptions in the batch
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
        """Use OpenAI to detect chapter breaks and determine titles"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": "You are a text formatting analyzer. Given a text block, determine if it represents a chapter break and extract the chapter title if present. Respond in JSON format with 'is_chapter' (boolean) and 'title' (string or null)."
                }, {
                    "role": "user",
                    "content": f"Analyze this text block for chapter characteristics:\n{text}"
                }],
                temperature=0.3  # Added lower temperature for more consistent results
            )

            result = re.sub(r'^```json|```$', '',
                          response.choices[0].message.content.strip())
            result_json = json.loads(result)
            return result_json.get("is_chapter", False), result_json.get("title")
        except Exception as e:
            logger.error(f"Error using OpenAI for chapter detection: {e}")
            return False, None

    async def analyze_page_content(self, page_text: str,
                                 page_num: int) -> List[FormattedText]:
        """Analyze page content and return formatted text blocks"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": """You are a text formatting analyzer. Analyze the given page content and identify text blocks with their formatting attributes. 
                    Return a JSON array where each object has:
                    - text: the content
                    - format_type: string ('header', 'subheader', 'paragraph', 'list_item', 'quote', 'code')
                    - metadata: object with additional properties like indentation_level (0-3) and formatting (['bold', 'italic', 'underline'])"""
                }, {
                    "role": "user",
                    "content": f"Page {page_num}:\n{page_text}"
                }],
                temperature=0.3  # Added lower temperature for more consistent results
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
                        "formatting": block.get("metadata", {}).get("formatting", [])
                    }
                ) for block in blocks
            ]
        except Exception as e:
            logger.error(f"Error analyzing page {page_num}: {e}")
            # Return a simple formatted text block as fallback
            return [FormattedText(
                text=page_text,
                format_type=TextFormatting.PARAGRAPH,
                metadata={"indentation_level": 0, "formatting": []}
            )]
