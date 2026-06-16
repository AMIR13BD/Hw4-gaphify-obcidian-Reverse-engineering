"""Build obsidian/reports/graph_summary.md."""

from __future__ import annotations

from ex04_agent.obsidian.vault_context import VaultContext, node_wikilink


class ReportBuilder:
    """Summarize GRAPH_REPORT and metrics for the vault."""

    def build(self, context: VaultContext) -> str:
        metrics = context.metrics
        summary = metrics.get("summary", {})
        relation_counts = metrics.get("relation_counts", {})
        confidence_counts = metrics.get("confidence_counts", {})
        communities = metrics.get("communities", {})
        low_conf = metrics.get("low_confidence_links", [])
        top_hubs = metrics.get("top_hubs", [])

        lines = [
            "# Graph Summary Report",
            "",
            f"**Phase:** `{context.phase}` · **Repository:** `{context.repo_name}`",
            "",
            "## Metrics Overview",
            "",
            f"- Nodes: {summary.get('node_count', 0)}",
            f"- Links: {summary.get('link_count', 0)}",
            f"- Communities: {len(communities)}",
            f"- Connected components: {summary.get('connected_component_count', 0)}",
            f"- Low-confidence links: {summary.get('low_confidence_link_count', len(low_conf))}",
            "",
            "## Relation Counts",
            "",
        ]
        for relation, count in relation_counts.items():
            lines.append(f"- `{relation}`: {count}")

        lines.extend(["", "## Confidence Counts", ""])
        for confidence, count in confidence_counts.items():
            lines.append(f"- `{confidence}`: {count}")

        extracted_total = confidence_counts.get("EXTRACTED", 0)
        link_total = summary.get("link_count", 0)
        if link_total and extracted_total == link_total:
            lines.extend(
                [
                    "",
                    "All links in the current AST-only graph are **EXTRACTED** "
                    f"({extracted_total}/{link_total}). No INFERRED or AMBIGUOUS edges were emitted.",
                ]
            )

        lines.extend(["", "## Communities (node counts)", ""])
        for community, count in communities.items():
            lines.append(f"- Community {community}: {count} nodes")

        lines.extend(["", "## Top Hubs", ""])
        for hub in top_hubs[:8]:
            lines.append(
                f"- {node_wikilink(hub['id'], hub.get('label', hub['id']))} "
                f"(degree {hub.get('total_degree', 0)})"
            )

        lines.extend(["", "## Low-Confidence / Ambiguous Links", ""])
        if low_conf:
            for link in low_conf[:20]:
                lines.append(
                    f"- `{link.get('source')}` → `{link.get('target')}` "
                    f"({link.get('relation')}, {link.get('confidence')})"
                )
        else:
            lines.append("- None in current graph — all links are EXTRACTED.")

        lines.extend(["", "## GRAPH_REPORT Excerpt", ""])
        if context.graph_report_text:
            excerpt = "\n".join(context.graph_report_text.splitlines()[:40])
            lines.append(excerpt)
        else:
            lines.append("_GRAPH_REPORT.md not found for this phase._")

        lines.extend(
            [
                "",
                "_Graph metrics suggest where to look next; source validation is required "
                "before architecture or bug conclusions._",
            ]
        )
        return "\n".join(lines) + "\n"
