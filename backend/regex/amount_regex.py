"""
Amount Regex Extractor - Extract monetary amounts from invoices
Member 2: Backend Engineer
"""

import re
from typing import Optional, Dict


class AmountRegexExtractor:
    """
    Extracts monetary amounts: subtotal, discount, tax, total
    """

    def __init__(self):
        currency = r"(?:Rs\.?|INR|₹|USD|\$|EUR|€)?"

        self.total_patterns = [
            rf"Grand\s*Total\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
            rf"Total\s*(?:Amount)?\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
            rf"Amount\s*Payable\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
            rf"Amount\s*Due\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
            rf"Net\s*Amount\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
        ]

        self.subtotal_patterns = [
            rf"Sub\s*Total\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
            rf"Subtotal\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
            rf"Amount\s*Before\s*Tax\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
        ]

        self.discount_patterns = [
            rf"Discount\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
            rf"Discount\s*Amount\s*:?\s*{currency}\s*([0-9,]+(?:\.\d+)?)",
        ]

    def clean_amount(self, amount_str: str) -> Optional[float]:
        try:
            cleaned = (
                amount_str.replace(",", "")
                .replace("₹", "")
                .replace("Rs", "")
                .replace("INR", "")
                .replace("USD", "")
                .replace("$", "")
                .replace("EUR", "")
                .replace("€", "")
                .strip()
            )
            return float(cleaned)
        except (ValueError, AttributeError):
            return None

    def extract_total_amount(self, text: str) -> Optional[float]:
        for pattern in self.total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_amount(match.group(1))
        return None

    def extract_subtotal(self, text: str) -> Optional[float]:
        for pattern in self.subtotal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_amount(match.group(1))
        return None

    def extract_discount(self, text: str) -> Optional[float]:
        for pattern in self.discount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_amount(match.group(1))
        return 0.0

    def extract_all_amounts(self, text: str) -> Dict[str, Optional[float]]:
        return {
            "subtotal": self.extract_subtotal(text),
            "discount": self.extract_discount(text),
            "total_amount": self.extract_total_amount(text),
        }

    def find_all_amounts(self, text: str) -> list:
        currency = r"(?:Rs\.?|INR|₹|USD|\$|EUR|€)?"
        pattern = rf"{currency}\s*([0-9,]+(?:\.\d+)?)"

        matches = re.findall(pattern, text)
        amounts = []

        for match in matches:
            amount = self.clean_amount(match)
            if amount and amount > 0:
                amounts.append(amount)

        return amounts


amount_extractor = AmountRegexExtractor()