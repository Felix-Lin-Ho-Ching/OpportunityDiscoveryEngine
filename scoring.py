from __future__ import annotations

from dataclasses import dataclass

from extraction import Opportunity
from schema import RawSignal


DEFAULT_WEIGHTS = {
    "money_potential": 0.23,
    "urgency": 0.13,
    "pain_severity": 0.14,
    "repeatability": 0.12,
    "ai_executability": 0.17,
    "speed_to_first_test": 0.09,
    "reachability_of_buyers": 0.08,
    "competition_inverse": 0.04,
}


@dataclass
class OpportunityScore:
    money_potential: int
    urgency: int
    pain_severity: int
    repeatability: int
    ai_executability: int
    speed_to_first_test: int
    reachability_of_buyers: int
    competition_risk: int
    total_score: float


def _clamp(v: int, lo: int = 1, hi: int = 10) -> int:
    return max(lo, min(hi, v))


def score_opportunity(signal: RawSignal, opp: Opportunity, weights: dict[str, float] | None = None) -> OpportunityScore:
    text = f"{signal.title} {signal.text}".lower()
    w = {**DEFAULT_WEIGHTS, **(weights or {})}

    money = 5 + sum(k in text for k in ["revenue", "sales", "profit", "cost", "chargeback", "churn"])
    urgency = 4 + sum(k in text for k in ["urgent", "late", "daily", "weekly", "missed", "backlog"])
    pain = 4 + sum(k in text for k in ["manual", "error", "broken", "overwhelmed", "delay", "waste"])
    repeat = 4 + sum(k in text for k in ["daily", "weekly", "each", "every", "repetitive", "volume"])
    ai_exec = 5 + sum(k in text for k in ["inbox", "scheduling", "report", "triage", "support", "reconciliation"])
    speed = 5 + sum(k in text for k in ["csv", "email", "spreadsheet", "api", "zapier", "notion"])
    reach = 4 + sum(k in text for k in ["local", "smb", "clinic", "seller", "agency", "shopify"])
    comp_risk = 3 + sum(k in text for k in ["saturated", "many tools", "crowded", "commodity"])

    money = _clamp(money)
    urgency = _clamp(urgency)
    pain = _clamp(pain)
    repeat = _clamp(repeat)
    ai_exec = _clamp(ai_exec)
    speed = _clamp(speed)
    reach = _clamp(reach)
    comp_risk = _clamp(comp_risk)

    weighted_total = (
        money * w["money_potential"]
        + urgency * w["urgency"]
        + pain * w["pain_severity"]
        + repeat * w["repeatability"]
        + ai_exec * w["ai_executability"]
        + speed * w["speed_to_first_test"]
        + reach * w["reachability_of_buyers"]
        + (11 - comp_risk) * w["competition_inverse"]
    )

    return OpportunityScore(
        money_potential=money,
        urgency=urgency,
        pain_severity=pain,
        repeatability=repeat,
        ai_executability=ai_exec,
        speed_to_first_test=speed,
        reachability_of_buyers=reach,
        competition_risk=comp_risk,
        total_score=round(weighted_total, 2),
    )