"""Shared helpers for Obsidian vault builders."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ex04_agent.graph.indexer import GraphIndexer


@dataclass(frozen=True)
class VaultContext:
    """Inputs for deterministic vault generation."""

    phase: str
    repo_name: str
    repo_path: str
    metrics: dict[str, Any]
    indexer: GraphIndexer
    graph_report_text: str | None
    index_max_chars: int


def sanitize_filename(node_id: str) -> str:
    """Return a safe Obsidian note filename stem from a graph node id."""
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", node_id.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned[:120] or "node"


def node_wikilink(node_id: str, label: str) -> str:
    """Build a wikilink to a node page under nodes/."""
    stem = sanitize_filename(node_id)
    safe_label = label.replace("]]", "")
    return f"[[nodes/{stem}|{safe_label}]]"


def metrics_node_map(metrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index per-node metrics by graph id."""
    nodes = metrics.get("summary", {}).get("nodes", [])
    return {node["id"]: node for node in nodes if isinstance(node, dict) and "id" in node}
