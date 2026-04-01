from __future__ import annotations

from .config import PROCESSED_DIR
from .models import ComplaintTheme, ExtractedComplaint
from .utils import save_json, tokenize


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def group_complaints(complaints: list[ExtractedComplaint], threshold: float = 0.3) -> list[ComplaintTheme]:
    print("[4/6] grouping themes")
    groups: list[dict] = []

    for complaint in complaints:
        tokens = tokenize(complaint.sentence)
        placed = False

        for group in groups:
            similarity = _jaccard(tokens, group["tokens"])
            if similarity >= threshold:
                group["items"].append(complaint)
                group["tokens"] |= tokens
                placed = True
                break

        if not placed:
            groups.append({"tokens": set(tokens), "items": [complaint]})

    themes: list[ComplaintTheme] = []
    for i, group in enumerate(groups, start=1):
        items: list[ExtractedComplaint] = group["items"]
        label = items[0].sentence[:80]
        theme = ComplaintTheme(
            theme_id=f"theme_{i}",
            label=label,
            complaint_count=len(items),
            evidence=[item.sentence for item in items[:5]],
            severity_score=sum(item.severity_hints for item in items),
            buying_signal_score=sum(item.buying_hints for item in items),
        )
        themes.append(theme)

    save_json(PROCESSED_DIR / "grouped_themes.json", [item.model_dump() for item in themes])
    print(f"  - grouped into {len(themes)} themes")
    print(f"  - saved to {PROCESSED_DIR / 'grouped_themes.json'}")
    return themes