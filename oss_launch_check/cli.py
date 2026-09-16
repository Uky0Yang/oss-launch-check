from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .report import render_json, render_markdown, render_text
from .rules import PROFILES, audit
from .scanner import scan_repo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-launch-check",
        description="Audit whether a repository is ready to launch as an open-source project.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository or directory to audit.")
    parser.add_argument("--format", choices=("text", "markdown", "json"), default="text", help="Output format.")
    parser.add_argument("--profile", choices=tuple(PROFILES), default="library", help="Select applicable checks (default: library).")
    parser.add_argument("--output", "-o", help="Write report to a file.")
    parser.add_argument("--min-score", type=int, default=0, help="Exit non-zero if score percent is below this threshold.")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit non-zero when error findings exist.")
    parser.add_argument("--include-passes", action="store_true", help="Include passing checks in text or markdown reports.")
    parser.add_argument("--max-files", type=int, default=4000, help="Maximum files to scan.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = audit(scan_repo(Path(args.path), max_files=args.max_files), profile=args.profile)

    if args.format == "json":
        output = render_json(result)
    elif args.format == "markdown":
        output = render_markdown(result, include_passes=args.include_passes)
    else:
        output = render_text(result, include_passes=args.include_passes)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8", newline="\n")
    else:
        print(output)

    if args.fail_on_error and result.error_count:
        return 1
    if args.min_score and result.percent < args.min_score:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
