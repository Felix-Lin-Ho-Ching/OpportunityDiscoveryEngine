from __future__ import annotations

from dataclasses import dataclass

from storage import get_policy_state, get_recent_outcomes, update_policy_state


@dataclass
class LearningReport:
    updated: bool
    reason: str
    previous_min_exec_score: float
    new_min_exec_score: float
    outcomes_seen: int
    win_rate: float
    avg_revenue: float


def apply_self_improvement_cycle(min_outcomes: int = 5) -> LearningReport:
    state = get_policy_state()
    outcomes = get_recent_outcomes(100)

    if len(outcomes) < min_outcomes:
        return LearningReport(
            updated=False,
            reason="not-enough-outcomes",
            previous_min_exec_score=state["min_exec_score"],
            new_min_exec_score=state["min_exec_score"],
            outcomes_seen=len(outcomes),
            win_rate=0.0,
            avg_revenue=0.0,
        )

    wins = sum(1 for o in outcomes if o["won"])
    avg_revenue = sum(o["revenue"] for o in outcomes) / len(outcomes)
    win_rate = wins / len(outcomes)

    new_score = state["min_exec_score"]
    new_weights = dict(state["weights"])

    if win_rate < 0.25:
        new_score = min(9.0, round(new_score + 0.2, 2))
        new_weights["money_potential"] = round(new_weights["money_potential"] + 0.01, 3)
        new_weights["competition_inverse"] = round(new_weights["competition_inverse"] + 0.005, 3)
        reason = f"auto-tighten low-win-rate({win_rate:.2f})"
    elif win_rate > 0.5 and avg_revenue > 1000:
        new_score = max(4.5, round(new_score - 0.1, 2))
        new_weights["repeatability"] = round(new_weights["repeatability"] + 0.01, 3)
        reason = f"auto-expand high-win-rate({win_rate:.2f})"
    else:
        reason = f"stable-policy win-rate({win_rate:.2f})"

    # keep weights simple and bounded
    for key in new_weights:
        new_weights[key] = min(0.5, max(0.01, new_weights[key]))

    # normalize to 1.0 for predictability
    total = sum(new_weights.values())
    new_weights = {k: round(v / total, 4) for k, v in new_weights.items()}

    updated = (new_score != state["min_exec_score"]) or (new_weights != state["weights"])
    if updated:
        update_policy_state(min_exec_score=new_score, weights=new_weights, reason=reason)

    return LearningReport(
        updated=updated,
        reason=reason,
        previous_min_exec_score=state["min_exec_score"],
        new_min_exec_score=new_score,
        outcomes_seen=len(outcomes),
        win_rate=round(win_rate, 3),
        avg_revenue=round(avg_revenue, 2),
    )