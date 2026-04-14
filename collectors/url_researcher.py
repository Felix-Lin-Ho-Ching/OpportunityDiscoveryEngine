from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen


@dataclass
class URLResearcher:
    urls: list[str]
    timeout_s: int = 8

    def collect(self) -> list[dict[str, Any]]:
        posts: list[dict[str, Any]] = []
        for url in self.urls:
            text = self._read_url(url)
            if not text.strip():
                continue
            title = self._title_for(url)
            posts.append(
                {
                    "source": urlparse(url).netloc or "local-file",
                    "source_type": "url",
                    "title": title,
                    "text": text[:6000],
                    "url": url,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "engagement": {},
                }
            )
        return posts

    def _read_url(self, url: str) -> str:
        path = Path(url)
        if path.exists():
            return path.read_text(encoding="utf-8")
        if url.startswith("file://"):
            return Path(url[7:]).read_text(encoding="utf-8")
        with urlopen(url, timeout=self.timeout_s) as response:
            return response.read().decode("utf-8", errors="replace")

    def _title_for(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme in {"http", "https"}:
            return parsed.netloc + parsed.path
        return Path(url.replace("file://", "")).name or "Local research source"

