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

    result = PipelineResult(
        niche=niche,
        source_count=len(sources),
        extracted_count=len(complaints),
        ranked_themes=ranked,
    )

    write_report(result)
    print("Pipeline complete.")
    return result


if __name__ == "__main__":
    run_pipeline()