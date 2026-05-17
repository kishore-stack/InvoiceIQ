"""
Main dataset generation script.
Produces 500 synthetic invoice documents with annotations.json,
train_manifest.csv, and test_manifest.csv.

Usage:
    python -m generator.generate --output-dir . --count 500
"""
import os
import io
import json
import random
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple

import fitz  # PyMuPDF
from PIL import Image
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4

from generator.faker_data import generate_invoice_data, pick_error_set
from generator.templates import TEMPLATES, draw_terms_page, pick_template
from generator.augment import augment_image, pick_noise_level
from pipeline.logging_utils import get_logger

log = get_logger("GENERATOR")

random.seed(42)
PAGE_W, PAGE_H = A4

# ── Document type distribution ────────────────────────────────────────────────

# Distribution for the default 800-doc dataset. Keeps multi-invoice share
# at ~35% (above the 25% requirement) while expanding stress-test coverage:
# each type gets enough volume that the new edge cases (merged headers, long
# page-spanning tables, CGST/SGST/Cess tax breakdowns) appear in every
# document type with statistical significance.
DOC_TYPES = [
    "single_invoice",
    "multiple_invoices",
    "invoice_with_extra_pages",
    "repeated_invoice_copy",
    "non_invoice_document",
]

DOC_TYPE_COUNTS = {
    "single_invoice": 280,
    "multiple_invoices": 280,
    "invoice_with_extra_pages": 120,
    "repeated_invoice_copy": 80,
    "non_invoice_document": 40,
}

# ── Core rendering ────────────────────────────────────────────────────────────

def render_invoices_to_pdf(
    invoice_data_list: List[Dict[str, Any]],
    include_terms: bool = False,
    include_cover: bool = False,
) -> Tuple[bytes, List[Tuple[int, int]]]:
    """
    Render one or more invoices into a PDF.

    Returns:
        (pdf_bytes, page_ranges) where page_ranges[i] = (page_start, page_end)
        for the i-th invoice (1-indexed).
    """
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    page_ranges: List[Tuple[int, int]] = []

    for idx, inv in enumerate(invoice_data_list):
        if idx > 0:
            c.showPage()
        page_start = c.getPageNumber()
        template_fn = pick_template()
        template_fn(c, inv, PAGE_H - 20)
        page_end = c.getPageNumber()
        page_ranges.append((page_start, page_end))

    if include_terms:
        c.showPage()
        draw_terms_page(c)

    c.save()
    return buf.getvalue(), page_ranges


def pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> List[Image.Image]:
    """Convert PDF bytes to list of PIL images."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images


def images_to_pdf(images: List[Image.Image]) -> bytes:
    """Convert list of PIL images back to a PDF."""
    buf = io.BytesIO()
    if len(images) == 1:
        images[0].save(buf, format="PDF")
    else:
        images[0].save(buf, format="PDF", save_all=True, append_images=images[1:])
    return buf.getvalue()


# ── Document generators by type ───────────────────────────────────────────────

def make_single_invoice(doc_id: str, docs_dir: Path, noise_level: str) -> Dict[str, Any]:
    errors = pick_error_set()
    # ~20% of singles are deliberately long (page-spanning),
    # ~25% emit a CGST/SGST/IGST tax breakdown.
    inv = generate_invoice_data(
        inject_errors=errors,
        force_long=random.random() < 0.20,
        force_multi_tax=random.random() < 0.25,
    )
    pdf_bytes, page_ranges = render_invoices_to_pdf([inv])
    ps, pe = page_ranges[0]

    fmt = random.choices(["pdf", "png", "jpg"], weights=[40, 35, 25])[0]
    file_path, _ = _save_document(pdf_bytes, doc_id, fmt, noise_level, docs_dir)

    return {
        "document_id": doc_id,
        "document_type": "single_invoice",
        "invoice_count": 1,
        "file_path": file_path,
        "noise_level": noise_level,
        "invoices": [_build_invoice_annotation(inv, doc_id, 0, ps, pe)],
    }


def make_multiple_invoices(doc_id: str, docs_dir: Path, noise_level: str) -> Dict[str, Any]:
    count = random.randint(2, 5)
    invoice_data_list = []
    for _ in range(count):
        errors = pick_error_set()
        invoice_data_list.append(generate_invoice_data(
            inject_errors=errors,
            force_long=random.random() < 0.15,
            force_multi_tax=random.random() < 0.25,
        ))

    # Inject a duplicate-number error in ~10% of multi-invoice docs.
    # Document type stays "multiple_invoices" — only one invoice carries
    # the duplicate flag.
    inject_dup = random.random() < 0.10
    if inject_dup and len(invoice_data_list) >= 2:
        invoice_data_list[1]["invoice_number"] = invoice_data_list[0]["invoice_number"]

    pdf_bytes, page_ranges = render_invoices_to_pdf(invoice_data_list)
    fmt = "pdf"
    file_path, _ = _save_document(pdf_bytes, doc_id, fmt, noise_level, docs_dir)

    annotations = []
    for i, inv in enumerate(invoice_data_list):
        ps, pe = page_ranges[i]
        if inject_dup and i == 1:
            inv["validation_errors"] = list(set(inv["validation_errors"] + ["duplicate_invoice_in_document"]))
        annotations.append(_build_invoice_annotation(inv, doc_id, i, ps, pe))

    return {
        "document_id": doc_id,
        "document_type": "multiple_invoices",
        "invoice_count": count,
        "file_path": file_path,
        "noise_level": noise_level,
        "invoices": annotations,
    }


def make_invoice_with_extra_pages(doc_id: str, docs_dir: Path, noise_level: str) -> Dict[str, Any]:
    inv = generate_invoice_data(
        inject_errors=pick_error_set(),
        force_long=random.random() < 0.20,
        force_multi_tax=random.random() < 0.25,
    )
    pdf_bytes, page_ranges = render_invoices_to_pdf([inv], include_terms=True)
    ps, pe = page_ranges[0]
    fmt = "pdf"
    file_path, _ = _save_document(pdf_bytes, doc_id, fmt, noise_level, docs_dir)

    ann = _build_invoice_annotation(inv, doc_id, 0, ps, pe)
    ann["validation_errors"] = list(set(ann["validation_errors"] + ["non_invoice_page_detected"]))

    return {
        "document_id": doc_id,
        "document_type": "invoice_with_extra_pages",
        "invoice_count": 1,
        "file_path": file_path,
        "noise_level": noise_level,
        "invoices": [ann],
    }


def make_repeated_invoice_copy(doc_id: str, docs_dir: Path, noise_level: str) -> Dict[str, Any]:
    # A repeated_invoice_copy contains two rendered copies of the same invoice.
    # invoice_count reflects the number of invoice instances present (2), so
    # it matches what the segmenter will detect at inference time.
    inv = generate_invoice_data(inject_errors=pick_error_set())
    pdf_bytes, page_ranges = render_invoices_to_pdf([inv, inv])
    fmt = "pdf"
    file_path, _ = _save_document(pdf_bytes, doc_id, fmt, noise_level, docs_dir)

    ps1, pe1 = page_ranges[0]
    ps2, pe2 = page_ranges[1]
    ann1 = _build_invoice_annotation(inv, doc_id, 0, ps1, pe1)
    ann2 = _build_invoice_annotation(inv, doc_id, 1, ps2, pe2)
    # Both copies flag the duplicate so the post-pass on the pipeline side
    # (which marks every occurrence) lines up with the ground truth.
    ann1["validation_errors"] = list(set(ann1["validation_errors"] + ["duplicate_invoice_in_document"]))
    ann2["validation_errors"] = list(set(ann2["validation_errors"] + ["duplicate_invoice_in_document"]))

    return {
        "document_id": doc_id,
        "document_type": "repeated_invoice_copy",
        "invoice_count": 2,
        "file_path": file_path,
        "noise_level": noise_level,
        "invoices": [ann1, ann2],
    }


def make_non_invoice_document(doc_id: str, docs_dir: Path, noise_level: str) -> Dict[str, Any]:
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    draw_terms_page(c)
    c.save()
    pdf_bytes = buf.getvalue()

    fmt = random.choices(["pdf", "png"], weights=[60, 40])[0]
    file_path, _ = _save_document(pdf_bytes, doc_id, fmt, noise_level, docs_dir)

    return {
        "document_id": doc_id,
        "document_type": "non_invoice_document",
        "invoice_count": 0,
        "file_path": file_path,
        "noise_level": noise_level,
        "invoices": [],
    }


# ── Save helpers ──────────────────────────────────────────────────────────────

def _save_document(
    pdf_bytes: bytes,
    doc_id: str,
    fmt: str,
    noise_level: str,
    docs_dir: Path,
) -> Tuple[str, int]:
    images = pdf_to_images(pdf_bytes)
    aug_images = [augment_image(img, noise_level) for img in images]

    if fmt == "pdf":
        final_bytes = images_to_pdf(aug_images)
        fpath = docs_dir / f"{doc_id}.pdf"
        fpath.write_bytes(final_bytes)
        return str(fpath), len(aug_images)
    elif fmt == "png":
        fpath = docs_dir / f"{doc_id}.png"
        aug_images[0].save(str(fpath), format="PNG")
        return str(fpath), 1
    else:  # jpg
        fpath = docs_dir / f"{doc_id}.jpg"
        quality = {"low": 95, "medium": 80, "high": 60}[noise_level]
        aug_images[0].save(str(fpath), format="JPEG", quality=quality)
        return str(fpath), 1


def _build_invoice_annotation(
    inv: Dict[str, Any],
    doc_id: str,
    idx: int,
    page_start: int,
    page_end: int,
) -> Dict[str, Any]:
    line_items = [
        {
            "description": item["description"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"],
            "tax_amount": item["tax_amount"],
            "discount_amount": item["discount_amount"],
            "line_total": item["line_total"],
        }
        for item in inv["line_items"]
    ]
    return {
        "invoice_id": f"{doc_id}_inv_{idx + 1}",
        "invoice_number": inv["invoice_number"],
        "seller_name": inv["seller"]["name"],
        "buyer_name": inv["buyer"]["name"],
        "issue_date": inv["issue_date"],
        "currency": inv["currency"],
        "subtotal": inv["subtotal"],
        "tax_amount": inv["tax_amount"],
        "discount_amount": inv["discount_amount"],
        "total_amount": inv["total_amount"],
        "payment_terms_days": inv["payment_terms_days"],
        "page_start": page_start,
        "page_end": page_end,
        "line_items": line_items,
        "validation_errors": inv["validation_errors"],
    }


# ── Manifest writers ──────────────────────────────────────────────────────────

def write_manifest(records: List[Dict[str, Any]], path: Path) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["document_id", "file_path", "document_type", "invoice_count"])
        writer.writeheader()
        for r in records:
            writer.writerow({
                "document_id": r["document_id"],
                "file_path": r["file_path"],
                "document_type": r["document_type"],
                "invoice_count": r["invoice_count"],
            })


# ── Main ──────────────────────────────────────────────────────────────────────

GENERATORS = {
    "single_invoice": make_single_invoice,
    "multiple_invoices": make_multiple_invoices,
    "invoice_with_extra_pages": make_invoice_with_extra_pages,
    "repeated_invoice_copy": make_repeated_invoice_copy,
    "non_invoice_document": make_non_invoice_document,
}


def generate(output_dir: str = ".", count: int = 800) -> None:
    base = Path(output_dir)
    docs_dir = base / "documents"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Build ordered list of doc types
    doc_type_list: List[str] = []
    for dtype, n in DOC_TYPE_COUNTS.items():
        doc_type_list.extend([dtype] * n)
    random.shuffle(doc_type_list)
    doc_type_list = doc_type_list[:count]

    annotations = []
    log.info(f"Generating {count} synthetic documents into {docs_dir}")

    for i, dtype in enumerate(doc_type_list):
        doc_id = f"doc_{i+1:04d}"
        noise_level = pick_noise_level()
        gen_fn = GENERATORS[dtype]

        try:
            record = gen_fn(doc_id, docs_dir, noise_level)
            annotations.append(record)
            if (i + 1) % 50 == 0:
                log.info(f"Progress: {i + 1}/{count} documents generated")
        except Exception as e:
            log.warning(f"{doc_id} ({dtype}) failed: {e}")

    ann_path = base / "annotations.json"
    with open(ann_path, "w") as f:
        json.dump(annotations, f, indent=2)
    log.info(f"Wrote {ann_path.name} ({len(annotations)} records)")

    # Split train/test 80/20 — adapts to whatever count was actually produced.
    # At --count 500 this yields the spec-required 400/100 split; at the new
    # default of 800 it yields 640/160.
    random.shuffle(annotations)
    n_total = len(annotations)
    n_test = max(100, int(round(n_total * 0.20)))
    train = annotations[:-n_test]
    test = annotations[-n_test:]

    write_manifest(train, base / "train_manifest.csv")
    write_manifest(test, base / "test_manifest.csv")
    log.info(f"Wrote train_manifest.csv ({len(train)} rows)")
    log.info(f"Wrote test_manifest.csv ({len(test)} rows)")
    log.info("Dataset generation complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=".", help="Base output directory")
    parser.add_argument("--count", type=int, default=800)
    args = parser.parse_args()
    generate(args.output_dir, args.count)
