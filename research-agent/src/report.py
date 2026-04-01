from __future__ import annotations

from .config import OUTPUTS_DIR
from .models import PipelineResult
from .utils import save_json


def _opportunity_suggestion(label: str) -> str:
    return f"Build a lightweight workflow fix focused on: {label.lower()}."


def write_report(result: PipelineResult) -> None:
    print("[6/6] writing report")
    report_json_path = OUTPUTS_DIR / "report.json"
    report_md_path = OUTPUTS_DIR / "report.md"

    save_json(report_json_path, result.model_dump())

    lines: list[str] = []
    lines.append(f"# Research Agent Report\n")
    lines.append(f"- Niche: **{result.niche}**")
    lines.append(f"- Source documents: **{result.source_count}**")
    lines.append(f"- Extracted complaints: **{result.extracted_count}**\n")

    lines.append("## Top Complaint Themes\n")
    for idx, theme in enumerate(result.ranked_themes, start=1):
        lines.append(f"### {idx}. {theme.label}")
        lines.append(f"- Frequency: {theme.complaint_count}")
        lines.append(f"- Severity hints: {theme.severity_score}")
        lines.append(f"- Buying signal hints: {theme.buying_signal_score}")
        lines.append(f"- Importance score: {theme.importance_score}")
        lines.append("- Evidence:")
        for evidence in theme.evidence[:3]:
            lines.append(f"  - {evidence}")
        lines.append(f"- Opportunity suggestion: {_opportunity_suggestion(theme.label)}\n")

    report_md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"  - wrote {report_md_path}")
    print(f"  - wrote {report_json_path}")