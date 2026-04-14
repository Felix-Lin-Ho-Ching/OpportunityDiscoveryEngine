from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_post(payload: dict[str, Any], default_subreddit: str) -> dict[str, Any]:
    title = str(payload.get("title") or payload.get("headline") or "Untitled reddit post").strip()
    text = str(payload.get("text") or payload.get("selftext") or payload.get("body") or "").strip()
    subreddit = str(payload.get("subreddit") or default_subreddit).strip().lstrip("r/")
    url = str(payload.get("url") or f"https://reddit.com/r/{subreddit}").strip()
    created_at = str(payload.get("created_at") or payload.get("timestamp") or _now())
    engagement = payload.get("engagement") if isinstance(payload.get("engagement"), dict) else {}
    if "score" in payload:
        engagement.setdefault("score", payload["score"])
    if "comments" in payload:
        engagement.setdefault("comments", payload["comments"])

    return {
        "source": f"r/{subreddit}",
        "source_type": "reddit",
        "title": title,
        "text": text,
        "url": url,
        "created_at": created_at,
        "engagement": engagement,
    }


@dataclass
class RedditCollector:
    """Offline-first reddit collector.

    If ``seed_file`` is provided it reads JSON posts from disk. Otherwise it
    emits deterministic synthetic posts from the requested subreddits/topics so
    tests and local runs do not depend on live network APIs.
    """

    subreddits: list[str]
    seed_file: str | None = None
    limit: int = 25

    def collect(self) -> list[dict[str, Any]]:
        if self.seed_file:
            payload = json.loads(Path(self.seed_file).read_text(encoding="utf-8"))
            posts = payload if isinstance(payload, list) else payload.get("posts", [])
            return [_normalize_post(p, self.subreddits[0] if self.subreddits else "startups") for p in posts[: self.limit]]

        if not self.subreddits:
            self.subreddits = ["startups"]

        templates = [
            (
                "Manual reporting is eating our week",
                "Every Monday we copy customer data between spreadsheets, miss follow-ups, and lose renewals when the backlog grows.",
            ),
            (
                "Support triage keeps breaking as volume grows",
                "We need a better way to monitor tickets, summarize urgent issues, and alert the team before customers churn.",
            ),
        ]
        posts: list[dict[str, Any]] = []
        for subreddit in self.subreddits:
            for idx, (title, text) in enumerate(templates, start=1):
                posts.append(
                    _normalize_post(
                        {
                            "title": title,
                            "text": text,
                            "subreddit": subreddit,
                            "url": f"https://reddit.com/r/{subreddit}/comments/ori_seed_{idx}",
                            "created_at": "2026-01-01T00:00:00+00:00",
                            "engagement": {"score": 12 + idx, "comments": 4 + idx},
                        },
                        subreddit,
                    )
                )
        return posts[: self.limit]

