from __future__ import annotations

from typing import Any


def score_opportunities(opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for opportunity in opportunities:
        severity = float(opportunity.get("avg_severity", 1))
        repeatability = min(10, 3 + int(opportunity.get("pain_count", 0)) * 2)
        buyer_pull = min(10, 4 + len(opportunity.get("evidence", [])))
        build_speed = 8 if any(k in opportunity.get("theme", "") for k in ["reporting", "monitoring", "triage"]) else 6
        competition_risk = 4 if opportunity.get("theme") != "operations pain" else 5
        total = round(
            severity * 0.32
            + repeatability * 0.2
            + buyer_pull * 0.18
            + build_speed * 0.18
            + (11 - competition_risk) * 0.12,
            2,
        )
        enriched = dict(opportunity)
        enriched["scores"] = {
            "severity": round(severity, 2),
            "repeatability": repeatability,
            "buyer_pull": buyer_pull,
            "build_speed": build_speed,
            "competition_risk": competition_risk,
            "total": total,
        }
        scored.append(enriched)
    return sorted(scored, key=lambda item: (-item["scores"]["total"], item["theme"]))

