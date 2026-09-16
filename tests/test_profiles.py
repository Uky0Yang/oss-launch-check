import tempfile
import unittest
from pathlib import Path

from oss_launch_check.rules import audit
from oss_launch_check.scanner import scan_repo


class ProfileTests(unittest.TestCase):
    def test_docs_profile_removes_package_requirement_but_keeps_security(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = scan_repo(Path(directory))
            default = audit(snapshot)
            docs = audit(snapshot, profile='docs')
            rules = {f.rule_id for f in docs.findings}
            self.assertNotIn('packaging.metadata', rules)
            self.assertIn('security.secret-patterns', rules)
            self.assertLess(docs.max_score, default.max_score)

    def test_invalid_profile_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                audit(scan_repo(Path(directory)), profile='typo')
