"""
Preprocessor: converts any supported input file (PDF, PNG, JPG) into
a list of cleaned page images ready for OCR and layout analysis.
"""
import math
from pathlib import Path
from typing import List, Tuple

import cv2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image

from pipeline.logging_utils import get_logger

log = get_logger("DATA INGESTION")

DPI = 200  # resolution for PDF rasterisation


# ── File → raw page images ────────────────────────────────────────────────────

def load_pages(file_path: str) -> List[np.ndarray]:
    """Return a list of BGR numpy arrays, one per page."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    log.info(f"Loading file '{path.name}' ({suffix})")

    if suffix == ".pdf":
        pages = _pdf_to_pages(file_path)
    elif suffix in (".png", ".jpg", ".jpeg"):
        pages = _image_to_pages(file_path)
    else:
        log.error(f"Unsupported file type: {suffix}")
        raise ValueError(f"Unsupported file type: {suffix}")

    log.info(f"File loaded successfully — {len(pages)} page(s) rasterised at {DPI} DPI")
    return pages


def _pdf_to_pages(file_path: str) -> List[np.ndarray]:
    doc = fitz.open(file_path)
    pages = []
    mat = fitz.Matrix(DPI / 72, DPI / 72)
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        pages.append(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    doc.close()
    return pages


def _image_to_pages(file_path: str) -> List[np.ndarray]:
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Could not read image: {file_path}")
    return [img]


# ── Deskew ────────────────────────────────────────────────────────────────────

def deskew(img: np.ndarray) -> np.ndarray:
    """Detect and correct skew angle using Hough line transform."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    coords = np.column_stack(np.where(binary > 0))
    if len(coords) < 50:
        return img

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90

    if abs(angle) < 0.3:
        return img

    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        img, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return rotated


# ── Denoise ───────────────────────────────────────────────────────────────────

def denoise(img: np.ndarray) -> np.ndarray:
    """Apply non-local means denoising."""
    return cv2.fastNlMeansDenoisingColored(img, None, h=10, hColor=10,
                                           templateWindowSize=7, searchWindowSize=21)


# ── Quality score ─────────────────────────────────────────────────────────────

def blur_score(img: np.ndarray) -> float:
    """Laplacian variance — higher = sharper."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def quality_label(score: float) -> str:
    if score > 500:
        return "high"
    elif score > 100:
        return "medium"
    return "low"


# ── Full pipeline ─────────────────────────────────────────────────────────────

def preprocess(file_path: str) -> List[Tuple[np.ndarray, str]]:
    """
    Load, deskew, and denoise all pages.

    Returns:
        List of (processed_bgr_image, quality_label) tuples, one per page.
    """
    raw_pages = load_pages(file_path)
    result = []
    quality_counts = {"high": 0, "medium": 0, "low": 0}
    for idx, page in enumerate(raw_pages, 1):
        page = deskew(page)
        score = blur_score(page)
        label = quality_label(score)
        quality_counts[label] += 1
        if label == "low":
            log.warning(
                f"Page {idx}: low sharpness ({score:.0f}) — applying Non-Local Means denoise"
            )
            page = denoise(page)
        else:
            log.debug(f"Page {idx}: quality={label} (Laplacian variance={score:.0f})")
        result.append((page, label))
    log.info(
        f"Preprocessing complete — high={quality_counts['high']}, "
        f"medium={quality_counts['medium']}, low={quality_counts['low']}"
    )
    return result
