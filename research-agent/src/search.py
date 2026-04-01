from __future__ import annotations

from pathlib import Path

from .config import PROCESSED_DIR, RAW_DIR
from .models import SourceItem
from .utils import load_text, save_json


def collect_sources(niche: str) -> list[SourceItem]:
    print(f"[2/6] collecting sources for niche: {niche}")
    files = sorted(RAW_DIR.glob("*.txt"))
    if not files:
        raise FileNotFoundError(f"No .txt files found in {RAW_DIR}")

    collected: list[SourceItem] = []
    for file in files:
        text = load_text(file)
        item = SourceItem(
            source_id=file.stem,
            title=file.stem.replace("_", " ").title(),
            text=text,
        )
        collected.append(item)
        print(f"  - loaded {file.name} ({len(text)} chars)")

    save_json(
        PROCESSED_DIR / "collected_sources.json",
        [item.model_dump() for item in collected],
    )
    print(f"  - saved collected sources to {PROCESSED_DIR / 'collected_sources.json'}")
    return collected


def add_source_file(filename: str, content: str) -> Path:
    path = RAW_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path