"""
OCR module: wraps pytesseract to extract text with word-level
bounding boxes and per-word confidence scores.
"""
import os
import shutil
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
import pytesseract
from PIL import Image
import cv2

from pipeline.logging_utils import get_logger

log = get_logger("OCR")


def _resolve_tesseract_binary() -> None:
    """
    Make sure pytesseract can find the Tesseract executable.

    Order of resolution:
      1. TESSERACT_CMD environment variable (explicit override).
      2. `tesseract` on PATH.
      3. Common Windows install locations.

    If found, pin pytesseract.tesseract_cmd so it doesn't have to re-search.
    """
    override = os.environ.get("TESSERACT_CMD")
    if override and os.path.isfile(override):
        pytesseract.pytesseract.tesseract_cmd = override
        log.debug(f"Using TESSERACT_CMD={override}")
        return

    on_path = shutil.which("tesseract")
    if on_path:
        pytesseract.pytesseract.tesseract_cmd = on_path
        log.debug(f"Found tesseract on PATH: {on_path}")
        return

    if os.name == "nt":
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                pytesseract.pytesseract.tesseract_cmd = candidate
                log.info(f"Tesseract not on PATH, falling back to: {candidate}")
                return

    log.warning(
        "Could not locate the tesseract binary. Install it from "
        "https://github.com/UB-Mannheim/tesseract/wiki and add it to PATH, "
        "or set TESSERACT_CMD=<full path to tesseract.exe>."
    )


_resolve_tesseract_binary()


@dataclass
class Word:
    text: str
    x: int
    y: int
    w: int
    h: int
    conf: float  # 0.0 – 1.0

    @property
    def x2(self) -> int:
        return self.x + self.w

    @property
    def y2(self) -> int:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


@dataclass
class OcrResult:
    full_text: str
    words: List[Word] = field(default_factory=list)
    avg_confidence: float = 0.0


def _bgr_to_pil(img: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def run_ocr(img: np.ndarray, lang: str = "eng") -> OcrResult:
    """
    Run Tesseract OCR on a BGR numpy array.
    Returns full text, per-word bboxes, and confidence scores.
    """
    pil_img = _bgr_to_pil(img)
    log.debug(
        f"Running Tesseract (oem=3, psm=6, lang={lang}) on "
        f"{pil_img.width}x{pil_img.height} page"
    )

    try:
        data = pytesseract.image_to_data(
            pil_img,
            lang=lang,
            output_type=pytesseract.Output.DICT,
            config="--oem 3 --psm 6",
        )
    except pytesseract.TesseractNotFoundError:
        log.critical("Tesseract binary not found on PATH — install tesseract-ocr")
        raise

    words: List[Word] = []
    confidences: List[float] = []

    for i, text in enumerate(data["text"]):
        text = text.strip()
        if not text:
            continue
        conf_raw = int(data["conf"][i])
        if conf_raw < 0:
            continue
        conf = conf_raw / 100.0
        words.append(Word(
            text=text,
            x=data["left"][i],
            y=data["top"][i],
            w=data["width"][i],
            h=data["height"][i],
            conf=conf,
        ))
        confidences.append(conf)

    full_text = pytesseract.image_to_string(pil_img, lang=lang, config="--oem 3 --psm 6")
    avg_conf = float(np.mean(confidences)) if confidences else 0.0

    if not words:
        log.warning("OCR returned no words for this page")
    elif avg_conf < 0.55:
        log.warning(
            f"Low OCR confidence (avg={avg_conf:.2f}) — extraction quality may suffer"
        )
    else:
        log.info(f"OCR extracted {len(words)} words (avg confidence {avg_conf:.2f})")

    return OcrResult(full_text=full_text, words=words, avg_confidence=avg_conf)


def words_in_region(words: List[Word], x1: int, y1: int, x2: int, y2: int) -> List[Word]:
    """Filter words whose centre falls within the given bounding box."""
    return [w for w in words if x1 <= w.cx <= x2 and y1 <= w.cy <= y2]


def region_text(words: List[Word], x1: int, y1: int, x2: int, y2: int) -> str:
    """Return space-joined text of words in region, ordered by reading direction."""
    subset = words_in_region(words, x1, y1, x2, y2)
    subset.sort(key=lambda w: (w.y, w.x))
    return " ".join(w.text for w in subset)


def region_confidence(words: List[Word], x1: int, y1: int, x2: int, y2: int) -> float:
    subset = words_in_region(words, x1, y1, x2, y2)
    if not subset:
        return 0.0
    return float(np.mean([w.conf for w in subset]))
