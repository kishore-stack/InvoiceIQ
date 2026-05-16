"""
Invoice Regex Extractor - Extract invoice fields using regex patterns
Member 2: Backend Engineer
"""

import re
from typing import Optional, Dict
from datetime import datetime

class InvoiceRegexExtractor:
    """
    Extracts invoice fields from OCR text using regex patterns
    """
    
    def __init__(self):
        # Invoice number patterns
        self.invoice_patterns = [
            r'Invoice\s*(?:Number|No|#)?\s*:?\s*([A-Z0-9\-/]+)',
            r'Bill\s*(?:Number|No|#)?\s*:?\s*([A-Z0-9\-/]+)',
            r'INV[:\-\s]*([A-Z0-9\-/]+)',
            r'Invoice\s*([A-Z0-9\-/]{3,})',
        ]
        
        # Date patterns
        self.date_patterns = [
            r'Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Invoice\s*Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Bill\s*Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        ]
        
        # Seller/Buyer name patterns
        self.name_patterns = [
            r'(?:Seller|From|Vendor|Billed\s*By)\s*:?\s*([A-Za-z\s&.,]+?)(?:\n|Address|GST)',
            r'(?:Buyer|To|Customer|Bill\s*To)\s*:?\s*([A-Za-z\s&.,]+?)(?:\n|Address|GST)',
        ]
    
    def extract_invoice_number(self, text: str) -> Optional[str]:
        """
        Extract invoice number
        
        Args:
            text: OCR extracted text
            
        Returns:
            Invoice number or None
        """
        for pattern in self.invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """
        Extract invoice date
        
        Args:
            text: OCR extracted text
            
        Returns:
            Date string or None
        """
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_seller_name(self, text: str) -> Optional[str]:
        """
        Extract seller name
        
        Args:
            text: OCR extracted text
            
        Returns:
            Seller name or None
        """
        patterns = [
            r'(?:Seller|From|Vendor|Billed\s*By)\s*:?\s*([A-Za-z\s&.,]+?)(?:\n|Address|GST|Phone)',
            r'(?:Seller|From)\s*:?\s*\n\s*([A-Za-z\s&.,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up name
                name = re.sub(r'\s+', ' ', name)
                return name[:100]  # Limit length
        
        return None
    
    def extract_buyer_name(self, text: str) -> Optional[str]:
        """
        Extract buyer name
        
        Args:
            text: OCR extracted text
            
        Returns:
            Buyer name or None
        """
        patterns = [
            r'(?:Buyer|To|Customer|Bill\s*To)\s*:?\s*([A-Za-z\s&.,]+?)(?:\n|Address|GST|Phone)',
            r'(?:Buyer|To)\s*:?\s*\n\s*([A-Za-z\s&.,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up name
                name = re.sub(r'\s+', ' ', name)
                return name[:100]  # Limit length
        
        return None
    
    def extract_all_fields(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract all invoice fields
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with extracted fields
        """
        return {
            "invoice_number": self.extract_invoice_number(text),
            "date": self.extract_date(text),
            "seller_name": self.extract_seller_name(text),
            "buyer_name": self.extract_buyer_name(text),
        }


# Create singleton instance
invoice_extractor = InvoiceRegexExtractor()
