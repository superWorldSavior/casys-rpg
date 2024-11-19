import json
import re
from typing import Tuple, Optional, List
import openai
from ..domain.entities import FormattedText


class AIProcessor:

    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()

    async def detect_chapter_with_ai(self,
                                   text: str) -> Tuple[bool, Optional[str]]:
        """Use OpenAI to detect chapter breaks and determine titles"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-mini",  # Fixed model name
                messages=[{
                    "role":
                    "system",
                    "content":
                    "You are a text formatting analyzer. Given a text block, determine if it represents a chapter break and extract the chapter title if present. Respond in JSON format with 'is_chapter' (boolean) and 'title' (string or null)."
                }, {
                    "role": "user",
                    "content": f"Analyze this text block for chapter characteristics:\n{text}"
                }])

            result = re.sub(r'^```json|```$', '',
                          response.choices[0].message.content.strip())
            result_json = json.loads(result)
            return result_json.get("is_chapter", False), result_json.get("title")
        except Exception as e:
            print(f"Error using OpenAI for chapter detection: {e}")
            return False, None

    async def analyze_page_content(self, page_text: str,
                                 page_num: int) -> List[FormattedText]:
        """Analyze page content and return formatted text blocks"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-mini",
                messages=[{
                    "role":
                    "system",
                    "content":
                    """You are a text formatting analyzer. Analyze the given page content and identify text blocks with their formatting attributes. 
                    Return a JSON array where each object has:
                    - text: the content
                    - is_title: boolean if it's a title
                    - is_header: boolean if it's a header
                    - indentation_level: number (0-3)
                    - formatting: array of strings ('bold', 'italic', 'underline')"""
                }, {
                    "role":
                    "user",
                    "content":
                    f"Page {page_num}:\n{page_text}"
                }])

            result = re.sub(r'^```json|```$', '',
                          response.choices[0].message.content.strip())
            blocks = json.loads(result)
            
            return [
                FormattedText(
                    text=block["text"],
                    is_title=block.get("is_title", False),
                    is_header=block.get("is_header", False),
                    indentation_level=block.get("indentation_level", 0),
                    formatting=block.get("formatting", [])
                ) for block in blocks
            ]
        except Exception as e:
            print(f"Error analyzing page {page_num}: {e}")
            return [FormattedText(text=page_text, is_title=False, is_header=False, indentation_level=0, formatting=[])]
