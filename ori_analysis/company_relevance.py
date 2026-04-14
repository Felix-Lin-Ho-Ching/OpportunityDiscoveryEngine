from __future__ import annotations

from typing import Any


def add_company_relevance(opportunities: list[dict[str, Any]], company_profile: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    profile = company_profile or {}
    focus_terms = {str(term).lower() for term in profile.get("focus_terms", [])}
    capabilities = {str(term).lower() for term in profile.get("capabilities", [])}
    enriched: list[dict[str, Any]] = []
    for opportunity in opportunities:
        text = " ".join(
            [
                str(opportunity.get("theme", "")),
                str(opportunity.get("solution_angle", "")),
                " ".join(opportunity.get("keywords", [])),
            ]
        ).lower()
        hits = sorted(term for term in focus_terms | capabilities if term and term in text)
        relevance = min(10, 5 + len(hits) * 2) if profile else 6
        item = dict(opportunity)
        item["company_relevance"] = {
            "score": relevance,
            "matched_terms": hits,
            "rationale": "Matches stated focus/capabilities." if hits else "Generic fit for AI workflow services.",
        }
        enriched.append(item)
    return enriched

