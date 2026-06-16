"""Parse Graphify graph.json into domain models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ex04_agent.graph.models import GraphDocument, GraphLink, GraphNode


class GraphParser:
    """Load and validate Graphify graph.json files."""

    def load(self, path: Path | str) -> GraphDocument:
        """Read graph.json from disk and parse it."""
        file_path = Path(path)
        if not file_path.is_file():
            msg = f"Graph file not found: {file_path}"
            raise FileNotFoundError(msg)
        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            msg = f"Malformed graph JSON: {file_path}"
            raise ValueError(msg) from exc
        return self.parse(raw)

    def parse(self, raw: dict[str, Any]) -> GraphDocument:
        """Parse a raw Graphify JSON object."""
        if not isinstance(raw, dict):
            msg = "Graph JSON root must be an object"
            raise ValueError(msg)

        nodes_raw = raw.get("nodes")
        links_raw = raw.get("links")
        if not isinstance(nodes_raw, list):
            msg = "Graph JSON must contain a 'nodes' list"
            raise ValueError(msg)
        if not isinstance(links_raw, list):
            msg = "Graph JSON must contain a 'links' list"
            raise ValueError(msg)

        nodes = tuple(self._parse_node(item) for item in nodes_raw)
        links = tuple(self._parse_link(item) for item in links_raw)
        metadata = {
            key: value
            for key, value in raw.items()
            if key not in {"nodes", "links"}
        }
        return GraphDocument(
            directed=bool(raw.get("directed", True)),
            nodes=nodes,
            links=links,
            built_at_commit=self._optional_str(raw.get("built_at_commit")),
            raw_metadata=metadata,
        )

    def _parse_node(self, raw: Any) -> GraphNode:
        if not isinstance(raw, dict):
            msg = "Each node must be an object"
            raise ValueError(msg)
        node_id = raw.get("id")
        if not isinstance(node_id, str) or not node_id:
            msg = "Each node requires a non-empty string 'id'"
            raise ValueError(msg)
        node_type = raw.get("file_type") or raw.get("type") or "unknown"
        return GraphNode(
            id=node_id,
            label=str(raw.get("label", node_id)),
            node_type=str(node_type),
            source_file=self._optional_str(raw.get("source_file")),
            source_location=self._optional_str(raw.get("source_location")),
            origin=self._optional_str(raw.get("_origin") or raw.get("origin")),
            community=self._optional_int(raw.get("community")),
            raw=dict(raw),
        )

    def _parse_link(self, raw: Any) -> GraphLink:
        if not isinstance(raw, dict):
            msg = "Each link must be an object"
            raise ValueError(msg)
        source = raw.get("source")
        target = raw.get("target")
        if not isinstance(source, str) or not source:
            msg = "Each link requires a non-empty string 'source'"
            raise ValueError(msg)
        if not isinstance(target, str) or not target:
            msg = "Each link requires a non-empty string 'target'"
            raise ValueError(msg)
        relation = raw.get("relation") or raw.get("label") or "unknown"
        confidence = raw.get("confidence") or raw.get("edge_type") or "UNKNOWN"
        return GraphLink(
            source=source,
            target=target,
            relation=str(relation),
            confidence=str(confidence),
            confidence_score=self._optional_float(raw.get("confidence_score")),
            source_file=self._optional_str(raw.get("source_file")),
            source_location=self._optional_str(raw.get("source_location")),
            weight=float(raw.get("weight", 1.0) or 1.0),
            raw=dict(raw),
        )

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        return str(value) if isinstance(value, str) and value else None

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
