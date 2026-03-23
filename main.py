from __future__ import annotations

import argparse
import os
from pathlib import Path

from agents import (
    AgentEngine,
    DiscordWebhookExecutorAdapter,
    FileSignalAdapter,
    FanoutExecutorAdapter,
    LoggingExecutorAdapter,
    MultiOpenClawHTTPExecutorAdapter,
    OpenClawHTTPExecutorAdapter,
)
from governance import generate_health_report
from learning import apply_self_improvement_cycle
from storage import get_policy_state, record_outcome


def build_executor(mode: str):
    if mode == "openclaw":
        endpoint = os.getenv("OPENCLAW_ENDPOINT", "").strip()
        if not endpoint:
            raise ValueError("OPENCLAW_ENDPOINT is required when --executor openclaw")
        return OpenClawHTTPExecutorAdapter(
            endpoint=endpoint,
            api_key=os.getenv("OPENCLAW_API_KEY"),
            timeout_s=int(os.getenv("OPENCLAW_TIMEOUT_S", "20")),
        )

    if mode == "openclaw-multi":
        research = os.getenv("OPENCLAW_RESEARCH_ENDPOINT", "").strip()
        if not research:
            raise ValueError("OPENCLAW_RESEARCH_ENDPOINT is required when --executor openclaw-multi")
        return MultiOpenClawHTTPExecutorAdapter(
            research_endpoint=research,
            build_endpoint=os.getenv("OPENCLAW_BUILD_ENDPOINT"),
            sales_endpoint=os.getenv("OPENCLAW_SALES_ENDPOINT"),
            api_key=os.getenv("OPENCLAW_API_KEY"),
            timeout_s=int(os.getenv("OPENCLAW_TIMEOUT_S", "20")),
        )

    if mode == "openclaw-discord":
        endpoint = os.getenv("OPENCLAW_ENDPOINT", "").strip()
        webhook = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
        if not endpoint:
            raise ValueError("OPENCLAW_ENDPOINT is required when --executor openclaw-discord")
        if not webhook:
            raise ValueError("DISCORD_WEBHOOK_URL is required when --executor openclaw-discord")

        return FanoutExecutorAdapter(
            adapters=[
                OpenClawHTTPExecutorAdapter(
                    endpoint=endpoint,
                    api_key=os.getenv("OPENCLAW_API_KEY"),
                    timeout_s=int(os.getenv("OPENCLAW_TIMEOUT_S", "20")),
                ),
                DiscordWebhookExecutorAdapter(
                    webhook_url=webhook,
                    timeout_s=int(os.getenv("DISCORD_TIMEOUT_S", "10")),
                    username=os.getenv("DISCORD_WEBHOOK_USERNAME", "opportunity-engine"),
                ),
            ],
            require_all_success=True,
        )

    if mode == "openclaw-multi-discord":
        research = os.getenv("OPENCLAW_RESEARCH_ENDPOINT", "").strip()
        webhook = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
        if not research:
            raise ValueError("OPENCLAW_RESEARCH_ENDPOINT is required when --executor openclaw-multi-discord")
        if not webhook:
            raise ValueError("DISCORD_WEBHOOK_URL is required when --executor openclaw-multi-discord")

        return FanoutExecutorAdapter(
            adapters=[
                MultiOpenClawHTTPExecutorAdapter(
                    research_endpoint=research,
                    build_endpoint=os.getenv("OPENCLAW_BUILD_ENDPOINT"),
                    sales_endpoint=os.getenv("OPENCLAW_SALES_ENDPOINT"),
                    api_key=os.getenv("OPENCLAW_API_KEY"),
                    timeout_s=int(os.getenv("OPENCLAW_TIMEOUT_S", "20")),
                ),
                DiscordWebhookExecutorAdapter(
                    webhook_url=webhook,
                    timeout_s=int(os.getenv("DISCORD_TIMEOUT_S", "10")),
                    username=os.getenv("DISCORD_WEBHOOK_USERNAME", "opportunity-engine"),
                ),
            ],
            require_all_success=True,
        )

    return LoggingExecutorAdapter()


def main() -> None:
    parser = argparse.ArgumentParser(description="Layer 1 opportunity research engine")
    parser.add_argument("--signals", default="sample_signals.json", help="Path to signal JSON")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between cycles")
    parser.add_argument("--iterations", type=int, default=None, help="Optional max cycles for loop mode")
    parser.add_argument(
        "--executor",
        choices=["log", "openclaw", "openclaw-multi", "openclaw-discord", "openclaw-multi-discord"],
        default="log",
        help="Execution adapter",
    )
    parser.add_argument(
        "--min-exec-score",
        type=float,
        default=None,
        help="Override policy threshold for execution (optional)",
    )

    parser.add_argument("--record-outcome", action="store_true", help="Record outcome for an execution id")
    parser.add_argument("--execution-id", type=int, default=None, help="Execution id for outcome recording")
    parser.add_argument("--won", type=int, choices=[0, 1], default=None, help="Outcome win flag (0/1)")
    parser.add_argument("--revenue", type=float, default=0.0, help="Outcome revenue amount")
    parser.add_argument("--notes", default="", help="Optional outcome notes")

    parser.add_argument("--self-improve", action="store_true", help="Run one self-improvement policy update cycle")
    parser.add_argument("--health-report", action="store_true", help="Evaluate high-probability readiness metrics")
    parser.add_argument("--monthly-token-cost", type=float, default=0.0, help="Token + infra cost for unit economics")
    args = parser.parse_args()

    if args.record_outcome:
        if args.execution_id is None or args.won is None:
            raise ValueError("--record-outcome requires --execution-id and --won")
        record_outcome(execution_id=args.execution_id, won=bool(args.won), revenue=args.revenue, notes=args.notes)
        print(f"Recorded outcome for execution_id={args.execution_id}")
        return

    if args.self_improve:
        report = apply_self_improvement_cycle()
        state = get_policy_state()
        print(
            f"Self-improve updated={report.updated} reason={report.reason} "
            f"win_rate={report.win_rate} avg_revenue={report.avg_revenue} "
            f"min_exec_score={report.previous_min_exec_score}->{report.new_min_exec_score} "
            f"policy_version={state['policy_version']}"
        )
        return

    if args.health_report:
        hr = generate_health_report(monthly_token_cost=args.monthly_token_cost)
        print(f"outcomes_seen={hr.outcomes_seen}")
        print(f"out_of_sample_win_rate={hr.out_of_sample_win_rate}")
        print(f"false_positive_rate={hr.false_positive_rate}")
        print(f"avg_revenue_per_execution={hr.avg_revenue_per_execution}")
        print(f"source_drift_gap={hr.source_drift_gap}")
        print(f"unit_economics_margin={hr.unit_economics_margin}")
        print(f"is_high_probability_ready={hr.is_high_probability_ready}")
        print(f"notes={'; '.join(hr.notes) if hr.notes else 'none'}")
        return

    source = FileSignalAdapter(path=Path(args.signals))
    executor = build_executor(args.executor)
    engine = AgentEngine(sources=[source], executor=executor, override_min_score_to_execute=args.min_exec_score)

    if args.loop:
        engine.run_loop(interval_seconds=args.interval, iterations=args.iterations)
        return

    collected, saved, executed = engine.run_once()
    policy = get_policy_state()
    print(f"Collected signals: {collected}")
    print(f"Saved opportunities: {saved}")
    print(f"Executed opportunities: {executed}")
    print(f"Policy version: {policy['policy_version']} | Min exec score: {policy['min_exec_score']}")


if __name__ == "__main__":
    main()