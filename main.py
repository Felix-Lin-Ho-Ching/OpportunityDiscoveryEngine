from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, cast

from tasks.task_runner import TaskRunner
from tasks.task_schema import Mode, ResearchTask, default_task


def load_tasks(mode: Mode, task_file: str | None, jobs_config: str | None) -> list[ResearchTask]:
    if jobs_config:
        payload = json.loads(Path(jobs_config).read_text(encoding="utf-8"))
        jobs = payload if isinstance(payload, list) else payload.get("jobs", [])
        if not isinstance(jobs, list):
            raise ValueError("--jobs-config must contain a list or an object with a jobs list")
        return [ResearchTask.from_dict(job, default_mode=mode) for job in jobs]

    if task_file:
        task = ResearchTask.from_file(task_file, default_mode=mode)
        if task.jobs:
            return [ResearchTask.from_dict(job, default_mode=task.mode) for job in task.jobs]
        return [task]

    return [default_task(mode)]


def run_tasks(tasks: list[ResearchTask]) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for task in tasks:
        report = TaskRunner(task).run_once()
        reports.append(report)
        summary = report.get("summary", {})
        print(
            f"{task.task_id}: mode={task.mode} sources={summary.get('source_count', 0)} "
            f"pain_points={summary.get('pain_point_count', 0)} "
            f"opportunities={summary.get('opportunity_count', 0)}"
        )
    return reports


def main() -> None:
    parser = argparse.ArgumentParser(description="Ori-style deterministic research agent")
    parser.add_argument("--mode", choices=["pain_monitor", "deep_research"], default="pain_monitor")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between loop cycles")
    parser.add_argument("--iterations", type=int, default=None, help="Optional max cycles for loop mode")
    parser.add_argument("--task-file", default=None, help="JSON task payload")
    parser.add_argument("--jobs-config", default=None, help="JSON list of task payloads or object with jobs")
    args = parser.parse_args()

    cycle = 0
    mode = cast(Mode, args.mode)
    while True:
        cycle += 1
        tasks = load_tasks(mode, args.task_file, args.jobs_config)
        run_tasks(tasks)

        if not args.loop:
            break
        if args.iterations is not None and cycle >= args.iterations:
            break
        print(f"cycle={cycle} sleeping={args.interval}s")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
