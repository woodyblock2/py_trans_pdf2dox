from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image


class PdfRenderError(Exception):
    pass


def render_pdf_to_images(pdf_path: Path, dpi: int, debug_dir: Path | None = None) -> list[Image.Image]:
    images: list[Image.Image] = []
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:  # noqa: BLE001
        raise PdfRenderError(f"Failed to open PDF: {pdf_path}") from exc

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        mode = "RGB" if pix.n < 5 else "CMYK"
        image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        if mode == "CMYK":
            image = image.convert("RGB")
        images.append(image)
        if debug_dir is not None:
            debug_path = debug_dir / f"page_{page_index + 1:03d}_render.png"
            image.save(debug_path)
    doc.close()
    return images
