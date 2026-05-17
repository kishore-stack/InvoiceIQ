"""
Unit Tests for Invoice Validator
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from validator.invoice_validator import invoice_validator

def test_invoice_validation():
    print("Testing Invoice Validator...")
    
    # Valid Invoice Data
    valid_data = {
        "invoice_number": "INV-101",
        "seller_name": "Tech Corp",
        "buyer_name": "Client LLC",
        "subtotal": 1000.00,
        "tax_amount": 100.00,
        "discount": 50.00,
        "total_amount": 1050.00,
        "seller_gst": "22AAAAA0000A1Z5"
    }
    
    result = invoice_validator.validate_invoice(valid_data)
    assert result["validation_status"] == True, f"Validation failed for valid data: {result['errors']}"
    assert len(result["errors"]) == 0
    
    # Invalid Calculation Data
    invalid_data = valid_data.copy()
    invalid_data["total_amount"] = 1200.00 # Incorrect total
    
    result2 = invoice_validator.validate_invoice(invalid_data)
    assert result2["validation_status"] == False, "Validation should fail for incorrect calculation"
    assert len(result2["errors"]) > 0
    assert "Calculation mismatch" in result2["errors"][0]
    
    # Missing Required Field
    missing_data = valid_data.copy()
    missing_data["seller_name"] = None
    
    result3 = invoice_validator.validate_invoice(missing_data)
    assert result3["validation_status"] == False
    assert any("Missing required field" in err for err in result3["errors"])
    
    # Invalid GST
    gst_data = valid_data.copy()
    gst_data["seller_gst"] = "INVALID123"
    
    result4 = invoice_validator.validate_invoice(gst_data)
    assert result4["validation_status"] == False
    assert any("Invalid GST format" in err for err in result4["errors"])
    
    print("Success: Invoice Validator tests passed!")

if __name__ == "__main__":
    test_invoice_validation()
