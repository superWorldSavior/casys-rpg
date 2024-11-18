import unittest
import os
import json
import shutil
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

    async def test_pre_section_extraction(self):
        """Test extraction of pre-section content"""
        sections = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
        
        # Verify pre-section chapters exist
        histoire_dir = os.path.join(self.output_dir, "test_book", "histoire")
        self.assertTrue(os.path.exists(histoire_dir))
        
        # Check for expected pre-section files
        expected_chapters = ["1.md", "2.md", "3.md", "4.md", "5.md"]
        for chapter in expected_chapters:
            self.assertTrue(
                os.path.exists(os.path.join(histoire_dir, chapter)),
                f"Pre-section chapter {chapter} not found"
            )

    async def test_chapter_formatting(self):
        """Test preservation of text formatting"""
        sections = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
        histoire_dir = os.path.join(self.output_dir, "test_book", "histoire")
        
        # Check title page formatting
        with open(os.path.join(histoire_dir, "1.md"), 'r') as f:
            content = f.read()
            self.assertIn("# THE DARK FORTRESS", content)
            self.assertIn("A Solo Adventure", content)

        # Check combat rules formatting
        with open(os.path.join(histoire_dir, "3.md"), 'r') as f:
            content = f.read()
            self.assertIn("# COMBAT RULES", content)
            self.assertIn("## Basic Combat", content)

    async def test_numbered_section_extraction(self):
        """Test extraction of numbered sections"""
        sections = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
        sections_dir = os.path.join(self.output_dir, "test_book", "sections")
        
        # Check numbered sections
        for i in range(1, 4):
            section_file = os.path.join(sections_dir, f"{i}.md")
            self.assertTrue(
                os.path.exists(section_file),
                f"Numbered section {i} not found"
            )
            
            # Verify section content
            with open(section_file, 'r') as f:
                content = f.read()
                self.assertIn(str(i), content)

    async def test_metadata_generation(self):
        """Test metadata file generation"""
        sections = await self.processor.extract_sections(self.test_pdf_path, self.output_dir)
        metadata_dir = os.path.join(self.output_dir, "test_book", "metadata")
        
        # Check metadata files exist
        required_metadata = ["book.json", "sections.json", "progress.json"]
        for metadata_file in required_metadata:
            self.assertTrue(
                os.path.exists(os.path.join(metadata_dir, metadata_file)),
                f"Metadata file {metadata_file} not found"
            )
        
        # Verify book.json content
        with open(os.path.join(metadata_dir, "book.json"), 'r') as f:
            book_metadata = json.load(f)
            self.assertEqual(book_metadata["title"], "test_book")
            self.assertGreater(book_metadata["total_sections"], 0)

        # Verify sections.json content
        with open(os.path.join(metadata_dir, "sections.json"), 'r') as f:
            sections_metadata = json.load(f)
            self.assertIsInstance(sections_metadata, list)
            self.assertGreater(len(sections_metadata), 0)

if __name__ == '__main__':
    unittest.main()
