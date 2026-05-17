"""
Unit Tests for Table Extractor
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from extractor.table_extractor import table_extractor

def test_table_extraction():
    print("Testing Table Extractor...")
    
    # Mock OCR text
    mock_text = """
    INVOICE
    Date: 2023-10-01
    
    Description    Quantity    Unit Price    Total
    Laptop Pro      1.0         1200.00      1200.00
    Wireless Mouse  2.0         25.00        50.00
    USB-C Cable     3.0         10.00        30.00
    
    Subtotal: 1280.00
    Tax: 128.00
    Total: 1408.00
    """
    
    result = table_extractor.extract_table_data(mock_text)
    
    assert result["success"] == True, "Table extraction should succeed"
    assert result["item_count"] == 3, f"Expected 3 items, got {result['item_count']}"
    
    items = result["line_items"]
    assert items[0]["item"].strip() == "Laptop Pro", f"Got description: {items[0]['item']}"
    assert items[0]["quantity"] == 1.0
    assert items[0]["line_total"] == 1200.0
    
    assert items[1]["item"].strip() == "Wireless Mouse"
    assert items[1]["quantity"] == 2.0
    assert items[1]["line_total"] == 50.0
    
    print("Success: Table Extractor tests passed!")

if __name__ == "__main__":
    test_table_extraction()
