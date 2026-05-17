import os
import shutil
from pathlib import Path
from utils.logger import logger
from config import settings

class CleanupManager:
    """
    Manages cleanup of temporary processing files
    """
    
    @staticmethod
    def cleanup_document_files(document_id: str):
        """
        Removes temporary images and processing artifacts for a specific document
        while preserving permanent logs.
        """
        try:
            # 1. Cleanup from upload directory
            for file_path in settings.UPLOAD_DIR.glob(f"{document_id}*"):
                if file_path.is_file():
                    os.remove(file_path)
            
            # 2. Cleanup from output directory (excluding logs)
            for file_path in settings.OUTPUT_DIR.glob(f"{document_id}*"):
                if file_path.is_file() and file_path.parent != settings.LOGS_DIR:
                    os.remove(file_path)
            
            # 3. Cleanup specific temporary subdirectories if they exist
            doc_output_dir = settings.OUTPUT_DIR / document_id
            if doc_output_dir.exists() and doc_output_dir.is_dir():
                shutil.rmtree(doc_output_dir)
                
            logger.info(f"Successfully cleaned up temporary files for document: {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup files for {document_id}: {str(e)}")

cleanup_manager = CleanupManager()
