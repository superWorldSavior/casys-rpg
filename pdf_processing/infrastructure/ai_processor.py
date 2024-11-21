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
        self.model_name = "gpt-4o-mini"
        self.max_concurrent = 5

    async def analyze_multimodal_page(self, page: Dict[str, any]) -> str:
        """Analyze both text and image layout of a page to extract meaningful information in Markdown."""
        def encode_image(image_path):
            """Encode image as base64 for AI analysis."""
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

            # Clean wrapping Markdown or JSON delimiters
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

    async def find_section(self, pages: List[Dict[str, Any]], section_number: int) -> Optional[int]:
        """Find the page where a section with the given number starts."""
        for page in pages:
            page_number = page["num"]
            page_text = page["text"]

            messages = [
                {
                    "role": "system",
                    "content": (
                        f"You are a document structure analyzer. Identify if the given text contains a section "
                        f"number '{section_number}' that is centered, bold, and followed by a line break. "
                        "Section 1 usually start on a new page. Return strictly valid JSON with a single key "
                        "The number should't be a part of a list or a paragraph."
                        "The section number is always very distinct from the rest of the text. "
                        "'contains_section' and a boolean value."
                    )
                },
                {
                    "role": "user",
                    "content": f"Analyze the following text:\n{page_text}"
                }
            ]

            try:
                response = await self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=100
                )
                raw_content = response.choices[0].message.content.strip()
                raw_content = self._clean_wrapping_json_or_markdown(raw_content)

                if self._is_valid_json(raw_content):
                    result_json = json.loads(raw_content)
                    if result_json.get("contains_section", False):
                        logger.info(f"Section {section_number} detected on page {page_number}.")
                        return page_number

            except Exception as e:
                logger.error(f"Error detecting section {section_number} on page {page_number}: {e}")

        logger.info(f"Section {section_number} not found in the document.")
        return None

    async def detect_chapter_with_ai(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect if the given text is the title of a new chapter."""
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
                model=self.model_name,
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
        """Remove wrapping delimiters such as ```markdown or ```json and clean JSON encapsulation if needed."""
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
        """Check if the response appears to be valid Markdown."""
        return data.startswith("#") or data.strip() != ""

    @staticmethod
    def _is_valid_json(data: str) -> bool:
        """Helper to check if a string is valid JSON."""
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False
