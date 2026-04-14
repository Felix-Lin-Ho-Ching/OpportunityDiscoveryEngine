from __future__ import annotations

from typing import Any


def summarize_research(task: dict[str, Any], posts: list[dict[str, Any]], pain_points: list[dict[str, Any]], opportunities: list[dict[str, Any]]) -> dict[str, Any]:
    top = opportunities[0] if opportunities else None
    return {
        "task_id": task.get("task_id"),
        "mode": task.get("mode"),
        "query": task.get("query"),
        "summary": _summary_sentence(top, len(posts), len(pain_points)),
        "source_count": len(posts),
        "pain_point_count": len(pain_points),
        "opportunity_count": len(opportunities),
        "top_opportunity": top,
    }


def _summary_sentence(top: dict[str, Any] | None, post_count: int, pain_count: int) -> str:
    if not top:
        return f"Reviewed {post_count} sources and found no strong repeated pain signals."
    return (
        f"Reviewed {post_count} sources and found {pain_count} pain signals. "
        f"The strongest opportunity is {top['theme']} with score {top['scores']['total']}."
    )

