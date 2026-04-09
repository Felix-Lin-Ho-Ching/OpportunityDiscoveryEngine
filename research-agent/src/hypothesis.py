from __future__ import annotations

from src.models import OpportunityHypothesis, ResearchSignal


def build_opportunity_hypotheses(
    signals: list[ResearchSignal],
) -> list[OpportunityHypothesis]:
    hypotheses: list[OpportunityHypothesis] = []
    for signal in signals:
        confidence = round(
            (
                signal.urgency
                + signal.market_pull
                + signal.implementation_clarity
            )
            / 30,
            2,
        )
        hypotheses.append(
            OpportunityHypothesis(
                title=signal.name,
                target_audience=signal.audience,
                problem_statement=signal.pain_point,
                solution_concept=(
                    f"Workflow automation product for {signal.audience.lower()} "
                    f"that compresses cycle time around {signal.pain_point.lower()}"
                ),
                evidence=signal.evidence,
                confidence=confidence,
                estimated_value=_estimate_value(signal),
                key_risks=_key_risks(signal),
            )
        )
    return hypotheses


def _estimate_value(signal: ResearchSignal) -> str:
    weighted_score = signal.urgency + signal.market_pull + signal.implementation_clarity
    if weighted_score >= 24:
        return "high"
    if weighted_score >= 20:
        return "medium"
    return "low"


def _key_risks(signal: ResearchSignal) -> list[str]:
    risks = ["Need crisp ICP definition before outbound validation."]
    if signal.implementation_clarity < 8:
        risks.append("Operational workflows may vary enough to require custom onboarding.")
    if signal.market_pull < 8:
        risks.append("Budget priority may slip if ROI proof is weak in the first 30 days.")
    return risks
