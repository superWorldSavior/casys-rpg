from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

def create_test_pdf(filename="test_book.pdf"):
    # Use absolute path
    abs_path = os.path.abspath(filename)
    doc = SimpleDocTemplate(abs_path, pagesize=letter)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    chapter_style = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading3'],
        fontSize=16,
        spaceAfter=15,
        spaceBefore=15,
        alignment=TA_LEFT
    )
    
    normal_style = styles['Normal']
    centered_style = ParagraphStyle(
        'Centered',
        parent=styles['Normal'],
        alignment=TA_CENTER
    )
    
    # Create content
    story = []
    
    # Front matter
    story.append(Paragraph("The Test Book", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Introduction
    story.append(Paragraph("Introduction", chapter_style))
    story.append(Paragraph("""
        This is a test book created to validate the PDF processor's ability to handle
        various text formats and section types. The content includes pre-section chapters,
        numbered sections, and different formatting styles.
    """, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Preface
    story.append(Paragraph("Preface", chapter_style))
    story.append(Paragraph("""
        The following content demonstrates:
        • Different text alignments
        • Formatted lists
        • Chapter numbering
        • Section breaks
    """, normal_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Game Rules
    story.append(Paragraph("Game Rules", chapter_style))
    
    # Game Overview
    story.append(Paragraph("Game Overview", section_style))
    story.append(Paragraph("""
        Welcome to the adventure! Before you begin your journey, familiarize yourself
        with these essential game rules and mechanics.
    """, normal_style))
    
    # Character Creation
    story.append(Paragraph("Character Creation", section_style))
    story.append(Paragraph("""
        To create your character:
        • Roll 2d6 for Strength (minimum 7)
        • Roll 2d6 for Dexterity (minimum 7)
        • Roll 2d6 for Intelligence (minimum 7)
    """, normal_style))
    
    # Combat Rules
    story.append(Paragraph("Combat Rules", section_style))
    story.append(Paragraph("""
        Combat follows these steps:
        1. Roll for initiative
        2. Choose your action
        3. Roll attack dice
        4. Calculate damage
    """, normal_style))
    
    # Special Rules
    story.append(Paragraph("Special Rules", centered_style))
    story.append(Paragraph("""
        Critical hits occur on natural 20
        Fumbles occur on natural 1
    """, centered_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Numbered Chapters
    for i in range(1, 4):
        story.append(Paragraph(f"{i}", chapter_style))
        story.append(Paragraph(f"This is section {i} content.", normal_style))
        
        # Add some formatted content
        story.append(Paragraph(f"""
            This section demonstrates various formatting options:
            • Bullet point 1
            • Bullet point 2
            1. Numbered item
            2. Another numbered item
        """, normal_style))
        
        # Add centered text
        story.append(Paragraph(f"Section {i} - Centered Text Example", centered_style))
        
        story.append(Paragraph(f"You can go to other sections.", normal_style))
        story.append(Spacer(1, 0.5*inch))
    
    # Build the PDF
    doc.build(story)
    return abs_path

if __name__ == "__main__":
    pdf_path = create_test_pdf()
    print(f"Test PDF created successfully at: {pdf_path}")
