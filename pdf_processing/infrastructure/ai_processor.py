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




#v2 fonctionne mais sans buffer de chaputre

# import json
# import asyncio
# import base64
# import os
# import re
# from typing import Optional, List, Dict, Any, Tuple
# import openai
# import logging
#
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
#
# class AIProcessor:
#     def __init__(self):
#         self.openai_client = openai.AsyncOpenAI()
#         self.model_name = "gpt-4o-mini"
#         self.max_concurrent = 5
#
#     async def analyze_multimodal_page(self, page: Dict[str, any]) -> str:
#         """
#         Analyze both text and image layout of a page to extract meaningful information in Markdown.
#         """
#         def encode_image(image_path):
#             """Encode image as base64 for AI analysis."""
#             if image_path and os.path.exists(image_path):
#                 with open(image_path, "rb") as image_file:
#                     return base64.b64encode(image_file.read()).decode('utf-8')
#             return None
#
#         base64_image = encode_image(page.get("image_path"))
#         messages = [
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a multimodal document analyzer. Extract content in Markdown format "
#                     "based on the exact text and visual layout seen in the image. "
#                     "Do not wrap the Markdown output in ```markdown or any other code block delimiters. "
#                     "Ensure the output directly represents the document structure without adding extra annotations."
#                 ),
#             },
#             {
#                 "role": "user",
#                 "content": json.dumps({
#                     "text": page["text"],
#                     "page_number": page["num"],
#                     "image_base64": base64_image
#                 })
#             }
#         ]
#
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model=self.model_name,
#                 messages=messages,
#                 temperature=0.0,
#                 max_tokens=4000
#             )
#             raw_content = response.choices[0].message.content.strip()
#
#             # Clean wrapping Markdown or JSON delimiters
#             raw_content = self._clean_wrapping_json_or_markdown(raw_content)
#
#             if not raw_content:
#                 raise ValueError(f"AI returned empty content for page {page['num']}")
#
#             if self._is_valid_markdown(raw_content):
#                 logger.info(f"Markdown extracted for page {page['num']}")
#                 return raw_content
#             else:
#                 logger.warning(f"AI returned non-Markdown response for page {page['num']}: {raw_content}")
#                 return ""
#
#         except Exception as e:
#             logger.error(f"Error in multimodal page analysis for page {page['num']}: {e}")
#             return ""
#
#     async def find_section(self, pages: List[Dict[str, Any]], section_number: int) -> Optional[int]:
#         """
#         Find the page where a section with the given number starts.
#         """
#         for page in pages:
#             page_number = page["num"]
#             page_text = page["text"]
#
#             messages = [
#                 {
#                     "role": "system",
#                     "content": (
#                         f"You are a document structure analyzer. Identify if the given text contains a section "
#                         f"number '{section_number}' that is centered, bold, and followed by a line break. "
#                         "Section 1 always starts on a new page! Return strictly valid JSON with a single key "
#                         "The number shouldnt be a part of a list or a paragraph."
#                         "The section number is always very distinct from the rest of the text. "
#                         "'contains_section' and a boolean value."
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": f"Analyze the following text:\n{page_text}"
#                 }
#             ]
#
#             try:
#                 response = await self.openai_client.chat.completions.create(
#                     model=self.model_name,
#                     messages=messages,
#                     temperature=0.0,
#                     max_tokens=100
#                 )
#                 raw_content = response.choices[0].message.content.strip()
#                 raw_content = self._clean_wrapping_json_or_markdown(raw_content)
#
#                 if self._is_valid_json(raw_content):
#                     result_json = json.loads(raw_content)
#                     if result_json.get("contains_section", False):
#                         logger.info(f"Section {section_number} detected on page {page_number}.")
#                         return page_number
#
#             except Exception as e:
#                 logger.error(f"Error detecting section {section_number} on page {page_number}: {e}")
#
#         logger.info(f"Section {section_number} not found in the document.")
#         return None
#
#     async def detect_chapter_with_ai(self, text: str) -> Tuple[bool, Optional[str]]:
#         """
#         Detect if the given text is the title of a new chapter.
#         """
#         messages = [
#             {
#                 "role": "system",
#                 "content": (
#                     "You are an AI that detects chapter titles. Chapter titles often have a specific typography, "
#                     "such as being centered or using a unique style compared to regular text. "
#                     "Return strictly valid JSON with keys 'is_chapter' (boolean) and 'chapter_title' (string or null)."
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": f"Analyze the following text:\n{text}"
#             }
#         ]
#
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model=self.model_name,
#                 messages=messages,
#                 temperature=0.0,
#                 max_tokens=100
#             )
#             raw_content = response.choices[0].message.content.strip()
#             raw_content = self._clean_wrapping_json_or_markdown(raw_content)
#
#             if self._is_valid_json(raw_content):
#                 result_json = json.loads(raw_content)
#                 return result_json.get("is_chapter", False), result_json.get("chapter_title", None)
#
#         except Exception as e:
#             logger.error(f"Error detecting chapter title: {e}")
#             return False, None
#
#     @staticmethod
#     def _clean_wrapping_json_or_markdown(content: str) -> str:
#         """
#         Remove wrapping delimiters such as ```markdown or ```json and clean JSON encapsulation if needed.
#         """
#         content = re.sub(r'^```(?:markdown|json)?\n|```$', '', content, flags=re.DOTALL).strip()
#         try:
#             if content.startswith("{") or content.startswith("["):
#                 parsed = json.loads(content)
#                 if isinstance(parsed, dict) and "content" in parsed:
#                     return parsed["content"]
#         except json.JSONDecodeError:
#             pass
#         return content
#
#     @staticmethod
#     def _is_valid_markdown(data: str) -> bool:
#         """Check if the response appears to be valid Markdown."""
#         return data.startswith("#") or data.strip() != ""
#
#     @staticmethod
#     def _is_valid_json(data: str) -> bool:
#         """Helper to check if a string is valid JSON."""
#         try:
#             json.loads(data)
#             return True
#         except json.JSONDecodeError:
#             return False


















# #V1 FONCTIONNE ANALYSE MULTI MODALE
# import json

# import asyncio
# import base64
# import os
# import re
# from typing import Optional, List, Dict, Any
# import openai
# import logging
#
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
#
# class AIProcessor:
#     def __init__(self):
#         self.openai_client = openai.AsyncOpenAI()
#         self.model_name = "gpt-4o-mini"
#         self.max_concurrent = 5
#
#     async def analyze_multimodal_page(self, page: Dict[str, any]) -> str:
#         """
#         Analyze both text and image layout of a page to extract meaningful information in Markdown.
#         """
#         def encode_image(image_path):
#             """Encode image as base64 for AI analysis."""
#             if image_path and os.path.exists(image_path):
#                 with open(image_path, "rb") as image_file:
#                     return base64.b64encode(image_file.read()).decode('utf-8')
#             return None
#
#         base64_image = encode_image(page.get("image_path"))
#         messages = [
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a multimodal document analyzer. Extract content in Markdown format "
#                     "based on the exact text and visual layout seen in the image. "
#                     "Do not wrap the Markdown output in ```markdown or any other code block delimiters. "
#                     "Ensure the output directly represents the document structure without adding extra annotations."
#                 ),
#             },
#             {
#                 "role": "user",
#                 "content": json.dumps({
#                     "text": page["text"],
#                     "page_number": page["num"],
#                     "image_base64": base64_image
#                 })
#             }
#         ]
#
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model=self.model_name,
#                 messages=messages,
#                 temperature=0.0,
#                 max_tokens=4000
#             )
#             raw_content = response.choices[0].message.content.strip()
#
#             # Clean wrapping Markdown or JSON delimiters
#             raw_content = self._clean_wrapping_json_or_markdown(raw_content)
#
#             if not raw_content:
#                 raise ValueError(f"AI returned empty content for page {page['num']}")
#
#             if self._is_valid_markdown(raw_content):
#                 logger.info(f"Markdown extracted for page {page['num']}")
#                 return raw_content
#             else:
#                 logger.warning(f"AI returned non-Markdown response for page {page['num']}: {raw_content}")
#                 return ""
#
#         except Exception as e:
#             logger.error(f"Error in multimodal page analysis for page {page['num']}: {e}")
#             return ""
#
#     async def find_section(self, pages: List[Dict[str, Any]], section_number: int) -> Optional[int]:
#         """
#         Find the page where a section with the given number starts.
#
#         Args:
#             pages (List[Dict[str, Any]]): List of pages with their text and number.
#             section_number (int): The number of the section to find.
#
#         Returns:
#             Optional[int]: The page number where the section starts, or None if not found.
#         """
#         for page in pages:
#             page_number = page["num"]
#             page_text = page["text"]
#
#             messages = [
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a document structure analyzer. Identify if the given text contains "
#                         f"a chapter titled '{section_number}' centered or on a single line, at the beginning of the text. Return strictly valid JSON "
#                         "with a single key 'contains_section' and a boolean value."
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": f"Analyze the following text:\n{page_text}"
#                 }
#             ]
#
#             try:
#                 response = await self.openai_client.chat.completions.create(
#                     model=self.model_name,
#                     messages=messages,
#                     temperature=0.0,
#                     max_tokens=100
#                 )
#                 raw_content = response.choices[0].message.content.strip()
#                 raw_content = self._clean_wrapping_json_or_markdown(raw_content)
#
#                 if self._is_valid_json(raw_content):
#                     result_json = json.loads(raw_content)
#                     if result_json.get("contains_section", False):
#                         logger.info(f"Section {section_number} detected on page {page_number}.")
#                         return page_number
#
#             except Exception as e:
#                 logger.error(f"Error detecting section {section_number} on page {page_number}: {e}")
#
#         logger.info(f"Section {section_number} not found in the document.")
#         return None
#
#     @staticmethod
#     def _clean_wrapping_json_or_markdown(content: str) -> str:
#         """
#         Remove wrapping delimiters such as ```markdown or ```json and clean JSON encapsulation if needed.
#         """
#         # Remove Markdown or JSON delimiters like ```markdown, ```json, and ```
#         content = re.sub(r'^```(?:markdown|json)?\n|```$', '', content, flags=re.DOTALL).strip()
#         try:
#             if content.startswith("{") or content.startswith("["):
#                 parsed = json.loads(content)
#                 if isinstance(parsed, dict) and "content" in parsed:
#                     return parsed["content"]
#         except json.JSONDecodeError:
#             pass
#         return content
#
#     @staticmethod
#     def _is_valid_markdown(data: str) -> bool:
#         """Check if the response appears to be valid Markdown."""
#         return data.startswith("#") or data.strip() != ""
#
#     @staticmethod
#     def _is_valid_json(data: str) -> bool:
#         """Helper to check if a string is valid JSON."""
#         try:
#             json.loads(data)
#             return True
#         except json.JSONDecodeError:
#             return False








#code legacy sans le multimodal

# import json
# import asyncio
# import base64
# from typing import Tuple, Optional, List, Dict
# import openai
# import logging
# from ..domain.entities import FormattedText, TextFormatting
#
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#
#
# logger = logging.getLogger(__name__)
#
#
# class AIProcessor:
#     def __init__(self):
#         self.openai_client = openai.AsyncOpenAI()
#         self.model_name = "gpt-4o-mini"
#         self.max_concurrent = 5
#
#     async def process_pages_concurrently(self, pages: List[Dict[str, any]]) -> List[List[FormattedText]]:
#         """Process multiple pages concurrently using asyncio.gather()"""
#         try:
#             tasks = [self.analyze_page_content(page['text'], page['num']) for page in pages]
#             batch_results = await asyncio.gather(*tasks, return_exceptions=True)
#
#             results = []
#             for i, result in enumerate(batch_results):
#                 if isinstance(result, Exception):
#                     logger.error(f"Error processing page {pages[i]['num']}: {str(result)}")
#                     results.append([FormattedText(
#                         text=pages[i]['text'],
#                         format_type=TextFormatting.PARAGRAPH,
#                         metadata={"error": str(result), "page_number": pages[i]['num']}
#                     )])
#                 else:
#                     results.append(result)
#
#             return results
#         except Exception as e:
#             logger.error(f"Error in concurrent page processing: {e}")
#             raise
#
#     async def detect_chapter_with_ai(self, text: str) -> Tuple[bool, Optional[str]]:
#         """Use AI to detect chapter and extract title."""
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model=self.model_name,
#                 messages=[{
#                     "role": "system",
#                     "content": "You are a text structure analyzer. Return strictly valid JSON with no extra markdown formatting."
#                 }, {
#                     "role": "user",
#                     "content": f"Does this text represent a chapter? Include a title if available.\n{text}"
#                 }],
#                 temperature=0.3
#             )
#
#             raw_content = response.choices[0].message.content.strip()
#
#             # Ensure the format is valid JSON
#             if not raw_content.startswith("{") or not raw_content.endswith("}"):
#                 logger.error(f"Unexpected AI response format: {raw_content}")
#                 return False, None
#
#             result_json = json.loads(raw_content)
#             return result_json.get("is_chapter", False), result_json.get("title")
#
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON parsing error: {e}")
#             return False, None
#         except Exception as e:
#             logger.error(f"Error detecting chapter: {e}")
#             return False, None
#
#     async def analyze_page_content(self, page_text: str, page_num: int) -> List[FormattedText]:
#         """Analyze page content and return formatted text blocks."""
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model=self.model_name,
#                 messages=[{
#                     "role": "system",
#                     "content": """You are a text formatting analyzer. Return strictly valid JSON with the following structure:
#                     [
#                         {"text": "content", "format_type": "header", "metadata": {"indentation_level": 0, "formatting": []}}
#                     ]. No markdown delimiters."""
#                 }, {
#                     "role": "user",
#                     "content": f"Page {page_num}:\n{page_text}"
#                 }],
#                 temperature=0.3
#             )
#
#             raw_content = response.choices[0].message.content.strip()
#
#             # Validate JSON format
#             if not (raw_content.startswith("[") and raw_content.endswith("]")):
#                 raise ValueError(f"Unexpected response format: {raw_content}")
#
#             blocks = json.loads(raw_content)
#
#             formatted_text_blocks = []
#             for block in blocks:
#                 try:
#                     format_type = block.get("format_type", "PARAGRAPH").upper()
#                     if format_type not in TextFormatting.__members__:
#                         logger.warning(
#                             f"Unknown format_type '{format_type}' on page {page_num}. Defaulting to PARAGRAPH.")
#                         format_type = "PARAGRAPH"
#
#                     formatted_text_block = FormattedText(
#                         text=block["text"],
#                         format_type=TextFormatting[format_type],
#                         metadata={
#                             "indentation_level": block.get("metadata", {}).get("indentation_level", 0),
#                             "formatting": block.get("metadata", {}).get("formatting", []),
#                             "page_number": page_num
#                         }
#                     )
#                     formatted_text_blocks.append(formatted_text_block)
#                 except KeyError as e:
#                     logger.error(f"Missing key in block: {block}, error: {e}")
#                 except Exception as e:
#                     logger.error(f"Error processing block: {block}, error: {e}")
#
#             logger.info(f"Formatted text blocks for page {page_num}: {formatted_text_blocks}")
#             return formatted_text_blocks
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON parsing error for page {page_num}: {e}")
#             return [
#                 FormattedText(
#                     text=page_text,
#                     format_type=TextFormatting.PARAGRAPH,
#                     metadata={"error": f"JSON parsing error: {str(e)}", "page_number": page_num}
#                 )
#             ]
#         except Exception as e:
#             logger.error(f"Error analyzing page {page_num}: {e}")
#             return [
#                 FormattedText(
#                     text=page_text,
#                     format_type=TextFormatting.PARAGRAPH,
#                     metadata={"error": str(e), "page_number": page_num}
#                 )
#             ]
#
#     async def detect_section_with_ai(self, text: str) -> Tuple[Optional[int], Optional[str]]:
#         """Use AI to detect sections in text and return section details."""
#         messages = [
#             {
#                 "role": "system",
#                 "content": "You are an AI that detects section numbers and their attributes. Return strictly valid JSON."
#             },
#             {
#                 "role": "user",
#                 "content": f"Please analyze this text and detect any sections:\n{text}"
#             }
#         ]
#
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model=self.model_name,
#                 messages=messages,
#                 temperature=0.3
#             )
#
#             raw_content = response.choices[0].message.content.strip()
#
#             # Validate JSON format
#             if not (raw_content.startswith("{") and raw_content.endswith("}")):
#                 raise ValueError(f"Unexpected response format: {raw_content}")
#
#             result_json = json.loads(raw_content)
#
#             section_num = result_json.get("section_num", None)
#             attributes = result_json.get("attributes", "")
#
#             return section_num, attributes
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON parsing error: {e}")
#             return None, None
#         except Exception as e:
#             logger.error(f"Error detecting section: {e}")
#             return None, None
#
#     async def analyze_multimodal_content(self, text: str, image_path: str) -> Dict[str, any]:
#         """Use AI to analyze text and corresponding image content."""
#
#         def encode_image(image_path):
#             with open(image_path, "rb") as image_file:
#                 return base64.b64encode(image_file.read()).decode('utf-8')
#
#         base64_image = encode_image(image_path)
#
#         messages = [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": "Analyze the following text and image together."},
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     },
#                     {"type": "text", "text": text}
#                 ]
#             }
#         ]
#
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model=self.model_name,
#                 messages=messages,
#                 temperature=0.3,
#                 max_tokens=300
#             )
#
#             raw_content = response.choices[0].message.content.strip()
#             result_json = json.loads(raw_content)
#             return result_json
#
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON parsing error: {e}")
#             return {"error": str(e)}
#         except Exception as e:
#             logger.error(f"Error in multimodal analysis: {e}")
#             return {"error": str(e)}




# fonctionne mais on avait pas l'enregistremetn de tout je crois


# import json
# import asyncio
# import base64
# from typing import Tuple, Optional, List, Dict
# import openai
# import logging
# from ..domain.entities import FormattedText, TextFormatting
#
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
#
#
# class AIProcessor:
#     def __init__(self):
#         self.openai_client = openai.AsyncOpenAI()
#         self.model_name = "gpt-4o-mini"  # Ensure GPT-4 with vision support is used.
#
#     async def detect_section_with_ai(self, text: str) -> Tuple[Optional[int], Optional[str]]:
#         """Use AI to detect sections in text and return section details."""
#         messages = [
#             {
#                 "role": "system",
#                 "content": "You are an AI that detects sections in a document. Return strictly valid JSON with keys 'section_num' and 'attributes'."
#             },
#             {
#                 "role": "user",
#                 "content": f"Analyze this text and detect section details:\n{text}"
#             }
#         ]
#
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model=self.model_name,
#                 messages=messages,
#                 temperature=0.3
#             )
#
#             raw_content = response.choices[0].message.content.strip()
#
#             # Validate JSON format
#             if not (raw_content.startswith("{") and raw_content.endswith("}")):
#                 raise ValueError(f"Unexpected response format: {raw_content}")
#
#             result_json = json.loads(raw_content)
#             section_num = result_json.get("section_num")
#             attributes = result_json.get("attributes", "")
#
#             return section_num, attributes
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON parsing error: {e}")
#             return None, None
#         except Exception as e:
#             logger.error(f"Error detecting section: {e}")
#             return None, None
#
#     async def analyze_multimodal_content(self, text: str, image_path: str) -> Dict[str, any]:
#         """Use AI to analyze text and corresponding image content."""
#
#         def encode_image(image_path):
#             with open(image_path, "rb") as image_file:
#                 return base64.b64encode(image_file.read()).decode('utf-8')
#
#         base64_image = encode_image(image_path)
#
#         messages = [
#             {
#                 "role": "system",
#                 "content": "You are an AI capable of analyzing documents with both text and images. Return valid JSON responses."
#             },
#             {
#                 "role": "user",
#                 "content": f"Analyze this text and image together:\n{text}",
#                 "image": {"image_base64": base64_image}
#             }
#         ]
#
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model=self.model_name,
#                 messages=messages,
#                 temperature=0.3,
#                 max_tokens=300
#             )
#
#             raw_content = response.choices[0].message.content.strip()
#             if not (raw_content.startswith("{") and raw_content.endswith("}")):
#                 raise ValueError(f"Unexpected response format: {raw_content}")
#
#             result_json = json.loads(raw_content)
#             return result_json
#
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON parsing error: {e}")
#             return {"error": str(e)}
#         except Exception as e:
#             logger.error(f"Error in multimodal analysis: {e}")
#             return {"error": str(e)}
#
#     async def analyze_page_with_vision(self, image_path: str, page_text: str, page_num: int) -> List[FormattedText]:
#         """Analyze a PDF page using vision (image) and text content."""
#         try:
#             multimodal_result = await self.analyze_multimodal_content(page_text, image_path)
#             if "error" in multimodal_result:
#                 raise ValueError(multimodal_result["error"])
#
#             blocks = multimodal_result.get("blocks", [])
#
#             formatted_text_blocks = [
#                 FormattedText(
#                     text=block["text"],
#                     format_type=TextFormatting.get(block["format_type"].upper(), TextFormatting.PARAGRAPH),
#                     metadata=block.get("metadata", {})
#                 )
#                 for block in blocks
#             ]
#
#             return formatted_text_blocks
#         except Exception as e:
#             logger.error(f"Error analyzing page {page_num} with vision: {e}")
#             return [
#                 FormattedText(
#                     text=page_text,
#                     format_type=TextFormatting.PARAGRAPH,
#                     metadata={"error": str(e), "page_number": page_num}
#                 )
#             ]
