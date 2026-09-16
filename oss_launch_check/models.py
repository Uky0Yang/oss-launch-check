from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


SEVERITY_ORDER = {"pass": 0, "info": 1, "warning": 2, "error": 3}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    category: str
    severity: str
    message: str
    points: int
    max_points: int
    path: str | None = None
    recommendation: str | None = None

    def to_dict(self) -> dict:
        data = {
            "rule_id": self.rule_id,
            "title": self.title,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "points": self.points,
            "max_points": self.max_points,
        }
        if self.path:
            data["path"] = self.path
        if self.recommendation:
            data["recommendation"] = self.recommendation
        return data


@dataclass
class RepoSnapshot:
    root: Path
    files: set[str]
    text_cache: dict[str, str] = field(default_factory=dict)

    def has(self, path: str) -> bool:
        return normalize(path) in self.files

    def any_file(self, paths: list[str] | tuple[str, ...]) -> str | None:
        for path in paths:
            if self.has(path):
                return normalize(path)
        return None

    def glob_any(self, prefix: str, suffix: str | None = None) -> list[str]:
        prefix = normalize(prefix)
        matches = [path for path in self.files if path.startswith(prefix)]
        if suffix is not None:
            matches = [path for path in matches if path.endswith(suffix)]
        return sorted(matches)

    def read_text(self, path: str) -> str:
        path = normalize(path)
        if path not in self.text_cache:
            full_path = self.root / path
            try:
                self.text_cache[path] = full_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                self.text_cache[path] = ""
        return self.text_cache[path]


@dataclass
class AuditResult:
    root: str
    score: int
    max_score: int
    grade: str
    findings: list[Finding]
    categories: dict[str, dict[str, int]]
    profile: str = "library"

    @property
    def percent(self) -> int:
        if self.max_score == 0:
            return 0
        return round(self.score * 100 / self.max_score)

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "profile": self.profile,
            "score": self.score,
            "max_score": self.max_score,
            "percent": self.percent,
            "grade": self.grade,
            "summary": {
                "errors": self.error_count,
                "warnings": self.warning_count,
            },
            "categories": self.categories,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def normalize(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        return normalized[2:]
    return normalized
