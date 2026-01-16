from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from PIL import Image


def _score_ocr_result(ocr_result: list) -> float:
    total_conf = 0.0
    total_len = 0
    chinese_count = 0
    pattern = re.compile(r"[\u4e00-\u9fff]")
    for line in ocr_result:
        if not line:
            continue
        for _, (text, conf) in line:
            total_conf += conf
            total_len += len(text)
            chinese_count += len(pattern.findall(text))
    if total_len == 0:
        return 0.0
    avg_conf = total_conf / max(total_len, 1)
    return chinese_count * 2 + total_len + avg_conf


def correct_orientation(
    image: Image.Image,
    ocr_engine,
    rotation_strategy: str = "ocr_score",
    debug_dir: Path | None = None,
    page_index: int = 1,
) -> tuple[Image.Image, int]:
    if rotation_strategy != "ocr_score":
        return image, 0

    candidates = [0, 90, 180, 270]
    best_score = -1.0
    best_angle = 0
    best_image = image

    for angle in candidates:
        rotated = image.rotate(angle, expand=True)
        ocr_result = ocr_engine.ocr(rotated, cls=False)
        score = _score_ocr_result(ocr_result)
        if debug_dir is not None:
            debug_path = debug_dir / f"page_{page_index:03d}_rot_{angle}.png"
            rotated.save(debug_path)
        if score > best_score:
            best_score = score
            best_angle = angle
            best_image = rotated

    return best_image, best_angle
