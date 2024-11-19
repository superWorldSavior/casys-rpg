import json
import re
import time
from typing import Tuple, Optional, Dict
import openai
from functools import lru_cache
import asyncio
from ..domain.entities import ProcessingError

class AIProcessor:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.last_api_call = 0
        self.min_delay = 1.0  # Minimum delay between API calls in seconds
        self._cache: Dict[str, Tuple[bool, Optional[str]]] = {}
        self.max_retries = 3
        self.retry_delay = 2

    def _get_cache_key(self, text: str) -> str:
        """Generate a cache key for the text"""
        # Use first 100 chars of cleaned text as cache key
        clean_text = re.sub(r'\s+', ' ', text.strip())
        return clean_text[:100]

    async def _make_api_call(self, text: str, attempt: int = 1) -> Tuple[bool, Optional[str]]:
        """Make an API call with rate limiting and error handling"""
        try:
            # Implement rate limiting
            current_time = time.time()
            time_since_last_call = current_time - self.last_api_call
            if time_since_last_call < self.min_delay:
                await asyncio.sleep(self.min_delay - time_since_last_call)

            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a text formatting analyzer. Given a text block, determine if it represents a chapter break and extract the chapter title if present. Respond in JSON format with 'is_chapter' (boolean) and 'title' (string or null)."
                }, {
                    "role": "user",
                    "content": f"Analyze this text block for chapter characteristics:\n{text}"
                }])

            self.last_api_call = time.time()
            result = re.sub(r'^```json|```$', '', response.choices[0].message.content.strip())
            result_json = json.loads(result)
            return result_json.get("is_chapter", False), result_json.get("title")

        except openai.RateLimitError:
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay * attempt)
                return await self._make_api_call(text, attempt + 1)
            raise ProcessingError("Rate limit exceeded after retries")

        except openai.APIError as e:
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay * attempt)
                return await self._make_api_call(text, attempt + 1)
            raise ProcessingError(f"OpenAI API error: {str(e)}")

        except json.JSONDecodeError:
            raise ProcessingError("Invalid response format from OpenAI API")

        except Exception as e:
            raise ProcessingError(f"Unexpected error: {str(e)}")

    async def detect_chapter_with_ai(self, text: str) -> Tuple[bool, Optional[str]]:
        """Use OpenAI to detect chapter breaks and determine titles with caching"""
        # Skip empty or very short text
        if not text or len(text.strip()) < 10:
            return False, None

        # Check cache first
        cache_key = self._get_cache_key(text)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Basic heuristics to avoid unnecessary API calls
        text_lower = text.strip().lower()
        if len(text.split()) > 50 or \
           any(word in text_lower for word in ['copyright', 'all rights reserved']):
            return False, None

        try:
            result = await self._make_api_call(text)
            # Cache the result
            self._cache[cache_key] = result
            return result
        except ProcessingError as e:
            # Log the error and return a safe default
            print(f"Error in chapter detection: {e}")
            return False, None
