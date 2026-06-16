"""Graphify graph.json domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GraphNode:
    """Normalized Graphify node."""

    id: str
    label: str
    node_type: str
    source_file: str | None
    source_location: str | None
    origin: str | None
    community: int | None
    raw: dict[str, Any]


@dataclass(frozen=True)
class GraphLink:
    """Normalized Graphify link."""

    source: str
    target: str
    relation: str
    confidence: str
    confidence_score: float | None
    source_file: str | None
    source_location: str | None
    weight: float
    raw: dict[str, Any]


@dataclass(frozen=True)
class GraphDocument:
    """Parsed Graphify graph document."""

    directed: bool
    nodes: tuple[GraphNode, ...]
    links: tuple[GraphLink, ...]
    built_at_commit: str | None
    raw_metadata: dict[str, Any]
