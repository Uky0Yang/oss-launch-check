# Contributing

Thanks for helping improve `oss-launch-check`.

## Good Contributions

- Better checks for real open-source launch readiness
- Lower false positives
- More ecosystem-specific package metadata detection
- Better report formats
- Tests for realistic repository layouts
- Documentation examples for CI, pre-commit, and release workflows

## Before Opening a PR

Run:

```bash
python -m unittest discover -s tests
python -m oss_launch_check .
```

If a rule changes behavior, add or update tests.

## Rule Design

Rules should be:

- Easy to explain
- Deterministic
- Useful without network access
- Safe for public and private repositories
- Broad enough to apply across languages

Avoid checks that require private GitHub API access or personal taste.
