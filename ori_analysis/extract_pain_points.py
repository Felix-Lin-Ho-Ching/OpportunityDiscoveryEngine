from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any


PAIN_TERMS = {
    "manual",
    "slow",
    "missed",
    "backlog",
    "error",
    "errors",
    "broken",
    "churn",
    "lost",
    "lose",
    "cost",
    "costly",
    "delay",
    "urgent",
    "overwhelmed",
    "repetitive",
    "waste",
    "triage",
}


@dataclass
class PainPoint:
    id: str
    source: str
    source_type: str
    title: str
    url: str
    text: str
    pain_terms: list[str]
    severity: int
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_pain_points(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pain_points: list[dict[str, Any]] = []
    for idx, post in enumerate(posts, start=1):
        text = f"{post.get('title', '')} {post.get('text', '')}".lower()
        terms = sorted(term for term in PAIN_TERMS if re.search(rf"\b{re.escape(term)}\b", text))
        if not terms:
            continue
        severity = min(10, 3 + len(terms) + _engagement_bonus(post.get("engagement", {})))
        evidence = _first_sentence(str(post.get("text") or post.get("title") or ""))
        pain_points.append(
            PainPoint(
                id=f"pain-{idx:04d}",
                source=str(post.get("source") or "unknown"),
                source_type=str(post.get("source_type") or "unknown"),
                title=str(post.get("title") or "Untitled"),
                url=str(post.get("url") or ""),
                text=str(post.get("text") or ""),
                pain_terms=terms,
                severity=severity,
                evidence=evidence,
            ).to_dict()
        )
    return pain_points


def _engagement_bonus(engagement: Any) -> int:
    if not isinstance(engagement, dict):
        return 0
    total = 0
    for key in ("score", "comments", "mentions", "likes", "reposts"):
        try:
            total += int(engagement.get(key, 0))
        except (TypeError, ValueError):
            pass
    if total >= 25:
        return 2
    if total >= 8:
        return 1
    return 0


def _first_sentence(text: str) -> str:
    sentence = re.split(r"(?<=[.!?])\s+", text.strip())[0]
    return sentence[:280]

