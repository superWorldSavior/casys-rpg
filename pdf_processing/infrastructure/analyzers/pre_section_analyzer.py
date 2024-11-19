from typing import List, Optional, Tuple
from ...domain.analyzers import PreSectionAnalyzer
from ...domain.entities import Section, FormattedText
from ..adapters.text_formatting_adapter import RegexTextFormatDetector
from ..adapters.openai_adapter import OpenAIAnalyzer
from ..logging_config import StructuredLogger

class MuPDFPreSectionAnalyzer(PreSectionAnalyzer):
    def __init__(self):
        self.text_detector = RegexTextFormatDetector()
        self.ai_analyzer = OpenAIAnalyzer()
        self.logger = StructuredLogger("PreSectionAnalyzer")

    async def is_pre_section_content(self, text: str) -> bool:
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            chapter_num, _ = await self.text_detector.detect_chapter(line)
            if chapter_num is not None:
                return False
        return True

    async def analyze_pre_sections(self, text: str) -> List[Section]:
        sections = []
        try:
            formatted_blocks = await self._process_text_block(text, is_pre_section=True)
            
            # Use AI to detect chapter breaks
            current_chapter = []
            chapter_count = 0
            
            for block in formatted_blocks:
                is_chapter, title = await self.ai_analyzer.analyze_chapter_break(block.text)
                
                if is_chapter and current_chapter:
                    # Save current chapter
                    chapter_count += 1
                    section = Section(
                        number=chapter_count,
                        content="\n".join(text.text for text in current_chapter),
                        page_number=1,  # Pre-sections are typically at the start
                        file_path="",   # Will be set by repository
                        pdf_name="",    # Will be set by processor
                        title=title,
                        formatted_content=current_chapter,
                        is_chapter=True,
                        chapter_number=chapter_count
                    )
                    sections.append(section)
                    current_chapter = []
                
                current_chapter.append(block)
            
            # Save last chapter if exists
            if current_chapter:
                chapter_count += 1
                section = Section(
                    number=chapter_count,
                    content="\n".join(text.text for text in current_chapter),
                    page_number=1,
                    file_path="",
                    pdf_name="",
                    title=None,
                    formatted_content=current_chapter,
                    is_chapter=True,
                    chapter_number=chapter_count
                )
                sections.append(section)
                
        except Exception as e:
            self.logger.error("Error analyzing pre-sections", e)
            raise
            
        return sections

    async def _process_text_block(self, text: str, is_pre_section: bool = False) -> List[FormattedText]:
        formatted_texts = []
        lines = text.splitlines()
        current_block = []
        current_format = None

        for line in lines:
            line = line.strip()
            if not line:
                if current_block:
                    formatted_text = await self.text_detector.detect_formatting(
                        "\n".join(current_block),
                        is_pre_section=is_pre_section
                    )
                    formatted_texts.append(formatted_text)
                    current_block = []
                    current_format = None
                continue

            # Get format for current line
            formatted_line = await self.text_detector.detect_formatting(
                line,
                is_pre_section=is_pre_section
            )

            if (formatted_line.format_type != current_format or 
                formatted_line.format_type in [TextFormatting.HEADER, TextFormatting.SUBHEADER]):
                if current_block:
                    formatted_text = await self.text_detector.detect_formatting(
                        "\n".join(current_block),
                        is_pre_section=is_pre_section
                    )
                    formatted_texts.append(formatted_text)
                    current_block = []
                current_format = formatted_line.format_type

            current_block.append(line)

        # Add remaining block
        if current_block:
            formatted_text = await self.text_detector.detect_formatting(
                "\n".join(current_block),
                is_pre_section=is_pre_section
            )
            formatted_texts.append(formatted_text)

        return formatted_texts
