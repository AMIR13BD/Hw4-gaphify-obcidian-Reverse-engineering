"""Build per-node Obsidian pages."""

from __future__ import annotations

from ex04_agent.graph.models import GraphNode
from ex04_agent.obsidian.vault_context import (
    VaultContext,
    metrics_node_map,
    node_wikilink,
    sanitize_filename,
)


class NodePageBuilder:
    """Generate Markdown pages for important graph nodes."""

    def select_node_ids(self, context: VaultContext) -> list[str]:
        """Choose nodes for dedicated pages: hubs, god candidates, and sourced nodes."""
        metrics = context.metrics
        selected: list[str] = []
        seen: set[str] = set()

        def add(node_id: str | None) -> None:
            if node_id and node_id not in seen:
                seen.add(node_id)
                selected.append(node_id)

        for hub in metrics.get("top_hubs", []):
            add(hub.get("id"))
        for node in metrics.get("potential_god_nodes", []):
            add(node.get("id"))
        for node in metrics.get("summary", {}).get("nodes", []):
            if node.get("source_file"):
                add(node.get("id"))
        return selected

    def build_page(self, context: VaultContext, node: GraphNode) -> str:
        """Render a single node investigation page."""
        stats = metrics_node_map(context.metrics).get(node.id, {})
        incoming = context.indexer.incoming_by_target.get(node.id, [])
        outgoing = context.indexer.outgoing_by_source.get(node.id, [])

        lines = [
            f"# {node.label}",
            "",
            "Back: [[../index|index]] · Hot list: [[../hot|hot]]",
            "",
            "## Identity",
            "",
            f"- **Node id:** `{node.id}`",
            f"- **Source file:** `{node.source_file or 'n/a'}`",
            f"- **Community:** {node.community if node.community is not None else 'n/a'}",
            f"- **Type:** `{node.node_type}`",
            "",
            "## Degree (from metrics)",
            "",
            f"- In-degree: {stats.get('in_degree', len(incoming))}",
            f"- Out-degree: {stats.get('out_degree', len(outgoing))}",
            f"- Total degree: {stats.get('total_degree', len(incoming) + len(outgoing))}",
            "",
            "## Incoming Relations",
            "",
        ]
        if incoming:
            for link in incoming[:12]:
                target_label = context.indexer.nodes_by_id.get(link.source, None)
                label = target_label.label if target_label else link.source
                lines.append(
                    f"- `{link.relation}` from {node_wikilink(link.source, label)} "
                    f"({link.confidence})"
                )
        else:
            lines.append("- _(none)_")

        lines.extend(["", "## Outgoing Relations", ""])
        if outgoing:
            for link in outgoing[:12]:
                target = context.indexer.nodes_by_id.get(link.target)
                label = target.label if target else link.target
                lines.append(
                    f"- `{link.relation}` → {node_wikilink(link.target, label)} "
                    f"({link.confidence})"
                )
        else:
            lines.append("- _(none)_")

        lines.extend(
            [
                "",
                "## Investigation Notes",
                "",
                "- Graph evidence ranks this node; it is **not** confirmed as a bug or design flaw.",
                "- Validate claims by opening the source file and related tests manually.",
                "- Cross-check confidence in [[../reports/graph_summary|graph_summary]].",
            ]
        )
        return "\n".join(lines) + "\n"

    def filename_for(self, node_id: str) -> str:
        """Return sanitized markdown filename for a node id."""
        return f"{sanitize_filename(node_id)}.md"
