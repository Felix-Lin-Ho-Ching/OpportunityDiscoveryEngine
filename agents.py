from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol
from urllib import error, request

from analysis import analyze_signal
from extraction import extract_opportunity
from schema import RawSignal
from scoring import score_opportunity
from storage import get_policy_state, init_db, log_execution, save_opportunity


class SignalSourceAdapter(Protocol):
    name: str

    def fetch_signals(self) -> Iterable[RawSignal]:
        ...


class ExecutorAdapter(Protocol):
    name: str

    def execute(self, opportunity_payload: dict) -> bool:
        ...


@dataclass
class FileSignalAdapter:
    path: Path
    name: str = "file-sample-adapter"

    def fetch_signals(self) -> Iterable[RawSignal]:
        payloads = json.loads(self.path.read_text())
        return [RawSignal.from_dict(item) for item in payloads]


@dataclass
class LoggingExecutorAdapter:
    name: str = "logging-executor"

    def execute(self, opportunity_payload: dict) -> bool:
        print(f"[executor:{self.name}] queued({opportunity_payload.get('target_agent','research')}): {opportunity_payload['title']}")
        return True


@dataclass
class OpenClawHTTPExecutorAdapter:
    endpoint: str
    api_key: str | None = None
    timeout_s: int = 20
    name: str = "openclaw-http"

    def execute(self, opportunity_payload: dict) -> bool:
        data = json.dumps(opportunity_payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = request.Request(self.endpoint, data=data, headers=headers, method="POST")

        try:
            with request.urlopen(req, timeout=self.timeout_s) as resp:
                return 200 <= resp.status < 300
        except error.URLError as exc:
            print(f"[executor:{self.name}] request failed: {exc}")
            return False


@dataclass
class DiscordWebhookExecutorAdapter:
    webhook_url: str
    timeout_s: int = 10
    username: str = "opportunity-engine"
    name: str = "discord-webhook"

    def execute(self, opportunity_payload: dict) -> bool:
        title = opportunity_payload.get("title", "Untitled opportunity")
        target = opportunity_payload.get("target_agent", "research")
        score = opportunity_payload.get("score", "n/a")
        delivery_type = opportunity_payload.get("delivery_type", "n/a")
        summary = opportunity_payload.get("opportunity_summary", "")

        message = (
            f"🚀 **Opportunity queued**\n"
            f"**Title:** {title}\n"
            f"**Lane:** {target}\n"
            f"**Score:** {score}\n"
            f"**Delivery:** {delivery_type}\n"
            f"**Summary:** {summary[:400]}"
        )
        data = json.dumps({"username": self.username, "content": message}).encode("utf-8")
        req = request.Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_s) as resp:
                return 200 <= resp.status < 300
        except error.URLError as exc:
            print(f"[executor:{self.name}] request failed: {exc}")
            return False


@dataclass
class FanoutExecutorAdapter:
    adapters: list[ExecutorAdapter]
    require_all_success: bool = True
    name: str = "fanout-executor"

    def execute(self, opportunity_payload: dict) -> bool:
        if not self.adapters:
            return False
        results = [adapter.execute(opportunity_payload) for adapter in self.adapters]
        return all(results) if self.require_all_success else any(results)


@dataclass
class MultiOpenClawHTTPExecutorAdapter:
    research_endpoint: str
    build_endpoint: str | None = None
    sales_endpoint: str | None = None
    api_key: str | None = None
    timeout_s: int = 20
    name: str = "openclaw-multi"

    def execute(self, opportunity_payload: dict) -> bool:
        target = opportunity_payload.get("target_agent", "research")
        endpoint_map = {
            "research": self.research_endpoint,
            "build": self.build_endpoint or self.research_endpoint,
            "sales": self.sales_endpoint or self.research_endpoint,
        }
        endpoint = endpoint_map.get(target, self.research_endpoint)

        data = json.dumps(opportunity_payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = request.Request(endpoint, data=data, headers=headers, method="POST")

        try:
            with request.urlopen(req, timeout=self.timeout_s) as resp:
                return 200 <= resp.status < 300
        except error.URLError as exc:
            print(f"[executor:{self.name}:{target}] request failed: {exc}")
            return False


def recommend_next_agents(delivery_type: str, score: float) -> list[str]:
    # research is always first lane, then downstream lanes based on opportunity profile
    lanes = ["research"]
    text = delivery_type.lower()
    if score >= 6.5 and any(k in text for k in ["automation", "workflow", "operations"]):
        lanes.append("build")
    if score >= 6.8 and any(k in text for k in ["service", "reporting", "subscription", "performance"]):
        lanes.append("sales")
    return lanes


@dataclass
class AgentEngine:
    sources: list[SignalSourceAdapter]
    executor: ExecutorAdapter
    override_min_score_to_execute: float | None = None

    def run_once(self) -> tuple[int, int, int]:
        init_db()
        policy = get_policy_state()

        min_exec_score = self.override_min_score_to_execute or policy["min_exec_score"]
        weights = policy["weights"]
        policy_version = policy["policy_version"]

        collected = 0
        saved = 0
        executed = 0

        for source in self.sources:
            for signal in source.fetch_signals():
                collected += 1
                analysis = analyze_signal(signal)
                if not analysis.accepted:
                    continue

                opp = extract_opportunity(signal)
                score = score_opportunity(signal, opp, weights=weights)
                opp_id = save_opportunity(opp=opp, score=score, analysis_reasons=analysis.reasons)
                saved += 1

                if score.total_score >= min_exec_score:
                    lanes = recommend_next_agents(opp.delivery_type, score.total_score)
                    for lane in lanes:
                        payload = {
                            "title": opp.title,
                            "source": opp.source,
                            "target_customer": opp.target_customer,
                            "opportunity_summary": opp.opportunity_summary,
                            "delivery_type": opp.delivery_type,
                            "business_model_guess": opp.business_model_guess,
                            "score": score.total_score,
                            "policy_version": policy_version,
                            "target_agent": lane,
                        }
                        if self.executor.execute(payload):
                            log_execution(
                                opportunity_id=opp_id,
                                score=score.total_score,
                                policy_version=policy_version,
                                payload=payload,
                            )
                            executed += 1

        return collected, saved, executed

    def run_loop(self, interval_seconds: int = 300, iterations: int | None = None) -> None:
        i = 0
        while True:
            i += 1
            collected, saved, executed = self.run_once()
            print(
                f"Cycle {i}: collected={collected}, saved={saved}, executed={executed}, "
                f"sleep={interval_seconds}s"
            )

            if iterations is not None and i >= iterations:
                break
            time.sleep(interval_seconds)