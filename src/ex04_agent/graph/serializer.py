"""Serialize graph metrics to JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ex04_agent.graph.metrics import MetricsReport


class MetricsSerializer:
    """Write metrics reports to disk."""

    def to_dict(self, report: MetricsReport) -> dict[str, Any]:
        return {
            "phase": report.phase,
            "graph_path": report.graph_path,
            "summary": report.summary,
            "top_hubs": report.top_hubs,
            "bottleneck_candidates": report.bottleneck_candidates,
            "potential_god_nodes": report.potential_god_nodes,
            "relation_counts": report.relation_counts,
            "confidence_counts": report.confidence_counts,
            "communities": report.communities,
            "components": report.components,
            "low_confidence_links": report.low_confidence_links,
            "generated_at": report.generated_at,
        }

    def write(self, report: MetricsReport, path: Path | str) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.to_dict(report), indent=2),
            encoding="utf-8",
        )
        return output_path

    def format_terminal_summary(self, report: MetricsReport) -> str:
        summary = report.summary
        lines = [
            f"phase: {report.phase}",
            f"graph_path: {report.graph_path}",
            f"node_count: {summary['node_count']}",
            f"link_count: {summary['link_count']}",
            f"connected_component_count: {summary['connected_component_count']}",
            f"potential_god_nodes: {len(report.potential_god_nodes)}",
            f"low_confidence_links: {summary['low_confidence_link_count']}",
            "top_hubs:",
        ]
        for hub in report.top_hubs[:5]:
            lines.append(f"  - {hub['label']} (degree={hub['total_degree']})")
        return "\n".join(lines)
