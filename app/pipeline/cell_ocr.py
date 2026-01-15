from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from PIL import Image


@dataclass
class CellResult:
    row: int
    col: int
    rowspan: int
    colspan: int
    bbox: list[int]
    text: str
    confidence: float


def _run_ocr(ocr_engine, image: Image.Image) -> tuple[str, float]:
    result = ocr_engine.ocr(image, cls=False)
    texts: list[str] = []
    confs: list[float] = []
    for line in result:
        for _, (text, conf) in line:
            texts.append(text)
            confs.append(conf)
    if not texts:
        return "", 0.0
    avg_conf = float(sum(confs) / max(len(confs), 1))
    return " ".join(texts).strip(), avg_conf


def ocr_cells(
    image: Image.Image,
    cells: list[dict[str, Any]],
    ocr_engine,
) -> list[CellResult]:
    results: list[CellResult] = []
    np_image = np.array(image)
    for cell in cells:
        x1, y1, x2, y2 = cell["bbox"]
        roi = np_image[y1:y2, x1:x2]
        if roi.size == 0:
            text, conf = "", 0.0
        else:
            roi_image = Image.fromarray(roi)
            text, conf = _run_ocr(ocr_engine, roi_image)
        results.append(
            CellResult(
                row=cell["row"],
                col=cell["col"],
                rowspan=cell.get("rowspan", 1),
                colspan=cell.get("colspan", 1),
                bbox=[int(x1), int(y1), int(x2), int(y2)],
                text=text,
                confidence=conf,
            )
        )
    return results
