from __future__ import annotations

from typing import Any

import cv2
import numpy as np
from PIL import Image


def _cluster_positions(values: list[int], threshold: int = 10) -> list[int]:
    if not values:
        return []
    values = sorted(values)
    clusters = [values[0]]
    for v in values[1:]:
        if abs(v - clusters[-1]) > threshold:
            clusters.append(v)
    return clusters


def detect_grid_cells(image: Image.Image) -> dict[str, Any] | None:
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 10
    )

    horizontal = binary.copy()
    vertical = binary.copy()
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    horizontal = cv2.morphologyEx(horizontal, cv2.MORPH_OPEN, h_kernel)
    vertical = cv2.morphologyEx(vertical, cv2.MORPH_OPEN, v_kernel)
    grid = cv2.addWeighted(horizontal, 0.5, vertical, 0.5, 0.0)

    contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < 20 or h < 20:
            continue
        boxes.append((x, y, x + w, y + h))

    if not boxes:
        return None

    xs = _cluster_positions([b[0] for b in boxes] + [b[2] for b in boxes])
    ys = _cluster_positions([b[1] for b in boxes] + [b[3] for b in boxes])
    cols = max(len(xs) - 1, 1)
    rows = max(len(ys) - 1, 1)

    cells = []
    for r in range(rows):
        for c in range(cols):
            x1 = xs[c]
            x2 = xs[c + 1]
            y1 = ys[r]
            y2 = ys[r + 1]
            cells.append({"row": r, "col": c, "rowspan": 1, "colspan": 1, "bbox": [x1, y1, x2, y2]})

    return {
        "bbox": [min(xs), min(ys), max(xs), max(ys)],
        "rows": rows,
        "cols": cols,
        "cells": cells,
    }
