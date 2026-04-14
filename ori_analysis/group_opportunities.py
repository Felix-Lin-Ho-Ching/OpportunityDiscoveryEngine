from __future__ import annotations

from collections import defaultdict
from typing import Any


THEME_KEYWORDS = {
    "support triage": {"support", "ticket", "triage", "customer", "churn"},
    "reporting automation": {"report", "reporting", "spreadsheet", "dashboard", "manual"},
    "follow-up operations": {"follow-up", "missed", "sales", "lead", "renewal"},
    "workflow monitoring": {"monitor", "alert", "backlog", "delay", "urgent"},
}


def group_opportunities(pain_points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pain in pain_points:
        buckets[_theme_for(pain)].append(pain)

    opportunities: list[dict[str, Any]] = []
    for idx, (theme, pains) in enumerate(sorted(buckets.items()), start=1):
        terms = sorted({term for pain in pains for term in pain.get("pain_terms", [])})
        avg_severity = round(sum(int(p.get("severity", 1)) for p in pains) / max(len(pains), 1), 2)
        opportunities.append(
            {
                "id": f"opp-{idx:04d}",
                "theme": theme,
                "pain_count": len(pains),
                "avg_severity": avg_severity,
                "keywords": terms,
                "evidence": [p["evidence"] for p in pains[:5] if p.get("evidence")],
                "sources": [{"title": p.get("title"), "url": p.get("url"), "source": p.get("source")} for p in pains],
                "solution_angle": _solution_for(theme),
            }
        )
    return opportunities


def _theme_for(pain: dict[str, Any]) -> str:
    text = f"{pain.get('title', '')} {pain.get('text', '')} {' '.join(pain.get('pain_terms', []))}".lower()
    best_theme = "operations pain"
    best_hits = 0
    for theme, keywords in THEME_KEYWORDS.items():
        hits = sum(keyword in text for keyword in keywords)
        if hits > best_hits:
            best_theme = theme
            best_hits = hits
    return best_theme


def _solution_for(theme: str) -> str:
    return {
        "support triage": "AI support triage, issue summarization, and churn-risk alerts.",
        "reporting automation": "Automated reporting agent that reconciles inputs and publishes weekly decision summaries.",
        "follow-up operations": "Follow-up monitor that flags missed renewals, leads, and handoffs.",
        "workflow monitoring": "Operations monitor with backlog detection, alerts, and owner assignment.",
    }.get(theme, "Managed AI workflow audit followed by a narrow automation pilot.")

