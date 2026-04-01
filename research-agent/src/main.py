from __future__ import annotations

from .config import NICHE
from .extract import extract_complaints
from .models import PipelineResult
from .rank import rank_themes
from .report import write_report
from .search import collect_sources
from .cluster import group_complaints


def run_pipeline() -> PipelineResult:
    print("[1/6] loading niche")
    niche = NICHE
    print(f"  - niche: {niche}")

    sources = collect_sources(niche)
    complaints = extract_complaints(sources)
    themes = group_complaints(complaints)
    ranked = rank_themes(themes)