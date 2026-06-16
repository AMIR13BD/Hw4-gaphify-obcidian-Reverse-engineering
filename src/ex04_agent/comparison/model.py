"""Before/after comparison result models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class MetricDelta:
    name: str
    before: int | float
    after: int | float
    delta: int | float
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FindingDelta:
    before_count: int
    after_count: int
    resolved_or_removed: tuple[str, ...]
    remaining: tuple[str, ...]
    category_before: dict[str, int]
    category_after: dict[str, int]
    severity_before: dict[str, int]
    severity_after: dict[str, int]
    code_health_before: int
    code_health_after: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RecommendationDelta:
    before_count: int
    after_count: int
    action_before: dict[str, int]
    action_after: dict[str, int]
    priority_before: dict[str, int]
    priority_after: dict[str, int]
    patchable_before: int
    patchable_after: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphDelta:
    top_hubs_before: tuple[str, ...]
    top_hubs_after: tuple[str, ...]
    god_nodes_before: tuple[str, ...]
    god_nodes_after: tuple[str, ...]
    removed_nodes: tuple[str, ...]
    degree_changes: tuple[dict[str, Any], ...]
    story_summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ComparisonResult:
    before_phase: str
    after_phase: str
    metrics_delta: list[MetricDelta]
    findings_delta: FindingDelta
    recommendations_delta: RecommendationDelta
    graph_delta: GraphDelta
    improvement_summary: tuple[str, ...]
    remaining_risks: tuple[str, ...]
    evidence_paths: dict[str, str]
    output_paths: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "before_phase": self.before_phase,
            "after_phase": self.after_phase,
            "metrics_delta": [m.to_dict() for m in self.metrics_delta],
            "findings_delta": self.findings_delta.to_dict(),
            "recommendations_delta": self.recommendations_delta.to_dict(),
            "graph_delta": self.graph_delta.to_dict(),
            "improvement_summary": list(self.improvement_summary),
            "remaining_risks": list(self.remaining_risks),
            "evidence_paths": self.evidence_paths,
            "output_paths": self.output_paths,
        }

    def summary_counts(self) -> dict[str, Any]:
        nodes_b = next((m.before for m in self.metrics_delta if m.name == "node_count"), 0)
        nodes_a = next((m.after for m in self.metrics_delta if m.name == "node_count"), 0)
        return {
            "before_nodes": nodes_b,
            "after_nodes": nodes_a,
            "before_findings": self.findings_delta.before_count,
            "after_findings": self.findings_delta.after_count,
            "before_recommendations": self.recommendations_delta.before_count,
            "after_recommendations": self.recommendations_delta.after_count,
            "resolved_or_removed_findings_count": len(self.findings_delta.resolved_or_removed),
            "remaining_findings_count": len(self.findings_delta.remaining),
            "output_paths": self.output_paths,
        }
