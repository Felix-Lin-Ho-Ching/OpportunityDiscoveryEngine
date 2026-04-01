from __future__ import annotations

from .config import PROCESSED_DIR
from .models import ComplaintTheme, RankedTheme
from .utils import save_json


def rank_themes(themes: list[ComplaintTheme]) -> list[RankedTheme]:
    print("[5/6] ranking themes")
    ranked: list[RankedTheme] = []
    for theme in themes:
        score = (
            theme.complaint_count * 1.0
            + theme.severity_score * 0.7
            + theme.buying_signal_score * 0.6
        )
        ranked.append(
            RankedTheme(
                theme_id=theme.theme_id,
                label=theme.label,
                complaint_count=theme.complaint_count,
                severity_score=theme.severity_score,
                buying_signal_score=theme.buying_signal_score,
                importance_score=round(score, 2),
                evidence=theme.evidence,
            )
        )

    ranked.sort(key=lambda item: item.importance_score, reverse=True)
    save_json(PROCESSED_DIR / "ranked_themes.json", [item.model_dump() for item in ranked])
    print(f"  - ranked {len(ranked)} themes")
    print(f"  - saved to {PROCESSED_DIR / 'ranked_themes.json'}")
    return ranked