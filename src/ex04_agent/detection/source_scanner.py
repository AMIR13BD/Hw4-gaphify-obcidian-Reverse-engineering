"""Read-only source scanning for architecture detectors."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from ex04_agent.detection.source_scanner_rules import (
    detect_responsibilities,
    hidden_global_text_scan,
)

RESPONSIBILITY_TAGS = (
    "input",
    "output",
    "calculation",
    "drawing",
    "class_definition",
    "top_level_execution",
    "global_state",
)


@dataclass(frozen=True)
class FileScanResult:
    """Scan summary for one source file."""

    path: str
    responsibilities: tuple[str, ...]
    syntax_valid: bool
    syntax_error: str | None
    line_count: int


class SourceScanner:
    """Safely inspect target repo files without modifying them."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def exists(self, relative_path: str) -> bool:
        return (self._repo_root / relative_path).is_file()

    def read_lines(self, relative_path: str) -> list[str]:
        path = self._repo_root / relative_path
        if not path.is_file():
            return []
        return path.read_text(encoding="utf-8", errors="replace").splitlines()

    def scan_file(self, relative_path: str) -> FileScanResult | None:
        if not self.exists(relative_path):
            return None
        lines = self.read_lines(relative_path)
        text = "\n".join(lines)
        syntax_valid, syntax_error = self.validate_syntax(text, relative_path)
        return FileScanResult(
            path=relative_path,
            responsibilities=tuple(sorted(set(detect_responsibilities(lines)))),
            syntax_valid=syntax_valid,
            syntax_error=syntax_error,
            line_count=len(lines),
        )

    def validate_syntax(self, text: str, relative_path: str) -> tuple[bool, str | None]:
        try:
            compile(text, relative_path, "exec")
            return True, None
        except SyntaxError as exc:
            return False, str(exc)

    def find_lines(self, relative_path: str, pattern: str) -> list[int]:
        regex = re.compile(pattern)
        return [i for i, line in enumerate(self.read_lines(relative_path), start=1) if regex.search(line)]

    def hidden_global_uses(self, relative_path: str) -> list[tuple[str, int, str]]:
        """Return (function_name, line_no, global_name) for param/global mismatches."""
        if not self.exists(relative_path):
            return []
        lines = self.read_lines(relative_path)
        try:
            tree = ast.parse("\n".join(lines))
        except SyntaxError:
            return hidden_global_text_scan(lines)
        hits: list[tuple[str, int, str]] = []
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            params = {arg.arg for arg in node.args.args}
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.Name)
                    and child.id not in params
                    and child.id in {"score", "sides"}
                    and isinstance(child.ctx, ast.Load)
                ):
                    hits.append((node.name, child.lineno, child.id))
        return hits
