"""Compile, AST, and safe import validators for target Python files."""

from __future__ import annotations

import ast
from pathlib import Path

# Modules/patterns that require GUI, input, or are unsafe to import directly
_UNSAFE_PATTERNS = ("turtle", "input(", "tkinter", "pygame", "wx.")


def _is_import_safe(path: Path) -> tuple[bool, str]:
    """Check if a module is safe to import (no GUI, no top-level input)."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return False, str(exc)
    for pattern in _UNSAFE_PATTERNS:
        if pattern in source:
            return False, f"contains '{pattern}'"
    # top-level execution outside __main__ guard is unsafe
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return False, "syntax error"
    for node in tree.body:
        if isinstance(node, (ast.If,)):
            # Allow if __name__ == "__main__" blocks
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            return False, "top-level function call"
    return True, ""


def compile_validate(py_files: list[Path]) -> tuple[list[str], list[str]]:
    """Return (passed_paths, failed_paths) for compile() check."""
    passed, failed = [], []
    for path in py_files:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            compile(source, str(path), "exec")
            passed.append(str(path))
        except (SyntaxError, OSError):
            failed.append(str(path))
    return passed, failed


def ast_validate(py_files: list[Path]) -> tuple[list[str], list[str]]:
    """Return (passed_paths, failed_paths) for ast.parse() check."""
    passed, failed = [], []
    for path in py_files:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            ast.parse(source, filename=str(path))
            passed.append(str(path))
        except (SyntaxError, OSError):
            failed.append(str(path))
    return passed, failed


def import_validate(py_files: list[Path]) -> tuple[list[str], list[str], list[str]]:
    """Return (passed, failed, skipped) based on safe-import heuristics."""
    passed, failed, skipped = [], [], []
    for path in py_files:
        safe, reason = _is_import_safe(path)
        if not safe:
            skipped.append(str(path))
        else:
            passed.append(str(path))
    return passed, failed, skipped
