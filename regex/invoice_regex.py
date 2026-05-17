"""
Invoice Regex Extractor - Extract invoice fields using regex patterns
Member 2: Backend Engineer
"""

import re
from typing import Optional, Dict


class InvoiceRegexExtractor:
    """
    Extracts invoice fields from OCR text using regex patterns
    """

    def __init__(self):

        # Invoice number patterns
        self.invoice_patterns = [
            r'Invoice\s*(?:Number|No|#)?\s*[:\-]?\s*([A-Z0-9\-/]+)',
            r'INV[\s\-:]*([A-Z0-9\-/]+)',
            r'Bill\s*(?:Number|No)?\s*[:\-]?\s*([A-Z0-9\-/]+)',
        ]

        # Date patterns
        self.date_patterns = [
            r'Date\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})',
            r'Date\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Invoice\s*Date\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]

        # Amount patterns
        self.total_patterns = [
            r'Total\s*[:\-]?\s*(?:USD|INR|Rs\.?|₹|\$)?\s*([\d,]+\.?\d*)',
            r'Grand\s*Total\s*[:\-]?\s*(?:USD|INR|Rs\.?|₹|\$)?\s*([\d,]+\.?\d*)',
        ]

        self.subtotal_patterns = [
            r'Subtotal\s*[:\-]?\s*(?:USD|INR|Rs\.?|₹|\$)?\s*([\d,]+\.?\d*)',
        ]

        self.tax_patterns = [
            r'Tax\s*[:\-]?\s*(?:USD|INR|Rs\.?|₹|\$)?\s*([\d,]+\.?\d*)',
            r'GST\s*[:\-]?\s*(?:USD|INR|Rs\.?|₹|\$)?\s*([\d,]+\.?\d*)',
        ]

    # ==========================
    # Generic helper
    # ==========================

    def find_pattern(self, patterns, text):
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    # ==========================
    # Invoice Number
    # ==========================

    def extract_invoice_number(self, text: str) -> Optional[str]:
        return self.find_pattern(self.invoice_patterns, text)

    # ==========================
    # Date
    # ==========================

    def extract_date(self, text: str) -> Optional[str]:
        return self.find_pattern(self.date_patterns, text)

    # ==========================
    # Seller Name
    # ==========================

    def extract_seller_name(self, text: str) -> Optional[str]:

        patterns = [
            r'Seller\s*:\s*(.+)',
            r'From\s*:\s*(.+)',
            r'Vendor\s*:\s*(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                line = match.group(1).split("\n")[0].strip()
                return line

        return None

    # ==========================
    # Buyer Name
    # ==========================

    def extract_buyer_name(self, text: str) -> Optional[str]:

        patterns = [
            r'Buyer\s*:\s*(.+)',
            r'To\s*:\s*(.+)',
            r'Customer\s*:\s*(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                line = match.group(1).split("\n")[0].strip()
                return line

        return None

    # ==========================
    # Amount Extraction
    # ==========================

    def extract_total_amount(self, text: str) -> Optional[float]:

        result = self.find_pattern(self.total_patterns, text)

        if result:
            try:
                return float(result.replace(",", ""))
            except:
                return None

        return None

    def extract_subtotal(self, text: str) -> Optional[float]:

        result = self.find_pattern(self.subtotal_patterns, text)

        if result:
            try:
                return float(result.replace(",", ""))
            except:
                return None

        return None

    def extract_tax_amount(self, text: str) -> Optional[float]:

        result = self.find_pattern(self.tax_patterns, text)

        if result:
            try:
                return float(result.replace(",", ""))
            except:
                return None

        return None

    # ==========================
    # Extract Everything
    # ==========================

    def extract_all_fields(self, text: str) -> Dict:

        subtotal = self.extract_subtotal(text)
        tax = self.extract_tax_amount(text)
        total = self.extract_total_amount(text)

        return {
            "invoice_number": self.extract_invoice_number(text),
            "date": self.extract_date(text),
            "seller_name": self.extract_seller_name(text),
            "buyer_name": self.extract_buyer_name(text),
            "subtotal": subtotal,
            "tax_amount": tax,
            "total_amount": total,
        }


# Create singleton instance
invoice_extractor = InvoiceRegexExtractor()