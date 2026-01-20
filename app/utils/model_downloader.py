from __future__ import annotations

import shutil
import tarfile
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelSpec:
    key: str
    url: str
    description: str


MODEL_SPECS = (
    ModelSpec(
        key="det",
        url="https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar",
        description="PP-OCRv4 中文文本检测模型",
    ),
    ModelSpec(
        key="rec",
        url="https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_infer.tar",
        description="PP-OCRv4 中文文本识别模型",
    ),
    ModelSpec(
        key="cls",
        url="https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_ppocr_mobile_v2.0_cls_infer.tar",
        description="PP-OCR 方向分类模型",
    ),
    ModelSpec(
        key="table",
        url="https://paddleocr.bj.bcebos.com/PP-StructureV2/ch_ppstructure_mobile_v2.0_SLANet_infer.tar",
        description="PP-Structure 表格结构模型",
    ),
)


def download_models(
    models_dir: Path,
    logger,
    force: bool = False,
    specs: tuple[ModelSpec, ...] = MODEL_SPECS,
) -> None:
    models_dir.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        dest_dir = models_dir / spec.key
        if dest_dir.exists() and any(dest_dir.iterdir()) and not force:
            logger.info("Skip %s (already exists). Use --force to re-download.", dest_dir)
            continue
        if dest_dir.exists() and force:
            shutil.rmtree(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Downloading %s from %s", spec.description, spec.url)
        archive_path = _download_to_temp(spec.url)
        try:
            _extract_archive(archive_path, dest_dir)
        finally:
            archive_path.unlink(missing_ok=True)


def _download_to_temp(url: str) -> Path:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(url).suffix) as tmp_file:
        with urllib.request.urlopen(url) as response:
            shutil.copyfileobj(response, tmp_file)
        return Path(tmp_file.name)


def _extract_archive(archive_path: Path, dest_dir: Path) -> None:
    with tarfile.open(archive_path, "r:*") as archive:
        _safe_extract(archive, dest_dir)


def _safe_extract(archive: tarfile.TarFile, dest_dir: Path) -> None:
    dest_dir = dest_dir.resolve()
    for member in archive.getmembers():
        target_path = dest_dir / member.name
        if not str(target_path.resolve()).startswith(str(dest_dir)):
            raise RuntimeError(f"Unsafe path in archive: {member.name}")
    archive.extractall(dest_dir)
