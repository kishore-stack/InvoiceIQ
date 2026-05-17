"""
Validator: checks mathematical consistency of extracted invoice data
and flags all required error types.
"""
from typing import List, Optional, Dict, Any, Set

from pipeline.logging_utils import get_logger

log = get_logger("VALIDATION")

TOLERANCE = 0.02  # 2% tolerance for floating point / OCR rounding


def _within_tolerance(a: float, b: float) -> bool:
    if b == 0:
        return abs(a) < 0.01
    return abs(a - b) / abs(b) <= TOLERANCE


def validate_invoice(
    line_items: List[Dict[str, Any]],
    subtotal: Optional[float],
    tax_amount: Optional[float],
    discount_amount: Optional[float],
    total_amount: Optional[float],
    invoice_number: Optional[str],
    all_invoice_numbers_in_doc: List[Optional[str]],
    has_non_invoice_pages: bool = False,
) -> List[str]:
    """
    Returns a list of validation_error strings for this invoice.
    """
    errors: List[str] = []

    # missing_invoice_number
    if not invoice_number or invoice_number.strip() == "":
        errors.append("missing_invoice_number")

    # missing_line_items
    if not line_items:
        errors.append("missing_line_items")

    # subtotal_mismatch
    if line_items and subtotal is not None:
        computed_subtotal = sum(
            item.get("line_total") or 0.0 for item in line_items
        )
        if not _within_tolerance(computed_subtotal, subtotal):
            errors.append("subtotal_mismatch")

    # tax_mismatch — check if tax_amount is consistent with subtotal
    # (We don't know the tax rate, so we only flag if both subtotal and tax exist
    # and tax > subtotal, which is clearly wrong)
    if subtotal is not None and tax_amount is not None:
        if tax_amount > subtotal * 1.30:
            errors.append("tax_mismatch")
        # Also check: subtotal + tax - discount ≈ total
        disc = discount_amount or 0.0
        if total_amount is not None:
            computed_total = subtotal + tax_amount - disc
            if not _within_tolerance(computed_total, total_amount):
                if "total_mismatch" not in errors:
                    errors.append("total_mismatch")

    # discount_mismatch — flag if discount > 30% of subtotal
    if subtotal is not None and discount_amount is not None and subtotal > 0:
        if discount_amount > subtotal * 0.31:
            errors.append("discount_mismatch")

    # total_mismatch
    if subtotal is not None and total_amount is not None:
        tax = tax_amount or 0.0
        disc = discount_amount or 0.0
        computed = subtotal + tax - disc
        if not _within_tolerance(computed, total_amount):
            if "total_mismatch" not in errors:
                errors.append("total_mismatch")

    # duplicate_invoice_in_document
    if invoice_number:
        occurrences = sum(
            1 for n in all_invoice_numbers_in_doc
            if n and n.strip() == invoice_number.strip()
        )
        if occurrences > 1:
            errors.append("duplicate_invoice_in_document")

    # non_invoice_page_detected
    if has_non_invoice_pages:
        errors.append("non_invoice_page_detected")

    if errors:
        log.warning(f"Validation flagged {len(errors)} issue(s): {', '.join(errors)}")
    else:
        log.info("Validation passed — invoice is mathematically consistent")
    return errors


def compute_invoice_confidence(
    fields_confidence: Dict[str, float],
    line_items: List[Dict[str, Any]],
    ocr_avg_conf: float,
) -> float:
    """Weighted average confidence score for the whole invoice."""
    weights = {
        "invoice_number": 2.0,
        "seller_name": 1.5,
        "buyer_name": 1.5,
        "issue_date": 1.0,
        "currency": 1.0,
        "subtotal": 2.0,
        "total_amount": 2.0,
        "tax_amount": 1.0,
        "discount_amount": 0.5,
        "payment_terms_days": 0.5,
    }

    total_w, weighted_sum = 0.0, 0.0
    for field_name, w in weights.items():
        conf = fields_confidence.get(field_name, 0.0)
        weighted_sum += conf * w
        total_w += w

    # Penalise if no line items extracted
    if not line_items:
        weighted_sum *= 0.7

    base = weighted_sum / total_w if total_w > 0 else 0.0
    # Blend with raw OCR confidence
    return round(base * 0.7 + ocr_avg_conf * 0.3, 3)
