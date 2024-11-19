import asyncio
import os
from pdf_processing.infrastructure.pdf_processor import MuPDFProcessor
from pdf_processing.infrastructure.pdf_repository import FileSystemPDFRepository
from pdf_processing.infrastructure.adapters.openai_adapter import OpenAIAnalyzer
from pdf_processing.infrastructure.adapters.text_formatting_adapter import RegexTextFormatDetector
from pdf_processing.application.pdf_service import PDFService
from pdf_processing.infrastructure.logging_config import StructuredLogger

logger = StructuredLogger("MainProcessor")

def find_pdf_in_project():
    """Find the first PDF file in the project directory"""
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.pdf'):
                return os.path.join(root, file)
    return None

async def main():
    try:
        # Initialize components
        logger.info("Initializing PDF processing components")
        processor = MuPDFProcessor()
        repository = FileSystemPDFRepository()
        ai_analyzer = OpenAIAnalyzer()
        text_detector = RegexTextFormatDetector()
        
        service = PDFService(
            processor=processor,
            repository=repository,
            ai_analyzer=ai_analyzer,
            text_detector=text_detector
        )
        
        # Find and process PDF
        pdf_path = find_pdf_in_project()
        if pdf_path:
            logger.info("PDF found", {"path": pdf_path})
            try:
                processed_pdf = await service.process_pdf(pdf_path)
                logger.info(
                    "PDF processed successfully",
                    {
                        "pdf_name": processed_pdf.pdf_name,
                        "sections": len(processed_pdf.sections),
                        "images": len(processed_pdf.images)
                    }
                )
            except Exception as e:
                logger.error("Error processing PDF", e)
                raise
        else:
            logger.warning("No PDF found in the project")
            
    except Exception as e:
        logger.error("Fatal error in main process", e)
        raise

if __name__ == "__main__":
    asyncio.run(main())
