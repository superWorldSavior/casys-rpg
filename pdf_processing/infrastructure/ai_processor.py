import json
import asyncio
import base64
import os
import re
from typing import Optional, List, Dict, Any, Tuple
import openai
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.model_name = "gpt-4o"
        self.max_concurrent = 5

    async def analyze_multimodal_page(self, page: Dict[str, any]) -> str:
        def encode_image(image_path):
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            return None

        base64_image = encode_image(page.get("image_path"))
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a multimodal document analyzer. Extract content in Markdown format "
                    "based on the exact text and visual layout seen in the image. "
                    "Do not wrap the Markdown output in ```markdown or any other code block delimiters. "
                    "Ensure the output directly represents the document structure without adding extra annotations."
                ),
            },
            {
                "role": "user",
                "content": json.dumps({
                    "text": page["text"],
                    "page_number": page["num"],
                    "image_base64": base64_image
                })
            }
        ]

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0,
                max_tokens=4000
            )
            raw_content = response.choices[0].message.content.strip()
            raw_content = self._clean_wrapping_json_or_markdown(raw_content)

            if not raw_content:
                raise ValueError(f"AI returned empty content for page {page['num']}")

            if self._is_valid_markdown(raw_content):
                logger.info(f"Markdown extracted for page {page['num']}")
                return raw_content
            else:
                logger.warning(f"AI returned non-Markdown response for page {page['num']}: {raw_content}")
                return ""

        except Exception as e:
            logger.error(f"Error in multimodal page analysis for page {page['num']}: {e}")
            return ""

    async def detect_chapter_with_ai(self, text: str) -> Tuple[bool, Optional[str]]:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI that detects chapter titles. Chapter titles often have a specific typography, "
                    "such as being centered or using a unique style compared to regular text. "
                    "Return strictly valid JSON with keys 'is_chapter' (boolean) and 'chapter_title' (string or null)."
                )
            },
            {
                "role": "user",
                "content": f"Analyze the following text:\n{text}"
            }
        ]

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.0,
                max_tokens=100
            )
            raw_content = response.choices[0].message.content.strip()
            raw_content = self._clean_wrapping_json_or_markdown(raw_content)

            if self._is_valid_json(raw_content):
                result_json = json.loads(raw_content)
                return result_json.get("is_chapter", False), result_json.get("chapter_title", None)

        except Exception as e:
            logger.error(f"Error detecting chapter title: {e}")
            return False, None

    @staticmethod
    def _clean_wrapping_json_or_markdown(content: str) -> str:
        content = re.sub(r'^```(?:markdown|json)?\n|```$', '', content, flags=re.DOTALL).strip()
        try:
            if content.startswith("{") or content.startswith("["):
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "content" in parsed:
                    return parsed["content"]
        except json.JSONDecodeError:
            pass
        return content

    @staticmethod
    def _is_valid_markdown(data: str) -> bool:
        return data.startswith("#") or data.strip() != ""

    @staticmethod
    def _is_valid_json(data: str) -> bool:
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False