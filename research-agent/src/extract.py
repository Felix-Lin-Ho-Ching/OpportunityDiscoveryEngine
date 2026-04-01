from __future__ import annotations

from .config import PROCESSED_DIR
from .models import ExtractedComplaint, SourceItem
from .utils import save_json, sentence_split

COMPLAINT_KEYWORDS = {
    "frustrating",
    "slow",
    "bug",
    "broken",
    "miss",
    "missed",
    "wrong",
    "inaccurate",
    "error",
    "expensive",
    "costly",
    "cancel",
    "delay",
    "pain",
    "manual",
    "doesn't",
    "doesnt",
    "hard",
    "difficult",
    "waste",
}

SEVERITY_HINTS = {"always", "every", "critical", "urgent", "blocked", "can't", "cannot", "failed"}
BUYING_HINTS = {"pay", "price", "budget", "buy", "switch", "churn", "cancel", "renew"}


def extract_complaints(items: list[SourceItem]) -> list[ExtractedComplaint]:
    print("[3/6] extracting complaints")
    complaints: list[ExtractedComplaint] = []

    for item in items:
        sentences = sentence_split(item.text)
        for sentence in sentences:
            lowered = sentence.lower()
            if not any(keyword in lowered for keyword in COMPLAINT_KEYWORDS):
                continue

            severity = sum(h in lowered for h in SEVERITY_HINTS)
            buying = sum(h in lowered for h in BUYING_HINTS)
            complaints.append(
                ExtractedComplaint(
                    source_id=item.source_id,
                    sentence=sentence,
                    severity_hints=severity,
                    buying_hints=buying,
                )
            )

    save_json(
        PROCESSED_DIR / "extracted_complaints.json",
        [item.model_dump() for item in complaints],
    )
    print(f"  - extracted {len(complaints)} complaint-like sentences")
    print(f"  - saved to {PROCESSED_DIR / 'extracted_complaints.json'}")
    return complaints