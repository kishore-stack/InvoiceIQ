"""
Image Cleaner - OpenCV Preprocessing Pipeline
Member 2: Backend Engineer

Improves image quality for better OCR accuracy
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

class ImageCleaner:
    """
    Preprocesses invoice images using OpenCV for better OCR results
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.outputs_dir = self.base_dir / "outputs"
        self.outputs_dir.mkdir(exist_ok=True)
    
    def read_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Read image from file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image as numpy array or None if failed
        """
        try:
            img = cv2.imread(image_path)
            
            if img is None:
                print(f"Failed to read image: {image_path}")
                return None
            
            return img
        
        except Exception as e:
            print(f"Error reading image: {e}")
            return None
    
    def convert_to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        
        Args:
            img: Input image
            
        Returns:
            Grayscale image
        """
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img
    
    def apply_threshold(self, img: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding for better text clarity
        
        Args:
            img: Grayscale image
            
        Returns:
            Thresholded image
        """
        # Adaptive threshold works better for varying lighting
        return cv2.adaptiveThreshold(
            img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
    
    def denoise(self, img: np.ndarray) -> np.ndarray:
        """
        Remove noise from image
        
        Args:
            img: Input image
            
        Returns:
            Denoised image
        """
        # Use Gaussian blur for noise reduction
        return cv2.GaussianBlur(img, (5, 5), 0)
    
    def sharpen(self, img: np.ndarray) -> np.ndarray:
        """
        Sharpen image for better text clarity
        
        Args:
            img: Input image
            
        Returns:
            Sharpened image
        """
        # Sharpening kernel
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        
        return cv2.filter2D(img, -1, kernel)
    
    def resize_if_needed(self, img: np.ndarray, min_width: int = 800, max_width: int = 2000) -> np.ndarray:
        """
        Resize image if too small or too large
        
        Args:
            img: Input image
            min_width: Minimum width
            max_width: Maximum width
            
        Returns:
            Resized image
        """
        height, width = img.shape[:2]
        
        # Resize if too small
        if width < min_width:
            ratio = min_width / width
            new_height = int(height * ratio)
            return cv2.resize(img, (min_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Resize if too large
        if width > max_width:
            ratio = max_width / width
            new_height = int(height * ratio)
            return cv2.resize(img, (max_width, new_height), interpolation=cv2.INTER_AREA)
        
        return img
    
    def deskew(self, img: np.ndarray) -> np.ndarray:
        """
        Correct image rotation/skew
        
        Args:
            img: Input image
            
        Returns:
            Deskewed image
        """
        try:
            # Find coordinates of non-zero pixels
            coords = np.column_stack(np.where(img > 0))
            
            # Get minimum area rectangle
            angle = cv2.minAreaRect(coords)[-1]
            
            # Adjust angle
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Get image center
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            
            # Rotate image
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                img, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            
            return rotated
        
        except Exception as e:
            print(f"Deskew failed: {e}")
            return img
    
    def preprocess_pipeline(self, image_path: str, save_output: bool = True) -> dict:
        """
        Complete preprocessing pipeline
        
        Pipeline:
        1. Read image
        2. Resize if needed
        3. Convert to grayscale
        4. Denoise
        5. Sharpen
        6. Apply threshold
        7. Deskew (optional)
        
        Args:
            image_path: Path to input image
            save_output: Whether to save processed image
            
        Returns:
            Dictionary with results
        """
        try:
            # Read image
            img = self.read_image(image_path)
            
            if img is None:
                return {
                    "success": False,
                    "error": "Failed to read image",
                    "processed_path": None
                }
            
            # Resize if needed
            img = self.resize_if_needed(img)
            
            # Convert to grayscale
            gray = self.convert_to_grayscale(img)
            
            # Denoise
            denoised = self.denoise(gray)
            
            # Sharpen
            sharpened = self.sharpen(denoised)
            
            # Apply threshold
            thresholded = self.apply_threshold(sharpened)
            
            # Save processed image
            processed_path = None
            if save_output:
                base_name = Path(image_path).stem
                output_filename = f"{base_name}_processed.png"
                processed_path = self.outputs_dir / output_filename
                cv2.imwrite(str(processed_path), thresholded)
            
            return {
                "success": True,
                "original_path": image_path,
                "processed_path": str(processed_path) if processed_path else None,
                "processed_image": thresholded,
                "message": "Image preprocessing completed successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Preprocessing failed: {str(e)}",
                "processed_path": None
            }
    
    def get_image_quality_score(self, img: np.ndarray) -> float:
        """
        Estimate image quality (0-100)
        
        Args:
            img: Input image
            
        Returns:
            Quality score
        """
        try:
            # Calculate Laplacian variance (sharpness measure)
            gray = self.convert_to_grayscale(img) if len(img.shape) == 3 else img
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-100 scale
            quality = min(100, laplacian_var / 10)
            
            return round(quality, 2)
        
        except Exception as e:
            print(f"Quality score calculation failed: {e}")
            return 0.0


# Create singleton instance
image_cleaner = ImageCleaner()
