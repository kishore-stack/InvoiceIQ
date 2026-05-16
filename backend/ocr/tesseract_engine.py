"""
Tesseract OCR Engine - Text Extraction from Images
Member 2: Backend Engineer
"""

import pytesseract
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import os

class TesseractOCR:
    """
    Extracts text from invoice images using Tesseract OCR
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.outputs_dir = self.base_dir / "outputs"
        self.outputs_dir.mkdir(exist_ok=True)
        
        # OCR configuration
        self.language = 'eng'
        self.config = '--psm 6'  # Assume uniform block of text
        
        # Try to set Tesseract path (Windows)
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
    
    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from image
        
        Args:
            image: Image as numpy array
            
        Returns:
            Extracted text
        """
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=self.config
            )
            
            return text.strip()
        
        except Exception as e:
            print(f"OCR extraction failed: {e}")
            return ""
    
    def extract_text_from_path(self, image_path: str) -> dict:
        """
        Extract text from image file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with OCR results
        """
        try:
            # Extract text
            text = pytesseract.image_to_string(
                image_path,
                lang=self.language,
                config=self.config
            )
            
            if not text or not text.strip():
                return {
                    "success": False,
                    "text": "",
                    "error": "No text extracted from image",
                    "confidence": 0.0
                }
            
            return {
                "success": True,
                "text": text.strip(),
                "char_count": len(text.strip()),
                "line_count": len(text.strip().split('\n')),
                "message": "Text extracted successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"OCR failed: {str(e)}",
                "confidence": 0.0
            }
    
    def extract_with_confidence(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Extract text with confidence score
        
        Args:
            image: Image as numpy array
            
        Returns:
            Tuple of (text, confidence_score)
        """
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [
                int(conf) for conf in data['conf']
                if conf != '-1' and str(conf).isdigit()
            ]
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=self.config
            )
            
            return text.strip(), round(avg_confidence, 2)
        
        except Exception as e:
            print(f"OCR with confidence failed: {e}")
            return "", 0.0
    
    def extract_and_save(self, image_path: str, save_log: bool = True) -> dict:
        """
        Extract text and optionally save to log file
        
        Args:
            image_path: Path to image
            save_log: Whether to save OCR output to file
            
        Returns:
            Dictionary with OCR results
        """
        try:
            # Extract text
            result = self.extract_text_from_path(image_path)
            
            if not result["success"]:
                return result
            
            # Save OCR log if requested
            if save_log and result["text"]:
                base_name = Path(image_path).stem
                log_filename = f"{base_name}_ocr.txt"
                log_path = self.outputs_dir / log_filename
                
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(result["text"])
                
                result["log_path"] = str(log_path)
            
            return result
        
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"OCR processing failed: {str(e)}"
            }
    
    def extract_multiline(self, image_path: str) -> dict:
        """
        Extract text preserving line structure
        
        Args:
            image_path: Path to image
            
        Returns:
            Dictionary with lines of text
        """
        try:
            result = self.extract_text_from_path(image_path)
            
            if not result["success"]:
                return result
            
            # Split into lines
            lines = [line.strip() for line in result["text"].split('\n') if line.strip()]
            
            return {
                "success": True,
                "lines": lines,
                "line_count": len(lines),
                "full_text": result["text"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "lines": [],
                "error": f"Multiline extraction failed: {str(e)}"
            }
    
    def test_ocr_availability(self) -> dict:
        """
        Test if Tesseract OCR is available
        
        Returns:
            Dictionary with availability status
        """
        try:
            version = pytesseract.get_tesseract_version()
            
            return {
                "available": True,
                "version": str(version),
                "message": "Tesseract OCR is available"
            }
        
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "message": "Tesseract OCR not found. Please install Tesseract."
            }


# Create singleton instance
tesseract_ocr = TesseractOCR()
