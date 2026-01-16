from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def preprocess_image(
    image: Image.Image,
    debug_dir: Path | None = None,
    page_index: int = 1,
) -> Image.Image:
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    denoise = cv2.medianBlur(gray, 3)
    thresh = cv2.adaptiveThreshold(
        denoise,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2,
    )
    processed = Image.fromarray(thresh)
    if debug_dir is not None:
        debug_path = debug_dir / f"page_{page_index:03d}_preprocess.png"
        processed.save(debug_path)
    return processed
