from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf(filename="test_book.pdf"):
    # Use absolute path
    abs_path = os.path.abspath(filename)
    c = canvas.Canvas(abs_path, pagesize=letter)
    
    # Section 1
    c.drawString(100, 750, "1")
    c.drawString(100, 730, "This is section 1 content.")
    c.drawString(100, 710, "You can go to section 2 or 3.")
    
    c.showPage()
    
    # Section 2
    c.drawString(100, 750, "2")
    c.drawString(100, 730, "This is section 2 content.")
    c.drawString(100, 710, "You can go to section 1 or 3.")
    
    c.showPage()
    
    # Section 3
    c.drawString(100, 750, "3")
    c.drawString(100, 730, "This is section 3 content.")
    c.drawString(100, 710, "You can go to section 1 or 2.")
    
    c.save()
    return abs_path

if __name__ == "__main__":
    pdf_path = create_test_pdf()
    print(f"Test PDF created successfully at: {pdf_path}")
