"""Shared pure functions for source scanner behavior."""

from __future__ import annotations

import re


def detect_responsibilities(lines: list[str]) -> list[str]:
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
    if re.search(r"\bdef\s+\w+.*:", joined) and re.search(r"(sum|angle|calc|compute|polygon)", joined, re.I):
        tags.add("calculation")
    if re.search(r"^\s*(score|sides)\s*=", joined, re.M):
        tags.add("global_state")
    if module_level_execution(lines):
        tags.add("top_level_execution")
    return sorted(tags)


def hidden_global_text_scan(lines: list[str]) -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    current_fn = ""
    for index, line in enumerate(lines, start=1):
        if line.strip().startswith("def "):
            current_fn = line.strip().split("(")[0].replace("def ", "")
        if "print(" in line and "score" in line and "final_score" in current_fn:
            hits.append((current_fn, index, "score"))
    return hits


def module_level_execution(lines: list[str]) -> bool:
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
            and not stripped.startswith(("def ", "class ", "if ", "for ", "while ", "elif ", "else"))
        ):
            return True
    return False
