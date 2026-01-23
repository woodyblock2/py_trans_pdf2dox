#!/usr/bin/env python3
import importlib
import pkgutil


def main() -> int:
    try:
        import paddleocr
    except Exception as exc:  # pylint: disable=broad-except
        print("FAILED: paddleocr import error:", exc)
        return 1

    version = getattr(paddleocr, "__version__", "unknown")
    print("paddleocr version:", version)

    ppstructure_loader = pkgutil.find_loader("paddleocr.ppstructure")
    print("ppstructure module found:", bool(ppstructure_loader))

    ppstructure_cls = getattr(paddleocr, "PPStructure", None)
    print("PPStructure in paddleocr:", ppstructure_cls is not None)

    if not ppstructure_loader and ppstructure_cls is None:
        print("FAILED: PPStructure not available. Install PaddleOCR 2.8+ from official sources.")
        return 2

    print("OK: PPStructure available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
