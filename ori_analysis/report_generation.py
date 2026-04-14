from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_report(task: dict[str, Any], summary: dict[str, Any], opportunities: list[dict[str, Any]], handoff: dict[str, Any]) -> dict[str, Any]:
    return {
        "task": task,
        "summary": summary,
        "opportunities": opportunities,
        "handoff": handoff,
    }


def write_report_outputs(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "research_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output_dir / "research_report.md").write_text(render_markdown_report(report), encoding="utf-8")


def render_markdown_report(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Ori Research Report",
        "",
        f"Mode: {summary.get('mode', 'unknown')}",
        f"Query: {summary.get('query', '')}",
        "",
        "## Summary",
        "",
        str(summary.get("summary", "")),
        "",
        "## Opportunities",
        "",
    ]
    opportunities = report.get("opportunities", [])
    if not opportunities:
        lines.append("No scored opportunities found.")
    for opp in opportunities:
        score = opp.get("scores", {}).get("total", "n/a")
        relevance = opp.get("company_relevance", {}).get("score", "n/a")
        lines.extend(
            [
                f"### {opp.get('theme', 'Untitled')} ({score})",
                "",
                f"- Pain signals: {opp.get('pain_count', 0)}",
                f"- Company relevance: {relevance}",
                f"- Solution angle: {opp.get('solution_angle', '')}",
                f"- Evidence: {'; '.join(opp.get('evidence', [])[:3])}",
                "",
            ]
        )
    handoff = report.get("handoff", {})
    lines.extend(["## Handoff", "", f"Status: {handoff.get('status')}", f"Next agent: {handoff.get('next_agent')}"])
    for action in handoff.get("actions", []):
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)

