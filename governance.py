from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from storage import DB_PATH


@dataclass
class HealthReport:
    outcomes_seen: int
    out_of_sample_win_rate: float
    false_positive_rate: float
    avg_revenue_per_execution: float
    source_drift_gap: float
    unit_economics_margin: float
    is_high_probability_ready: bool
    notes: list[str]


def generate_health_report(monthly_token_cost: float = 0.0, db_path: Path = DB_PATH) -> HealthReport:
    with sqlite3.connect(db_path) as conn:
        # recency split: newest 30% = out-of-sample
        rows = conn.execute(
            """
            SELECT o.id, o.won, o.revenue, op.source_type
            FROM outcomes o
            JOIN executions e ON e.id = o.execution_id
            JOIN opportunities op ON op.id = e.opportunity_id
            ORDER BY o.id ASC
            """
        ).fetchall()

    if not rows:
        return HealthReport(0, 0.0, 1.0, 0.0, 1.0, -monthly_token_cost, False, ["no outcomes logged"])

    n = len(rows)
    split_idx = max(1, int(n * 0.7))
    holdout = rows[split_idx:]

    holdout_wins = sum(r[1] for r in holdout)
    out_of_sample_win_rate = holdout_wins / len(holdout)

    false_positive_rate = 1.0 - (sum(r[1] for r in rows) / n)
    avg_revenue = sum(float(r[2]) for r in rows) / n

    # source drift: max-min win rate across source types
    by_source: dict[str, list[int]] = {}
    for _, won, _, source_type in rows:
        by_source.setdefault(source_type, []).append(int(won))
    source_win_rates = [sum(v) / len(v) for v in by_source.values() if v]
    source_drift_gap = (max(source_win_rates) - min(source_win_rates)) if len(source_win_rates) > 1 else 0.0

    unit_econ_margin = sum(float(r[2]) for r in rows) - monthly_token_cost

    notes: list[str] = []
    if n < 30:
        notes.append("low statistical volume (<30 outcomes)")
    if out_of_sample_win_rate < 0.35:
        notes.append("holdout win-rate below target")
    if false_positive_rate > 0.65:
        notes.append("false-positive rate above target")
    if source_drift_gap > 0.35:
        notes.append("source drift too high")
    if unit_econ_margin <= 0:
        notes.append("negative/flat unit economics")

    ready = not notes
    return HealthReport(
        outcomes_seen=n,
        out_of_sample_win_rate=round(out_of_sample_win_rate, 3),
        false_positive_rate=round(false_positive_rate, 3),
        avg_revenue_per_execution=round(avg_revenue, 2),
        source_drift_gap=round(source_drift_gap, 3),
        unit_economics_margin=round(unit_econ_margin, 2),
        is_high_probability_ready=ready,
        notes=notes,
    )