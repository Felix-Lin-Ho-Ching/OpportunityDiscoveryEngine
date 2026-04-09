from __future__ import annotations

from src.discovery import discover_opportunities
from src.feasibility import assess_feasibility
from src.hypothesis import build_opportunity_hypotheses
from src.report import write_reports


def run() -> None:
    signals = discover_opportunities()
    hypotheses = build_opportunity_hypotheses(signals)
    feasibility_assessments = assess_feasibility(hypotheses)
    write_reports(hypotheses, feasibility_assessments)


if __name__ == "__main__":
    run()
