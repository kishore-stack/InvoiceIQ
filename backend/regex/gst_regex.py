"""
GST Regex Extractor - Extract GST numbers and tax information
Member 2: Backend Engineer
"""

import re
from typing import Optional, List

class GSTRegexExtractor:
    """
    Extracts GST numbers and tax information from invoice text
    """
    
    def __init__(self):
        # GST number pattern (Indian format: 22AAAAA0000A1Z5)
        self.gst_patterns = [
            r'GST(?:IN)?\s*:?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
            r'([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
        ]
        
        # Tax patterns
        self.tax_patterns = [
            r'(?:GST|Tax)\s*(?:Amount)?\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
            r'CGST\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
            r'SGST\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
            r'IGST\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
        ]
    
    def extract_gst_number(self, text: str) -> Optional[str]:
        """
        Extract GST number
        
        Args:
            text: OCR extracted text
            
        Returns:
            GST number or None
        """
        for pattern in self.gst_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_all_gst_numbers(self, text: str) -> List[str]:
        """
        Extract all GST numbers (seller and buyer)
        
        Args:
            text: OCR extracted text
            
        Returns:
            List of GST numbers
        """
        gst_numbers = []
        
        for pattern in self.gst_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            gst_numbers.extend(matches)
        
        # Remove duplicates
        return list(set(gst_numbers))
    
    def extract_tax_amount(self, text: str) -> Optional[float]:
        """
        Extract total tax amount
        
        Args:
            text: OCR extracted text
            
        Returns:
            Tax amount or None
        """
        for pattern in self.tax_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_cgst_sgst(self, text: str) -> dict:
        """
        Extract CGST and SGST separately
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with CGST and SGST amounts
        """
        cgst = None
        sgst = None
        igst = None
        
        # Extract CGST
        cgst_match = re.search(r'CGST\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)', text, re.IGNORECASE)
        if cgst_match:
            try:
                cgst = float(cgst_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # Extract SGST
        sgst_match = re.search(r'SGST\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)', text, re.IGNORECASE)
        if sgst_match:
            try:
                sgst = float(sgst_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # Extract IGST
        igst_match = re.search(r'IGST\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)', text, re.IGNORECASE)
        if igst_match:
            try:
                igst = float(igst_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        return {
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "total_tax": (cgst or 0) + (sgst or 0) + (igst or 0) if (cgst or sgst or igst) else None
        }


# Create singleton instance
gst_extractor = GSTRegexExtractor()
