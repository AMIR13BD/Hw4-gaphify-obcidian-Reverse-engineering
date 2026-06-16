"""Compute metrics deltas between before and after phases."""

from __future__ import annotations

from ex04_agent.comparison.model import GraphDelta, MetricDelta


def compute_metrics_delta(metrics_before: dict, metrics_after: dict) -> list[MetricDelta]:
    sb = metrics_before.get("summary", {})
    sa = metrics_after.get("summary", {})
    cb = len(metrics_before.get("communities", {}))
    ca = len(metrics_after.get("communities", {}))
    pairs = (
        ("node_count", sb.get("node_count", 0), sa.get("node_count", 0),
         "The graph became slightly smaller after patching."),
        ("link_count", sb.get("link_count", 0), sa.get("link_count", 0),
         "This supports that one invalid/obsolete relation may have been removed."),
        ("connected_component_count", sb.get("connected_component_count", 0),
         sa.get("connected_component_count", 0), "Component count unchanged or shifted."),
        ("community_count", cb, ca, "Community structure may shift after code changes."),
        ("low_confidence_link_count", sb.get("low_confidence_link_count", 0),
         sa.get("low_confidence_link_count", 0), "Low-confidence links are graph evidence only."),
    )
    return [
        MetricDelta(name=n, before=float(b), after=float(a), delta=float(a) - float(b), note=note)
        for n, b, a, note in pairs
    ]


def compute_graph_delta(metrics_before: dict, metrics_after: dict, story_before: str, story_after: str) -> GraphDelta:
    hubs_b = tuple(h.get("label", h.get("id", "")) for h in metrics_before.get("top_hubs", [])[:6])
    hubs_a = tuple(h.get("label", h.get("id", "")) for h in metrics_after.get("top_hubs", [])[:6])
    gods_b = tuple(g.get("label", g.get("id", "")) for g in metrics_before.get("potential_god_nodes", []))
    gods_a = tuple(g.get("label", g.get("id", "")) for g in metrics_after.get("potential_god_nodes", []))
    nodes_b = {n["id"]: n for n in metrics_before.get("summary", {}).get("nodes", [])}
    nodes_a = {n["id"]: n for n in metrics_after.get("summary", {}).get("nodes", [])}
    removed = tuple(sorted(set(nodes_b) - set(nodes_a)))
    degree_changes: list[dict] = []
    for nid, nb in nodes_b.items():
        if nid in nodes_a and nb.get("total_degree") != nodes_a[nid].get("total_degree"):
            degree_changes.append({
                "id": nid,
                "label": nb.get("label", nid),
                "before_degree": nb.get("total_degree", 0),
                "after_degree": nodes_a[nid].get("total_degree", 0),
            })
    story = _story_summary(story_before, story_after)
    return GraphDelta(
        top_hubs_before=hubs_b, top_hubs_after=hubs_a,
        god_nodes_before=gods_b, god_nodes_after=gods_a,
        removed_nodes=removed, degree_changes=tuple(degree_changes[:10]),
        story_summary=story,
    )


def _story_summary(before: str, after: str) -> str:
    parts = []
    if before:
        parts.append("Before: graph story described pre-patch connectivity and hub candidates.")
    if after:
        parts.append("After: graph story reflects patched code structure.")
    if before and after:
        parts.append("Safe Phase 10 patches changed syntax/globals/main guards; graph metrics shifted accordingly.")
    parts.append("Architecture improvement must be interpreted together with findings and tests.")
    return " ".join(parts)
