import os
import asyncio
import argparse
from pdf_processing.infrastructure.pdf_processor import MuPDFProcessor
from pdf_processing.infrastructure.pdf_repository import FileSystemPDFRepository
from pdf_processing.application.pdf_service import PDFService


def find_pdfs_in_project() -> list:
    """Search for all PDF files in the current project."""
    pdf_files = []
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files


async def process_single_pdf(service: PDFService, pdf_path: str):
    """Process a single PDF file."""
    try:
        print(f'Processing PDF: {pdf_path}')
        processed_pdf = await service.process_pdf(pdf_path)
        print(f'Successfully processed: {pdf_path}')
        print(
            f'Sections and images stored in: sections/{processed_pdf.pdf_name}'
        )
    except Exception as e:
        print(f'Error processing PDF {pdf_path}: {e}')


async def main():
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="PDF Processor Script")
    parser.add_argument('--pdf',
                        type=str,
                        help="Path to a specific PDF file to process")
    args = parser.parse_args()

    # Initialize components
    repository = FileSystemPDFRepository()
    processor = MuPDFProcessor(repository=repository)
    service = PDFService(processor, repository)

    if args.pdf:
        # Process a specific PDF provided via CLI
        if os.path.exists(args.pdf) and args.pdf.endswith('.pdf'):
            await process_single_pdf(service, args.pdf)
        else:
            print(f"Invalid PDF file: {args.pdf}")
    else:
        # Find and process all PDFs in the project
        pdf_files = find_pdfs_in_project()
        if not pdf_files:
            print("No PDF files found in the project.")
            return

        print(f"Found {len(pdf_files)} PDF(s):")
        for pdf in pdf_files:
            print(f"- {pdf}")

        for pdf_path in pdf_files:
            await process_single_pdf(service, pdf_path)


if __name__ == "__main__":
    asyncio.run(main())
