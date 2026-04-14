# Opportunity Discovery Engine

This repository contains an Ori-style research agent for finding repeated pain
signals and turning them into scored opportunity briefs.

The implementation is deterministic and Python-only. It does not require live
API access for normal local runs. Reddit and X collectors have offline seed
paths, URL research can read local files or HTTP URLs, and topic research emits
repeatable research briefs from task inputs.

## Modes

`pain_monitor`

Watches focused sources for repeated operational pain. This is the lightweight
mode for recurring scans of Reddit-style posts and optional X seed posts.

`deep_research`

Builds a fuller brief from topics, URLs, Reddit-style posts, and optional X seed
posts. This mode writes a Markdown and JSON research report and prepares a
handoff brief for the next agent.

## Quick Start

Run a deterministic pain monitor cycle:

```bash
python main.py --mode pain_monitor
```

Run deep research:

```bash
python main.py --mode deep_research
```

Run continuously:

```bash
python main.py --mode pain_monitor --loop --interval 300
```

Run a task payload:

```bash
python main.py --mode deep_research --task-file task.json
```

Run multiple jobs:

```bash
python main.py --mode pain_monitor --jobs-config jobs.json
```

## Task Payload

```json
{
  "task_id": "support-triage-001",
  "mode": "deep_research",
  "query": "support triage automation",
  "subreddits": ["SaaS", "smallbusiness"],
  "topics": ["support triage automation"],
  "urls": ["notes/customer-feedback.txt"],
  "reddit_seed_file": "data/reddit_seed.json",
  "x_seed_posts": [
    {
      "title": "Ticket triage is too slow",
      "text": "Manual support triage causes missed urgent customers and churn.",
      "url": "https://x.com/example/status/1"
    }
  ],
  "company_profile": {
    "focus_terms": ["support", "triage"],
    "capabilities": ["automation", "monitoring"]
  },
  "output_dir": "outputs"
}
```

A jobs config can be either a JSON list of task payloads or:

```json
{
  "jobs": [
    {
      "task_id": "job-1",
      "mode": "pain_monitor",
      "query": "invoice follow-up",
      "subreddits": ["smallbusiness"]
    }
  ]
}
```

## Outputs

Each run writes:

- `outputs/raw_posts.json`
- `outputs/pain_points.json`
- `outputs/opportunities.json`
- `outputs/research_report.json`
- `outputs/research_report.md`

If `DISCORD_WEBHOOK_URL` is set, `publishers/discord_publisher.py` posts a short
report summary to Discord. Without the environment variable, the publisher is a
no-op.

## Architecture

Collectors normalize source material into a shared raw post schema:

- `collectors/reddit_collector.py`
- `collectors/x_collector.py`
- `collectors/url_researcher.py`
- `collectors/topic_researcher.py`

Analysis modules transform raw posts into research artifacts:

- `ori_analysis/extract_pain_points.py`
- `ori_analysis/group_opportunities.py`
- `ori_analysis/score_opportunities.py`
- `ori_analysis/summarize_research.py`
- `ori_analysis/company_relevance.py`
- `ori_analysis/handoff.py`
- `ori_analysis/report_generation.py`

Task intake and orchestration live in:

- `tasks/task_schema.py`
- `tasks/task_runner.py`

SQLite persistence is in `storage.py`. The Ori tables are:

- `research_tasks`
- `research_reports`
- `pain_signals`
- `theme_history`
- `handoff_log`

The older opportunity engine tables remain in place for compatibility with the
existing root modules.

## Tests

Run the new tests:

```bash
python -m unittest tests.test_pain_pipeline tests.test_report_and_handoff
```

Run all unittest tests discoverable from the root:

```bash
python -m unittest discover
```
