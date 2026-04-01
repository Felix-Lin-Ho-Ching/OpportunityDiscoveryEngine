from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[a-zA-Z0-9']+")


def save_json(path: Path, payload: Any) -> None:
    def _default(obj: Any):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=_default), encoding="utf-8")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text.lower()) if len(token) > 2}


def sentence_split(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    return [chunk.strip() for chunk in chunks if chunk.strip()]