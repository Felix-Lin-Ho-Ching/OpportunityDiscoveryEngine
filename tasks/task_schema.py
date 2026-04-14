from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Literal


Mode = Literal["pain_monitor", "deep_research"]


@dataclass
class ResearchTask:
    mode: Mode
    query: str = "AI workflow opportunities"
    task_id: str = "default"
    subreddits: list[str] = field(default_factory=list)
    x_queries: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    reddit_seed_file: str | None = None
    x_seed_posts: list[dict[str, Any]] = field(default_factory=list)
    company_profile: dict[str, Any] = field(default_factory=dict)
    output_dir: str = "outputs"
    jobs: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any], default_mode: Mode | None = None) -> "ResearchTask":
        mode = payload.get("mode") or default_mode or "pain_monitor"
        if mode not in {"pain_monitor", "deep_research"}:
            raise ValueError("mode must be pain_monitor or deep_research")
        return cls(
            mode=mode,
            query=str(payload.get("query") or "AI workflow opportunities"),
            task_id=str(payload.get("task_id") or payload.get("id") or "default"),
            subreddits=[str(v) for v in payload.get("subreddits", [])],
            x_queries=[str(v) for v in payload.get("x_queries", [])],
            urls=[str(v) for v in payload.get("urls", [])],
            topics=[str(v) for v in payload.get("topics", [])],
            reddit_seed_file=payload.get("reddit_seed_file"),
            x_seed_posts=list(payload.get("x_seed_posts", [])),
            company_profile=dict(payload.get("company_profile", {})),
            output_dir=str(payload.get("output_dir") or "outputs"),
            jobs=list(payload.get("jobs", [])),
        )

    @classmethod
    def from_file(cls, path: str | Path, default_mode: Mode | None = None) -> "ResearchTask":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")), default_mode=default_mode)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_task(mode: Mode) -> ResearchTask:
    if mode == "deep_research":
        return ResearchTask(
            mode=mode,
            query="AI operations research",
            task_id="deep-research-default",
            topics=["customer support operations", "weekly reporting automation"],
            subreddits=["SaaS", "smallbusiness"],
        )
    return ResearchTask(
        mode=mode,
        query="recurring operational pain",
        task_id="pain-monitor-default",
        subreddits=["smallbusiness"],
    )

