"""Deterministic architecture metrics from a parsed graph."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from ex04_agent.graph.indexer import GraphIndexer
from ex04_agent.graph.metrics_topology import bridging_scores, connected_components, percentile_90
from ex04_agent.graph.models import GraphLink


@dataclass(frozen=True)
class MetricsReport:
    """Computed graph metrics ready for serialization."""

    phase: str
    graph_path: str
    summary: dict[str, Any]
    top_hubs: list[dict[str, Any]]
    bottleneck_candidates: list[dict[str, Any]]
    potential_god_nodes: list[dict[str, Any]]
    relation_counts: dict[str, int]
    confidence_counts: dict[str, int]
    communities: dict[str, int]
    components: dict[str, Any]
    low_confidence_links: list[dict[str, Any]]
    generated_at: str


class MetricsEngine:
    """Compute simple deterministic graph metrics without external graph libs."""

    def compute(self, indexer: GraphIndexer, *, phase: str, graph_path: str, generated_at: str) -> MetricsReport:
        nodes = indexer.document.nodes
        links = indexer.document.links
        node_ids = [node.id for node in nodes]
        in_degree = {node_id: len(indexer.incoming_by_target.get(node_id, [])) for node_id in node_ids}
        out_degree = {node_id: len(indexer.outgoing_by_source.get(node_id, [])) for node_id in node_ids}
        total_degree = {node_id: in_degree[node_id] + out_degree[node_id] for node_id in node_ids}
        max_degree = max(total_degree.values()) if total_degree else 0
        normalized_degree = {
            node_id: (total_degree[node_id] / max_degree if max_degree else 0.0)
            for node_id in node_ids
        }

        relation_counts = Counter(link.relation for link in links)
        confidence_counts = Counter(link.confidence for link in links)
        community_counts = Counter(
            str(node.community) for node in nodes if node.community is not None
        )
        components = connected_components(indexer.undirected_adjacency, node_ids)
        isolated = sum(1 for node_id in node_ids if total_degree[node_id] == 0)
        god_threshold = max(3, percentile_90(list(total_degree.values())))

        per_node = [
            {
                "id": node.id,
                "label": node.label,
                "in_degree": in_degree[node.id],
                "out_degree": out_degree[node.id],
                "total_degree": total_degree[node.id],
                "normalized_degree": round(normalized_degree[node.id], 4),
                "community": node.community,
                "source_file": node.source_file,
            }
            for node in nodes
        ]
        top_hubs = sorted(per_node, key=lambda item: (-item["total_degree"], item["id"]))[:10]
        bridging = bridging_scores(indexer, node_ids)
        bottleneck_candidates = sorted(
            (
                {
                    "id": node_id,
                    "label": indexer.nodes_by_id[node_id].label,
                    "bridging_score": round(score, 4),
                    "total_degree": total_degree[node_id],
                }
                for node_id, score in bridging.items()
            ),
            key=lambda item: (-item["bridging_score"], -item["total_degree"], item["id"]),
        )[:10]
        potential_god_nodes = [
            item for item in per_node if item["total_degree"] >= god_threshold
        ]
        low_confidence_links = [self._link_summary(link) for link in links if self._is_low_confidence(link)]

        summary = {
            "node_count": len(nodes),
            "link_count": len(links),
            "file_node_count": sum(1 for node in nodes if node.node_type == "file"),
            "code_node_count": sum(1 for node in nodes if node.node_type != "file"),
            "isolated_node_count": isolated,
            "connected_component_count": components["count"],
            "god_node_threshold": god_threshold,
            "low_confidence_link_count": len(low_confidence_links),
            "nodes": per_node,
        }
        return MetricsReport(
            phase=phase,
            graph_path=graph_path,
            summary=summary,
            top_hubs=top_hubs,
            bottleneck_candidates=bottleneck_candidates,
            potential_god_nodes=potential_god_nodes,
            relation_counts=dict(sorted(relation_counts.items())),
            confidence_counts=dict(sorted(confidence_counts.items())),
            communities=dict(sorted(community_counts.items())),
            components=components,
            low_confidence_links=low_confidence_links,
            generated_at=generated_at,
        )

    @staticmethod
    def _is_low_confidence(link: GraphLink) -> bool:
        if link.confidence != "EXTRACTED":
            return True
        return link.confidence_score is not None and link.confidence_score < 0.75

    @staticmethod
    def _link_summary(link: GraphLink) -> dict[str, Any]:
        return {
            "source": link.source,
            "target": link.target,
            "relation": link.relation,
            "confidence": link.confidence,
            "confidence_score": link.confidence_score,
            "source_file": link.source_file,
        }
