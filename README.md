# oss-launch-check

Audit whether a repository is ready to launch as an open-source project.

`oss-launch-check` is a dependency-free Python CLI that scans a repository and produces a launch readiness score across documentation, legal, community, automation, security, packaging, hygiene, quality, and AI-agent readiness.

## Why

Publishing a repository is easy. Launching one that people can understand, trust, run, contribute to, and share is harder.

This tool gives maintainers a practical pre-flight check before announcing a project, submitting it to directories, or asking for feedback. It is also useful in CI so open-source quality does not decay after launch.

## What It Checks

- README exists and is useful
- README covers why, install/usage, contribution, and license
- License file
- Contributing guide
- Code of conduct
- Security policy
- GitHub Actions workflow
- Tests or validation files
- Package metadata
- Issue template
- Pull request template
- `.gitignore`
- `.gitattributes`
- Agent instruction file such as `AGENTS.md`
- Roadmap
- Secret-like values in common text files

## Install

From this repository:

```bash
python -m pip install -e .
```

Or run without installing:

```bash
python -m oss_launch_check .
```

## Usage

Audit the current repository:

```bash
oss-launch-check .
```

Write a Markdown report:

```bash
oss-launch-check . --format markdown --output OSS_LAUNCH_REPORT.md
```

Write JSON for CI or dashboards:

```bash
oss-launch-check . --format json --output oss-launch-report.json
```

Fail CI below a score:

```bash
oss-launch-check . --min-score 80
```

Fail CI on error findings:

```bash
oss-launch-check . --fail-on-error
```

## Example Output

```text
oss-launch-check: B (84%)
score=82/98 errors=0 warnings=2

Categories:
  - automation: 10/10 (100%)
  - community: 12/21 (57%)
  - docs: 26/26 (100%)
```

## CI Example

```yaml
name: OSS launch check

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  oss-launch-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -e .
      - run: oss-launch-check . --min-score 80 --fail-on-error
```

## Design Principles

- No dependencies
- No model calls
- No network calls
- Deterministic reports
- Useful before and after launch
- Opinionated enough to help, but not tied to one language or framework

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests
python -m oss_launch_check . --format markdown --output OSS_LAUNCH_REPORT.md
```

## Related Ideas

This project pairs well with:

- repository context cards for coding agents
- agent instruction linting
- pre-commit checks
- GitHub Actions quality gates
- open-source launch checklists

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
