from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from oss_launch_check.report import render_markdown, render_text
from oss_launch_check.rules import audit
from oss_launch_check.scanner import scan_repo


class ReportTests(unittest.TestCase):
    def test_text_report_has_grade_and_categories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = audit(scan_repo(Path(directory)))
            report = render_text(result)

            self.assertIn("oss-launch-check:", report)
            self.assertIn("Categories:", report)

    def test_markdown_report_can_include_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "LICENSE").write_text("MIT", encoding="utf-8")
            result = audit(scan_repo(root))
            report = render_markdown(result, include_passes=True)

            self.assertIn("## Findings", report)
            self.assertIn("PASS", report)


if __name__ == "__main__":
    unittest.main()
