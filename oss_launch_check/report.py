from __future__ import annotations

import json

from .models import AuditResult


def render_text(result: AuditResult, include_passes: bool = False) -> str:
    lines = [
        f"oss-launch-check: {result.grade} ({result.percent}%)",
        f"score={result.score}/{result.max_score} errors={result.error_count} warnings={result.warning_count}",
        "",
        "Categories:",
    ]
    for category, data in sorted(result.categories.items()):
        percent = round(data["score"] * 100 / data["max_score"]) if data["max_score"] else 0
        lines.append(f"  - {category}: {data['score']}/{data['max_score']} ({percent}%)")

    findings = [finding for finding in result.findings if include_passes or finding.severity != "pass"]
    if findings:
        lines.extend(["", "Findings:"])
        for finding in findings:
            location = f" [{finding.path}]" if finding.path else ""
            lines.append(f"  [{finding.severity}] {finding.rule_id}{location}: {finding.message}")
            if finding.recommendation:
                lines.append(f"    fix: {finding.recommendation}")
    else:
        lines.extend(["", "No findings."])
    return "\n".join(lines)


def render_markdown(result: AuditResult, include_passes: bool = False) -> str:
    lines = [
        "# Open Source Launch Check",
        "",
        f"**Grade:** {result.grade} ({result.percent}%)",
        f"**Score:** {result.score}/{result.max_score}",
        f"**Errors:** {result.error_count}",
        f"**Warnings:** {result.warning_count}",
        "",
        "## Categories",
        "",
        "| Category | Score |",
        "| --- | --- |",
    ]
    for category, data in sorted(result.categories.items()):
        percent = round(data["score"] * 100 / data["max_score"]) if data["max_score"] else 0
        lines.append(f"| {category} | {data['score']}/{data['max_score']} ({percent}%) |")

    findings = [finding for finding in result.findings if include_passes or finding.severity != "pass"]
    lines.extend(["", "## Findings", ""])
    if not findings:
        lines.append("No findings.")
    for finding in findings:
        path = f" `{finding.path}`" if finding.path else ""
        lines.append(f"### {finding.severity.upper()}: {finding.title}")
        lines.append("")
        lines.append(f"- Rule: `{finding.rule_id}`")
        lines.append(f"- Category: `{finding.category}`")
        lines.append(f"- Score: `{finding.points}/{finding.max_points}`")
        if path:
            lines.append(f"- Path:{path}")
        lines.append(f"- Message: {finding.message}")
        if finding.recommendation:
            lines.append(f"- Recommendation: {finding.recommendation}")
        lines.append("")
    return "\n".join(lines)


def render_json(result: AuditResult) -> str:
    return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
