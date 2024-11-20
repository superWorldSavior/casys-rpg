import json
import re
import traceback
import time
import base64
from typing import Tuple, Optional, List, Dict
import openai
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from ..domain.entities import FormattedText, TextFormatting, PDFImage

logger = logging.getLogger(__name__)

class AIProcessor:

    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.model_name = "gpt-4o-mini"  # Using GPT-4-mini model exclusively
        self.max_tokens = 1000
        self.temperature = 0.1

    def _prepare_image_data(self, image: PDFImage) -> Dict:
        """Prepare image data in the correct format for gpt-4o-mini"""
        try:
            with open(image.image_path, 'rb') as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
                return {
                    "type": "image",
                    "image_data": {
                        "url": f"data:image/png;base64,{image_data}",
                        "width": image.width,
                        "height": image.height
                    }
                }
        except Exception as e:
            logger.error(f"Error preparing image data: {e}")
            return None

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_page_with_chapters(
        self,
        page_text: str,
        page_num: int,
        images: Optional[List[PDFImage]] = None,
        current_chapter: Optional[Dict] = None
    ) -> Tuple[List[FormattedText], Optional[Dict], bool]:
        """Optimized multimodal chapter analysis using gpt-4o-mini"""
        try:
            logger.info(f"Starting multimodal analysis for page {page_num}")

            # Simplified system prompt focusing on natural chapter detection
            system_prompt = """You are a document analyzer that detects natural chapter boundaries and structures content.
Analyze the text and any images to identify chapter transitions and content structure.
Return a JSON response with:
{
  "chapter_status": "NEW|CONTINUE|END",
  "chapter_info": {"title": "string", "type": "string"},
  "blocks": [{"type": "header|subheader|paragraph|list", "text": "string"}]
}"""

            # Prepare minimal context with improved image handling
            messages = [{"role": "system", "content": system_prompt}]
            
            context = {
                "page_number": page_num,
                "current_chapter": current_chapter["title"] if current_chapter else None,
                "text": page_text[:500],  # Keep context concise
            }

            # Add image context if available
            if images:
                page_images = [img for img in images if img.page_number == page_num]
                image_data = []
                for img in page_images:
                    img_data = self._prepare_image_data(img)
                    if img_data:
                        image_data.append(img_data)
                if image_data:
                    context["images"] = image_data

            messages.append({
                "role": "user",
                "content": json.dumps(context)
            })

            logger.debug(f"Sending request to GPT-4-mini for page {page_num}")
            start_time = time.time()
            
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"})

            processing_time = time.time() - start_time
            logger.info(f"Analysis completed in {processing_time:.2f}s")

            # Parse and validate response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from AI model")

            result = json.loads(content)
            logger.debug(f"AI Response for page {page_num}: {result}")

            # Process blocks into formatted text
            formatted_blocks = []
            for block in result.get("blocks", []):
                format_type = {
                    'header': TextFormatting.HEADER,
                    'subheader': TextFormatting.SUBHEADER,
                    'paragraph': TextFormatting.PARAGRAPH,
                    'list': TextFormatting.LIST_ITEM
                }.get(block.get("type"), TextFormatting.PARAGRAPH)

                formatted_blocks.append(
                    FormattedText(
                        text=block.get("text", ""),
                        format_type=format_type,
                        metadata={
                            "type": block.get("type"),
                            "context": result.get("chapter_status")
                        }
                    ))

            # Update chapter info
            chapter_info = current_chapter
            if result.get("chapter_status") == "NEW":
                chapter_info = result.get("chapter_info", {})
                chapter_info["start_page"] = page_num
                logger.info(f"New chapter detected: {chapter_info.get('title')}")

            is_chapter_complete = result.get("chapter_status") == "END"
            if is_chapter_complete:
                logger.info(f"Chapter complete at page {page_num}")

            logger.info(
                f"Processed {len(formatted_blocks)} blocks for page {page_num}")
            return formatted_blocks, chapter_info, is_chapter_complete

        except Exception as e:
            logger.error(
                f"Error in multimodal analysis for page {page_num}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return [
                FormattedText(text=page_text,
                             format_type=TextFormatting.PARAGRAPH,
                             metadata={"error": str(e)})
            ], current_chapter, False
