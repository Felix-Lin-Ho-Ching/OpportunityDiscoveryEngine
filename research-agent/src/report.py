from __future__ import annotations

import json
from pathlib import Path

from src.models import FeasibilityAssessment, OpportunityHypothesis


OUTPUT_DIR = Path("outputs")


def write_reports(
    hypotheses: list[OpportunityHypothesis],
    feasibility_assessments: list[FeasibilityAssessment],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(
        OUTPUT_DIR / "opportunity_hypotheses.json",
        [hypothesis.to_dict() for hypothesis in hypotheses],
    )
    _write_json(
        OUTPUT_DIR / "feasibility_report.json",
        [assessment.to_dict() for assessment in feasibility_assessments],
    )
    _write_markdown(OUTPUT_DIR / "feasibility_report.md", feasibility_assessments)


def _write_json(path: Path, payload: list[dict[str, object]]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_markdown(
    path: Path, feasibility_assessments: list[FeasibilityAssessment]
) -> None:
    lines = ["# Feasibility Report", ""]
    for assessment in feasibility_assessments:
        lines.extend(
            [
                f"## {assessment.title}",
                f"- Decision: {assessment.decision}",
                f"- Score: {assessment.score}",
                f"- Technical complexity: {assessment.technical_complexity}",
                f"- Go-to-market readiness: {assessment.go_to_market_readiness}",
                f"- Rationale: {assessment.rationale}",
                "- Dependencies:",
            ]
        )
        lines.extend(f"  - {dependency}" for dependency in assessment.dependencies)
        lines.append("- Next steps:")
        lines.extend(f"  - {step}" for step in assessment.next_steps)
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
