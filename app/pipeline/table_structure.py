from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from paddleocr import PPStructure


@dataclass
class CellSpec:
    row: int
    col: int
    rowspan: int
    colspan: int


class TableHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[dict[str, int]]] = []
        self._current_row: list[dict[str, int]] = []
        self._in_tr = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._in_tr = True
            self._current_row = []
        if tag in {"td", "th"} and self._in_tr:
            attr_dict = {key: value for key, value in attrs}
            rowspan = int(attr_dict.get("rowspan", "1") or 1)
            colspan = int(attr_dict.get("colspan", "1") or 1)
            self._current_row.append({"rowspan": rowspan, "colspan": colspan})

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self._in_tr:
            self.rows.append(self._current_row)
            self._current_row = []
            self._in_tr = False


def _parse_html_table(html: str) -> tuple[int, int, list[CellSpec]]:
    parser = TableHTMLParser()
    parser.feed(html)

    row_count = len(parser.rows)
    col_count = 0
    for row in parser.rows:
        col_count = max(col_count, sum(cell["colspan"] for cell in row))

    occupancy: dict[tuple[int, int], bool] = {}
    cells: list[CellSpec] = []
    for r, row in enumerate(parser.rows):
        c = 0
        for cell in row:
            while occupancy.get((r, c), False):
                c += 1
            rowspan = cell["rowspan"]
            colspan = cell["colspan"]
            cells.append(CellSpec(row=r, col=c, rowspan=rowspan, colspan=colspan))
            for rr in range(r, r + rowspan):
                for cc in range(c, c + colspan):
                    occupancy[(rr, cc)] = True
            c += colspan
    return row_count, col_count, cells


def create_table_engine(models_dir: Path) -> PPStructure:
    table_model_dir = models_dir / "table"
    engine = PPStructure(
        table=True,
        ocr=False,
        table_model_dir=str(table_model_dir),
        show_log=False,
        lang="ch",
    )
    return engine


def detect_tables(
    image,
    table_engine: PPStructure,
) -> list[dict[str, Any]]:
    results = table_engine(image)
    tables: list[dict[str, Any]] = []
    for item in results:
        if item.get("type") != "table":
            continue
        bbox = item.get("bbox") or item.get("box") or item.get("dt_boxes")
        html = ""
        res = item.get("res")
        if isinstance(res, dict):
            html = res.get("html", "") or res.get("structure", "") or ""
        if not html and "html" in item:
            html = item.get("html", "")

        if html:
            rows, cols, cell_specs = _parse_html_table(html)
            cells = [
                {"row": cell.row, "col": cell.col, "rowspan": cell.rowspan, "colspan": cell.colspan}
                for cell in cell_specs
            ]
        else:
            rows, cols, cells = 0, 0, []

        tables.append(
            {
                "bbox": bbox,
                "rows": rows,
                "cols": cols,
                "cell_specs": cells,
            }
        )
    return tables
