"""
Table extractor: extracts line-item rows from invoice pages.

Strategy:
  1. Try pdfplumber for native PDF tables (fast, accurate).
  2. Fall back to OpenCV contour-based grid detection for image tables.
  3. Fall back to whitespace column inference for borderless tables.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

import cv2
import numpy as np
import pdfplumber

from pipeline.logging_utils import get_logger

log = get_logger("TABLE EXTRACTION")

# Column header synonyms for fuzzy matching. Sub-components like CGST/SGST/IGST
# all map to tax_amount; the extractor sums them per row.
HEADER_SYNONYMS: Dict[str, List[str]] = {
    "description": ["description", "item", "details", "particulars", "product", "service"],
    "quantity":    ["quantity", "qty", "units", "no.", "count"],
    "unit_price":  ["unit price", "rate", "price", "unit cost", "unit rate"],
    "tax_amount":  ["tax", "vat", "gst", "hst", "cgst", "sgst", "igst", "cess", "tax amount"],
    "discount_amount": ["discount", "disc", "rebate"],
    "line_total":  ["total", "line total", "amount", "line amount", "net"],
}

AMOUNT_RE = re.compile(r"[-]?[\d,]+\.?\d{0,2}")


@dataclass
class LineItem:
    description: str = ""
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    line_total: Optional[float] = None
    confidence: float = 0.0


def _parse_num(s: str) -> Optional[float]:
    s = s.strip().replace(",", "").lstrip("$€£₹").strip()
    m = AMOUNT_RE.search(s)
    if m:
        try:
            return float(m.group(0).replace(",", ""))
        except ValueError:
            return None
    return None


def _match_column(header: str) -> Optional[str]:
    h = header.lower().strip()
    for field_name, synonyms in HEADER_SYNONYMS.items():
        if any(syn in h for syn in synonyms):
            return field_name
    return None


def _rows_to_items(rows: List[List[str]], header_map: Dict[int, str]) -> List[LineItem]:
    """
    Convert raw row strings to LineItem objects using header_map.

    Multiple columns can map to the same field — most commonly several tax
    sub-columns (CGST, SGST, IGST) all mapped to tax_amount. For tax and
    discount we sum across columns; for the rest we take the first non-empty.
    """
    items: List[LineItem] = []

    # Identify which header_map columns are tax/discount (summable) vs. scalar
    tax_cols = [c for c, f in header_map.items() if f == "tax_amount"]
    disc_cols = [c for c, f in header_map.items() if f == "discount_amount"]

    for row in rows:
        if not any(c.strip() for c in row):
            continue

        item = LineItem()
        # Scalar fields
        for col_idx, field_name in header_map.items():
            if col_idx >= len(row):
                continue
            val = row[col_idx].strip()
            if not val:
                continue
            if field_name == "description" and not item.description:
                item.description = val
            elif field_name == "quantity" and item.quantity is None:
                item.quantity = _parse_num(val)
            elif field_name == "unit_price" and item.unit_price is None:
                item.unit_price = _parse_num(val)
            elif field_name == "line_total" and item.line_total is None:
                item.line_total = _parse_num(val)

        # Sum multi-component tax columns
        tax_sum = 0.0
        tax_seen = False
        for c in tax_cols:
            if c < len(row):
                v = _parse_num(row[c])
                if v is not None:
                    tax_sum += v
                    tax_seen = True
        if tax_seen:
            item.tax_amount = round(tax_sum, 2)

        # Same for discount columns
        disc_sum = 0.0
        disc_seen = False
        for c in disc_cols:
            if c < len(row):
                v = _parse_num(row[c])
                if v is not None:
                    disc_sum += v
                    disc_seen = True
        if disc_seen:
            item.discount_amount = round(disc_sum, 2)

        # Multi-line description: if no numerics, merge with previous
        has_nums = item.quantity is not None or item.unit_price is not None or item.line_total is not None
        if not has_nums and item.description and items:
            items[-1].description += " " + item.description
            continue

        if item.description or item.line_total:
            items.append(item)

    return items


def _build_header_map(header_rows: List[List[str]]) -> Dict[int, str]:
    """
    Build column-index -> field-name map from one or more header rows.

    Supports:
      - Single-row header.
      - Two-row header where the top row contains group labels (e.g. 'Tax')
        with merged cells, and the bottom row contains sub-labels
        (e.g. 'CGST', 'SGST').

    For each column we concatenate non-empty cells from every header row and
    run the synonym matcher on the combined string. So a CGST column under a
    merged 'Tax' header is matched correctly even if either label alone is
    ambiguous.
    """
    if not header_rows:
        return {}

    n_cols = max(len(r) for r in header_rows)
    header_map: Dict[int, str] = {}

    # Forward-fill merged cells in upper rows: a non-empty cell in row N
    # implicitly carries until the next non-empty cell to its right.
    filled_rows: List[List[str]] = []
    for r in header_rows[:-1]:  # only forward-fill group/parent rows
        row = [str(c or "").strip() for c in r]
        last = ""
        ff_row = []
        for c in row:
            if c:
                last = c
            ff_row.append(last)
        filled_rows.append(ff_row)
    # Last row (most specific) is NOT forward-filled
    filled_rows.append([str(c or "").strip() for c in header_rows[-1]])

    for col in range(n_cols):
        parts: List[str] = []
        for r in filled_rows:
            if col < len(r) and r[col]:
                parts.append(r[col].lower())
        combined = " ".join(parts)
        field_name = _match_column(combined)
        if field_name:
            header_map[col] = field_name

    return header_map


def _looks_like_header_row(row: List[str]) -> bool:
    """A row is header-ish if it has text but no parseable numbers."""
    has_text = any(c and c.strip() for c in row)
    has_nums = any(_parse_num(c or "") is not None for c in row)
    return has_text and not has_nums


def _detect_header_rows(table: List[List[str]]) -> int:
    """
    Return how many leading rows of the table are header rows (1 or 2).

    Heuristic: if row 0 has fewer non-empty cells than row 1 AND row 1 has
    text with no numbers, treat both as header (merged group + sub-headers).
    """
    if len(table) < 3:
        return 1

    row0 = [str(c or "").strip() for c in table[0]]
    row1 = [str(c or "").strip() for c in table[1]]

    row0_filled = sum(1 for c in row0 if c)
    row1_filled = sum(1 for c in row1 if c)

    if row1_filled > row0_filled and _looks_like_header_row(row1) and row0_filled >= 1:
        return 2
    return 1


# ── pdfplumber extraction ─────────────────────────────────────────────────────

def extract_via_pdfplumber(
    file_path: str, page_start: int, page_end: int
) -> List[LineItem]:
    """
    Extract line items using pdfplumber.

    Handles:
      - Single-row headers (standard case).
      - Two-row headers with merged group cells (Tax > CGST/SGST).
      - Continuation tables: a table on a later page whose first row already
        contains numeric data is treated as a continuation of the previous
        page's table — its rows are appended using the last seen header_map.
    """
    items: List[LineItem] = []
    last_header_map: Dict[int, str] = {}
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num in range(page_start - 1, min(page_end, len(pdf.pages))):
                page = pdf.pages[page_num]
                tables = page.extract_tables()
                log.debug(f"pdfplumber found {len(tables)} table(s) on page {page_num + 1}")
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # Is this a continuation table (no header row, just data)?
                    first_row = [str(c or "").strip() for c in table[0]]
                    is_continuation = (
                        last_header_map
                        and any(_parse_num(c) is not None for c in first_row)
                        and not _looks_like_header_row(first_row)
                    )

                    if is_continuation:
                        log.debug(
                            f"Page {page_num + 1}: treating table as continuation "
                            f"of previous page"
                        )
                        data_rows = [[str(c or "").strip() for c in r] for r in table]
                        items.extend(_rows_to_items(data_rows, last_header_map))
                        continue

                    # Detect 1- vs 2-row header and build the column map
                    n_header = _detect_header_rows(table)
                    header_rows = table[:n_header]
                    header_map = _build_header_map(header_rows)

                    if (
                        "line_total" not in header_map.values()
                        and "unit_price" not in header_map.values()
                    ):
                        continue

                    if n_header == 2:
                        log.debug(
                            f"Page {page_num + 1}: detected 2-row (merged) header"
                        )

                    last_header_map = header_map
                    data_rows = [[str(c or "").strip() for c in r] for r in table[n_header:]]
                    items.extend(_rows_to_items(data_rows, header_map))
    except Exception as e:
        log.error(f"pdfplumber failed: {e}")
    return items


# ── OpenCV grid-based extraction ──────────────────────────────────────────────

def _detect_table_cells(img: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """Returns list of (x, y, w, h) cell bboxes from a bordered table."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    h_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_h)
    v_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_v)

    grid = cv2.add(h_lines, v_lines)
    contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cells = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 40 and h > 10 and w < img.shape[1] * 0.95:
            cells.append((x, y, w, h))
    return cells


def extract_via_opencv(img: np.ndarray) -> List[LineItem]:
    """Fallback OCR-based table extraction from image."""
    import pytesseract
    from PIL import Image

    cells = _detect_table_cells(img)
    if not cells:
        return _extract_borderless(img)

    # Group cells into rows by y proximity
    cells.sort(key=lambda c: (c[1], c[0]))
    row_tol = 10
    rows: List[List[Tuple[int, int, int, int]]] = []
    current_row: List[Tuple[int, int, int, int]] = [cells[0]]

    for cell in cells[1:]:
        if abs(cell[1] - current_row[0][1]) <= row_tol:
            current_row.append(cell)
        else:
            rows.append(sorted(current_row, key=lambda c: c[0]))
            current_row = [cell]
    rows.append(sorted(current_row, key=lambda c: c[0]))

    if len(rows) < 2:
        return []

    # OCR header row
    header_row = rows[0]
    header_texts = []
    for x, y, w, h in header_row:
        crop = img[max(0, y):y+h, max(0, x):x+w]
        pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        t = pytesseract.image_to_string(pil, config="--oem 3 --psm 6").strip().lower()
        header_texts.append(t)

    header_map: Dict[int, str] = {}
    for i, h in enumerate(header_texts):
        fn = _match_column(h)
        if fn:
            header_map[i] = fn

    if not header_map:
        return []

    # OCR data rows
    all_rows: List[List[str]] = []
    for row_cells in rows[1:]:
        row_texts = []
        for x, y, w, h in row_cells:
            crop = img[max(0, y):y+h, max(0, x):x+w]
            pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
            t = pytesseract.image_to_string(pil, config="--oem 3 --psm 6").strip()
            row_texts.append(t)
        all_rows.append(row_texts)

    return _rows_to_items(all_rows, header_map)


def _extract_borderless(img: np.ndarray) -> List[LineItem]:
    """Whitespace column inference for borderless tables."""
    import pytesseract
    from pytesseract import Output

    pil = __import__("PIL").Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    data = pytesseract.image_to_data(pil, output_type=Output.DICT, config="--oem 3 --psm 6")

    words_by_line: Dict[int, List[Dict]] = {}
    for i, text in enumerate(data["text"]):
        if not text.strip() or int(data["conf"][i]) < 30:
            continue
        line_num = data["line_num"][i]
        words_by_line.setdefault(line_num, []).append({
            "text": text,
            "x": data["left"][i],
            "y": data["top"][i],
        })

    lines = [
        sorted(ws, key=lambda w: w["x"])
        for ws in words_by_line.values()
    ]

    # Detect column x-boundaries by clustering x positions
    if len(lines) < 2:
        return []

    all_x = [w["x"] for line in lines for w in line]
    col_boundaries = _cluster_x_positions(all_x, gap=30)

    def assign_col(x: int) -> int:
        for i, (lo, hi) in enumerate(col_boundaries):
            if lo <= x <= hi:
                return i
        return len(col_boundaries)

    items: List[LineItem] = []
    for line in lines:
        row_map: Dict[int, str] = {}
        for w in line:
            col = assign_col(w["x"])
            row_map[col] = row_map.get(col, "") + " " + w["text"]
        row = [row_map.get(c, "").strip() for c in range(len(col_boundaries) + 1)]

        # Simple heuristic: first col = description, last col with number = total
        desc = row[0] if row else ""
        nums = [_parse_num(v) for v in row[1:] if _parse_num(v) is not None]
        if not nums:
            continue
        line_total = nums[-1]
        unit_price = nums[-2] if len(nums) >= 2 else None
        qty = nums[0] if len(nums) >= 3 else None

        items.append(LineItem(
            description=desc,
            quantity=qty,
            unit_price=unit_price,
            line_total=line_total,
        ))

    return items


def _cluster_x_positions(positions: List[int], gap: int = 30) -> List[Tuple[int, int]]:
    if not positions:
        return []
    sorted_pos = sorted(set(positions))
    clusters: List[List[int]] = [[sorted_pos[0]]]
    for x in sorted_pos[1:]:
        if x - clusters[-1][-1] <= gap:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    return [(min(c), max(c) + gap) for c in clusters]


# ── Unified entry point ───────────────────────────────────────────────────────

def extract_line_items(
    file_path: str,
    page_images: List[np.ndarray],
    page_start: int,
    page_end: int,
) -> List[LineItem]:
    """
    Try pdfplumber first; fall back to image-based extraction.
    """
    if file_path.lower().endswith(".pdf"):
        items = extract_via_pdfplumber(file_path, page_start, page_end)
        if items:
            for item in items:
                item.confidence = 0.85
            log.info(f"pdfplumber extracted {len(items)} line item(s) for pages {page_start}-{page_end}")
            return items
        log.warning("pdfplumber found no usable tables — falling back to OpenCV grid detection")

    # Image-based fallback
    all_items: List[LineItem] = []
    for img in page_images:
        all_items.extend(extract_via_opencv(img))

    for item in all_items:
        item.confidence = 0.65

    if all_items:
        log.info(f"OpenCV fallback extracted {len(all_items)} line item(s)")
    else:
        log.warning("No line items extracted by any strategy")

    return all_items
