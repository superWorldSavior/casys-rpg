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
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Updated model name
                messages=[{
                    "role": "system",
                    "content": "You are a text formatting analyzer. Given text, identify if it's a chapter break and extract title. Return JSON with {'is_chapter': boolean, 'title': string or null}."
                }, {
                    "role": "user",
                    "content": f"Analyze this text for chapter characteristics:\n{text}"
                }],
                temperature=0.3  # Added temperature parameter
            )
            
            if not response.choices or not response.choices[0].message:
                self.logger.error("Invalid response from OpenAI")
                return False, None
                
            result = response.choices[0].message.content
            if not result or not result.strip():
                self.logger.error("Empty response from OpenAI")
                return False, None
                
            try:
                result_json = json.loads(result)
                if not isinstance(result_json, dict):
                    self.logger.error("Invalid JSON structure")
                    return False, None
                    
                return result_json.get("is_chapter", False), result_json.get("title")
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing error: {e}")
                return False, None
                
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return False, None
