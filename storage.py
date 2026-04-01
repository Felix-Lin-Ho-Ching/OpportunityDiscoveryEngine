from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from extraction import Opportunity
from scoring import DEFAULT_WEIGHTS, OpportunityScore


DB_PATH = Path("opportunities.db")


DEFAULT_MIN_EXEC_SCORE = 6.2


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db(db_path: Path = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_type TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                problem_summary TEXT NOT NULL,
                opportunity_summary TEXT NOT NULL,
                target_customer TEXT NOT NULL,
                delivery_type TEXT NOT NULL,
                business_model_guess TEXT NOT NULL,
                money_potential INTEGER NOT NULL,
                urgency INTEGER NOT NULL,
                pain_severity INTEGER NOT NULL,
                repeatability INTEGER NOT NULL,
                ai_executability INTEGER NOT NULL,
                speed_to_first_test INTEGER NOT NULL,
                reachability_of_buyers INTEGER NOT NULL,
                competition_risk INTEGER NOT NULL,
                total_score REAL NOT NULL,
                analysis_reasons TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS policy_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                policy_version INTEGER NOT NULL,
                min_exec_score REAL NOT NULL,
                weights_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                update_reason TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS policy_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_version INTEGER NOT NULL,
                min_exec_score REAL NOT NULL,
                weights_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                update_reason TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER NOT NULL,
                policy_version INTEGER NOT NULL,
                score REAL NOT NULL,
                payload_json TEXT NOT NULL,
                executed_at TEXT NOT NULL,
                FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER NOT NULL,
                won INTEGER NOT NULL,
                revenue REAL NOT NULL,
                notes TEXT,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY(execution_id) REFERENCES executions(id)
            )
            """
        )

        row = conn.execute("SELECT COUNT(*) FROM policy_state").fetchone()
        if row and row[0] == 0:
            conn.execute(
                """
                INSERT INTO policy_state (id, policy_version, min_exec_score, weights_json, updated_at, update_reason)
                VALUES (1, ?, ?, ?, ?, ?)
                """,
                (1, DEFAULT_MIN_EXEC_SCORE, json.dumps(DEFAULT_WEIGHTS), utc_now(), "bootstrap-default-policy"),
            )


def get_policy_state(db_path: Path = DB_PATH) -> dict[str, Any]:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT policy_version, min_exec_score, weights_json, updated_at, update_reason FROM policy_state WHERE id = 1"
        ).fetchone()

    assert row is not None
    return {
        "policy_version": int(row[0]),
        "min_exec_score": float(row[1]),
        "weights": json.loads(row[2]),
        "updated_at": row[3],
        "update_reason": row[4],
    }


def update_policy_state(min_exec_score: float, weights: dict[str, float], reason: str, db_path: Path = DB_PATH) -> dict[str, Any]:
    state = get_policy_state(db_path)
    new_version = state["policy_version"] + 1
    timestamp = utc_now()

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE policy_state
            SET policy_version = ?, min_exec_score = ?, weights_json = ?, updated_at = ?, update_reason = ?
            WHERE id = 1
            """,
            (new_version, min_exec_score, json.dumps(weights), timestamp, reason),
        )
        conn.execute(
            """
            INSERT INTO policy_history (policy_version, min_exec_score, weights_json, updated_at, update_reason)
            VALUES (?, ?, ?, ?, ?)
            """,
            (new_version, min_exec_score, json.dumps(weights), timestamp, reason),
        )

    return get_policy_state(db_path)


def save_opportunity(
    opp: Opportunity,
    score: OpportunityScore,
    analysis_reasons: list[str],
    db_path: Path = DB_PATH,
) -> int:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO opportunities (
                source, source_type, title, url, timestamp,
                problem_summary, opportunity_summary, target_customer, delivery_type, business_model_guess,
                money_potential, urgency, pain_severity, repeatability,
                ai_executability, speed_to_first_test, reachability_of_buyers,
                competition_risk, total_score, analysis_reasons
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                opp.source,
                opp.source_type,
                opp.title,
                opp.url,
                opp.timestamp,
                opp.problem_summary,
                opp.opportunity_summary,
                opp.target_customer,
                opp.delivery_type,
                opp.business_model_guess,
                score.money_potential,
                score.urgency,
                score.pain_severity,
                score.repeatability,
                score.ai_executability,
                score.speed_to_first_test,
                score.reachability_of_buyers,
                score.competition_risk,
                score.total_score,
                json.dumps(analysis_reasons),
            ),
        )
        return int(cur.lastrowid)


def log_execution(opportunity_id: int, score: float, policy_version: int, payload: dict[str, Any], db_path: Path = DB_PATH) -> int:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO executions (opportunity_id, policy_version, score, payload_json, executed_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (opportunity_id, policy_version, score, json.dumps(payload), utc_now()),
        )
        return int(cur.lastrowid)


def record_outcome(execution_id: int, won: bool, revenue: float, notes: str = "", db_path: Path = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO outcomes (execution_id, won, revenue, notes, recorded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (execution_id, 1 if won else 0, revenue, notes, utc_now()),
        )


def get_recent_outcomes(limit: int = 100, db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT o.won, o.revenue, e.score
            FROM outcomes o
            JOIN executions e ON e.id = o.execution_id
            ORDER BY o.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [{"won": bool(r[0]), "revenue": float(r[1]), "score": float(r[2])} for r in rows]