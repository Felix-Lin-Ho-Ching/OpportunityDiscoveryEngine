from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from src.main import run


class SmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.output_dir = Path("outputs")
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)

    def test_pipeline_writes_expected_outputs(self) -> None:
        run()

        opportunity_path = self.output_dir / "opportunity_hypotheses.json"
        feasibility_json_path = self.output_dir / "feasibility_report.json"
        feasibility_md_path = self.output_dir / "feasibility_report.md"

        self.assertTrue(opportunity_path.exists())
        self.assertTrue(feasibility_json_path.exists())
        self.assertTrue(feasibility_md_path.exists())

        hypotheses = json.loads(opportunity_path.read_text(encoding="utf-8"))
        feasibility = json.loads(feasibility_json_path.read_text(encoding="utf-8"))
        markdown = feasibility_md_path.read_text(encoding="utf-8")

        self.assertEqual(len(hypotheses), 2)
        self.assertEqual(len(feasibility), 2)
        self.assertEqual(hypotheses[0]["title"], feasibility[0]["title"])
        self.assertIn("decision", feasibility[0])
        self.assertIn("# Feasibility Report", markdown)


if __name__ == "__main__":
    unittest.main()
