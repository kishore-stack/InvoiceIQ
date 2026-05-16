"""
Invoice Validator - Validation Engine for Invoice Data
Member 2: Backend Engineer

Validates invoice calculations and detects anomalies
"""

from typing import Dict, List, Tuple, Optional

class InvoiceValidator:
    """
    Validates invoice data and detects calculation errors
    """
    
    def __init__(self):
        # Tolerance for floating point comparisons (1 cent)
        self.tolerance = 0.01
    
    def validate_required_fields(self, invoice_data: dict) -> Tuple[bool, List[str]]:
        """
        Validate that required fields are present
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        required_fields = ['invoice_number', 'seller_name', 'buyer_name', 'total_amount']
        
        for field in required_fields:
            if not invoice_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        return len(errors) == 0, errors
    
    def validate_amounts(self, invoice_data: dict) -> Tuple[bool, List[str]]:
        """
        Validate that amounts are positive and valid
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check total amount
        total = invoice_data.get('total_amount')
        if total is not None:
            if total < 0:
                errors.append("Total amount cannot be negative")
            if total == 0:
                errors.append("Total amount cannot be zero")
        
        # Check subtotal
        subtotal = invoice_data.get('subtotal')
        if subtotal is not None and subtotal < 0:
            errors.append("Subtotal cannot be negative")
        
        # Check tax
        tax = invoice_data.get('tax_amount')
        if tax is not None and tax < 0:
            errors.append("Tax amount cannot be negative")
        
        # Check discount
        discount = invoice_data.get('discount', 0)
        if discount < 0:
            errors.append("Discount cannot be negative")
        
        return len(errors) == 0, errors
    
    def validate_calculation(self, invoice_data: dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate invoice calculation: subtotal + tax - discount = total
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            Tuple of (is_valid, list of errors, list of warnings)
        """
        errors = []
        warnings = []
        
        subtotal = invoice_data.get('subtotal')
        tax = invoice_data.get('tax_amount')
        discount = invoice_data.get('discount', 0)
        total = invoice_data.get('total_amount')
        
        # Check if we have enough data to validate
        if subtotal is None or tax is None or total is None:
            warnings.append("Insufficient data for calculation validation")
            return True, errors, warnings
        
        # Calculate expected total
        expected_total = subtotal + tax - discount
        
        # Check if matches actual total
        difference = abs(expected_total - total)
        
        if difference > self.tolerance:
            errors.append(
                f"Calculation mismatch: Expected {expected_total:.2f}, "
                f"Found {total:.2f} (Difference: {difference:.2f})"
            )
            return False, errors, warnings
        
        return True, errors, warnings
    
    def validate_gst_format(self, gst_number: Optional[str]) -> Tuple[bool, List[str]]:
        """
        Validate GST number format
        
        Args:
            gst_number: GST number string
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        if not gst_number:
            return True, errors  # GST is optional
        
        # GST format: 22AAAAA0000A1Z5 (15 characters)
        if len(gst_number) != 15:
            errors.append(f"Invalid GST format: {gst_number} (should be 15 characters)")
            return False, errors
        
        # Basic format check
        import re
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        
        if not re.match(gst_pattern, gst_number):
            errors.append(f"Invalid GST format: {gst_number}")
            return False, errors
        
        return True, errors
    
    def validate_invoice(self, invoice_data: dict) -> dict:
        """
        Complete invoice validation
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            Validation result dictionary
        """
        all_errors = []
        all_warnings = []
        
        # Validate required fields
        valid_fields, field_errors = self.validate_required_fields(invoice_data)
        all_errors.extend(field_errors)
        
        # Validate amounts
        valid_amounts, amount_errors = self.validate_amounts(invoice_data)
        all_errors.extend(amount_errors)
        
        # Validate calculation
        valid_calc, calc_errors, calc_warnings = self.validate_calculation(invoice_data)
        all_errors.extend(calc_errors)
        all_warnings.extend(calc_warnings)
        
        # Validate GST numbers
        seller_gst = invoice_data.get('seller_gst')
        if seller_gst:
            valid_gst, gst_errors = self.validate_gst_format(seller_gst)
            all_errors.extend(gst_errors)
        
        buyer_gst = invoice_data.get('buyer_gst')
        if buyer_gst:
            valid_gst, gst_errors = self.validate_gst_format(buyer_gst)
            all_errors.extend(gst_errors)
        
        # Determine overall status
        is_valid = len(all_errors) == 0
        
        if is_valid:
            status = "valid"
        elif len(all_warnings) > 0 and len(all_errors) == 0:
            status = "review"
        else:
            status = "invalid"
        
        return {
            "is_valid": is_valid,
            "validation_status": status,
            "errors": all_errors,
            "warnings": all_warnings
        }
    
    def detect_anomalies(self, invoice_data: dict) -> List[str]:
        """
        Detect potential anomalies in invoice data
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for unusually high amounts
        total = invoice_data.get('total_amount', 0)
        if total > 1000000:  # 10 lakhs
            anomalies.append(f"Unusually high total amount: ₹{total:,.2f}")
        
        # Check for missing GST on high-value invoices
        if total > 50000 and not invoice_data.get('seller_gst'):
            anomalies.append("High-value invoice without GST number")
        
        # Check for discount higher than subtotal
        discount = invoice_data.get('discount', 0)
        subtotal = invoice_data.get('subtotal', 0)
        if discount > subtotal:
            anomalies.append(f"Discount (₹{discount:.2f}) exceeds subtotal (₹{subtotal:.2f})")
        
        # Check for tax rate anomalies
        tax = invoice_data.get('tax_amount', 0)
        if subtotal > 0:
            tax_rate = (tax / subtotal) * 100
            if tax_rate > 30:
                anomalies.append(f"Unusually high tax rate: {tax_rate:.1f}%")
        
        return anomalies


# Create singleton instance
invoice_validator = InvoiceValidator()
