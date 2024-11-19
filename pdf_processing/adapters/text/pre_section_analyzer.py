from typing import List, Optional, Dict, Tuple
from ...domain.entities import Section, FormattedText, TextFormatting
from ...domain.analyzers import PreSectionAnalyzer
from ...domain.ports import DirectoryManager
from ...infrastructure.logging_config import StructuredLogger

class MuPDFPreSectionAnalyzer(PreSectionAnalyzer):
    def __init__(self, directory_manager: DirectoryManager):
        self.logger = StructuredLogger("PreSectionAnalyzer")
        self.directory_manager = directory_manager

    async def analyze_pre_sections(self, text: str, pdf_name: str, base_output_dir: str) -> List[Section]:
        """Analyze and extract pre-sections from text content"""
        try:
            # Ensure histoire directory exists
            histoire_dir = await self.directory_manager.get_histoire_directory(
                base_output_dir,
                pdf_name
            )
            
            formatted_blocks = await self._process_text_block(text, is_pre_section=True)
            sections = []
            current_chapter = []
            chapter_count = 0
            current_title = None

            for block in formatted_blocks:
                if block.format_type in [TextFormatting.HEADER, TextFormatting.SUBHEADER]:
                    if current_chapter:
                        chapter_count += 1
                        # Create the content with markdown formatting
                        formatted_content = []
                        if current_title:
                            formatted_content.append(f"# {current_title}\n")
                        formatted_content.extend(self._format_block_to_markdown(block) for block in current_chapter)
                        
                        sections.append(
                            Section(
                                number=chapter_count,
                                content="\n".join(formatted_content),
                                page_number=1,  # Pre-sections are always at the start
                                file_path=f"{histoire_dir}/chapter_{chapter_count}.txt",
                                pdf_name=pdf_name,
                                title=current_title,
                                formatted_content=current_chapter,
                                is_chapter=True,
                                chapter_number=chapter_count
                            )
                        )
                        current_chapter = []
                    current_title = block.text
                current_chapter.append(block)

            # Add final chapter if exists
            if current_chapter:
                chapter_count += 1
                # Create the content with markdown formatting
                formatted_content = []
                if current_title:
                    formatted_content.append(f"# {current_title}\n")
                formatted_content.extend(self._format_block_to_markdown(block) for block in current_chapter)
                
                sections.append(
                    Section(
                        number=chapter_count,
                        content="\n".join(formatted_content),
                        page_number=1,
                        file_path=f"{histoire_dir}/chapter_{chapter_count}.txt",
                        pdf_name=pdf_name,
                        title=current_title,
                        formatted_content=current_chapter,
                        is_chapter=True,
                        chapter_number=chapter_count
                    )
                )

            return sections
        except Exception as e:
            self.logger.error("Error analyzing pre-sections", e)
            raise

    def _format_block_to_markdown(self, block: FormattedText) -> str:
        """Convert a formatted text block to markdown format"""
        if block.format_type == TextFormatting.HEADER:
            return f"# {block.text}\n"
        elif block.format_type == TextFormatting.SUBHEADER:
            return f"## {block.text}\n"
        elif block.format_type == TextFormatting.LIST_ITEM:
            return f"- {block.text}"
        elif block.format_type == TextFormatting.CODE:
            return f"```\n{block.text}\n```"
        elif block.format_type == TextFormatting.QUOTE:
            return f"> {block.text}"
        else:
            return block.text

    async def is_pre_section_content(self, text: str) -> bool:
        """Determine if the given text is pre-section content"""
        try:
            lines = text.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Check for standalone section number indicating main content
                if line.isdigit() and len(line) <= 3:
                    return False
            return True
        except Exception as e:
            self.logger.error("Error checking pre-section content", e)
            return False

    async def _process_text_block(self, text: str, is_pre_section: bool = False) -> List[FormattedText]:
        """Process a block of text and return formatted text segments"""
        formatted_texts = []
        lines = text.splitlines()
        current_block = []
        current_format = None

        for line in lines:
            line = line.strip()
            if not line:
                if current_block:
                    format_type = self._detect_format_type("\n".join(current_block))
                    formatted_texts.append(
                        FormattedText(
                            text="\n".join(current_block),
                            format_type=format_type
                        )
                    )
                    current_block = []
                    current_format = None
                continue

            # Detect format for current line
            line_format = self._detect_format_type(line)

            # Start new block if format changes or if it's a header/subheader
            if (line_format != current_format or 
                line_format in [TextFormatting.HEADER, TextFormatting.SUBHEADER]):
                if current_block:
                    format_type = self._detect_format_type("\n".join(current_block))
                    formatted_texts.append(
                        FormattedText(
                            text="\n".join(current_block),
                            format_type=format_type
                        )
                    )
                    current_block = []
                current_format = line_format

            current_block.append(line)

        # Add remaining block
        if current_block:
            format_type = self._detect_format_type("\n".join(current_block))
            formatted_texts.append(
                FormattedText(
                    text="\n".join(current_block),
                    format_type=format_type
                )
            )

        return formatted_texts

    def _detect_format_type(self, text: str) -> TextFormatting:
        """Detect the formatting type of a text block"""
        text = text.strip()
        
        # Check for headers
        if text.isupper() and len(text.split()) <= 5:
            return TextFormatting.HEADER
        
        # Check for subheaders
        if text.istitle() and len(text.split()) <= 7:
            return TextFormatting.SUBHEADER
        
        # Check for list items
        if text.startswith(('- ', '• ', '* ')):
            return TextFormatting.LIST_ITEM
        
        # Check for code blocks
        if text.startswith(('```', '    ')):
            return TextFormatting.CODE
        
        # Check for quotes
        if text.startswith('>'):
            return TextFormatting.QUOTE
        
        # Default to paragraph
        return TextFormatting.PARAGRAPH
