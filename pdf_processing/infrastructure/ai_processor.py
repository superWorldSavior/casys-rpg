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
        self.model_name = "gpt-4"  # Default to GPT-4 since GPT-4-mini is not available
        self.max_tokens = 1000
        self.temperature = 0.3

    async def analyze_page_content(self, page_text: str, page_num: int) -> List[FormattedText]:
        """Analyze page content sequentially and return formatted text blocks"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": """You are a text formatting analyzer. Analyze the given page content and identify text blocks with their formatting attributes. 
                    Return a JSON array where each object has:
                    - text: the content
                    - format_type: string ('HEADER', 'SUBHEADER', 'PARAGRAPH', 'LIST_ITEM', 'QUOTE', 'CODE')
                    - metadata: object with additional properties like indentation_level and formatting (['bold', 'italic', 'underline'])"""
                }, {
                    "role": "user",
                    "content": f"Page {page_num}:\n{page_text}"
                }],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            result = re.sub(r'^```json|```$', '', response.choices[0].message.content.strip())
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
                temperature=self.temperature,
                max_tokens=100
            )

            result = re.sub(r'^```json|```$', '', response.choices[0].message.content.strip())
            result_json = json.loads(result)
            return result_json.get("is_chapter", False), result_json.get("title")
        except Exception as e:
            logger.error(f"Error using OpenAI for chapter detection: {e}")
            return False, None
