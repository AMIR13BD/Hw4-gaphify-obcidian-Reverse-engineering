"""Persist Graphify run logs and metadata."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.graph.collector import CollectResult
from ex04_agent.graph.graphify_run_result import GraphifyRunResult


def build_error(return_code: int, collect: CollectResult) -> str | None:
    """Build a human-readable error message when a run fails."""
    if return_code != 0:
        return f"Graphify exited with code {return_code}"
    if collect.missing_required:
        missing = ", ".join(collect.missing_required)
        return f"Missing required artifacts: {missing}"
    return None


def write_log(result: GraphifyRunResult) -> None:
    """Write stdout/stderr capture for a Graphify run."""
    path = Path(result.log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"Graphify run — phase={result.phase}",
        f"Timestamp: {result.timestamp}",
        f"Command: {' '.join(result.command)}",
        f"CWD: {result.cwd}",
        f"Return code: {result.return_code}",
        f"Graphify CLI: {result.graphify_cli} ({result.graphify_cli_path})",
        f"Success: {result.success}",
        "",
        "=== STDOUT ===",
        result.stdout or "(empty)",
        "",
        "=== STDERR ===",
        result.stderr or "(empty)",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_metadata(result: GraphifyRunResult) -> None:
    """Write machine-readable metadata for a Graphify run."""
    path = Path(result.metadata_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
