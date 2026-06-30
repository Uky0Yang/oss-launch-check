from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from oss_launch_check.cli import main


class CliTests(unittest.TestCase):
    def test_json_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "report.json"
            (root / "README.md").write_text("# Demo", encoding="utf-8")

            self.assertEqual(main([str(root), "--format", "json", "--output", str(output)]), 0)

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("score", data)
            self.assertIn("findings", data)

    def test_min_score_can_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(StringIO()):
                code = main([directory, "--min-score", "90"])

            self.assertEqual(code, 1)

    def test_markdown_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "OSS_LAUNCH_REPORT.md"
            (root / "README.md").write_text("# Demo", encoding="utf-8")

            self.assertEqual(main([str(root), "--format", "markdown", "--output", str(output)]), 0)

            self.assertIn("# Open Source Launch Check", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
