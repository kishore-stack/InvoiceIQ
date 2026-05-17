"""
Amount Regex Extractor - Extract monetary amounts from invoices
Member 2: Backend Engineer
"""

import re
from typing import Optional, Dict

class AmountRegexExtractor:
    """
    Extracts monetary amounts (subtotal, discount, tax, total) from invoice text
    """
    
    def __init__(self):
        # Total amount patterns
        self.total_patterns = [
            r'Total\s*(?:Amount)?\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
            r'Grand\s*Total\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
            r'Amount\s*Payable\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
            r'Net\s*Amount\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
        ]
        
        # Subtotal patterns
        self.subtotal_patterns = [
            r'Sub\s*Total\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
            r'Subtotal\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
            r'Amount\s*Before\s*Tax\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
        ]
        
        # Discount patterns
        self.discount_patterns = [
            r'Discount\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
            r'Discount\s*Amount\s*:?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)',
        ]
    
    def clean_amount(self, amount_str: str) -> Optional[float]:
        """
        Clean and convert amount string to float
        
        Args:
            amount_str: Amount as string
            
        Returns:
            Amount as float or None
        """
        try:
            # Remove commas and currency symbols
            cleaned = amount_str.replace(',', '').replace('₹', '').replace('Rs', '').strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def extract_total_amount(self, text: str) -> Optional[float]:
        """
        Extract total amount
        
        Args:
            text: OCR extracted text
            
        Returns:
            Total amount or None
        """
        for pattern in self.total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_amount(match.group(1))
        
        return None
    
    def extract_subtotal(self, text: str) -> Optional[float]:
        """
        Extract subtotal amount
        
        Args:
            text: OCR extracted text
            
        Returns:
            Subtotal or None
        """
        for pattern in self.subtotal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_amount(match.group(1))
        
        return None
    
    def extract_discount(self, text: str) -> Optional[float]:
        """
        Extract discount amount
        
        Args:
            text: OCR extracted text
            
        Returns:
            Discount amount or None
        """
        for pattern in self.discount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_amount(match.group(1))
        
        return 0.0  # Default to 0 if no discount found
    
    def extract_all_amounts(self, text: str) -> Dict[str, Optional[float]]:
        """
        Extract all monetary amounts
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with all amounts
        """
        return {
            "subtotal": self.extract_subtotal(text),
            "discount": self.extract_discount(text),
            "total_amount": self.extract_total_amount(text),
        }
    
    def find_all_amounts(self, text: str) -> list:
        """
        Find all monetary amounts in text
        
        Args:
            text: OCR extracted text
            
        Returns:
            List of all amounts found
        """
        # Pattern to match any amount
        pattern = r'(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?\d*)'
        
        matches = re.findall(pattern, text)
        amounts = []
        
        for match in matches:
            amount = self.clean_amount(match)
            if amount and amount > 0:
                amounts.append(amount)
        
        return amounts


# Create singleton instance
amount_extractor = AmountRegexExtractor()
