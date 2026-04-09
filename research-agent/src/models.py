from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ResearchSignal:
    name: str
    audience: str
    pain_point: str
    evidence: list[str]
    urgency: int
    market_pull: int
    implementation_clarity: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OpportunityHypothesis:
    title: str
    target_audience: str
    problem_statement: str
    solution_concept: str
    evidence: list[str]
    confidence: float
    estimated_value: str
    key_risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FeasibilityAssessment:
    title: str
    decision: str
    score: float
    rationale: str
    technical_complexity: str
    go_to_market_readiness: str
    dependencies: list[str]
    next_steps: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
