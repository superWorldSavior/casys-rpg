import os
from typing import Optional
from ..domain.ports import DirectoryManager
from .logging_config import StructuredLogger

class FileSystemDirectoryManager(DirectoryManager):
    """File system implementation of the DirectoryManager port"""
    
    def __init__(self):
        self.logger = StructuredLogger("FileSystemDirectoryManager")
    
    async def create_directory(self, path: str) -> None:
        """Create a directory and its parents if they don't exist"""
        try:
            os.makedirs(path, exist_ok=True)
            self.logger.info(f"Created directory", {"path": path})
        except Exception as e:
            self.logger.error(f"Error creating directory", e, {"path": path})
            raise
    
    async def ensure_directory_exists(self, path: str) -> bool:
        """Check if a directory exists and create it if it doesn't"""
        try:
            if not os.path.exists(path):
                await self.create_directory(path)
            return True
        except Exception as e:
            self.logger.error(f"Error ensuring directory exists", e, {"path": path})
            return False
    
    async def get_section_directory(self, base_dir: str, pdf_name: str) -> str:
        """Get the sections directory path and ensure it exists"""
        path = os.path.join(base_dir, pdf_name, "sections")
        await self.ensure_directory_exists(path)
        return path
    
    async def get_metadata_directory(self, base_dir: str, pdf_name: str) -> str:
        """Get the metadata directory path and ensure it exists"""
        path = os.path.join(base_dir, pdf_name, "metadata")
        await self.ensure_directory_exists(path)
        return path
    
    async def get_histoire_directory(self, base_dir: str, pdf_name: str) -> str:
        """Get the histoire directory path and ensure it exists"""
        path = os.path.join(base_dir, pdf_name, "histoire")
        await self.ensure_directory_exists(path)
        return path
