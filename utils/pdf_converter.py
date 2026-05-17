"""
PDF Converter - Convert PDF invoices to images
Member 2: Backend Engineer
"""

import os
from pathlib import Path
from typing import List, Optional
from pdf2image import convert_from_path
from PIL import Image
from config import settings

class PDFConverter:
    """
    Converts PDF files to images for OCR processing
    """
    
    def __init__(self):
        self.outputs_dir = settings.OUTPUT_DIR
        self.outputs_dir.mkdir(exist_ok=True)
        
        # Conversion settings
        self.dpi = 300  # High quality for OCR
        self.image_format = 'PNG'
    
    def is_pdf(self, file_path: str) -> bool:
        """
        Check if file is a PDF
        
        Args:
            file_path: Path to file
            
        Returns:
            True if PDF, False otherwise
        """
        return Path(file_path).suffix.lower() == '.pdf'
    
    def convert_pdf_to_images(self, pdf_path: str) -> dict:
        """
        Convert PDF to images
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with conversion results
        """
        try:
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": "PDF file not found",
                    "image_paths": []
                }
            
            # Convert PDF to images using Poppler
            images = convert_from_path(
    pdf_path,
    dpi=self.dpi,
    fmt=self.image_format.lower(),
    thread_count=4,
    poppler_path=r"C:\Users\Gowtham k\Downloads\InvoiceIQ-backend-dev\InvoiceIQ-backend-dev\poppler-26.02.0\Library\bin"
)
            if not images:
                return {
                    "success": False,
                    "error": "No pages found in PDF",
                    "image_paths": []
                }
            
            # Save each page as image
            image_paths = []
            base_name = Path(pdf_path).stem
            
            for page_num, image in enumerate(images, start=1):
                # Generate output filename
                output_filename = f"{base_name}_page_{page_num}.png"
                output_path = self.outputs_dir / output_filename
                
                # Save image
                image.save(output_path, self.image_format)
                image_paths.append(str(output_path))
            
            return {
                "success": True,
                "page_count": len(images),
                "image_paths": image_paths,
                "message": f"Converted {len(images)} page(s) successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF conversion failed: {str(e)}",
                "image_paths": []
            }
    
    def convert_if_pdf(self, file_path: str) -> dict:
        """
        Convert file to images if it's a PDF, otherwise return original path
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with image paths
        """
        if self.is_pdf(file_path):
            # Convert PDF to images
            result = self.convert_pdf_to_images(file_path)
            
            if result["success"]:
                return {
                    "is_pdf": True,
                    "success": True,
                    "image_paths": result["image_paths"],
                    "page_count": result["page_count"]
                }
            else:
                return {
                    "is_pdf": True,
                    "success": False,
                    "error": result["error"],
                    "image_paths": []
                }
        else:
            # Not a PDF, return original path
            return {
                "is_pdf": False,
                "success": True,
                "image_paths": [file_path],
                "page_count": 1
            }
    
    def optimize_image(self, image_path: str, max_width: int = 2000) -> str:
        """
        Optimize image size for OCR processing
        
        Args:
            image_path: Path to image
            max_width: Maximum width in pixels
            
        Returns:
            Path to optimized image
        """
        try:
            img = Image.open(image_path)
            
            # Check if resize needed
            if img.width > max_width:
                # Calculate new height maintaining aspect ratio
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                
                # Resize image
                img = img.resize((max_width, new_height), Image.LANCZOS)
                
                # Save optimized image
                img.save(image_path)
            
            return image_path
        
        except Exception as e:
            print(f"Image optimization failed: {e}")
            return image_path
    
    def get_image_info(self, image_path: str) -> Optional[dict]:
        """
        Get information about an image
        
        Args:
            image_path: Path to image
            
        Returns:
            Dictionary with image information
        """
        try:
            img = Image.open(image_path)
            
            return {
                "path": image_path,
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode
            }
        
        except Exception as e:
            print(f"Error getting image info: {e}")
            return None


# Create singleton instance
pdf_converter = PDFConverter()