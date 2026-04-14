from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class TopicResearcher:
    topics: list[str]
    limit: int = 10

    def collect(self) -> list[dict[str, Any]]:
        posts: list[dict[str, Any]] = []
        for topic in self.topics[: self.limit]:
            clean = topic.strip() or "operations workflow"
            posts.append(
                {
                    "source": "topic-researcher",
                    "source_type": "topic",
                    "title": f"Research brief: {clean}",
                    "text": (
                        f"Teams discussing {clean} mention manual work, missed follow-up, slow reporting, "
                        "costly errors, and repeated weekly coordination. Buyers want monitoring, summaries, "
                        "alerts, and a faster way to turn customer data into decisions."
                    ),
                    "url": f"topic://{clean.replace(' ', '-')}",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "engagement": {"mentions": 3},
                }
            )
        return posts

