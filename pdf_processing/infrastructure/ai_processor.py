import json
import re
from typing import Tuple, Optional
import openai

class AIProcessor:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()

    async def detect_chapter_with_ai(self, text: str) -> Tuple[bool, Optional[str]]:
        """Use OpenAI to detect chapter breaks and determine titles"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a text formatting analyzer. Given a text block, determine if it represents a chapter break and extract the chapter title if present. Respond in JSON format with 'is_chapter' (boolean) and 'title' (string or null)."
                }, {
                    "role": "user",
                    "content": f"Analyze this text block for chapter characteristics:\n{text}"
                }])

            result = re.sub(r'^```json|```$', '', response.choices[0].message.content.strip())
            result_json = json.loads(result)
            return result_json.get("is_chapter", False), result_json.get("title")
        except Exception as e:
            print(f"Error using OpenAI for chapter detection: {e}")
            return False, None
