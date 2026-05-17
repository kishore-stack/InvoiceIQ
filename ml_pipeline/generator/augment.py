"""
Applies visual augmentations to invoice images to simulate real-world degradation.
Noise level: low | medium | high
"""
import random
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from typing import Literal

NoiseLevel = Literal["low", "medium", "high"]

NOISE_PARAMS = {
    "low":    {"rotation": (-2, 2),   "blur_radius": (0, 0.8), "noise_std": (0, 5)},
    "medium": {"rotation": (-5, 5),   "blur_radius": (0, 1.5), "noise_std": (5, 20)},
    "high":   {"rotation": (-10, 10), "blur_radius": (0, 3.0), "noise_std": (20, 50)},
}

STAMP_TEXTS = ["PAID", "RECEIVED", "APPROVED", "PROCESSED", "DUPLICATE"]
STAMP_COLORS = ["red", "blue", "green", "purple"]


def _apply_rotation(img: Image.Image, level: NoiseLevel) -> Image.Image:
    lo, hi = NOISE_PARAMS[level]["rotation"]
    angle = random.uniform(lo, hi)
    if abs(angle) < 0.5:
        return img
    return img.rotate(angle, expand=False, fillcolor=(255, 255, 255))


def _apply_blur(img: Image.Image, level: NoiseLevel) -> Image.Image:
    lo, hi = NOISE_PARAMS[level]["blur_radius"]
    radius = random.uniform(lo, hi)
    if radius < 0.3:
        return img
    return img.filter(ImageFilter.GaussianBlur(radius=radius))


def _apply_noise(img: Image.Image, level: NoiseLevel) -> Image.Image:
    lo, hi = NOISE_PARAMS[level]["noise_std"]
    std = random.uniform(lo, hi)
    if std < 1:
        return img
    arr = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, std, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def _apply_stamp(img: Image.Image) -> Image.Image:
    """Overlay a semi-transparent stamp text on the image."""
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    text = random.choice(STAMP_TEXTS)
    color_name = random.choice(STAMP_COLORS)
    color_map = {
        "red": (200, 30, 30, 80),
        "blue": (30, 30, 200, 80),
        "green": (30, 150, 30, 80),
        "purple": (120, 30, 180, 80),
    }
    color = color_map[color_name]

    font_size = random.randint(40, 70)
    # Use default font since custom fonts may not be available
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    w, h = img.size
    x = random.randint(int(w * 0.2), int(w * 0.6))
    y = random.randint(int(h * 0.2), int(h * 0.6))
    angle = random.uniform(-30, 30)

    # Draw rotated text via temporary image
    txt_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((x, y), text, font=font, fill=color)
    txt_img = txt_img.rotate(angle, center=(x, y))
    result = Image.alpha_composite(img.convert("RGBA"), txt_img)
    return result.convert("RGB")


def _apply_background_texture(img: Image.Image) -> Image.Image:
    """Add very light paper texture noise."""
    arr = np.array(img, dtype=np.float32)
    texture = np.random.uniform(-8, 8, arr.shape)
    arr = np.clip(arr + texture, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def augment_image(img: Image.Image, level: NoiseLevel) -> Image.Image:
    """Apply full augmentation pipeline to a PIL image."""
    img = img.convert("RGB")
    img = _apply_rotation(img, level)
    img = _apply_blur(img, level)
    img = _apply_noise(img, level)

    if random.random() < 0.15:
        img = _apply_stamp(img)

    if level in ("medium", "high") and random.random() < 0.3:
        img = _apply_background_texture(img)

    return img


def pick_noise_level() -> NoiseLevel:
    return random.choices(
        ["low", "medium", "high"],
        weights=[40, 40, 20]
    )[0]
