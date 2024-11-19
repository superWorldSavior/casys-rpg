import unittest
import os
import json
import shutil
import asyncio
from pdf_processing.infrastructure.pdf_processor import MuPDFProcessor
from pdf_processing.domain.entities import Section, ProcessingStatus, FormattedText, TextFormatting

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = MuPDFProcessor()
        self.test_pdf_path = "test_book.pdf"
        self.output_dir = "test_sections"
        # Clean up test directory if it exists
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def tearDown(self):
        # Clean up after tests
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_pre_section_extraction(self):
        """Test extraction of pre-section content with enhanced formatting"""
        async def run_test():
            processed_pdf = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
            
            # Verify pre-section chapters exist
            histoire_dir = os.path.join(self.output_dir, "test_book", "histoire")
            self.assertTrue(os.path.exists(histoire_dir))
            
            # Verify metadata directory exists
            metadata_dir = os.path.join(self.output_dir, "test_book", "metadata")
            self.assertTrue(os.path.exists(metadata_dir))
            
            # Check for expected pre-section files
            pre_sections = [section for section in processed_pdf.sections if section.is_chapter]
            self.assertGreater(len(pre_sections), 0, "No pre-sections found")
            
            # Verify content formatting for each pre-section
            for section in pre_sections:
                self.assertTrue(
                    os.path.exists(section.file_path),
                    f"Pre-section file {section.file_path} not found"
                )
                
                with open(section.file_path, 'r') as f:
                    content = f.read()
                    # Headers should use markdown formatting
                    self.assertTrue(
                        any(line.startswith('#') for line in content.split('\n')),
                        f"No proper header formatting found in {section.file_path}"
                    )

        asyncio.run(run_test())

    def test_chapter_formatting(self):
        """Test preservation of text formatting"""
        async def run_test():
            processed_pdf = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
            sections = processed_pdf.sections
            
            # Verify sections exist
            self.assertGreater(len(sections), 0, "No sections found")
            
            # Check formatting for each section
            for section in sections:
                self.assertTrue(
                    os.path.exists(section.file_path),
                    f"Section file {section.file_path} not found"
                )
                
                with open(section.file_path, 'r') as f:
                    content = f.read()
                    # Content should not be empty
                    self.assertTrue(content.strip(), f"Section {section.number} is empty")
                    # Verify markdown formatting
                    if section.title:
                        self.assertIn(f"# {section.title}", content)

        asyncio.run(run_test())

    def test_numbered_section_extraction(self):
        """Test extraction of numbered sections with proper formatting"""
        async def run_test():
            processed_pdf = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
            numbered_sections = [s for s in processed_pdf.sections if not s.is_chapter]
            
            # Verify numbered sections exist
            self.assertGreater(len(numbered_sections), 0, "No numbered sections found")
            
            # Check each numbered section
            for section in numbered_sections:
                self.assertTrue(
                    os.path.exists(section.file_path),
                    f"Section file {section.file_path} not found"
                )
                
                with open(section.file_path, 'r') as f:
                    content = f.read()
                    # Content should be properly formatted
                    self.assertTrue(
                        content.strip(),
                        f"Section {section.number} is empty"
                    )

        asyncio.run(run_test())

    def test_metadata_generation(self):
        """Test metadata file generation with enhanced properties"""
        async def run_test():
            processed_pdf = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
            metadata_dir = os.path.join(self.output_dir, "test_book", "metadata")
            
            # Verify metadata directory exists
            self.assertTrue(os.path.exists(metadata_dir), "Metadata directory not found")
            
            # Check book.json exists and has correct content
            book_json_path = os.path.join(metadata_dir, "book.json")
            self.assertTrue(
                os.path.exists(book_json_path),
                "book.json not found"
            )
            
            with open(book_json_path, 'r') as f:
                metadata = json.load(f)
                # Verify required fields
                self.assertEqual(metadata["title"], "test_book")
                self.assertGreater(metadata["total_sections"], 0)
                self.assertIn("sections", metadata)
                self.assertIn("images", metadata)
                self.assertIn("progress", metadata)
                
                # Verify sections metadata
                for section in metadata["sections"]:
                    self.assertIn("number", section)
                    self.assertIn("page_number", section)
                    self.assertIn("file_path", section)
                    self.assertIn("is_chapter", section)
                    self.assertIn("chapter_number", section)
                    self.assertIn("formatting", section)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
