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
            sections = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
            
            # Verify pre-section chapters exist
            histoire_dir = os.path.join(self.output_dir, "test_book", "histoire")
            self.assertTrue(os.path.exists(histoire_dir))
            
            # Check for expected pre-section files and formatting
            expected_chapters = ["1.md", "2.md", "3.md", "4.md", "5.md"]
            for chapter in expected_chapters:
                chapter_path = os.path.join(histoire_dir, chapter)
                self.assertTrue(
                    os.path.exists(chapter_path),
                    f"Pre-section chapter {chapter} not found"
                )
                
                # Verify content formatting
                with open(chapter_path, 'r') as f:
                    content = f.read()
                    # Headers should use markdown formatting
                    self.assertTrue(
                        any(line.startswith('#') for line in content.split('\n')),
                        f"No proper header formatting found in {chapter}"
                    )

        asyncio.run(run_test())

    def test_chapter_formatting(self):
        """Test preservation of text formatting"""
        async def run_test():
            sections = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
            histoire_dir = os.path.join(self.output_dir, "test_book", "histoire")
            
            # Check title page formatting
            with open(os.path.join(histoire_dir, "1.md"), 'r') as f:
                content = f.read()
                self.assertIn("# THE DARK FORTRESS", content)
                self.assertIn("A Solo Adventure", content)
                # Section numbers should not appear as titles
                self.assertNotIn("# 1", content)

            # Check combat rules formatting
            with open(os.path.join(histoire_dir, "3.md"), 'r') as f:
                content = f.read()
                self.assertIn("# COMBAT RULES", content)
                self.assertIn("## Basic Combat", content)
                # List items should be properly formatted
                self.assertTrue(
                    any(line.strip().startswith('- ') or line.strip().startswith('* ') for line in content.split('\n')),
                    "List items not properly formatted"
                )

        asyncio.run(run_test())

    def test_numbered_section_extraction(self):
        """Test extraction of numbered sections with proper formatting"""
        async def run_test():
            sections = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
            sections_dir = os.path.join(self.output_dir, "test_book", "sections")
            
            # Check numbered sections
            for i in range(1, 4):
                section_file = os.path.join(sections_dir, f"{i}.md")
                self.assertTrue(
                    os.path.exists(section_file),
                    f"Numbered section {i} not found"
                )
                
                # Verify section content formatting
                with open(section_file, 'r') as f:
                    content = f.read()
                    # Section number should not appear as a title
                    self.assertNotIn(f"# {i}", content)
                    # Content should be properly formatted
                    self.assertTrue(
                        content.strip(),
                        f"Section {i} is empty"
                    )

        asyncio.run(run_test())

    def test_metadata_generation(self):
        """Test metadata file generation with enhanced properties"""
        async def run_test():
            sections = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
            metadata_dir = os.path.join(self.output_dir, "test_book", "metadata")
            
            # Check metadata files exist
            required_metadata = ["book.json", "sections.json", "progress.json"]
            for metadata_file in required_metadata:
                metadata_path = os.path.join(metadata_dir, metadata_file)
                self.assertTrue(
                    os.path.exists(metadata_path),
                    f"Metadata file {metadata_file} not found"
                )
            
            # Verify book.json content
            with open(os.path.join(metadata_dir, "book.json"), 'r') as f:
                book_metadata = json.load(f)
                self.assertEqual(book_metadata["title"], "test_book")
                self.assertGreater(book_metadata["total_sections"], 0)
                self.assertIn("sections", book_metadata)

            # Verify sections.json content
            with open(os.path.join(metadata_dir, "sections.json"), 'r') as f:
                sections_metadata = json.load(f)
                self.assertIsInstance(sections_metadata, list)
                self.assertGreater(len(sections_metadata), 0)
                # Check section structure
                for section in sections_metadata:
                    self.assertIn("section_number", section)
                    self.assertIn("file_path", section)
                    self.assertIn("pdf_name", section)
                    self.assertIn("page_number", section)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
