from __future__ import annotations

from src.models import ResearchSignal


def discover_opportunities() -> list[ResearchSignal]:
    """Deterministic discovery seed used by the smoke test and main entrypoint."""
    return [
        ResearchSignal(
            name="B2B grant matching copilot",
            audience="Small and midsize exporters",
            pain_point="Teams miss grant deadlines because discovery is fragmented and manual.",
            evidence=[
                "Funding programs change frequently across state and federal portals.",
                "Operators rely on spreadsheets and email reminders to track eligibility shifts.",
            ],
            urgency=8,
            market_pull=7,
            implementation_clarity=8,
        ),
        ResearchSignal(
            name="Maintenance quote response assistant",
            audience="Commercial facilities contractors",
            pain_point="Inbound quote requests arrive faster than teams can scope and respond.",
            evidence=[
                "Sales teams lose deals when site notes are translated into proposals too slowly.",
                "High-value jobs require fast follow-up before buyers collect competing bids.",
            ],
            urgency=9,
            market_pull=8,
            implementation_clarity=7,
        ),
    ]
