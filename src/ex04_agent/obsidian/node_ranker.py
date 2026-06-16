"""Rank graph nodes for dynamic hot.md investigation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ex04_agent.graph.indexer import GraphIndexer
from ex04_agent.obsidian.rank_proximity import build_nodes_by_source, diff_proximity_score
from ex04_agent.obsidian.vault_context import metrics_node_map
from ex04_agent.shared.config import HotMdWeights


@dataclass(frozen=True)
class RankedNode:
    """Scored investigation candidate."""

    node_id: str
    label: str
    source_file: str | None
    total_degree: int
    score: float
    degree_score: float
    betweenness_score: float
    diff_score: float
    test_score: float
    ambiguous_score: float
    god_node_score: float
    reasons: tuple[str, ...]


class NodeRanker:
    """Deterministic node ranking from metrics, graph, and git diff."""

    def rank(
        self,
        metrics: dict[str, Any],
        indexer: GraphIndexer,
        *,
        changed_files: tuple[str, ...],
        failing_test_files: tuple[str, ...] = (),
        weights: HotMdWeights,
    ) -> list[RankedNode]:
        node_metrics = metrics_node_map(metrics)
        god_ids = {node["id"] for node in metrics.get("potential_god_nodes", [])}
        bridging = {
            item["id"]: float(item.get("bridging_score", 0.0))
            for item in metrics.get("bottleneck_candidates", [])
        }
        max_bridge = max(bridging.values()) if bridging else 0.0
        low_conf_ids = self._low_confidence_node_ids(metrics)
        nodes_by_source = build_nodes_by_source(indexer)

        ranked: list[RankedNode] = []
        for node_id, stats in sorted(node_metrics.items()):
            degree_score = float(stats.get("normalized_degree", 0.0))
            betweenness_score = (
                bridging.get(node_id, 0.0) / max_bridge if max_bridge else 0.0
            )
            source_file = stats.get("source_file")
            diff_score = diff_proximity_score(
                node_id, source_file, changed_files, indexer, nodes_by_source
            )
            test_score = diff_proximity_score(
                node_id, source_file, failing_test_files, indexer, nodes_by_source
            )
            ambiguous_score = 1.0 if node_id in low_conf_ids else 0.0
            god_node_score = 1.0 if node_id in god_ids else 0.0
            score = (
                weights.degree * degree_score
                + weights.betweenness * betweenness_score
                + weights.diff_proximity * diff_score
                + weights.test_proximity * test_score
                + weights.ambiguous * ambiguous_score
                + weights.god_node * god_node_score
            )
            reasons = self._reasons(
                diff_score, test_score, ambiguous_score, god_node_score, degree_score
            )
            ranked.append(
                RankedNode(
                    node_id=node_id,
                    label=str(stats.get("label", node_id)),
                    source_file=source_file,
                    total_degree=int(stats.get("total_degree", 0)),
                    score=round(score, 4),
                    degree_score=round(degree_score, 4),
                    betweenness_score=round(betweenness_score, 4),
                    diff_score=round(diff_score, 4),
                    test_score=round(test_score, 4),
                    ambiguous_score=round(ambiguous_score, 4),
                    god_node_score=round(god_node_score, 4),
                    reasons=reasons,
                )
            )

        ranked.sort(key=lambda item: (-item.score, -item.total_degree, item.node_id))
        return ranked

    @staticmethod
    def _low_confidence_node_ids(metrics: dict[str, Any]) -> set[str]:
        ids: set[str] = set()
        for link in metrics.get("low_confidence_links", []):
            if link.get("source"):
                ids.add(str(link["source"]))
            if link.get("target"):
                ids.add(str(link["target"]))
        return ids

    @staticmethod
    def _reasons(
        diff_score: float,
        test_score: float,
        ambiguous_score: float,
        god_node_score: float,
        degree_score: float,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if diff_score >= 1.0:
            reasons.append("source file changed in git diff")
        elif diff_score >= 0.6:
            reasons.append("same directory as a changed file")
        elif diff_score >= 0.3:
            reasons.append("connected to a changed-file node")
        if test_score > 0:
            reasons.append("near a failing test file path")
        if ambiguous_score > 0:
            reasons.append("involved in low-confidence/ambiguous link")
        if god_node_score > 0:
            reasons.append("possible god-node candidate")
        if degree_score >= 0.5 and not reasons:
            reasons.append("elevated graph centrality")
        if not reasons:
            reasons.append("graph context only — validate in source")
        return tuple(reasons)
