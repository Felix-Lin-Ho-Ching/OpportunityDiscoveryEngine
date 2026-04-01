from __future__ import annotations

from pathlib import Path
import unittest

from src.main import run_pipeline


class SmokeTest(unittest.TestCase):
    def test_pipeline_writes_outputs(self) -> None:
        result = run_pipeline()
        self.assertGreater(result.source_count, 0)
        self.assertGreaterEqual(result.extracted_count, 1)
        self.assertTrue(Path("outputs/report.md").exists())
        self.assertTrue(Path("outputs/report.json").exists())


if __name__ == "__main__":
    unittest.main()