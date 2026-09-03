"""Regenerate responsive paper figures while keeping the original images intact.

Usage: python scripts/optimize_images.py
Dependencies: Pillow, PyYAML
"""
from pathlib import Path

import yaml
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def main():
    papers = yaml.safe_load((ROOT / "_data/publications.yml").read_text(encoding="utf-8"))
    original_bytes = preview_bytes = 0
    for paper in papers:
        original = ROOT / paper["image_original"]
        original_bytes += original.stat().st_size
        with Image.open(original) as source:
            for field, width in (("image", 480), ("image_large", 960)):
                output = ROOT / paper[field]
                height = round(source.height * width / source.width)
                source.resize((width, height), Image.Resampling.LANCZOS).save(
                    output, "WEBP", quality=90, method=6
                )
            preview_bytes += (ROOT / paper["image"]).stat().st_size
    print(f"{len(papers)} figures: {original_bytes:,} original bytes; {preview_bytes:,} bytes at 480px.")


if __name__ == "__main__":
    main()
