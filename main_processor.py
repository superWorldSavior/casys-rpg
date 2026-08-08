import asyncio
from pdf_processing.infrastructure.pdf_processor import MuPDFProcessor
from pdf_processing.infrastructure.pdf_repository import FileSystemPDFRepository
from pdf_processing.application.pdf_service import PDFService

def find_pdf_in_project():
    import os
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.pdf'):
                return os.path.join(root, file)
    return None

async def main():
    # Initialize components
    processor = MuPDFProcessor()
    repository = FileSystemPDFRepository()
    service = PDFService(processor, repository)

    # Find and process PDF
    pdf_path = find_pdf_in_project()
    if pdf_path:
        print(f'PDF found: {pdf_path}')
        try:
            processed_pdf = await service.process_pdf(pdf_path)
            print(f'PDF processed successfully. Sections and images stored in: sections/{processed_pdf.pdf_name}')
        except Exception as e:
            print(f'Error processing PDF: {e}')
    else:
        print('No PDF found in the project')

if __name__ == "__main__":
    asyncio.run(main())
