from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.utils.logger import setup_logger
from app.utils.model_downloader import MODEL_SPECS, download_models


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download PaddleOCR models")
    parser.add_argument("--models", required=True, help="Local models directory")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download and overwrite existing model directories",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger = setup_logger(debug=True)
    models_dir = Path(args.models)

    logger.info("Preparing to download %d models", len(MODEL_SPECS))
    download_models(models_dir, logger, force=args.force)
    logger.info("Models are ready at %s", models_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
