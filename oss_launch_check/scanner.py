from __future__ import annotations

from pathlib import Path
import os

from .models import RepoSnapshot


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "target",
    ".next",
    ".turbo",
    "coverage",
}

IGNORE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
    ".map",
}


def scan_repo(root: Path, max_files: int = 4000) -> RepoSnapshot:
    root = root.resolve()
    files: set[str] = set()
    count = 0

    for current_root, dirs, filenames in os.walk(root):
        dirs[:] = sorted(directory for directory in dirs if directory not in IGNORE_DIRS)
        for filename in sorted(filenames):
            if should_ignore(filename):
                continue
            full_path = Path(current_root) / filename
            files.add(full_path.relative_to(root).as_posix())
            count += 1
            if count >= max_files:
                return RepoSnapshot(root=root, files=files)

    return RepoSnapshot(root=root, files=files)


def should_ignore(filename: str) -> bool:
    if filename in {".DS_Store", "Thumbs.db"}:
        return True
    return any(filename.endswith(suffix) for suffix in IGNORE_SUFFIXES)
