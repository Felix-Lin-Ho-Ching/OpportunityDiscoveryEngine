from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request


@dataclass
class DiscordPublisher:
    webhook_url: str | None = None
    username: str = "ori-research-agent"
    timeout_s: int = 10

    @classmethod
    def from_env(cls) -> "DiscordPublisher":
        return cls(
            webhook_url=os.getenv("DISCORD_WEBHOOK_URL"),
            username=os.getenv("DISCORD_WEBHOOK_USERNAME", "ori-research-agent"),
            timeout_s=int(os.getenv("DISCORD_TIMEOUT_S", "10")),
        )

    def publish(self, report: dict[str, Any]) -> bool:
        if not self.webhook_url:
            return False
        summary = report.get("summary", {})
        top = summary.get("top_opportunity") or {}
        content = (
            "**Ori research report**\n"
            f"Mode: {summary.get('mode')}\n"
            f"Summary: {summary.get('summary')}\n"
            f"Top opportunity: {top.get('theme', 'none')}"
        )
        payload = json.dumps({"username": self.username, "content": content}).encode("utf-8")
        req = request.Request(
            self.webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_s) as resp:
                return 200 <= resp.status < 300
        except error.URLError as exc:
            print(f"[discord] publish failed: {exc}")
            return False

