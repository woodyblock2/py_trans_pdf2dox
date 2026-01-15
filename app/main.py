from __future__ import annotations

import argparse
import sys
from pathlib import Path

from paddleocr import PaddleOCR

from app.pipeline.cell_ocr import ocr_cells
from app.pipeline.docx_writer import DocxWriter
from app.pipeline.fallback_grid import detect_grid_cells
from app.pipeline.pdf_to_images import PdfRenderError, render_pdf_to_images
from app.pipeline.preprocess import preprocess_image
from app.pipeline.rotation import correct_orientation
from app.pipeline.table_structure import create_table_engine, detect_tables
from app.utils.io import InputError, collect_pdfs, ensure_dir, stem_safe
from app.utils.json_report import add_page, add_table, init_report, save_report
from app.utils.logger import setup_logger

REQUIRED_MODEL_DIRS = ["det", "rec", "cls", "table"]


def validate_models(models_dir: Path) -> None:
    if not models_dir.exists():
        raise FileNotFoundError(f"Models directory not found: {models_dir}")
    for sub in REQUIRED_MODEL_DIRS:
        sub_dir = models_dir / sub
        if not sub_dir.exists():
            raise FileNotFoundError(f"Missing model directory: {sub_dir}")
        files = [p for p in sub_dir.iterdir() if p.is_file()]
        if not files:
            raise FileNotFoundError(f"Model directory is empty: {sub_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PDF table to DOCX demo")
    parser.add_argument("--input", required=True, help="PDF file or directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--models", required=True, help="Local models directory")
    parser.add_argument("--dpi", type=int, default=300, help="Render DPI")
    parser.add_argument("--debug", action="store_true", help="Save debug images")
    parser.add_argument("--max-pages", type=int, default=0, help="Limit pages")
    parser.add_argument("--no-fallback", action="store_true", help="Disable fallback")
    parser.add_argument(
        "--rotation-strategy",
        default="ocr_score",
        choices=["ocr_score", "none"],
        help="Rotation strategy",
    )
    return parser.parse_args()


def build_cells_from_table(table: dict, image_size: tuple[int, int]) -> list[dict]:
    bbox = table.get("bbox")
    if bbox is None:
        x1, y1, x2, y2 = 0, 0, image_size[0], image_size[1]
    else:
        x1, y1, x2, y2 = map(int, bbox)
    rows = max(table.get("rows", 0), 1)
    cols = max(table.get("cols", 0), 1)

    cell_specs = table.get("cell_specs") or []
    if not cell_specs:
        cell_specs = [
            {"row": r, "col": c, "rowspan": 1, "colspan": 1}
            for r in range(rows)
            for c in range(cols)
        ]

    cell_width = max(int((x2 - x1) / cols), 1)
    cell_height = max(int((y2 - y1) / rows), 1)

    cells = []
    for spec in cell_specs:
        row = spec["row"]
        col = spec["col"]
        rowspan = spec.get("rowspan", 1)
        colspan = spec.get("colspan", 1)
        if "bbox" in spec:
            cx1, cy1, cx2, cy2 = spec["bbox"]
        else:
            cx1 = x1 + col * cell_width
            cy1 = y1 + row * cell_height
            cx2 = x1 + (col + colspan) * cell_width
            cy2 = y1 + (row + rowspan) * cell_height
        cells.append(
            {
                "row": row,
                "col": col,
                "rowspan": rowspan,
                "colspan": colspan,
                "bbox": [int(cx1), int(cy1), int(cx2), int(cy2)],
            }
        )
    return cells


def main() -> int:
    args = parse_args()
    logger = setup_logger(args.debug)

    input_path = Path(args.input)
    output_dir = ensure_dir(Path(args.output))
    models_dir = Path(args.models)

    try:
        validate_models(models_dir)
    except FileNotFoundError as exc:
        logger.error(str(exc))
        return 1

    try:
        pdfs = collect_pdfs(input_path)
    except InputError as exc:
        logger.error(str(exc))
        return 1

    logger.info("Initializing OCR engines")
    ocr_engine = PaddleOCR(
        det_model_dir=str(models_dir / "det"),
        rec_model_dir=str(models_dir / "rec"),
        cls_model_dir=str(models_dir / "cls"),
        use_angle_cls=False,
        lang="ch",
        show_log=False,
    )
    table_engine = create_table_engine(models_dir)

    for pdf_path in pdfs:
        logger.info("Processing PDF: %s", pdf_path)
        pdf_name = stem_safe(pdf_path)
        pdf_output_dir = ensure_dir(output_dir / pdf_name)
        debug_dir = ensure_dir(pdf_output_dir / "debug") if args.debug else None
        report = init_report(pdf_path.name)
        docx_writer = DocxWriter()

        try:
            images = render_pdf_to_images(pdf_path, args.dpi, debug_dir)
        except PdfRenderError as exc:
            logger.error(str(exc))
            continue

        for page_index, image in enumerate(images, start=1):
            if args.max_pages and page_index > args.max_pages:
                break
            logger.info("Page %d/%d", page_index, len(images))
            page_debug_dir = None
            if debug_dir is not None:
                page_debug_dir = ensure_dir(debug_dir / f"page_{page_index:03d}")

            rotated, angle = correct_orientation(
                image,
                ocr_engine,
                rotation_strategy=args.rotation_strategy,
                debug_dir=page_debug_dir,
                page_index=page_index,
            )
            preprocessed = preprocess_image(rotated, debug_dir=page_debug_dir, page_index=page_index)
            _ = preprocessed
            page_info = add_page(report, page_index, angle)

            tables = detect_tables(rotated, table_engine)
            if not tables and not args.no_fallback:
                fallback = detect_grid_cells(rotated)
                if fallback:
                    tables = [
                        {
                            "bbox": fallback["bbox"],
                            "rows": fallback["rows"],
                            "cols": fallback["cols"],
                            "cell_specs": fallback["cells"],
                            "fallback": True,
                        }
                    ]

            for table in tables:
                rows = table.get("rows", 0)
                cols = table.get("cols", 0)
                if rows == 0 or cols == 0:
                    if args.no_fallback:
                        continue
                    fallback = detect_grid_cells(rotated)
                    if not fallback:
                        continue
                    table = {
                        "bbox": fallback["bbox"],
                        "rows": fallback["rows"],
                        "cols": fallback["cols"],
                        "cell_specs": fallback["cells"],
                        "fallback": True,
                    }

                cells_meta = build_cells_from_table(table, rotated.size)
                cell_results = ocr_cells(rotated, cells_meta, ocr_engine)

                table_data = {
                    "bbox": table.get("bbox"),
                    "rows": max(table.get("rows", 0), 1),
                    "cols": max(table.get("cols", 0), 1),
                    "cells": [
                        {
                            "row": cell.row,
                            "col": cell.col,
                            "rowspan": cell.rowspan,
                            "colspan": cell.colspan,
                            "bbox": cell.bbox,
                            "text": cell.text,
                            "confidence": cell.confidence,
                        }
                        for cell in cell_results
                    ],
                    "fallback_used": bool(table.get("fallback")),
                }

                add_table(page_info, table_data)
                docx_writer.add_table(table_data)

            if page_index < len(images):
                docx_writer.add_page_break()

        docx_path = pdf_output_dir / f"{pdf_name}.docx"
        json_path = pdf_output_dir / f"{pdf_name}.json"
        docx_writer.save(docx_path)
        save_report(report, json_path)
        logger.info("Saved outputs to %s", pdf_output_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
