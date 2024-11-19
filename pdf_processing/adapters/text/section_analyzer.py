from typing import List, Optional, Dict, Tuple
from ...domain.entities import Section, FormattedText, TextFormatting
from ...domain.analyzers import SectionAnalyzer
from ...domain.ports import DirectoryManager
from ...infrastructure.logging_config import StructuredLogger

class MuPDFSectionAnalyzer(SectionAnalyzer):
    def __init__(self, directory_manager: DirectoryManager):
        self.logger = StructuredLogger("SectionAnalyzer")
        self.directory_manager = directory_manager

    async def analyze_sections(self, text: str, page_number: int, pdf_name: str, base_output_dir: str) -> List[Section]:
        """Analyze and extract sections from text content"""
        try:
            # Ensure sections directory exists
            sections_dir = await self.directory_manager.get_section_directory(
                base_output_dir,
                pdf_name
            )
            
            sections = []
            lines = text.splitlines()
            current_section = None
            current_text = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                section_number = self._detect_section_number(line)
                if section_number is not None:
                    # Save previous section if exists
                    if current_section is not None and current_text:
                        sections.append(await self._create_section(
                            current_section,
                            current_text,
                            page_number,
                            pdf_name,
                            sections_dir
                        ))
                        current_text = []

                    # Start new section
                    current_section = section_number
                else:
                    current_text.append(line)

            # Save last section if exists
            if current_section is not None and current_text:
                sections.append(await self._create_section(
                    current_section,
                    current_text,
                    page_number,
                    pdf_name,
                    sections_dir
                ))

            return sections

        except Exception as e:
            self.logger.error(f"Error analyzing sections on page {page_number}", e)
            raise

    def _detect_section_number(self, text: str) -> Optional[int]:
        """Detect if a line contains a standalone section number"""
        text = text.strip()
        try:
            if text.isdigit() and len(text) <= 3:
                return int(text)
        except ValueError:
            pass
        return None

    async def _create_section(self, section_number: int, text_lines: List[str], page_number: int, pdf_name: str, sections_dir: str) -> Section:
        """Create a section object from the extracted content"""
        content = "\n".join(text_lines)
        formatted_content = self._format_content(content)
        file_path = os.path.join(sections_dir, f"section_{section_number}.txt")

        return Section(
            number=section_number,
            content=content,
            page_number=page_number,
            file_path=file_path,
            pdf_name=pdf_name,
            formatted_content=formatted_content,
            is_chapter=False,
            chapter_number=section_number
        )

    def _format_content(self, content: str) -> List[FormattedText]:
        """Format the content into structured blocks"""
        formatted_blocks = []
        paragraphs = content.split("\n\n")

        for paragraph in paragraphs:
            if not paragraph.strip():
                continue

            format_type = self._detect_format_type(paragraph)
            formatted_blocks.append(
                FormattedText(
                    text=paragraph.strip(),
                    format_type=format_type
                )
            )

        return formatted_blocks

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
