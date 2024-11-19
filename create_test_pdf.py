from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

def centered_text(c, text, y, font='Helvetica-Bold', size=16):
    c.setFont(font, size)
    text_width = c.stringWidth(text, font, size)
    x = (letter[0] - text_width) / 2
    c.drawString(x, y, text)

def create_test_pdf(filename="test_book.pdf"):
    # Use absolute path
    abs_path = os.path.abspath(filename)
    c = canvas.Canvas(abs_path, pagesize=letter)
    width, height = letter

    # Title Page
    centered_text(c, "THE DARK FORTRESS", height - 200, size=24)
    centered_text(c, "A Solo Adventure", height - 250, 'Helvetica', 18)
    centered_text(c, "By", height - 300, 'Helvetica', 14)
    centered_text(c, "John Developer", height - 330, 'Helvetica-Bold', 16)
    c.showPage()

    # Introduction Chapter
    centered_text(c, "INTRODUCTION", height - 100, size=20)
    c.setFont('Helvetica', 12)
    intro_text = """
    Welcome to The Dark Fortress, a solo adventure where YOUR choices determine the story's outcome. 
    Before beginning your journey, read the following sections carefully to understand the rules and 
    mechanics that will guide you through this perilous quest.
    """
    y = height - 150
    for line in intro_text.split('\n'):
        line = line.strip()
        if line:
            c.drawString(100, y, line)
            y -= 20
    c.showPage()

    # Combat Rules Chapter
    centered_text(c, "COMBAT RULES", height - 100, size=20)
    y = height - 150
    c.setFont('Helvetica-Bold', 14)
    c.drawString(100, y, "Basic Combat")
    y -= 30

    c.setFont('Helvetica', 12)
    combat_text = """
    Combat in The Dark Fortress follows these simple steps:

    1. Roll two dice and add your SKILL score
    2. Roll two dice and add the enemy's SKILL score
    3. The higher total wins that round
    4. The loser loses 2 STAMINA points
    """
    for line in combat_text.split('\n'):
        line = line.strip()
        if line:
            c.drawString(100, y, line)
            y -= 20
    c.showPage()

    # Game Rules Chapter
    centered_text(c, "GAME RULES", height - 100, size=20)
    y = height - 150
    c.setFont('Helvetica-Bold', 14)
    c.drawString(100, y, "Character Creation")
    y -= 30

    c.setFont('Helvetica', 12)
    rules_text = """
    To create your character, you'll need to determine three key attributes:

    SKILL - Roll one die and add 6
    STAMINA - Roll two dice and add 12
    LUCK - Roll one die and add 6

    These scores represent your initial and maximum attribute scores.
    """
    for line in rules_text.split('\n'):
        line = line.strip()
        if line:
            c.drawString(100, y, line)
            y -= 20
    c.showPage()

    # Equipment List
    centered_text(c, "EQUIPMENT", height - 100, size=20)
    y = height - 150
    c.setFont('Helvetica-Bold', 14)
    c.drawString(100, y, "Starting Items")
    y -= 30

    equipment_list = [
        "• Sword (SKILL +2)",
        "• Leather Armor (reduces damage by 1)",
        "• Backpack (holds up to 8 items)",
        "• Lantern (provides light in dark areas)",
        "• 10 Gold Pieces",
        "• 2 Provisions (restore 4 STAMINA each)"
    ]

    c.setFont('Helvetica', 12)
    for item in equipment_list:
        c.drawString(100, y, item)
        y -= 20
    c.showPage()

    # Add blank page for spacing
    c.showPage()

    # Numbered Sections with centered numbers
    sections = [
        {
            "number": "1",
            "content": [
                "The dark fortress looms before you, its ancient stones casting long shadows",
                "in the dying light. You can:",
                "• Enter through the main gate (turn to 2)",
                "• Search for a side entrance (turn to 3)"
            ]
        },
        {
            "number": "2",
            "content": [
                "The heavy iron gates creak as you push them open.",
                "You find yourself in a torch-lit courtyard. Turn to 3."
            ]
        },
        {
            "number": "3",
            "content": [
                "A guard spots you! Prepare for combat.",
                "GUARD: SKILL 7  STAMINA 6",
                "If you win, turn to 2. If you lose, your adventure ends here."
            ]
        }
    ]

    for section in sections:
        # Center the section number
        centered_text(c, section["number"], height - 50, font='Helvetica-Bold', size=16)

        # Display section content
        y = height - 80
        c.setFont('Helvetica', 12)
        for line in section["content"]:
            line = line.strip()
            if line.startswith("•"):
                c.drawString(120, y, line)
            else:
                c.drawString(100, y, line)
            y -= 20
        c.showPage()

    c.save()
    return abs_path

if __name__ == "__main__":
    pdf_path = create_test_pdf()
    print(f"Test PDF created successfully at: {pdf_path}")
