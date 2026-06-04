import numpy as np
import fitz

try:
    from PIL import Image
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


def pdf_to_image(
    pdf_path: str,
    page_number: int = 0,
    dpi: int = 216,
    max_side: int = 2500,
) -> np.ndarray:
    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise FileNotFoundError(f"Could not open PDF '{pdf_path}': {exc}") from exc

    with doc:
        if not (0 <= page_number < len(doc)):
            raise ValueError(
                f"page_number {page_number} is out of range — "
                f"document has {len(doc)} page(s) (0-indexed)."
            )
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        pix = doc[page_number].get_pixmap(matrix=matrix, alpha=False, colorspace=fitz.csRGB)
        image_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, 3
        )
        if max_side and max(pix.width, pix.height) > max_side:
            image_np = _resize_max_side(image_np, max_side)
        return image_np


def pdf_to_images(
    pdf_path: str,
    dpi: int = 216,
    max_side: int = 2500,
) -> list:
    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise FileNotFoundError(f"Could not open PDF '{pdf_path}': {exc}") from exc

    images = []
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    with doc:
        for page in doc:
            pix = page.get_pixmap(matrix=matrix, alpha=False, colorspace=fitz.csRGB)
            image_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, 3
            )
            if max_side and max(pix.width, pix.height) > max_side:
                image_np = _resize_max_side(image_np, max_side)
            images.append(image_np)

    return images


def _resize_max_side(image_np: np.ndarray, max_side: int) -> np.ndarray:
    if not _PIL_AVAILABLE:
        raise ImportError(
            "Pillow is required for resizing. Install it with: pip install pillow"
        )
    h, w = image_np.shape[:2]
    scale = max_side / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    img = Image.fromarray(image_np)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    return np.array(img)