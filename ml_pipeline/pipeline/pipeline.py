"""
Main pipeline: orchestrates all stages and returns structured output.

Input : file_path (PDF, PNG, JPG)
Output: PipelineResult containing per-invoice structured data
"""
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any

import numpy as np

from pipeline.logging_utils import get_logger
from pipeline.preprocessor import preprocess
from pipeline.ocr import run_ocr, OcrResult
from pipeline.page_classifier import classify_pages
from pipeline.invoice_segmenter import segment_invoices
from pipeline.field_extractor import extract_fields, ExtractedFields
from pipeline.table_extractor import extract_line_items, LineItem
from pipeline.validator import validate_invoice, compute_invoice_confidence

log = get_logger("PIPELINE")


# ── Output models ─────────────────────────────────────────────────────────────

@dataclass
class LineItemOut:
    description: str
    quantity: Optional[float]
    unit_price: Optional[float]
    tax_amount: float
    discount_amount: float
    line_total: Optional[float]


@dataclass
class InvoiceOut:
    invoice_id: str
    invoice_number: Optional[str]
    seller_name: Optional[str]
    buyer_name: Optional[str]
    issue_date: Optional[str]
    currency: Optional[str]
    subtotal: Optional[float]
    tax_amount: Optional[float]
    discount_amount: Optional[float]
    total_amount: Optional[float]
    payment_terms_days: Optional[int]
    page_start: int
    page_end: int
    line_items: List[LineItemOut]
    validation_errors: List[str]
    confidence_score: float


@dataclass
class PipelineResult:
    document_id: str
    file_path: str
    document_type: str
    invoice_count: int
    invoices: List[InvoiceOut]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Document type inference ───────────────────────────────────────────────────

def _infer_document_type(
    invoice_count: int,
    has_non_invoice_pages: bool,
    invoice_numbers: List[Optional[str]],
) -> str:
    """
    Classify the document. A `repeated_invoice_copy` is the case where every
    detected invoice carries the SAME invoice number — i.e. the whole document
    is just copies of one invoice. A `multiple_invoices` document with one
    stray duplicate is still `multiple_invoices`.
    """
    if invoice_count == 0:
        return "non_invoice_document"

    if invoice_count >= 2:
        non_null = [n.strip() for n in invoice_numbers if n and n.strip()]
        all_same = (
            len(non_null) == invoice_count and len(set(non_null)) == 1
        )
        if all_same:
            return "repeated_invoice_copy"
        return "multiple_invoices"

    # Single detected invoice
    if has_non_invoice_pages:
        return "invoice_with_extra_pages"
    return "single_invoice"


# ── Core run ──────────────────────────────────────────────────────────────────

def run(file_path: str, document_id: Optional[str] = None) -> PipelineResult:
    if document_id is None:
        document_id = Path(file_path).stem

    log.info(f"=== Pipeline START | document_id={document_id} | file={Path(file_path).name} ===")
    t0 = time.perf_counter()

    # Stage 1: Preprocess
    page_tuples = preprocess(file_path)
    page_images = [img for img, _ in page_tuples]

    # Stage 2: OCR all pages
    log.info(f"Starting OCR on {len(page_images)} page(s)")
    ocr_results: List[OcrResult] = [run_ocr(img) for img in page_images]
    page_texts: List[str] = [r.full_text for r in ocr_results]

    # Stage 3: Page classification
    page_labels = classify_pages(page_texts)

    # Stage 4: Invoice segmentation
    segments = segment_invoices(page_labels, page_texts)

    if not segments:
        log.info(
            f"=== Pipeline END | non_invoice_document | "
            f"elapsed={time.perf_counter() - t0:.2f}s ==="
        )
        return PipelineResult(
            document_id=document_id,
            file_path=file_path,
            document_type="non_invoice_document",
            invoice_count=0,
            invoices=[],
        )

    # Stage 5–7: Per-segment extraction and validation
    invoices_out: List[InvoiceOut] = []
    all_invoice_numbers: List[Optional[str]] = []

    for seg_idx, seg in enumerate(segments):
        page_start = seg["page_start"]
        page_end = seg["page_end"]
        has_non_inv = seg.get("has_non_invoice_pages", False)
        log.info(
            f"Processing invoice {seg_idx + 1}/{len(segments)} "
            f"(pages {page_start}-{page_end})"
        )

        # Collect pages for this segment
        seg_pages = page_images[page_start - 1: page_end]
        seg_ocr = ocr_results[page_start - 1: page_end]
        combined_text = "\n".join(r.full_text for r in seg_ocr)
        avg_ocr_conf = (
            sum(r.avg_confidence for r in seg_ocr) / len(seg_ocr) if seg_ocr else 0.5
        )

        # Stage 5: Field extraction
        ef: ExtractedFields = extract_fields(combined_text, avg_ocr_conf)
        all_invoice_numbers.append(ef.invoice_number)

        # Stage 6: Table extraction
        raw_items: List[LineItem] = extract_line_items(
            file_path, seg_pages, page_start, page_end
        )
        line_items_out = [
            LineItemOut(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_amount=item.tax_amount,
                discount_amount=item.discount_amount,
                line_total=item.line_total,
            )
            for item in raw_items
        ]

        # Stage 7: Validation (partial — duplicate check done after all invoices)
        errors = validate_invoice(
            line_items=[li.__dict__ for li in line_items_out],
            subtotal=ef.subtotal,
            tax_amount=ef.tax_amount,
            discount_amount=ef.discount_amount,
            total_amount=ef.total_amount,
            invoice_number=ef.invoice_number,
            all_invoice_numbers_in_doc=[],  # filled after
            has_non_invoice_pages=has_non_inv,
        )

        conf = compute_invoice_confidence(ef.confidence, [li.__dict__ for li in line_items_out], avg_ocr_conf)

        invoices_out.append(InvoiceOut(
            invoice_id=f"{document_id}_inv_{seg_idx + 1}",
            invoice_number=ef.invoice_number,
            seller_name=ef.seller_name,
            buyer_name=ef.buyer_name,
            issue_date=ef.issue_date,
            currency=ef.currency,
            subtotal=ef.subtotal,
            tax_amount=ef.tax_amount,
            discount_amount=ef.discount_amount,
            total_amount=ef.total_amount,
            payment_terms_days=ef.payment_terms_days,
            page_start=page_start,
            page_end=page_end,
            line_items=line_items_out,
            validation_errors=errors,
            confidence_score=conf,
        ))

    # Post-pass: add duplicate_invoice_in_document errors
    for inv in invoices_out:
        occurrences = sum(
            1 for n in all_invoice_numbers
            if n and inv.invoice_number and n.strip() == inv.invoice_number.strip()
        )
        if occurrences > 1 and "duplicate_invoice_in_document" not in inv.validation_errors:
            inv.validation_errors.append("duplicate_invoice_in_document")

    has_non_invoice_pages = any(
        "non_invoice_page_detected" in inv.validation_errors for inv in invoices_out
    )

    doc_type = _infer_document_type(
        invoice_count=len(invoices_out),
        has_non_invoice_pages=has_non_invoice_pages,
        invoice_numbers=[inv.invoice_number for inv in invoices_out],
    )

    elapsed = time.perf_counter() - t0
    log.info(
        f"=== Pipeline END | document_type={doc_type} | "
        f"invoices={len(invoices_out)} | elapsed={elapsed:.2f}s ==="
    )

    return PipelineResult(
        document_id=document_id,
        file_path=file_path,
        document_type=doc_type,
        invoice_count=len(invoices_out),
        invoices=invoices_out,
    )
