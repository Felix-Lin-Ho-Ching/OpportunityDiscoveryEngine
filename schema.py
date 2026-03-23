from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class RawSignal:
    source: str
    source_type: str
    title: str
    text: str
    url: str
    timestamp: str
    engagement: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "RawSignal":
        required = ["source", "source_type", "title", "text", "url", "timestamp"]
        missing = [k for k in required if not payload.get(k)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        timestamp = payload["timestamp"]
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"Invalid timestamp format: {timestamp}") from exc

        engagement = payload.get("engagement", {}) or {}
        if not isinstance(engagement, dict):
            raise ValueError("engagement must be an object/dict when present")

        return cls(
            source=str(payload["source"]),
            source_type=str(payload["source_type"]),
            title=str(payload["title"]),
            text=str(payload["text"]),
            url=str(payload["url"]),
            timestamp=str(timestamp),
            engagement=engagement,
        )