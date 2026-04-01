from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # fallback for environments without package install access
    def load_dotenv() -> None:
        return None


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

NICHE = "AI note taking tools for sales teams"

OPTIONAL_LABELER_API_KEY = os.getenv("OPTIONAL_LABELER_API_KEY", "")

for path in [RAW_DIR, PROCESSED_DIR, OUTPUTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)