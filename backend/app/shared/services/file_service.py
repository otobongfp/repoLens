import os
from typing import List, Set
import logging

logger = logging.getLogger(__name__)

class FileService:
    """Service for file system operations."""
    
    @staticmethod
    def find_files_with_extension(root_dir: str, extensions: List[str]) -> List[str]:
        """
        Recursively find files with specified extensions.
        
        Args:
            root_dir: Root directory to search
            extensions: List of file extensions to match
            
        Returns:
            List of file paths matching the extensions
        """
        matches = []
        for root, _, files in os.walk(root_dir):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    matches.append(os.path.join(root, file))
        return matches
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Get the file extension from a file path."""
        return os.path.splitext(file_path)[-1]
    
    @staticmethod
    def get_relative_path(file_path: str, base_path: str) -> str:
        """Get relative path from base path."""
        return os.path.relpath(file_path, base_path)
    
    @staticmethod
    def get_file_name(file_path: str) -> str:
        """Get the file name from a file path."""
        return os.path.basename(file_path) 