"""Python source validation via compile()."""

from __future__ import annotations

import ast
from pathlib import Path


def validate_text(source: str, filename: str = "<string>") -> tuple[bool, str]:
    """Return (ok, error_message). Error is empty string on success."""
    try:
        compile(source, filename, "exec")
        return True, ""
    except SyntaxError as exc:
        return False, str(exc)


def validate_file(path: Path) -> tuple[bool, str]:
    """Validate a file on disk."""
    if not path.is_file():
        return False, f"File not found: {path}"
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        return validate_text(source, str(path))
    except OSError as exc:
        return False, str(exc)


def ast_parse_text(source: str, filename: str = "<string>") -> tuple[bool, str]:
    """Try ast.parse; return (ok, error_message)."""
    try:
        ast.parse(source, filename=filename)
        return True, ""
    except SyntaxError as exc:
        return False, str(exc)
