"""Helper functions for resolving token-efficiency file paths."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.shared.phase_paths import architecture_report_path


def required_input_paths(root: Path, obsidian: Path, phase: str) -> list[Path]:
    return [
        architecture_report_path(root, "metrics", phase, "json"),
        architecture_report_path(root, "findings", phase, "json"),
        architecture_report_path(root, "recommendations", phase, "json"),
        obsidian / "index.md",
        obsidian / "hot.md",
        root / "reports" / "comparison" / "before_after.json",
    ]


def top_node_pages(root: Path, obsidian: Path, phase: str, limit: int = 5) -> list[Path]:
    metrics = architecture_report_path(root, "metrics", phase, "json")
    if not metrics.is_file():
        return []
    data = json.loads(metrics.read_text(encoding="utf-8"))
    pages: list[Path] = []
    for hub in data.get("top_hubs", [])[:limit]:
        node_id = str(hub.get("id", ""))
        page = obsidian / "nodes" / f"{node_id}.md"
        if page.is_file():
            pages.append(page)
    return pages


def hub_source_files(root: Path, repo: Path, phase: str, limit: int = 5) -> list[Path]:
    metrics = architecture_report_path(root, "metrics", phase, "json")
    if not metrics.is_file():
        return []
    data = json.loads(metrics.read_text(encoding="utf-8"))
    out: list[Path] = []
    for hub in data.get("top_hubs", [])[:limit]:
        rel = hub.get("source_file")
        if rel:
            path = repo / str(rel)
            if path.is_file():
                out.append(path)
    return out


def affected_source_files(root: Path, repo: Path, phase: str) -> list[Path]:
    findings_path = architecture_report_path(root, "findings", phase, "json")
    if not findings_path.is_file():
        return []
    data = json.loads(findings_path.read_text(encoding="utf-8"))
    out: list[Path] = []
    for item in data.get("findings", []):
        for rel in item.get("affected_files", []):
            path = repo / str(rel)
            if path.is_file():
                out.append(path)
    return sorted(set(out), key=lambda x: str(x))
