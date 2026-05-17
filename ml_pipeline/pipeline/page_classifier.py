"""
Page classifier: determines whether a page is an invoice page or not.
Uses keyword density scoring — no ML model required.
"""
import re
from typing import List, Tuple

from pipeline.logging_utils import get_logger

log = get_logger("PAGE CLASSIFIER")

INVOICE_KEYWORDS = [
    r"\binvoice\b", r"\bbill\s+to\b", r"\bsold\s+to\b", r"\bship\s+to\b",
    r"\bsubtotal\b", r"\btotal\s+amount\b", r"\bamount\s+due\b",
    r"\bpayment\s+terms?\b", r"\bdue\s+date\b", r"\bissue\s+date\b",
    r"\binvoice\s+(no|number|#|num)\b", r"\bunit\s+price\b",
    r"\bline\s+total\b", r"\btax\s+amount\b", r"\bdiscount\b",
    r"\bquantity\b", r"\bqty\b", r"\bdescription\b",
    r"\bremit\s+to\b", r"\bpurchase\s+order\b",
]

NON_INVOICE_KEYWORDS = [
    r"\bterms\s+and\s+conditions\b", r"\bprivacy\s+policy\b",
    r"\brefund\s+policy\b", r"\bwarranty\b", r"\blegal\s+notice\b",
    r"\bcopyright\b", r"\ball\s+rights\s+reserved\b",
    r"\btable\s+of\s+contents\b", r"\bappendix\b", r"\bglossary\b",
]


def _count_matches(text: str, patterns: List[str]) -> int:
    text_lower = text.lower()
    return sum(1 for p in patterns if re.search(p, text_lower))


def classify_page(text: str) -> Tuple[str, float]:
    """
    Classify a page's OCR text.

    Returns:
        (label, confidence)
        label ∈ {"invoice_page", "non_invoice_page"}
        confidence: 0.0 – 1.0
    """
    if not text or len(text.strip()) < 20:
        return "non_invoice_page", 0.90

    inv_hits = _count_matches(text, INVOICE_KEYWORDS)
    non_hits = _count_matches(text, NON_INVOICE_KEYWORDS)

    total_patterns = len(INVOICE_KEYWORDS)
    inv_score = inv_hits / total_patterns

    # Strong non-invoice signals override
    if non_hits >= 3 and inv_hits <= 2:
        conf = min(0.95, 0.70 + non_hits * 0.05)
        return "non_invoice_page", conf

    if inv_hits >= 3:
        conf = min(0.98, 0.60 + inv_hits * 0.04)
        return "invoice_page", conf

    if inv_hits >= 1:
        return "invoice_page", 0.55

    return "non_invoice_page", 0.65


def classify_pages(texts: List[str]) -> List[Tuple[str, float]]:
    results = [classify_page(t) for t in texts]
    inv = sum(1 for label, _ in results if label == "invoice_page")
    non_inv = len(results) - inv
    log.info(f"Classified {len(results)} page(s): {inv} invoice, {non_inv} non-invoice")
    for i, (label, conf) in enumerate(results, 1):
        log.debug(f"Page {i}: {label} (conf={conf:.2f})")
    return results
