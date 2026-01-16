from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def init_report(pdf_name: str) -> dict[str, Any]:
    return {
        "pdf": pdf_name,
        "pages": [],
    }


def add_page(report: dict[str, Any], page_index: int, rotation: int) -> dict[str, Any]:
    page_info = {
        "page_index": page_index,
        "rotation": rotation,
        "tables": [],
    }
    report["pages"].append(page_info)
    return page_info


def add_table(page_info: dict[str, Any], table_data: dict[str, Any]) -> None:
    page_info["tables"].append(table_data)


def save_report(report: dict[str, Any], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
