"""Dependency injection container for PDF processing application."""
from typing import Dict, Any, Type, Optional
import logging
import os
import openai
from ..domain.ports import PDFProcessor, PDFRepository, TextAnalyzer, ImageAnalyzer, ProcessPDFUseCasePort
from ..application.services.pdf_service import PDFService
from ..application.usecases.process_pdf_usecase import ProcessPDFUseCase
from .pdf_processor import MuPDFProcessor
from .repositories.pdf_repository import FilePDFRepository
from .analyzers.text_analyzer import TextAnalyzer as TextAnalyzerImpl
from .analyzers.image_analyzer import ImageAnalyzer as ImageAnalyzerImpl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerError(Exception):
    """Custom exception for container-related errors."""
    pass

class OpenAIClient:
    """Wrapper for OpenAI client to use as interface."""
    pass

class Container:
    """Dependency injection container."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Container, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize container with default implementations."""
        try:
            logger.info("Initializing dependency injection container")
            self._registry: Dict[Type, Any] = {}
            
            # Initialize OpenAI client
            logger.info("Initializing OpenAI client")
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            if not openai_api_key:
                raise ContainerError("OpenAI API key not found in environment variables")
            
            try:
                openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
                self.register_instance(OpenAIClient, openai_client)
                logger.info("Successfully initialized OpenAI client")
            except Exception as e:
                raise ContainerError(f"Failed to initialize OpenAI client: {str(e)}") from e
            
            # Register analyzers with OpenAI client
            logger.info("Registering text and image analyzers")
            try:
                text_analyzer = TextAnalyzerImpl()
                text_analyzer.openai_client = self.resolve(OpenAIClient)
                self.register_instance(TextAnalyzer, text_analyzer)
                logger.info("Successfully registered text analyzer")
            except Exception as e:
                raise ContainerError(f"Failed to initialize text analyzer: {str(e)}") from e
                
            try:
                self.register_instance(ImageAnalyzer, ImageAnalyzerImpl())
                logger.info("Successfully registered image analyzer")
            except Exception as e:
                raise ContainerError(f"Failed to initialize image analyzer: {str(e)}") from e
            
            # Register PDF processor
            logger.info("Registering PDF processor")
            try:
                pdf_processor = MuPDFProcessor()
                pdf_processor.text_analyzer = self.resolve(TextAnalyzer)
                self.register_instance(PDFProcessor, pdf_processor)
                logger.info("Successfully registered PDF processor")
            except Exception as e:
                raise ContainerError(f"Failed to initialize PDF processor: {str(e)}") from e
            
            # Register repository
            logger.info("Registering PDF repository")
            try:
                pdf_repository = FilePDFRepository()
                self.register_instance(PDFRepository, pdf_repository)
                logger.info("Successfully registered PDF repository")
            except Exception as e:
                raise ContainerError(f"Failed to initialize PDF repository: {str(e)}") from e
            
            # Register use case
            logger.info("Registering PDF processing use case")
            try:
                process_pdf_usecase = ProcessPDFUseCase(
                    pdf_processor=self.resolve(PDFProcessor),
                    pdf_repository=self.resolve(PDFRepository)
                )
                self.register_instance(ProcessPDFUseCasePort, process_pdf_usecase)
                logger.info("Successfully registered PDF processing use case")
            except Exception as e:
                raise ContainerError(f"Failed to initialize PDF use case: {str(e)}") from e
            
            # Register service
            logger.info("Registering PDF service")
            try:
                pdf_service = PDFService(
                    process_pdf_usecase=self.resolve(ProcessPDFUseCasePort)
                )
                self.register_instance(PDFService, pdf_service)
                logger.info("Successfully registered PDF service")
            except Exception as e:
                raise ContainerError(f"Failed to initialize PDF service: {str(e)}") from e
            
            logger.info("Container initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize container: {str(e)}", exc_info=True)
            raise ContainerError(f"Container initialization failed: {str(e)}") from e
    
    def register_instance(self, interface: Type, implementation: Any) -> None:
        """Register an implementation for an interface."""
        try:
            if interface is None:
                raise ContainerError("Interface cannot be None")
            if implementation is None:
                raise ContainerError("Implementation cannot be None")
                
            self._registry[interface] = implementation
            logger.debug(f"Registered implementation for {interface.__name__}")
            
        except Exception as e:
            logger.error(f"Failed to register implementation: {str(e)}", exc_info=True)
            raise ContainerError(f"Failed to register implementation: {str(e)}") from e
    
    def resolve(self, interface: Type) -> Any:
        """Resolve an implementation for an interface."""
        try:
            if interface is None:
                raise ContainerError("Interface cannot be None")
                
            implementation = self._registry.get(interface)
            if implementation is None:
                raise ContainerError(f"No implementation registered for interface: {interface}")
                
            return implementation
            
        except Exception as e:
            logger.error(f"Failed to resolve implementation: {str(e)}", exc_info=True)
            raise ContainerError(f"Failed to resolve implementation: {str(e)}") from e
    
    @classmethod
    def get_instance(cls) -> 'Container':
        """Get the singleton instance of the container."""
        return cls()
