"""
Table Extractor - Extract line items from invoice tables
Member 2: Backend Engineer
"""

import re
from typing import List, Dict, Optional

class TableExtractor:
    """
    Extracts line items/table data from invoice OCR text
    """
    
    def __init__(self):
        # Table header keywords
        self.header_keywords = [
            'description', 'item', 'product', 'particular',
            'quantity', 'qty', 'price', 'rate', 'amount', 'total'
        ]
    
    def find_table_start(self, lines: List[str]) -> int:
        """
        Find where the table starts in the text
        
        Args:
            lines: List of text lines
            
        Returns:
            Line index where table starts, or -1 if not found
        """
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains table headers
            keyword_count = sum(1 for keyword in self.header_keywords if keyword in line_lower)
            
            if keyword_count >= 2:  # At least 2 header keywords
                return i + 1  # Return next line (first data row)
        
        return -1
    
    def find_table_end(self, lines: List[str], start_index: int) -> int:
        """
        Find where the table ends
        
        Args:
            lines: List of text lines
            start_index: Where table starts
            
        Returns:
            Line index where table ends
        """
        footer_keywords = ['subtotal', 'total', 'tax', 'grand total', 'amount payable']
        
        for i in range(start_index, len(lines)):
            line_lower = lines[i].lower()
            
            # Check if we've reached footer
            if any(keyword in line_lower for keyword in footer_keywords):
                return i
        
        return len(lines)
    
    def parse_line_item(self, line: str) -> Optional[Dict]:
        """
        Parse a single line item
        
        Args:
            line: Text line containing item data
            
        Returns:
            Dictionary with item data or None
        """
        # Skip empty lines
        if not line.strip():
            return None
        
        # Extract all numbers from the line
        numbers = re.findall(r'\d+\.?\d*', line)
        
        if len(numbers) < 2:
            return None  # Need at least quantity and price
        
        # Extract description (text before first number)
        desc_match = re.match(r'^([A-Za-z\s]+)', line)
        description = desc_match.group(1).strip() if desc_match else "Item"
        
        # Parse numbers
        # Typical format: [qty, price, tax, total] or [qty, price, total]
        try:
            quantity = float(numbers[0])
            unit_price = float(numbers[1]) if len(numbers) > 1 else 0.0
            
            # Determine tax and total
            if len(numbers) >= 4:
                tax = float(numbers[2])
                total = float(numbers[3])
            elif len(numbers) == 3:
                tax = 0.0
                total = float(numbers[2])
            else:
                tax = 0.0
                total = quantity * unit_price
            
            return {
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
                "price": unit_price,
                "tax": tax,
                "discount": 0.0,
                "total": total
            }
        
        except (ValueError, IndexError):
            return None
    
    def extract_line_items(self, text: str) -> List[Dict]:
        """
        Extract all line items from invoice text
        
        Args:
            text: OCR extracted text
            
        Returns:
            List of line item dictionaries
        """
        lines = text.split('\n')
        line_items = []
        
        # Find table boundaries
        table_start = self.find_table_start(lines)
        
        if table_start == -1:
            return line_items  # No table found
        
        table_end = self.find_table_end(lines, table_start)
        
        # Extract items from table rows
        for i in range(table_start, table_end):
            if i >= len(lines):
                break
            
            line = lines[i].strip()
            
            # Parse line item
            item = self.parse_line_item(line)
            
            if item:
                line_items.append(item)
        
        return line_items
    
    def extract_with_patterns(self, text: str) -> List[Dict]:
        """
        Extract line items using pattern matching
        
        Args:
            text: OCR extracted text
            
        Returns:
            List of line items
        """
        line_items = []
        
        # Pattern: Description followed by numbers
        pattern = r'([A-Za-z\s]+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)'
        
        matches = re.findall(pattern, text)
        
        for match in matches:
            try:
                description = match[0].strip()
                quantity = float(match[1])
                unit_price = float(match[2])
                total = float(match[3])
                
                line_items.append({
                    "description": description,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "price": unit_price,
                    "tax": 0.0,
                    "discount": 0.0,
                    "total": total
                })
            
            except (ValueError, IndexError):
                continue
        
        return line_items
    
    def extract_table_data(self, text: str) -> dict:
        """
        Extract complete table data
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with table extraction results
        """
        # Try primary extraction method
        line_items = self.extract_line_items(text)
        
        # If no items found, try pattern matching
        if not line_items:
            line_items = self.extract_with_patterns(text)
        
        return {
            "success": len(line_items) > 0,
            "line_items": line_items,
            "item_count": len(line_items),
            "message": f"Extracted {len(line_items)} line item(s)" if line_items else "No line items found"
        }


# Create singleton instance
table_extractor = TableExtractor()
