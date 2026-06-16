"""Graph/metrics-based architecture detectors."""

from __future__ import annotations

from typing import Any

from ex04_agent.detection.finding import ArchitectureFinding, EvidenceItem


def _doc_hub(label: str, source_file: str | None) -> bool:
    if not source_file:
        return True
    lowered = source_file.lower()
    return lowered.endswith(".md") or "readme" in lowered


def detect_god_nodes(metrics: dict[str, Any]) -> list[ArchitectureFinding]:
    findings: list[ArchitectureFinding] = []
    for node in metrics.get("potential_god_nodes", []):
        label = str(node.get("label", node.get("id", "")))
        source = node.get("source_file")
        if _doc_hub(label, source):
            category = "documentation_hub"
            title = f"Documentation/knowledge hub candidate: {label}"
            observation = (
                f"The graph suggests `{label}` is a documentation/knowledge hub, "
                "not necessarily a code bottleneck."
            )
        else:
            category = "possible_hub"
            title = f"Possible code hub candidate: {label}"
            observation = (
                f"The graph suggests `{label}` is a possible hub with elevated connectivity."
            )
        findings.append(
            ArchitectureFinding(
                id=f"god_node_{node['id']}",
                title=title,
                detector="GodNodeCandidateDetector",
                category=category,
                severity="medium",
                confidence="medium",
                status="needs_manual_validation",
                observation=observation,
                relation="High total degree in metrics; graph suggests central role.",
                confidence_reason="Derived from potential_god_nodes in metrics JSON.",
                context="OBS: hub list in metrics. REL: inspect node links. CONF: AST graph is EXTRACTED.",
                affected_nodes=(str(node["id"]),),
                affected_files=(str(source),) if source else (),
                evidence=(
                    EvidenceItem(
                        "metric",
                        "reports/architecture/metrics_before.json",
                        None,
                        None,
                        f"total_degree={node.get('total_degree', 0)}",
                    ),
                ),
                source_validation="Graph centrality only; needs manual confirmation in source.",
                next_validation_steps=(
                    "Open source file and confirm responsibilities.",
                    "Compare with obsidian/hot.md ranking.",
                ),
            )
        )
    return findings


def detect_disconnected_components(metrics: dict[str, Any]) -> list[ArchitectureFinding]:
    summary = metrics.get("summary", {})
    count = int(summary.get("connected_component_count", 0))
    if count < 4:
        return []
    return [
        ArchitectureFinding(
            id="disconnected_components",
            title="Multiple disconnected graph components",
            detector="DisconnectedComponentsDetector",
            category="navigation_scope",
            severity="low",
            confidence="high",
            status="validated_by_source",
            observation=(
                f"The graph shows {count} disconnected components. "
                "This may be expected in a tutorial repo with separate exercises."
            ),
            relation="Weakly connected subgraphs increase navigation scope.",
            confidence_reason="connected_component_count from metrics.",
            context="CTX: tutorial repos often split steps into isolated files.",
            affected_nodes=(),
            affected_files=(),
            evidence=(
                EvidenceItem(
                    "metric",
                    None,
                    None,
                    None,
                    f"connected_component_count={count}",
                ),
            ),
            source_validation="Validated by metrics component analysis.",
            next_validation_steps=("Map each component to a tutorial module in README.",),
        )
    ]


def detect_low_confidence_edges(metrics: dict[str, Any]) -> list[ArchitectureFinding]:
    low = metrics.get("low_confidence_links", [])
    if not low:
        return []
    return [
        ArchitectureFinding(
            id=f"low_confidence_{index}",
            title="Low-confidence graph link",
            detector="LowConfidenceEdgeDetector",
            category="ambiguous_relation",
            severity="medium",
            confidence="medium",
            status="needs_manual_validation",
            observation="Graph suggests an ambiguous or low-confidence relation.",
            relation=f"{item.get('source')} -> {item.get('target')} ({item.get('relation')})",
            confidence_reason=str(item.get("confidence")),
            context="CONF: non-EXTRACTED or low confidence_score.",
            affected_nodes=(str(item.get("source", "")), str(item.get("target", ""))),
            affected_files=(),
            evidence=(EvidenceItem("graph", None, None, None, str(item)),),
            source_validation="Needs manual confirmation in source.",
            next_validation_steps=("Validate relation in source files.",),
        )
        for index, item in enumerate(low)
    ]
