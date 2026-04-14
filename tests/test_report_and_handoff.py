from __future__ import annotations

import json
import unittest
from pathlib import Path

from tasks.task_runner import TaskRunner
from tasks.task_schema import ResearchTask


class ReportAndHandoffTest(unittest.TestCase):
    def test_deep_research_report_and_handoff(self) -> None:
        output_dir = Path("outputs/test_report_and_handoff/run")
        output_dir.mkdir(parents=True, exist_ok=True)
        task = ResearchTask(
            mode="deep_research",
            task_id="test-deep",
            query="support triage automation",
            topics=["support triage automation"],
            subreddits=[],
            company_profile={"focus_terms": ["support", "triage"], "capabilities": ["automation"]},
            output_dir=str(output_dir),
        )

        report = TaskRunner(task).run_once()

        self.assertEqual(report["handoff"]["status"], "ready")
        self.assertIn(report["handoff"]["next_agent"], {"research", "build"})
        self.assertTrue((output_dir / "research_report.json").exists())
        self.assertTrue((output_dir / "research_report.md").exists())
        saved_report = json.loads((output_dir / "research_report.json").read_text(encoding="utf-8"))
        self.assertEqual(saved_report["task"]["task_id"], "test-deep")
        self.assertGreaterEqual(saved_report["opportunities"][0]["company_relevance"]["score"], 7)


if __name__ == "__main__":
    unittest.main()
