"""Write unified diffs for patch results."""

from __future__ import annotations

import difflib
from pathlib import Path


def make_unified_diff(original: str, patched: str, filename: str) -> str:
    """Return a unified diff string between original and patched content."""
    orig_lines = original.splitlines(keepends=True)
    new_lines = patched.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        lineterm="",
    )
    return "".join(diff)


def write_diff(diff_content: str, diff_dir: Path, stem: str) -> Path:
    """Write a unified diff to a .diff file. Returns the path."""
    diff_dir.mkdir(parents=True, exist_ok=True)
    safe_stem = stem.replace("/", "_").replace("\\", "_").replace(".", "_")
    diff_path = diff_dir / f"{safe_stem}.diff"
    diff_path.write_text(diff_content, encoding="utf-8")
    return diff_path
