from __future__ import annotations

from dataclasses import dataclass
from typing import List

from schema import RawSignal


MONEY_KEYWORDS = {
    "revenue",
    "sales",
    "profit",
    "lost",
    "cost",
    "chargeback",
    "payroll",
    "invoice",
    "refund",
    "margin",
    "price",
    "conversion",
    "churn",
}

PAIN_KEYWORDS = {
    "manual",
    "slow",
    "error",
    "late",
    "backlog",
    "missed",
    "waste",
    "bottleneck",
    "overwhelmed",
    "broken",
    "delay",
    "repetitive",
    "compliance",
}

AI_EXECUTION_KEYWORDS = {
    "data entry",
    "follow-up",
    "scheduling",
    "report",
    "triage",
    "qualification",
    "inbox",
    "support",
    "monitoring",
    "reconciliation",
    "onboarding",
    "document",
    "lead",
    "proposal",
}


@dataclass
class AnalysisResult:
    accepted: bool
    reasons: List[str]


def _contains_any(text: str, keywords: set[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def analyze_signal(signal: RawSignal) -> AnalysisResult:
    text_blob = f"{signal.title} {signal.text}".lower()
    reasons: List[str] = []

    has_money = _contains_any(text_blob, MONEY_KEYWORDS)
    has_pain = _contains_any(text_blob, PAIN_KEYWORDS)
    has_ai_executable_surface = _contains_any(text_blob, AI_EXECUTION_KEYWORDS)

    if has_money:
        reasons.append("clear money impact")
    if has_pain:
        reasons.append("clear operational pain")
    if has_ai_executable_surface:
        reasons.append("work appears AI-agent-executable")

    accepted = has_money and has_pain and has_ai_executable_surface
    if not accepted:
        reasons.append("rejected: weak monetizable + executable signal")

    return AnalysisResult(accepted=accepted, reasons=reasons)