"""Proximity scoring helpers for dynamic hot.md ranking."""

from __future__ import annotations

from pathlib import PurePosixPath

from ex04_agent.graph.indexer import GraphIndexer


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def diff_proximity_score(
    node_id: str,
    source_file: str | None,
    changed_files: tuple[str, ...],
    indexer: GraphIndexer,
    nodes_by_source: dict[str, list[str]],
) -> float:
    """Score how close a node is to git-changed files."""
    if not changed_files:
        return 0.0
    if source_file:
        normalized = normalize_path(source_file)
        best = 0.0
        for changed in changed_files:
            changed_norm = normalize_path(changed)
            if normalized == changed_norm:
                return 1.0
            if PurePosixPath(normalized).parent == PurePosixPath(changed_norm).parent:
                best = max(best, 0.6)
        if best:
            return best

    changed_node_ids: set[str] = set()
    for changed in changed_files:
        changed_norm = normalize_path(changed)
        changed_node_ids.update(nodes_by_source.get(changed_norm, []))

    adjacency = indexer.undirected_adjacency
    for changed_id in changed_node_ids:
        if node_id == changed_id or node_id in adjacency.get(changed_id, set()):
            return 0.3
    return 0.0


def build_nodes_by_source(indexer: GraphIndexer) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for node in indexer.document.nodes:
        if node.source_file:
            key = normalize_path(node.source_file)
            mapping.setdefault(key, []).append(node.id)
    return mapping
