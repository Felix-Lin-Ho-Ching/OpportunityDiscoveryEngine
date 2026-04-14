from __future__ import annotations

import json
import unittest
from pathlib import Path

from tasks.task_runner import TaskRunner
from tasks.task_schema import ResearchTask


class PainPipelineTest(unittest.TestCase):
    def test_pain_monitor_writes_pipeline_outputs(self) -> None:
        work_dir = Path("outputs/test_pain_pipeline")
        work_dir.mkdir(parents=True, exist_ok=True)
        seed_file = work_dir / "reddit_seed.json"
        output_dir = work_dir / "run"
        seed_file.write_text(
            json.dumps(
                [
                    {
                        "subreddit": "smallbusiness",
                        "title": "Manual invoice follow-up is costing us renewals",
                        "text": "Every week we miss follow-up, create errors, and lose revenue because the backlog is slow.",
                        "url": "https://reddit.com/r/smallbusiness/comments/1",
                        "score": 18,
                        "comments": 7,
                    }
                ]
            ),
            encoding="utf-8",
        )
        task = ResearchTask(
            mode="pain_monitor",
            task_id="test-pain",
            query="invoice follow-up",
            subreddits=["smallbusiness"],
            reddit_seed_file=str(seed_file),
            output_dir=str(output_dir),
        )

        report = TaskRunner(task).run_once()

        self.assertEqual(report["summary"]["pain_point_count"], 1)
        self.assertGreaterEqual(report["summary"]["opportunity_count"], 1)
        self.assertTrue((output_dir / "raw_posts.json").exists())
        self.assertTrue((output_dir / "pain_points.json").exists())
        self.assertTrue((output_dir / "opportunities.json").exists())
        pain_points = json.loads((output_dir / "pain_points.json").read_text(encoding="utf-8"))
        self.assertIn("manual", pain_points[0]["pain_terms"])


if __name__ == "__main__":
    unittest.main()
