from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from oss_launch_check.rules import audit
from oss_launch_check.scanner import scan_repo


class AuditTests(unittest.TestCase):
    def test_empty_repo_scores_low(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = audit(scan_repo(Path(directory)))

            self.assertLess(result.percent, 40)
            self.assertGreaterEqual(result.error_count, 2)

    def test_reasonable_python_repo_scores_well(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_launch_ready_repo(root)

            result = audit(scan_repo(root))

            self.assertGreaterEqual(result.percent, 80)
            self.assertEqual(result.error_count, 0)

    def test_detects_secret_like_value(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_launch_ready_repo(root)
            token = "sk-" + "abcdefghijklmnopqrstuvwxyz123456"
            (root / "README.md").write_text(f"# Demo\n\nToken {token}", encoding="utf-8")

            result = audit(scan_repo(root))

            self.assertGreaterEqual(result.error_count, 1)
            self.assertTrue(any(finding.rule_id == "security.secret-patterns" for finding in result.findings))


def write_launch_ready_repo(root: Path) -> None:
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "README.md").write_text(
        "# Demo\n\n"
        "Demo explains why this exists and the problem it solves.\n\n"
        "## Install\n\nRun setup.\n\n"
        "## Usage\n\nRun the CLI.\n\n"
        "## Contributing\n\nOpen a PR.\n\n"
        "## License\n\nMIT.\n\n"
        + "More detail. " * 40,
        encoding="utf-8",
    )
    (root / "LICENSE").write_text("MIT License", encoding="utf-8")
    (root / "CONTRIBUTING.md").write_text("# Contributing\n\nRun tests.", encoding="utf-8")
    (root / "SECURITY.md").write_text("# Security\n\nReport vulnerabilities privately.", encoding="utf-8")
    (root / "CODE_OF_CONDUCT.md").write_text("# Code of Conduct", encoding="utf-8")
    (root / "ROADMAP.md").write_text("# Roadmap", encoding="utf-8")
    (root / "AGENTS.md").write_text("# Agent Instructions", encoding="utf-8")
    (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    (root / ".gitattributes").write_text("* text=auto eol=lf\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='demo'\ndescription='Demo'\nlicense='MIT'\n", encoding="utf-8")
    (root / ".github" / "workflows" / "ci.yml").write_text("name: CI", encoding="utf-8")
    (root / ".github" / "ISSUE_TEMPLATE" / "bug.yml").write_text("name: Bug", encoding="utf-8")
    (root / ".github" / "PULL_REQUEST_TEMPLATE.md").write_text("## Summary", encoding="utf-8")
    (root / "tests" / "test_demo.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
