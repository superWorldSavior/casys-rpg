import openai
from typing import Tuple, Optional
import json
from ...domain.ports import AIContentAnalyzer
from ..logging_config import StructuredLogger

class OpenAIAnalyzer(AIContentAnalyzer):
    def __init__(self):
        self.client = openai.AsyncOpenAI()
        self.logger = StructuredLogger("OpenAIAnalyzer")
    
    async def analyze_chapter_break(self, text: str) -> Tuple[bool, Optional[str]]:
        """Use OpenAI to detect chapter breaks and determine titles"""
        try:
            self.logger.info("Analyzing text for chapter break", {"text_length": len(text)})
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a text formatting analyzer. Given a text block, determine if it represents a chapter break and extract the chapter title if present. Respond in JSON format with 'is_chapter' (boolean) and 'title' (string or null)."
                }, {
                    "role": "user",
                    "content": f"Analyze this text block for chapter characteristics:\n{text}"
                }]
            )
            
            result = response.choices[0].message.content
            result_json = json.loads(result)
            
            is_chapter = result_json.get("is_chapter", False)
            title = result_json.get("title")
            
            self.logger.info(
                "Chapter analysis complete",
                {"is_chapter": is_chapter, "has_title": bool(title)}
            )
            
            return is_chapter, title
            
        except Exception as e:
            self.logger.error("Error in chapter analysis", e, {"text_length": len(text)})
            return False, None
