from __future__ import annotations

from typing import Any


def build_handoff(task: dict[str, Any], opportunities: list[dict[str, Any]]) -> dict[str, Any]:
    top = opportunities[0] if opportunities else None
    if not top:
        return {
            "task_id": task.get("task_id"),
            "status": "no_handoff",
            "next_agent": None,
            "brief": "No opportunity crossed the research threshold.",
            "actions": [],
        }
    score = float(top.get("scores", {}).get("total", 0))
    next_agent = "build" if score >= 7 else "research"
    return {
        "task_id": task.get("task_id"),
        "status": "ready",
        "next_agent": next_agent,
        "opportunity_id": top.get("id"),
        "brief": f"Validate {top.get('theme')} with 5 buyer conversations and a narrow prototype.",
        "actions": [
            "Write buyer interview script from evidence snippets.",
            "Find 20 reachable buyers matching the source context.",
            "Prototype the smallest monitoring/reporting workflow implied by the pain.",
        ],
    }

