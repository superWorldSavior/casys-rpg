from typing import List, Optional, Tuple
from ...domain.analyzers import SectionAnalyzer
from ...domain.entities import Section, FormattedText, TextFormatting
from ..adapters.text_formatting_adapter import RegexTextFormatDetector
from ..adapters.openai_adapter import OpenAIAnalyzer
from ..logging_config import StructuredLogger

class MuPDFSectionAnalyzer(SectionAnalyzer):
    def __init__(self):
        self.text_detector = RegexTextFormatDetector()
        self.ai_analyzer = OpenAIAnalyzer()
        self.logger = StructuredLogger("SectionAnalyzer")

    async def analyze_sections(self, text: str, page_number: int) -> List[Section]:
        sections = []
        current_section = None
        current_text = []
        
        try:
            lines = text.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                chapter_num, title = await self.text_detector.detect_chapter(line)
                if chapter_num is not None:
                    # Save previous section if exists
                    if current_section is not None and current_text:
                        section = await self._create_section(
                            current_section,
                            current_text,
                            page_number
                        )
                        sections.append(section)
                        current_text = []

                    # Start new section
                    current_section = chapter_num
                else:
                    current_text.append(line)

            # Save last section if exists
            if current_section is not None and current_text:
                section = await self._create_section(
                    current_section,
                    current_text,
                    page_number
                )
                sections.append(section)

        except Exception as e:
            self.logger.error(f"Error analyzing sections on page {page_number}", e)
            raise

        return sections

    async def _create_section(self, section_number: int, text_lines: List[str], page_number: int) -> Section:
        content = "\n".join(text_lines)
        formatted_content = await self._format_content(content)
        return Section(
            number=section_number,
            content=content,
            page_number=page_number,
            formatted_content=formatted_content,
            is_chapter=True,
            chapter_number=section_number,
            file_path="",  # Will be set by repository
            pdf_name="",   # Will be set by processor
            title=None     # Will be determined by AI analyzer if needed
        )

    async def _format_content(self, content: str) -> List[FormattedText]:
        formatted_texts = []
        blocks = content.split("\n\n")
        
        for block in blocks:
            if not block.strip():
                continue
            formatted_text = await self.text_detector.detect_formatting(block)
            formatted_texts.append(formatted_text)
            
        return formatted_texts
