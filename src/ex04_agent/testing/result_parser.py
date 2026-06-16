"""Parse command output to extract useful status information."""

from __future__ import annotations

import contextlib
import re
from pathlib import Path


def _read(path: str) -> str:
    text = ""
    with contextlib.suppress(OSError):
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    return text


def parse_pytest_summary(stdout_path: str) -> tuple[int, int, list[str]]:
    """Return (passed, failed, failed_test_paths) from pytest stdout."""
    text = _read(stdout_path)
    passed = failed = 0
    m = re.search(r"(\d+) passed", text)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", text)
    if m:
        failed = int(m.group(1))
    failed_files = []
    for match in re.finditer(r"^FAILED (.+?)::", text, re.MULTILINE):
        fpath = match.group(1).strip()
        if fpath not in failed_files:
            failed_files.append(fpath)
    return passed, failed, failed_files


def parse_coverage_percent(stdout_path: str) -> float | None:
    """Extract total coverage percent from pytest-cov stdout."""
    text = _read(stdout_path)
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", text)
    return float(m.group(1)) if m else None


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def parse_ruff_issues(stdout_path: str, *, stderr_path: str = "") -> int:
    """Return number of ruff issues from command output."""
    text = _strip_ansi(_read(stdout_path) + _read(stderr_path))
    if "All checks passed" in text:
        return 0
    m = re.search(r"Found (\d+) errors?", text)
    if m:
        return int(m.group(1))
    return 1 if text.strip() else 0
