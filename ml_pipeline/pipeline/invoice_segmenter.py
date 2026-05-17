"""
Invoice segmenter: groups invoice pages into logical invoice units.

Strategy:
  - Scan pages left to right.
  - A new invoice starts when:
      (a) A new invoice number pattern appears after a total block has been seen, OR
      (b) A fresh "Bill To / Invoice" header appears on a page that follows a totals block.
  - Non-invoice pages are excluded from invoice spans but noted.
"""
import re
from typing import List, Tuple, Dict, Any

from pipeline.logging_utils import get_logger

log = get_logger("SEGMENTATION")

INVOICE_NUMBER_RE = re.compile(
    r"(?i)(?:invoice|inv)[\s#:\-]*([A-Z0-9][\w\-/]{2,})",
    re.IGNORECASE,
)

TOTAL_SIGNAL_RE = re.compile(
    r"(?i)(total\s+amount|amount\s+due|grand\s+total|balance\s+due)",
)

HEADER_SIGNAL_RE = re.compile(
    r"(?i)(invoice\s+(no|number|#)|bill\s+to|sold\s+to)",
)


def _has_invoice_number(text: str) -> bool:
    return bool(INVOICE_NUMBER_RE.search(text))


def _has_total_signal(text: str) -> bool:
    return bool(TOTAL_SIGNAL_RE.search(text))


def _has_header_signal(text: str) -> bool:
    return bool(HEADER_SIGNAL_RE.search(text))


def segment_invoices(
    page_labels: List[Tuple[str, float]],
    page_texts: List[str],
) -> List[Dict[str, Any]]:
    """
    Returns a list of invoice segment dicts:
    {
        "page_start": int,   # 1-indexed
        "page_end": int,
        "non_invoice_pages": List[int],
    }
    """
    assert len(page_labels) == len(page_texts)

    invoice_pages = []
    non_invoice_pages = []

    for i, ((label, _conf), text) in enumerate(zip(page_labels, page_texts)):
        page_num = i + 1
        if label == "invoice_page":
            invoice_pages.append((page_num, text))
        else:
            non_invoice_pages.append(page_num)

    if not invoice_pages:
        log.warning("No invoice pages detected — document will be classified as non_invoice_document")
        return []

    # Group consecutive invoice pages; split on new invoice header after a totals block
    segments: List[Dict[str, Any]] = []
    current_start = invoice_pages[0][0]
    current_end = invoice_pages[0][0]
    seen_total = False

    for page_num, text in invoice_pages[1:]:
        is_new_invoice = False

        if seen_total and (_has_header_signal(text) or _has_invoice_number(text)):
            is_new_invoice = True

        if is_new_invoice:
            segments.append({
                "page_start": current_start,
                "page_end": current_end,
                "non_invoice_pages": [p for p in non_invoice_pages
                                      if current_start <= p <= current_end],
            })
            current_start = page_num
            seen_total = False

        if _has_total_signal(text):
            seen_total = True

        current_end = page_num

    # Close final segment
    segments.append({
        "page_start": current_start,
        "page_end": current_end,
        "non_invoice_pages": [p for p in non_invoice_pages
                              if current_start <= p <= current_end],
    })

    # If no segmentation happened but non-invoice pages exist, flag them
    if not segments:
        return []

    for seg in segments:
        if non_invoice_pages:
            seg["has_non_invoice_pages"] = bool(seg["non_invoice_pages"])

    log.info(f"Detected {len(segments)} invoice segment(s) across {len(page_texts)} page(s)")
    for i, seg in enumerate(segments, 1):
        log.debug(
            f"Segment {i}: pages {seg['page_start']}-{seg['page_end']}"
            + (f", non-invoice pages: {seg['non_invoice_pages']}" if seg.get("non_invoice_pages") else "")
        )
    return segments
