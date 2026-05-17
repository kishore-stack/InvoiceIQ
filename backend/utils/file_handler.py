"""
File Handler - Secure File Upload and Management System
Member 2: Backend Engineer
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
import shutil
# import magic# For MIME checking (python-magic) - wait, python-magic needs system deps. Let's use mimetypes.
import mimetypes

from config import settings

class FileHandler:
    """
    Handles file uploads, validation, and storage
    """
    
    def __init__(self):
        # Define directories using config
        self.uploads_dir = settings.UPLOAD_DIR
        self.outputs_dir = settings.OUTPUT_DIR
        
        # Allowed file extensions and types
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
        self.allowed_mime_types = settings.ALLOWED_MIME_TYPES
        
        # Maximum file size
        self.max_file_size = settings.MAX_FILE_SIZE_BYTES
    
    def validate_file(self, file: UploadFile) -> bool:
        """
        Validate uploaded file
        
        Args:
            file: Uploaded file object
            
        Returns:
            True if valid
            
        Raises:
            HTTPException: If file is invalid
        """
        # Check if file exists
        if not file or not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file provided"
            )
        
        # Get file extension
        file_ext = Path(file.filename).suffix.lower().replace('.', '')
        
        # Validate extension
        if file_ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(self.allowed_extensions)}"
            )
            
        # Basic MIME check
        mime_type, _ = mimetypes.guess_type(file.filename)
        if mime_type and mime_type not in self.allowed_mime_types:
            raise HTTPException(
                status_code=400,
                detail="Suspicious file content. Invalid MIME type."
            )
        
        return True
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate unique filename to avoid duplicates
        
        Args:
            original_filename: Original uploaded filename
            
        Returns:
            Unique filename with UUID
        """
        # Get file extension
        file_ext = Path(original_filename).suffix.lower()
        
        # Generate unique ID
        unique_id = uuid.uuid4().hex[:8]
        
        # Create new filename
        base_name = Path(original_filename).stem
        safe_name = "".join(c for c in base_name if c.isalnum() or c in ('-', '_'))
        
        new_filename = f"{safe_name}_{unique_id}{file_ext}"
        
        return new_filename
    
    async def save_upload_file(self, file: UploadFile) -> dict:
        """
        Save uploaded file to uploads directory
        
        Args:
            file: Uploaded file object
            
        Returns:
            Dictionary with file information
            
        Raises:
            HTTPException: If save fails
        """
        try:
            # Validate file
            self.validate_file(file)
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Validate file size
            if file_size > self.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {self.max_file_size / (1024*1024):.0f}MB"
                )
            
            # Check if file is empty
            if file_size == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Empty file uploaded"
                )
            
            # Generate unique filename
            unique_filename = self.generate_unique_filename(file.filename)
            
            # Create full file path
            file_path = self.uploads_dir / unique_filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Return file information
            return {
                "success": True,
                "original_filename": file.filename,
                "saved_filename": unique_filename,
                "file_path": str(file_path),
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "file_type": Path(file.filename).suffix.lower()
            }
        
        except HTTPException:
            raise
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file safely
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def cleanup_temp_files(self, file_paths: list) -> None:
        """
        Clean up temporary files
        
        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            self.delete_file(file_path)
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information or None
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            file_stat = os.stat(file_path)
            
            return {
                "path": file_path,
                "size_bytes": file_stat.st_size,
                "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                "exists": True
            }
        
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None


# Create singleton instance
file_handler = FileHandler()
