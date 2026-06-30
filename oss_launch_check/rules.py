from __future__ import annotations

import re

from .models import AuditResult, Finding, RepoSnapshot, SEVERITY_ORDER


README_NAMES = ("README.md", "readme.md", "README.rst")
LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
CONTRIBUTING_NAMES = ("CONTRIBUTING.md", ".github/CONTRIBUTING.md")
SECURITY_NAMES = ("SECURITY.md", ".github/SECURITY.md")
CODE_OF_CONDUCT_NAMES = ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md")
PACKAGE_FILES = ("pyproject.toml", "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "composer.json")
AGENT_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursorrules", ".github/copilot-instructions.md")

SECRET_PATTERNS = (
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgho_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
)

README_SECTION_HINTS = {
    "install": ("install", "installation", "setup", "getting started", "quickstart", "usage", "安装", "使用"),
    "why": ("why", "problem", "motivation", "目标", "为什么"),
    "contribute": ("contributing", "contribute", "贡献"),
    "license": ("license", "许可证"),
}


def audit(snapshot: RepoSnapshot) -> AuditResult:
    findings = [
        check_readme(snapshot),
        check_readme_sections(snapshot),
        check_license(snapshot),
        check_contributing(snapshot),
        check_code_of_conduct(snapshot),
        check_security_policy(snapshot),
        check_ci(snapshot),
        check_tests(snapshot),
        check_package_metadata(snapshot),
        check_issue_template(snapshot),
        check_pr_template(snapshot),
        check_gitignore(snapshot),
        check_gitattributes(snapshot),
        check_agent_instructions(snapshot),
        check_roadmap(snapshot),
        check_secret_patterns(snapshot),
    ]
    return build_result(snapshot, findings)


def finding(
    rule_id: str,
    title: str,
    category: str,
    severity: str,
    message: str,
    points: int,
    max_points: int,
    path: str | None = None,
    recommendation: str | None = None,
) -> Finding:
    return Finding(rule_id, title, category, severity, message, points, max_points, path, recommendation)


def pass_finding(rule_id: str, title: str, category: str, points: int, path: str | None = None, message: str = "OK") -> Finding:
    return finding(rule_id, title, category, "pass", message, points, points, path)


def check_readme(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file(README_NAMES)
    if path:
        text = snapshot.read_text(path).strip()
        if len(text) >= 500:
            return pass_finding("docs.readme", "README exists", "docs", 12, path, "README is present and substantial.")
        return finding("docs.readme", "README exists", "docs", "warning", "README exists but is very short.", 6, 12, path, "Add purpose, install, usage, contribution, and license sections.")
    return finding("docs.readme", "README exists", "docs", "error", "No README found.", 0, 12, recommendation="Add a README.md that explains what the project does and how to use it.")


def check_readme_sections(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file(README_NAMES)
    if not path:
        return finding("docs.readme-sections", "README sections", "docs", "error", "Cannot inspect README sections without README.", 0, 10)
    text = snapshot.read_text(path).lower()
    present = [name for name, hints in README_SECTION_HINTS.items() if any(hint in text for hint in hints)]
    points = round(len(present) * 10 / len(README_SECTION_HINTS))
    if points == 10:
        return pass_finding("docs.readme-sections", "README sections", "docs", 10, path, "README covers core launch sections.")
    return finding("docs.readme-sections", "README sections", "docs", "warning", f"README covers {len(present)}/{len(README_SECTION_HINTS)} expected section groups.", points, 10, path, "Cover why, install/usage, contribution, and license.")


def check_license(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file(LICENSE_NAMES)
    if path:
        return pass_finding("legal.license", "License", "legal", 10, path, "License file exists.")
    return finding("legal.license", "License", "legal", "error", "No license file found.", 0, 10, recommendation="Add a LICENSE file, commonly MIT or Apache-2.0 for developer tools.")


def check_contributing(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file(CONTRIBUTING_NAMES)
    if path:
        return pass_finding("community.contributing", "Contributing guide", "community", 7, path, "Contribution guide exists.")
    return finding("community.contributing", "Contributing guide", "community", "warning", "No contributing guide found.", 0, 7, recommendation="Add CONTRIBUTING.md with setup, test, and PR expectations.")


def check_code_of_conduct(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file(CODE_OF_CONDUCT_NAMES)
    if path:
        return pass_finding("community.code-of-conduct", "Code of conduct", "community", 4, path, "Code of conduct exists.")
    return finding("community.code-of-conduct", "Code of conduct", "community", "info", "No code of conduct found.", 0, 4, recommendation="Consider adding CODE_OF_CONDUCT.md if you expect external contributors.")


def check_security_policy(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file(SECURITY_NAMES)
    if path:
        return pass_finding("security.policy", "Security policy", "security", 6, path, "Security policy exists.")
    return finding("security.policy", "Security policy", "security", "info", "No security policy found.", 0, 6, recommendation="Add SECURITY.md with vulnerability reporting instructions.")


def check_ci(snapshot: RepoSnapshot) -> Finding:
    workflows = snapshot.glob_any(".github/workflows/", (".yml", ".yaml"))
    if workflows:
        return pass_finding("automation.ci", "GitHub Actions", "automation", 10, workflows[0], f"Found {len(workflows)} workflow file(s).")
    return finding("automation.ci", "GitHub Actions", "automation", "warning", "No GitHub Actions workflow found.", 0, 10, recommendation="Add CI that runs tests or validation on push and pull_request.")


def check_tests(snapshot: RepoSnapshot) -> Finding:
    test_files = [path for path in snapshot.files if path.startswith("tests/") or path.startswith("test/") or "/test_" in path or path.endswith(".test.ts") or path.endswith(".spec.ts")]
    if test_files:
        return pass_finding("quality.tests", "Tests", "quality", 10, test_files[0], f"Found {len(test_files)} test-looking file(s).")
    return finding("quality.tests", "Tests", "quality", "warning", "No test-looking files found.", 0, 10, recommendation="Add at least a smoke test or validation script.")


def check_package_metadata(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file(PACKAGE_FILES)
    if not path:
        return finding("packaging.metadata", "Package metadata", "packaging", "info", "No common package metadata file found.", 0, 7, recommendation="Add pyproject.toml, package.json, Cargo.toml, go.mod, or equivalent when applicable.")
    text = snapshot.read_text(path)
    points = 7
    if path == "package.json":
        if '"description"' not in text:
            points -= 2
        if '"license"' not in text:
            points -= 2
    if path == "pyproject.toml":
        if "description" not in text:
            points -= 2
        if "license" not in text:
            points -= 2
    severity = "pass" if points == 7 else "warning"
    return finding("packaging.metadata", "Package metadata", "packaging", severity, "Package metadata is present." if points == 7 else "Package metadata is present but missing common fields.", points, 7, path, "Include description and license metadata.")


def check_issue_template(snapshot: RepoSnapshot) -> Finding:
    templates = snapshot.glob_any(".github/ISSUE_TEMPLATE/")
    if templates or snapshot.has(".github/ISSUE_TEMPLATE.md"):
        return pass_finding("community.issue-template", "Issue template", "community", 5, (templates[0] if templates else ".github/ISSUE_TEMPLATE.md"), "Issue template exists.")
    return finding("community.issue-template", "Issue template", "community", "info", "No issue template found.", 0, 5, recommendation="Add issue templates for bugs, features, or project recommendations.")


def check_pr_template(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file((".github/PULL_REQUEST_TEMPLATE.md", "PULL_REQUEST_TEMPLATE.md"))
    if path:
        return pass_finding("community.pr-template", "Pull request template", "community", 5, path, "Pull request template exists.")
    return finding("community.pr-template", "Pull request template", "community", "info", "No pull request template found.", 0, 5, recommendation="Add a PR template with summary and checks.")


def check_gitignore(snapshot: RepoSnapshot) -> Finding:
    if snapshot.has(".gitignore"):
        return pass_finding("hygiene.gitignore", ".gitignore", "hygiene", 4, ".gitignore", ".gitignore exists.")
    return finding("hygiene.gitignore", ".gitignore", "hygiene", "warning", "No .gitignore found.", 0, 4, recommendation="Add .gitignore for generated files and local environments.")


def check_gitattributes(snapshot: RepoSnapshot) -> Finding:
    if snapshot.has(".gitattributes"):
        return pass_finding("hygiene.gitattributes", ".gitattributes", "hygiene", 3, ".gitattributes", ".gitattributes exists.")
    return finding("hygiene.gitattributes", ".gitattributes", "hygiene", "info", "No .gitattributes found.", 0, 3, recommendation="Add .gitattributes to stabilize line endings.")


def check_agent_instructions(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file(AGENT_FILES)
    if path:
        return pass_finding("agent.instructions", "Agent instructions", "agent", 5, path, "Agent instruction file exists.")
    return finding("agent.instructions", "Agent instructions", "agent", "info", "No agent instruction file found.", 0, 5, recommendation="Add AGENTS.md if AI coding agents will work in this repository.")


def check_roadmap(snapshot: RepoSnapshot) -> Finding:
    path = snapshot.any_file(("ROADMAP.md", ".github/ROADMAP.md"))
    if path:
        return pass_finding("docs.roadmap", "Roadmap", "docs", 4, path, "Roadmap exists.")
    return finding("docs.roadmap", "Roadmap", "docs", "info", "No roadmap found.", 0, 4, recommendation="Add ROADMAP.md to show maintainership direction.")


def check_secret_patterns(snapshot: RepoSnapshot) -> Finding:
    candidates = [path for path in snapshot.files if path.endswith((".md", ".py", ".js", ".ts", ".toml", ".json", ".yml", ".yaml", ".env.example"))]
    for path in sorted(candidates)[:500]:
        text = snapshot.read_text(path)
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            return finding("security.secret-patterns", "Secret scan", "security", "error", "Secret-like value found.", 0, 10, path, "Remove the secret and rotate it if it was real.")
    return pass_finding("security.secret-patterns", "Secret scan", "security", 10, message="No secret-like values found in scanned text files.")


def build_result(snapshot: RepoSnapshot, findings: list[Finding]) -> AuditResult:
    score = sum(finding.points for finding in findings)
    max_score = sum(finding.max_points for finding in findings)
    percent = round(score * 100 / max_score) if max_score else 0
    grade = grade_for(percent)
    categories: dict[str, dict[str, int]] = {}
    for item in findings:
        bucket = categories.setdefault(item.category, {"score": 0, "max_score": 0})
        bucket["score"] += item.points
        bucket["max_score"] += item.max_points
    sorted_findings = sorted(findings, key=lambda item: (-SEVERITY_ORDER[item.severity], item.category, item.rule_id))
    return AuditResult(str(snapshot.root), score, max_score, grade, sorted_findings, categories)


def grade_for(percent: int) -> str:
    if percent >= 90:
        return "A"
    if percent >= 80:
        return "B"
    if percent >= 70:
        return "C"
    if percent >= 60:
        return "D"
    return "F"
