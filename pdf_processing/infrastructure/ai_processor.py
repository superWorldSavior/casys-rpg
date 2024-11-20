import json
import re
import asyncio
from typing import Tuple, Optional, List, Dict
import openai
import logging
from ..domain.entities import FormattedText, TextFormatting

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.model_name = "gpt-4-mini"
        self.max_concurrent = 5
        # Updated patterns for better detection
        self.chapter_pattern = r'^\s*(?:Chapter|CHAPTER)?\s*(\d+)(?:\s*[-:.]?\s*(.+))?$|^\s*(\d+)\s*$'
        self.section_pattern = r'^\s*(\d+)\s*[-.]?\s*(.+)?$'
        self.numbered_section_pattern = r'^\s*(\d+)\s*\.\s*(.+)?$'
        self.title_pattern = r'^[A-Z][A-Z\s]+(?:\s*[-:]\s*.+)?$'
        self.rules_pattern = r'^(?:\s*#\s*)?(?:COMBAT\s+RULES|Combat\s+Rules)\s*$'
        self.list_item_pattern = r'^\s*[-•*]\s+(.+)$'

    async def process_pages_concurrently(self, pages: List[Dict[str, any]]) -> List[List[FormattedText]]:
        """Process multiple pages concurrently using asyncio.gather()"""
        try:
            tasks = [self.analyze_page_with_chapters(page['text'], page['num']) for page in pages]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            results = []
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing page {pages[i]['num']}: {str(result)}")
                    results.append([FormattedText(
                        text=pages[i]['text'],
                        format_type=TextFormatting.PARAGRAPH,
                        metadata={"error": str(result), "page_number": pages[i]['num']}
                    )])
                else:
                    results.append(result)

            return results
        except Exception as e:
            logger.error(f"Error in concurrent page processing: {e}")
            raise

    async def analyze_page_with_chapters(self, text: str, page_num: int) -> List[FormattedText]:
        """Analyze page content for chapters, numbered sections, and rules."""
        try:
            blocks = []
            lines = text.split('\n')
            current_block = []
            current_context = None
            in_chapter = False
            chapter_num = None
            last_was_title = False

            for line in lines:
                line = line.strip()
                if not line:
                    if current_block:
                        blocks.append(FormattedText(
                            text='\n'.join(current_block),
                            format_type=TextFormatting.PARAGRAPH,
                            metadata={
                                "page_number": page_num,
                                "context": current_context,
                                "chapter_number": chapter_num if in_chapter else None
                            }
                        ))
                        current_block = []
                    continue

                # Check for COMBAT RULES section first
                if re.match(self.rules_pattern, line, re.IGNORECASE):
                    if current_block:
                        blocks.append(FormattedText(
                            text='\n'.join(current_block),
                            format_type=TextFormatting.PARAGRAPH,
                            metadata={"page_number": page_num, "context": current_context}
                        ))
                        current_block = []

                    # Always format as uppercase and ensure header prefix
                    blocks.append(FormattedText(
                        text="COMBAT RULES",
                        format_type=TextFormatting.HEADER,
                        metadata={
                            "page_number": page_num,
                            "context": "rules",
                            "is_rules_section": True,
                            "should_prefix_header": True
                        }
                    ))
                    current_context = "rules"
                    in_chapter = False
                    continue

                # Check for chapter headers
                chapter_match = re.match(self.chapter_pattern, line)
                if chapter_match:
                    if current_block:
                        blocks.append(FormattedText(
                            text='\n'.join(current_block),
                            format_type=TextFormatting.PARAGRAPH,
                            metadata={"page_number": page_num, "context": current_context}
                        ))
                        current_block = []

                    chapter_num = int(chapter_match.group(1) or chapter_match.group(3))
                    chapter_title = chapter_match.group(2)
                    
                    if chapter_title:
                        blocks.append(FormattedText(
                            text=chapter_title.strip().upper(),  # Ensure uppercase for chapter titles
                            format_type=TextFormatting.HEADER,
                            metadata={
                                "is_chapter": True,
                                "chapter_number": chapter_num,
                                "page_number": page_num,
                                "context": "chapter",
                                "should_prefix_header": True
                            }
                        ))
                    in_chapter = True
                    current_context = "chapter"
                    continue

                # Check for numbered sections
                numbered_section_match = re.match(self.numbered_section_pattern, line)
                if numbered_section_match:
                    if current_block:
                        blocks.append(FormattedText(
                            text='\n'.join(current_block),
                            format_type=TextFormatting.PARAGRAPH,
                            metadata={"page_number": page_num, "context": current_context}
                        ))
                        current_block = []

                    section_num = int(numbered_section_match.group(1))
                    section_title = numbered_section_match.group(2)
                    
                    if section_title:
                        blocks.append(FormattedText(
                            text=section_title.strip(),
                            format_type=TextFormatting.HEADER,
                            metadata={
                                "is_numbered_section": True,
                                "section_number": section_num,
                                "page_number": page_num,
                                "context": "numbered_section",
                                "should_prefix_header": True
                            }
                        ))
                    current_context = "numbered_section"
                    continue

                # Check for list items
                list_match = re.match(self.list_item_pattern, line)
                if list_match:
                    if current_block:
                        blocks.append(FormattedText(
                            text='\n'.join(current_block),
                            format_type=TextFormatting.PARAGRAPH,
                            metadata={"page_number": page_num, "context": current_context}
                        ))
                        current_block = []
                    
                    blocks.append(FormattedText(
                        text=list_match.group(1),
                        format_type=TextFormatting.LIST_ITEM,
                        metadata={
                            "page_number": page_num,
                            "context": current_context,
                            "indentation_level": 0
                        }
                    ))
                    continue

                # Check for subheaders in rules context
                if current_context == "rules" and (
                    line.istitle() or 
                    re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', line)
                ):
                    if current_block:
                        blocks.append(FormattedText(
                            text='\n'.join(current_block),
                            format_type=TextFormatting.PARAGRAPH,
                            metadata={"page_number": page_num, "context": current_context}
                        ))
                        current_block = []

                    blocks.append(FormattedText(
                        text=line.title(),  # Ensure proper title case
                        format_type=TextFormatting.SUBHEADER,
                        metadata={
                            "page_number": page_num,
                            "context": "rules",
                            "should_prefix_header": True
                        }
                    ))
                    continue

                # Check for all-caps titles
                if not in_chapter and re.match(self.title_pattern, line):
                    if current_block:
                        blocks.append(FormattedText(
                            text='\n'.join(current_block),
                            format_type=TextFormatting.PARAGRAPH,
                            metadata={"page_number": page_num, "context": current_context}
                        ))
                        current_block = []
                    
                    blocks.append(FormattedText(
                        text=line.upper(),  # Ensure uppercase for titles
                        format_type=TextFormatting.HEADER,
                        metadata={
                            "page_number": page_num,
                            "context": "title",
                            "is_chapter": True,
                            "should_prefix_header": True
                        }
                    ))
                    last_was_title = True
                    current_context = "title"
                    continue

                # Handle subtitles after main title
                if last_was_title and line.istitle():
                    blocks.append(FormattedText(
                        text=line,
                        format_type=TextFormatting.SUBHEADER,
                        metadata={
                            "page_number": page_num,
                            "context": "title",
                            "should_prefix_header": False
                        }
                    ))
                    continue

                # Regular text handling
                if line:
                    current_block.append(line)
                last_was_title = False

            # Add any remaining text
            if current_block:
                blocks.append(FormattedText(
                    text='\n'.join(current_block),
                    format_type=TextFormatting.PARAGRAPH,
                    metadata={
                        "page_number": page_num,
                        "context": current_context,
                        "chapter_number": chapter_num if in_chapter else None
                    }
                ))

            return blocks if blocks else [FormattedText(
                text=text,
                format_type=TextFormatting.PARAGRAPH,
                metadata={"page_number": page_num}
            )]

        except Exception as e:
            logger.error(f"Error analyzing page {page_num}: {e}")
            return [FormattedText(
                text=text,
                format_type=TextFormatting.PARAGRAPH,
                metadata={"error": str(e), "page_number": page_num}
            )]

    async def detect_chapter_with_ai(self, text: str) -> Tuple[bool, Optional[str]]:
        """Use OpenAI to detect chapter breaks and determine titles."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": "You are a text formatting analyzer. Given a text block, determine if it represents a chapter break and extract the chapter title if present. Respond in JSON format with 'is_chapter' (boolean) and 'title' (string or null)."
                }, {
                    "role": "user",
                    "content": f"Analyze this text block for chapter characteristics:\n{text}"
                }],
                temperature=0.3
            )

            raw_content = response.choices[0].message.content.strip()
            logger.debug(f"Raw response for chapter detection: {raw_content}")

            if not raw_content.startswith("{"):
                raise ValueError(f"Unexpected chapter detection response: {raw_content}")

            result_json = json.loads(raw_content)
            return result_json.get("is_chapter", False), result_json.get("title")
        except Exception as e:
            logger.error(f"Error detecting chapter with AI: {e}")
            return False, None
