from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class XCollector:
    """Integration path for X/Twitter collection.

    The repository stays Python-only and deterministic, so this class is a
    stub unless the caller injects seed posts. A live integration can replace
    ``collect`` with API-backed search while preserving the normalized schema.
    """

    queries: list[str]
    seed_posts: list[dict[str, Any]] | None = None
    limit: int = 25

    def collect(self) -> list[dict[str, Any]]:
        if self.seed_posts:
            return [self._normalize(post) for post in self.seed_posts[: self.limit]]
        return []

    def _normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        query = self.queries[0] if self.queries else "opportunity"
        return {
            "source": str(payload.get("source") or "x"),
            "source_type": "x",
            "title": str(payload.get("title") or f"X discussion: {query}"),
            "text": str(payload.get("text") or payload.get("body") or ""),
            "url": str(payload.get("url") or "https://x.com"),
            "created_at": str(payload.get("created_at") or datetime.now(timezone.utc).isoformat()),
            "engagement": payload.get("engagement") if isinstance(payload.get("engagement"), dict) else {},
        }

