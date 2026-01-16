from __future__ import annotations

from pathlib import Path
from typing import Iterable


class InputError(Exception):
    pass


def collect_pdfs(input_path: Path) -> list[Path]:
    if not input_path.exists():
        raise InputError(f"Input path does not exist: {input_path}")
    if input_path.is_file():
        if input_path.suffix.lower() != ".pdf":
            raise InputError(f"Input file is not a PDF: {input_path}")
        return [input_path]
    pdfs = sorted(input_path.glob("*.pdf"))
    if not pdfs:
        raise InputError(f"No PDF files found in directory: {input_path}")
    return pdfs


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def stem_safe(path: Path) -> str:
    return path.stem.replace(" ", "_")


def iter_pages(images: Iterable) -> Iterable:
    for idx, image in enumerate(images, start=1):
        yield idx, image
