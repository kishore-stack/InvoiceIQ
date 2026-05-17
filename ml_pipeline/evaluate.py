"""
Evaluation script: runs the extraction pipeline on all documents in
test_manifest.csv and computes accuracy against annotations.json.

Usage:
    python evaluate.py --manifest test_manifest.csv --annotations annotations.json
"""
import argparse
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional

from pipeline.logging_utils import get_logger
from pipeline.pipeline import run as run_pipeline

log = get_logger("EVALUATION")


# ── Metric helpers ────────────────────────────────────────────────────────────

def _str_match(pred: Optional[str], gt: Optional[str]) -> float:
    if gt is None:
        return 1.0
    if pred is None:
        return 0.0
    return 1.0 if pred.strip().lower() == gt.strip().lower() else 0.0


def _num_match(pred: Optional[float], gt: Optional[float], tol: float = 0.02) -> float:
    if gt is None:
        return 1.0
    if pred is None:
        return 0.0
    if gt == 0:
        return 1.0 if abs(pred) < 0.01 else 0.0
    return 1.0 if abs(pred - gt) / abs(gt) <= tol else 0.0


def _errors_match(pred: List[str], gt: List[str]) -> Dict[str, float]:
    gt_set = set(gt)
    pred_set = set(pred)
    all_errors = {
        "subtotal_mismatch", "tax_mismatch", "discount_mismatch",
        "total_mismatch", "missing_invoice_number", "missing_line_items",
        "duplicate_invoice_in_document", "non_invoice_page_detected",
    }
    tp = len(gt_set & pred_set)
    fp = len(pred_set - gt_set)
    fn = len(gt_set - pred_set)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def _line_items_recall(pred_items: List[Dict], gt_items: List[Dict]) -> float:
    if not gt_items:
        return 1.0
    if not pred_items:
        return 0.0
    matched = min(len(pred_items), len(gt_items))
    return matched / len(gt_items)


# ── Main evaluation ───────────────────────────────────────────────────────────

def evaluate(manifest_path: str, annotations_path: str) -> None:
    log.info(f"Loading annotations from {annotations_path}")
    with open(annotations_path) as f:
        annotations = json.load(f)
    ann_by_id = {a["document_id"]: a for a in annotations}

    log.info(f"Loading manifest from {manifest_path}")
    with open(manifest_path, newline="") as f:
        manifest = list(csv.DictReader(f))
    log.info(f"Evaluating {len(manifest)} documents")

    metrics = {
        "invoice_count_acc": [],
        "doc_type_acc": [],
        "invoice_number_acc": [],
        "seller_name_acc": [],
        "buyer_name_acc": [],
        "currency_acc": [],
        "subtotal_acc": [],
        "total_acc": [],
        "tax_acc": [],
        "validation_f1": [],
        "line_item_recall": [],
    }

    processed = 0
    failed = 0

    for row in manifest:
        doc_id = row["document_id"]
        file_path = row["file_path"]
        gt = ann_by_id.get(doc_id)

        if not gt or not Path(file_path).exists():
            failed += 1
            continue

        try:
            result = run_pipeline(file_path, document_id=doc_id)
        except Exception as e:
            log.error(f"{doc_id} pipeline failed: {e}")
            failed += 1
            continue

        processed += 1

        # Document-level
        metrics["invoice_count_acc"].append(1.0 if result.invoice_count == gt["invoice_count"] else 0.0)
        metrics["doc_type_acc"].append(_str_match(result.document_type, gt["document_type"]))

        # Per-invoice alignment (match by index)
        gt_invoices = gt.get("invoices", [])
        pred_invoices = result.invoices

        for i, gt_inv in enumerate(gt_invoices):
            if i >= len(pred_invoices):
                # Missing predicted invoice
                metrics["invoice_number_acc"].append(0.0)
                metrics["subtotal_acc"].append(0.0)
                metrics["total_acc"].append(0.0)
                metrics["validation_f1"].append(0.0)
                metrics["line_item_recall"].append(0.0)
                continue

            pred_inv = pred_invoices[i]
            metrics["invoice_number_acc"].append(_str_match(pred_inv.invoice_number, gt_inv.get("invoice_number")))
            metrics["seller_name_acc"].append(_str_match(pred_inv.seller_name, gt_inv.get("seller_name")))
            metrics["buyer_name_acc"].append(_str_match(pred_inv.buyer_name, gt_inv.get("buyer_name")))
            metrics["currency_acc"].append(_str_match(pred_inv.currency, gt_inv.get("currency")))
            metrics["subtotal_acc"].append(_num_match(pred_inv.subtotal, gt_inv.get("subtotal")))
            metrics["total_acc"].append(_num_match(pred_inv.total_amount, gt_inv.get("total_amount")))
            metrics["tax_acc"].append(_num_match(pred_inv.tax_amount, gt_inv.get("tax_amount")))

            err_metrics = _errors_match(pred_inv.validation_errors, gt_inv.get("validation_errors", []))
            metrics["validation_f1"].append(err_metrics["f1"])

            pred_li = [vars(li) for li in pred_inv.line_items]
            metrics["line_item_recall"].append(_line_items_recall(pred_li, gt_inv.get("line_items", [])))

    print(f"\n{'='*55}")
    print(f"  Evaluation Results")
    print(f"{'='*55}")
    print(f"  Documents processed : {processed}")
    print(f"  Documents failed    : {failed}")
    print(f"{'='*55}")

    for metric, values in metrics.items():
        if values:
            avg = sum(values) / len(values)
            print(f"  {metric:<28} {avg*100:6.2f}%")
        else:
            print(f"  {metric:<28}   N/A")

    print(f"{'='*55}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="test_manifest.csv")
    parser.add_argument("--annotations", default="annotations.json")
    args = parser.parse_args()
    evaluate(args.manifest, args.annotations)
