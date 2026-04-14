from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from collectors.reddit_collector import RedditCollector
from collectors.topic_researcher import TopicResearcher
from collectors.url_researcher import URLResearcher
from collectors.x_collector import XCollector
from ori_analysis.company_relevance import add_company_relevance
from ori_analysis.extract_pain_points import extract_pain_points
from ori_analysis.group_opportunities import group_opportunities
from ori_analysis.handoff import build_handoff
from ori_analysis.report_generation import build_report, write_report_outputs
from ori_analysis.score_opportunities import score_opportunities
from ori_analysis.summarize_research import summarize_research
from publishers.discord_publisher import DiscordPublisher
from storage import (
    init_db,
    log_handoff,
    save_pain_signals,
    save_research_report,
    save_research_task,
    save_theme_history,
)
from tasks.task_schema import ResearchTask


class TaskRunner:
    def __init__(self, task: ResearchTask):
        self.task = task
        self.output_dir = Path(task.output_dir)

    def run_once(self) -> dict[str, Any]:
        init_db()
        task_payload = self.task.to_dict()
        save_research_task(task_payload)
        posts = self._collect()
        pain_points = extract_pain_points(posts)
        opportunities = score_opportunities(group_opportunities(pain_points))
        opportunities = add_company_relevance(opportunities, self.task.company_profile)
        summary = summarize_research(task_payload, posts, pain_points, opportunities)
        handoff = build_handoff(task_payload, opportunities)
        report = build_report(task_payload, summary, opportunities, handoff)

        self._write_pipeline_outputs(posts, pain_points, opportunities)
        write_report_outputs(report, self.output_dir)
        save_pain_signals(pain_points, task_id=self.task.task_id)
        save_theme_history(opportunities, task_id=self.task.task_id)
        save_research_report(task_id=self.task.task_id, mode=self.task.mode, report=report)
        log_handoff(task_id=self.task.task_id, handoff=handoff)
        DiscordPublisher.from_env().publish(report)
        return report

    def _collect(self) -> list[dict[str, Any]]:
        posts: list[dict[str, Any]] = []
        subreddits = self.task.subreddits or (["smallbusiness"] if self.task.mode == "pain_monitor" else ["SaaS", "startups"])
        posts.extend(RedditCollector(subreddits=subreddits, seed_file=self.task.reddit_seed_file).collect())
        posts.extend(XCollector(queries=self.task.x_queries or [self.task.query], seed_posts=self.task.x_seed_posts).collect())
        if self.task.mode == "deep_research":
            topics = self.task.topics or [self.task.query]
            posts.extend(TopicResearcher(topics=topics).collect())
            if self.task.urls:
                posts.extend(URLResearcher(urls=self.task.urls).collect())
        return posts

    def _write_pipeline_outputs(self, posts: list[dict[str, Any]], pain_points: list[dict[str, Any]], opportunities: list[dict[str, Any]]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "raw_posts.json": posts,
            "pain_points.json": pain_points,
            "opportunities.json": opportunities,
        }
        for filename, payload in files.items():
            (self.output_dir / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")

