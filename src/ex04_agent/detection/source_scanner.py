"""Read-only source scanning for architecture detectors."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

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
        responsibilities = self.detect_responsibilities(lines)
        return FileScanResult(
            path=relative_path,
            responsibilities=tuple(sorted(set(responsibilities))),
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
        return [
            index
            for index, line in enumerate(self.read_lines(relative_path), start=1)
            if regex.search(line)
        ]

    def detect_responsibilities(self, lines: list[str]) -> list[str]:
        tags: set[str] = set()
        joined = "\n".join(lines)
        if re.search(r"\binput\s*\(", joined):
            tags.add("input")
        if re.search(r"\bprint\s*\(", joined) or re.search(r"^\s*print\s+", joined, re.M):
            tags.add("output")
        if re.search(r"\bclass\s+\w+", joined):
            tags.add("class_definition")
        if re.search(r"\bturtle\b|\.forward\(|\.right\(", joined):
            tags.add("drawing")
        if re.search(r"\bdef\s+\w+.*:", joined) and re.search(
            r"(sum|angle|calc|compute|polygon)", joined, re.I
        ):
            tags.add("calculation")
        if re.search(r"^\s*(score|sides)\s*=", joined, re.M):
            tags.add("global_state")
        module_level = self._module_level_execution(lines)
        if module_level:
            tags.add("top_level_execution")
        return sorted(tags)

    def hidden_global_uses(self, relative_path: str) -> list[tuple[str, int, str]]:
        """Return (function_name, line_no, global_name) for param/global mismatches."""
        if not self.exists(relative_path):
            return []
        lines = self.read_lines(relative_path)
        text = "\n".join(lines)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return self._hidden_global_text_scan(lines)
        hits: list[tuple[str, int, str]] = []
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            param_names = {arg.arg for arg in node.args.args}
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.Name)
                    and child.id not in param_names
                    and child.id in {"score", "sides"}
                    and isinstance(child.ctx, ast.Load)
                ):
                    hits.append((node.name, child.lineno, child.id))
        return hits

    def _hidden_global_text_scan(self, lines: list[str]) -> list[tuple[str, int, str]]:
        hits: list[tuple[str, int, str]] = []
        current_fn = ""
        for index, line in enumerate(lines, start=1):
            if line.strip().startswith("def "):
                current_fn = line.strip().split("(")[0].replace("def ", "")
            if "print(" in line and "score" in line and "final_score" in current_fn:
                hits.append((current_fn, index, "score"))
        return hits

    @staticmethod
    def _module_level_execution(lines: list[str]) -> bool:
        in_def = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("class "):
                in_def = True
                continue
            if not stripped or stripped.startswith("#"):
                continue
            if not in_def and re.search(r"\b(input|print|welcome_message|draw_polygon)\b", stripped):
                return True
            if (
                not line.startswith((" ", "\t"))
                and re.search(r"\w+\s*\(", stripped)
                and not stripped.startswith(
                    ("def ", "class ", "if ", "for ", "while ", "elif ", "else")
                )
            ):
                return True
        return False
