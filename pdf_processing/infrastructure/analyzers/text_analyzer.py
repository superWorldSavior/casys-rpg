"""Text analysis functionality extracted from pdf_processor."""
import re
import json
import asyncio
import logging
from typing import List, Tuple, Optional, Dict, Any
from ...domain.entities import TextFormatting, FormattedText
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIRequestError(Exception):
    """Custom exception for OpenAI API request errors."""
    pass

class JSONValidationError(Exception):
    """Custom exception for JSON validation errors."""
    pass

class TextAnalyzer:
    """Analyzes text content from PDFs."""
    
    def __init__(self):
        self.chapter_pattern = r'^\s*(\d+)\s*$'
        self.header_patterns = [
            r'^[A-Z][^a-z]{0,2}[A-Z].*$',  # All caps or nearly all caps
            r'^[A-Z][a-zA-Z\s]{0,50}$',  # Title case, not too long
        ]
        self.openai_client = openai.AsyncOpenAI()

    def _validate_openai_response(self, result: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate OpenAI API response structure."""
        if not isinstance(result, dict):
            raise JSONValidationError("Response must be a dictionary")
        
        is_chapter = result.get("is_chapter")
        title = result.get("title")
        
        if not isinstance(is_chapter, bool):
            raise JSONValidationError("is_chapter must be a boolean")
        
        if title is not None and not isinstance(title, str):
            raise JSONValidationError("title must be a string or null")
            
        return is_chapter, title

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APITimeoutError, openai.RateLimitError))
    )
    async def _make_openai_request(self, text: str) -> Dict[str, Any]:
        """Make OpenAI API request with retry mechanism and improved error handling."""
        try:
            logger.info("Making OpenAI API request for text analysis")
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a text formatting analyzer. Given a text block, determine if it represents a chapter break and extract the chapter title if present. Respond in JSON format with 'is_chapter' (boolean) and 'title' (string or null)."
                }, {
                    "role": "user",
                    "content": f"Analyze this text block for chapter characteristics:\n{text}"
                }]
            )
            
            if not response.choices:
                raise OpenAIRequestError("No choices returned in OpenAI response")
                
            result = response.choices[0].message.content
            
            try:
                return json.loads(result)
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse OpenAI response: {je}")
                raise JSONValidationError(f"Invalid JSON in OpenAI response: {je}")
                
        except openai.AuthenticationError as e:
            logger.error("OpenAI authentication failed", exc_info=True)
            raise OpenAIRequestError("Authentication failed with OpenAI API") from e
        except openai.APIError as e:
            logger.error("OpenAI API error occurred", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI request: {e}", exc_info=True)
            raise OpenAIRequestError(f"Unexpected error: {str(e)}") from e

    async def detect_chapter_with_ai(self, text: str) -> Tuple[bool, Optional[str]]:
        """Use OpenAI to detect chapter breaks and determine titles with improved error handling."""
        try:
            logger.info("Starting chapter detection with AI")
            result = await self._make_openai_request(text)
            return self._validate_openai_response(result)
            
        except (OpenAIRequestError, JSONValidationError) as e:
            logger.error(f"Error in chapter detection: {e}", exc_info=True)
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error in chapter detection: {e}", exc_info=True)
            return False, None

    def detect_chapter(self, text: str) -> Tuple[Optional[int], Optional[str]]:
        """Detect if text is a standalone number."""
        text = text.strip()
        match = re.match(self.chapter_pattern, text)
        if match:
            try:
                chapter_num = int(match.group(1))
                return chapter_num, ""
            except ValueError:
                logger.warning(f"Failed to convert chapter number: {text}")
                pass
        return None, None

    def is_centered_text(self, text: str, line_spacing: Optional[float] = None) -> bool:
        """Enhanced centered text detection."""
        text = text.strip()
        if not text:
            return False

        # Skip long paragraphs
        if len(text) > 100:
            return False

        # Check for common centered text indicators
        indicators = [
            text.isupper(),  # All uppercase
            text.istitle() and len(text.split()) <= 7,  # Short title case phrases
            text.startswith('    ') or text.startswith('\t'),  # Indentation
            text.startswith('*') and text.endswith('*'),  # Asterisk wrapping
            bool(re.match(r'^[-—=]{3,}$', text)),  # Horizontal rules
            bool(re.match(r'^[A-Z][^.!?]*(?:[.!?]|\s)*$', text) and len(text) < 60),  # Short complete sentence
            bool(re.match(r'^(?:by|written by|translated by)\s+[A-Z][a-zA-Z\s.]+$', text, re.I)),  # Author attribution
            bool(re.match(r'^[A-Z\s]+$', text) and len(text) < 50)  # All caps short text
        ]

        return any(indicators)

    def detect_formatting(self, text: str, is_pre_section: bool = False) -> TextFormatting:
        """Enhanced formatting detection."""
        text = text.strip()

        if not text:
            return TextFormatting.PARAGRAPH

        # Check for horizontal rules
        if re.match(r'^[-—=*]{3,}$', text):
            return TextFormatting.HEADER

        # Check for standalone section number
        chapter_num, _ = self.detect_chapter(text)
        if chapter_num is not None and not is_pre_section:
            return TextFormatting.HEADER

        # Enhanced centered text detection for pre-sections
        if is_pre_section and self.is_centered_text(text):
            # Check for main title indicators
            if text.isupper() or (text.istitle() and len(text.split()) <= 5):
                return TextFormatting.HEADER
            return TextFormatting.SUBHEADER

        # Check for headers
        if any(re.match(pattern, text) for pattern in self.header_patterns):
            return TextFormatting.HEADER

        # Check for list items
        if re.match(r'^\s*[-•*]\s+', text) or re.match(r'^\s*\d+\.\s+.+', text):
            return TextFormatting.LIST_ITEM

        # Check for code blocks
        if text.startswith('    ') or text.startswith('\t'):
            return TextFormatting.CODE

        # Check for quotes
        if text.startswith('>') or (text.startswith('"') and text.endswith('"')):
            return TextFormatting.QUOTE

        return TextFormatting.PARAGRAPH

    def process_text_block(self, text: str, is_pre_section: bool = False) -> List[FormattedText]:
        """Process a block of text and return formatted text segments."""
        formatted_texts = []
        current_format = None
        current_text = []

        try:
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    if current_text:
                        formatted_texts.append(
                            FormattedText(
                                text="\n".join(current_text),
                                format_type=current_format or TextFormatting.PARAGRAPH
                            )
                        )
                        current_text = []
                        current_format = None
                    continue

                format_type = self.detect_formatting(line, is_pre_section)

                # Always start a new block for headers and subheaders
                if format_type != current_format or format_type in [TextFormatting.HEADER, TextFormatting.SUBHEADER]:
                    if current_text:
                        formatted_texts.append(
                            FormattedText(
                                text="\n".join(current_text),
                                format_type=current_format or TextFormatting.PARAGRAPH
                            )
                        )
                        current_text = []
                    current_format = format_type

                current_text.append(line)

            if current_text:
                formatted_texts.append(
                    FormattedText(
                        text="\n".join(current_text),
                        format_type=current_format or TextFormatting.PARAGRAPH
                    )
                )

            return formatted_texts
        except Exception as e:
            logger.error(f"Error processing text block: {e}", exc_info=True)
            return []
