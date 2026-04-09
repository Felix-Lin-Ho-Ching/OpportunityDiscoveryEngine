from __future__ import annotations

from src.models import FeasibilityAssessment, OpportunityHypothesis


def assess_feasibility(
    hypotheses: list[OpportunityHypothesis],
) -> list[FeasibilityAssessment]:
    assessments: list[FeasibilityAssessment] = []
    for hypothesis in hypotheses:
        score = _score_hypothesis(hypothesis)
        decision = "go" if score >= 0.7 else "hold"
        assessments.append(
            FeasibilityAssessment(
                title=hypothesis.title,
                decision=decision,
                score=score,
                rationale=_rationale(hypothesis, score, decision),
                technical_complexity=_technical_complexity(hypothesis),
                go_to_market_readiness=_market_readiness(score),
                dependencies=_dependencies(hypothesis),
                next_steps=_next_steps(decision),
            )
        )
    return assessments


def _score_hypothesis(hypothesis: OpportunityHypothesis) -> float:
    risk_penalty = min(len(hypothesis.key_risks) * 0.05, 0.15)
    value_bonus = {"high": 0.15, "medium": 0.1, "low": 0.0}[hypothesis.estimated_value]
    score = hypothesis.confidence + value_bonus - risk_penalty
    return round(max(0.0, min(score, 1.0)), 2)


def _technical_complexity(hypothesis: OpportunityHypothesis) -> str:
    if "custom onboarding" in " ".join(hypothesis.key_risks).lower():
        return "medium"
    return "low"


def _market_readiness(score: float) -> str:
    if score >= 0.8:
        return "ready_for_design_partners"
    if score >= 0.7:
        return "needs_customer_validation"
    return "insufficient_signal"


def _dependencies(hypothesis: OpportunityHypothesis) -> list[str]:
    return [
        "Customer interviews with 5 target accounts",
        "Access to sample workflow data",
        f"Validation of pricing appetite for {hypothesis.target_audience.lower()}",
    ]


def _next_steps(decision: str) -> list[str]:
    if decision == "go":
        return [
            "Recruit design partners",
            "Prototype the narrowest workflow automation path",
            "Measure time-to-value over a two-week pilot",
        ]
    return [
        "Gather more problem interviews",
        "Refine segmentation and trigger conditions",
        "Re-run feasibility scoring after stronger evidence is collected",
    ]


def _rationale(
    hypothesis: OpportunityHypothesis, score: float, decision: str
) -> str:
    return (
        f"Decision {decision} with score {score} based on confidence "
        f"{hypothesis.confidence}, estimated value {hypothesis.estimated_value}, "
        f"and {len(hypothesis.key_risks)} tracked risks."
    )
