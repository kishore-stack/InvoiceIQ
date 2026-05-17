"""
Centralized Logger - Logging and Error Handling
Member 2: Backend Engineer
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

class InvoiceLogger:
    """
    Centralized logging system for invoice processing
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.logs_dir = self.base_dir / "outputs" / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('InvoiceIQ')
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # File handler
            log_file = self.logs_dir / f"invoice_processing_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)
    
    def log_upload(self, filename: str, file_size: int):
        """Log file upload"""
        self.info(f"File uploaded: {filename} ({file_size} bytes)")
    
    def log_ocr_start(self, image_path: str):
        """Log OCR processing start"""
        self.info(f"Starting OCR processing: {image_path}")
    
    def log_ocr_complete(self, image_path: str, char_count: int):
        """Log OCR completion"""
        self.info(f"OCR completed: {image_path} - Extracted {char_count} characters")
    
    def log_ocr_failure(self, image_path: str, error: str):
        """Log OCR failure"""
        self.error(f"OCR failed for {image_path}: {error}")
    
    def log_extraction_start(self, document_id: str):
        """Log extraction start"""
        self.info(f"Starting field extraction: {document_id}")
    
    def log_extraction_complete(self, document_id: str, fields_extracted: int):
        """Log extraction completion"""
        self.info(f"Extraction completed: {document_id} - {fields_extracted} fields extracted")
    
    def log_validation_result(self, document_id: str, is_valid: bool, error_count: int):
        """Log validation result"""
        status = "VALID" if is_valid else "INVALID"
        self.info(f"Validation {status}: {document_id} - {error_count} errors")
        
    def log_validation_errors(self, document_id: str, errors: list, warnings: list):
        """Explicitly log validation mismatches and missing fields"""
        if errors:
            self.error(f"Validation Errors for {document_id}: {', '.join(errors)}")
        if warnings:
            self.warning(f"Validation Warnings for {document_id}: {', '.join(warnings)}")
            
    def log_table_extraction_failure(self, document_id: str):
        """Log malformed tables or extraction failures"""
        self.warning(f"Table Extraction Warning: Malformed or missing table for {document_id}")
    
    def log_api_request(self, endpoint: str, method: str):
        """Log API request"""
        self.info(f"API Request: {method} {endpoint}")
    
    def log_api_error(self, endpoint: str, error: str):
        """Log API error"""
        self.error(f"API Error at {endpoint}: {error}")
    
    def log_processing_time(self, document_id: str, processing_time: float):
        """Log processing time"""
        self.info(f"Processing completed: {document_id} - {processing_time:.2f}s")


# Create singleton instance
logger = InvoiceLogger()
