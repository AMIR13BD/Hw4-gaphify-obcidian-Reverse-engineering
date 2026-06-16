"""Tests for graph parser, indexer, and metrics."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_agent.graph.indexer import GraphIndexer
from ex04_agent.graph.metrics import MetricsEngine
from ex04_agent.graph.parser import GraphParser


@pytest.fixture
def fixture_path() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "graph_sample.json"


@pytest.fixture
def document(fixture_path: Path):
    return GraphParser().load(fixture_path)


def test_parser_reads_nodes_and_links(document) -> None:
    """Parser loads Graphify nodes and links."""
    assert len(document.nodes) == 5
    assert len(document.links) == 4
    hub = next(node for node in document.nodes if node.id == "hub")
    assert hub.node_type == "code"
    assert hub.origin == "ast"
    assert hub.community == 1


def test_parser_accepts_missing_optional_fields(document) -> None:
    """Missing optional fields fall back to safe defaults."""
    leaf = next(node for node in document.nodes if node.id == "leaf_a")
    assert leaf.node_type == "unknown"
    assert leaf.source_file is None
    inferred = next(link for link in document.links if link.target == "leaf_b")
    assert inferred.relation == "imports"
    assert inferred.confidence == "INFERRED"


def test_parser_malformed_json_fails_clearly(tmp_path: Path) -> None:
    """Malformed JSON raises a clear ValueError."""
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed graph JSON"):
        GraphParser().load(bad)


def test_parser_missing_required_node_id() -> None:
    """Nodes without id raise a clear error."""
    with pytest.raises(ValueError, match="requires a non-empty string 'id'"):
        GraphParser().parse({"nodes": [{"label": "x"}], "links": []})


def test_parser_missing_required_link_endpoints() -> None:
    """Links without source/target raise a clear error."""
    payload = {"nodes": [{"id": "a"}], "links": [{"source": "a"}]}
    with pytest.raises(ValueError, match="requires a non-empty string 'target'"):
        GraphParser().parse(payload)


def test_indexer_outgoing_incoming_lookup(document) -> None:
    """Indexer builds outgoing and incoming link maps."""
    indexer = GraphIndexer(document)
    assert len(indexer.outgoing_by_source["hub"]) == 3
    assert len(indexer.incoming_by_target["leaf_a"]) == 1
    assert len(indexer.links_by_source_file["src/hub.py"]) == 1
    assert len(indexer.nodes_by_source_file["README.md"]) == 1


def test_metrics_relation_and_confidence_counts(document) -> None:
    """MetricsEngine aggregates relation and confidence counts."""
    report = MetricsEngine().compute(
        GraphIndexer(document),
        phase="before",
        graph_path="graph.json",
        generated_at="2026-01-01T00:00:00+00:00",
    )
    assert report.relation_counts["calls"] == 1
    assert report.relation_counts["imports"] == 1
    assert report.confidence_counts["EXTRACTED"] == 2
    assert report.confidence_counts["INFERRED"] == 1
    assert report.confidence_counts["AMBIGUOUS"] == 1


def test_metrics_potential_god_nodes(document) -> None:
    """High-degree hub is flagged as a potential god node."""
    report = MetricsEngine().compute(
        GraphIndexer(document),
        phase="before",
        graph_path="graph.json",
        generated_at="2026-01-01T00:00:00+00:00",
    )
    god_ids = {node["id"] for node in report.potential_god_nodes}
    assert "hub" in god_ids


def test_metrics_low_confidence_links(document) -> None:
    """Non-EXTRACTED and low-score links are flagged."""
    report = MetricsEngine().compute(
        GraphIndexer(document),
        phase="before",
        graph_path="graph.json",
        generated_at="2026-01-01T00:00:00+00:00",
    )
    assert report.summary["low_confidence_link_count"] == 3
    pairs = {(link["source"], link["target"]) for link in report.low_confidence_links}
    assert ("hub", "leaf_b") in pairs
    assert ("leaf_a", "readme") in pairs
    assert ("hub", "readme") in pairs


def test_metrics_components_and_isolated(document) -> None:
    """Connected components and isolated nodes are counted."""
    report = MetricsEngine().compute(
        GraphIndexer(document),
        phase="before",
        graph_path="graph.json",
        generated_at="2026-01-01T00:00:00+00:00",
    )
    assert report.summary["isolated_node_count"] == 1
    assert report.components["count"] == 2
