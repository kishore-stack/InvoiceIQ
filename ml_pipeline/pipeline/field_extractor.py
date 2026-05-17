"""
Field extractor: extracts invoice-level header fields from OCR text.
Uses regex patterns, key-value proximity, and dateparser.
"""
import re
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field

import dateparser

from pipeline.logging_utils import get_logger

log = get_logger("FIELD EXTRACTION")

# ── Regex patterns ────────────────────────────────────────────────────────────

INVOICE_NUMBER_RE = re.compile(
    r"(?i)(?:invoice|inv)[\s#:\-]*([A-Z0-9][\w\-/]{2,})"
)

DATE_LABEL_RE = re.compile(
    r"(?i)(?:issue\s+date|invoice\s+date|date)[:\s]+([^\n]{6,20})"
)

DUE_DATE_RE = re.compile(
    r"(?i)(?:due\s+date|payment\s+due|due\s+by)[:\s]+([^\n]{6,20})"
)

CURRENCY_CODE_RE = re.compile(
    r"\b(USD|EUR|GBP|INR|AED|SGD|AUD|CAD|JPY|CNY|CHF|MXN|BRL|ZAR)\b"
)

CURRENCY_SYMBOL_RE = re.compile(r"([$€£₹])")

SUBTOTAL_RE = re.compile(
    r"(?i)(?:subtotal|sub[\s\-]total)[:\s]*([\d,]+\.?\d{0,2})"
)

TAX_RE = re.compile(
    r"(?i)(?:tax|vat|gst|hst)[^:\n]*[:\s]*([\d,]+\.?\d{0,2})"
)

# Sub-component tax labels (Indian GST and similar regimes). We match all
# occurrences and sum them — a single invoice can have CGST + SGST + Cess
# rows or an IGST row, and tax_amount should reflect the total tax burden.
MULTI_TAX_RE = re.compile(
    r"(?i)\b(cgst|sgst|igst|utgst|cess)\b[^:\n]*[:\s]*([\d,]+\.?\d{0,2})"
)

DISCOUNT_RE = re.compile(
    r"(?i)discount[^:]*[:\s]*([\d,]+\.?\d{0,2})"
)

TOTAL_RE = re.compile(
    r"(?i)(?:total\s+amount|amount\s+due|grand\s+total|total)[:\s]*([\d,]+\.?\d{0,2})"
)

PAYMENT_TERMS_RE = re.compile(
    r"(?i)(?:payment\s+terms?|net)[:\s]*(?:net\s*)?(\d+)\s*days?"
)

BILL_TO_RE = re.compile(
    r"(?i)(?:bill\s+to|sold\s+to|customer)[:\s]*\n?([^\n]{3,60})"
)

FROM_RE = re.compile(
    r"(?i)(?:from|vendor|seller)[:\s]*\n?([^\n]{3,60})"
)

SYMBOL_TO_CODE = {"$": "USD", "€": "EUR", "£": "GBP", "₹": "INR"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_amount(raw: str) -> Optional[float]:
    try:
        return float(raw.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def _parse_date(raw: str) -> Optional[str]:
    try:
        dt = dateparser.parse(raw.strip(), settings={"RETURN_AS_TIMEZONE_AWARE": False})
        return dt.strftime("%Y-%m-%d") if dt else None
    except Exception:
        return None


def _first_match(pattern: re.Pattern, text: str) -> Optional[str]:
    m = pattern.search(text)
    return m.group(1).strip() if m else None


# ── Main extraction ───────────────────────────────────────────────────────────

@dataclass
class ExtractedFields:
    invoice_number: Optional[str] = None
    seller_name: Optional[str] = None
    buyer_name: Optional[str] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    currency: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    total_amount: Optional[float] = None
    payment_terms_days: Optional[int] = None
    confidence: Dict[str, float] = field(default_factory=dict)


def extract_fields(text: str, avg_ocr_conf: float = 0.8) -> ExtractedFields:
    ef = ExtractedFields()

    # Invoice number
    raw_inv = _first_match(INVOICE_NUMBER_RE, text)
    if raw_inv:
        ef.invoice_number = raw_inv
        ef.confidence["invoice_number"] = avg_ocr_conf

    # Dates
    raw_date = _first_match(DATE_LABEL_RE, text)
    if raw_date:
        ef.issue_date = _parse_date(raw_date)
        ef.confidence["issue_date"] = avg_ocr_conf * (0.9 if ef.issue_date else 0.3)

    raw_due = _first_match(DUE_DATE_RE, text)
    if raw_due:
        ef.due_date = _parse_date(raw_due)

    # Currency
    code_match = CURRENCY_CODE_RE.search(text)
    if code_match:
        ef.currency = code_match.group(1)
        ef.confidence["currency"] = avg_ocr_conf
    else:
        sym_match = CURRENCY_SYMBOL_RE.search(text)
        if sym_match:
            ef.currency = SYMBOL_TO_CODE.get(sym_match.group(1), "USD")
            ef.confidence["currency"] = avg_ocr_conf * 0.8

    # Amounts — try to match in order: subtotal, tax, discount, total
    raw_sub = _first_match(SUBTOTAL_RE, text)
    if raw_sub:
        ef.subtotal = _parse_amount(raw_sub)
        ef.confidence["subtotal"] = avg_ocr_conf

    # Tax: prefer summing CGST/SGST/IGST/Cess components when present;
    # fall back to a single TAX/VAT/GST line otherwise.
    sub_components = MULTI_TAX_RE.findall(text)
    if sub_components:
        total_sub_tax = 0.0
        for _label, raw in sub_components:
            amt = _parse_amount(raw)
            if amt is not None:
                total_sub_tax += amt
        if total_sub_tax > 0:
            ef.tax_amount = round(total_sub_tax, 2)
            ef.confidence["tax_amount"] = avg_ocr_conf
            log.debug(
                f"tax_amount summed from {len(sub_components)} component(s): "
                f"{[lbl for lbl, _ in sub_components]}"
            )
    if ef.tax_amount is None:
        raw_tax = _first_match(TAX_RE, text)
        if raw_tax:
            ef.tax_amount = _parse_amount(raw_tax)
            ef.confidence["tax_amount"] = avg_ocr_conf

    raw_disc = _first_match(DISCOUNT_RE, text)
    if raw_disc:
        ef.discount_amount = _parse_amount(raw_disc)
        ef.confidence["discount_amount"] = avg_ocr_conf

    # Total — use last match to avoid matching "subtotal" line
    total_matches = TOTAL_RE.findall(text)
    if total_matches:
        ef.total_amount = _parse_amount(total_matches[-1])
        ef.confidence["total_amount"] = avg_ocr_conf

    # Payment terms
    raw_terms = _first_match(PAYMENT_TERMS_RE, text)
    if raw_terms:
        try:
            ef.payment_terms_days = int(raw_terms)
            ef.confidence["payment_terms_days"] = avg_ocr_conf
        except ValueError:
            pass

    # Seller / buyer names (heuristic — first substantial line after label)
    raw_buyer = _first_match(BILL_TO_RE, text)
    if raw_buyer:
        ef.buyer_name = raw_buyer.strip()[:80]
        ef.confidence["buyer_name"] = avg_ocr_conf * 0.85

    raw_seller = _first_match(FROM_RE, text)
    if raw_seller:
        ef.seller_name = raw_seller.strip()[:80]
        ef.confidence["seller_name"] = avg_ocr_conf * 0.85

    # Fallback: seller is usually the largest / first text block on the page
    if not ef.seller_name:
        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 4]
        if lines:
            ef.seller_name = lines[0][:80]
            ef.confidence["seller_name"] = avg_ocr_conf * 0.50
            log.debug("seller_name resolved via first-line fallback")

    extracted = [
        name for name, val in [
            ("invoice_number", ef.invoice_number),
            ("issue_date", ef.issue_date),
            ("currency", ef.currency),
            ("subtotal", ef.subtotal),
            ("tax_amount", ef.tax_amount),
            ("total_amount", ef.total_amount),
            ("seller_name", ef.seller_name),
            ("buyer_name", ef.buyer_name),
            ("payment_terms_days", ef.payment_terms_days),
        ] if val is not None
    ]
    log.info(f"Extracted {len(extracted)}/9 header fields: {', '.join(extracted) or 'none'}")
    if not ef.invoice_number:
        log.warning("invoice_number not found")
    if ef.total_amount is None:
        log.warning("total_amount not found")
    return ef
