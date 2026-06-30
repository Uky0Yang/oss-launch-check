# Agent Instructions

## Purpose

Maintain `oss-launch-check`, a dependency-free Python CLI for auditing whether repositories are ready to launch as open-source projects.

## Scope

These instructions apply to code, tests, documentation, reports, and GitHub workflow files in this repository.

## Commands

Run these checks before publishing:

```bash
python -m unittest discover -s tests
python -m oss_launch_check . --min-score 80 --fail-on-error
```

## Safety

- Do not add network calls to the default audit path.
- Do not add model calls to the default audit path.
- Do not commit generated reports unless explicitly needed for docs.
- Do not print secret values in reports.
- Keep rules deterministic and covered by tests.

## Style

- Prefer standard-library Python.
- Keep rule messages short and actionable.
- Add tests when changing scoring or severity behavior.
- Keep report output useful in CI logs.
