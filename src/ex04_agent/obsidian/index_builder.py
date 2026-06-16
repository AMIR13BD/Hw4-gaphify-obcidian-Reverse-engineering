"""Build obsidian/index.md from graph metrics."""

from __future__ import annotations

from ex04_agent.obsidian.vault_context import VaultContext, node_wikilink


class IndexBuilder:
    """Create a compact navigation index for the Obsidian vault."""

    def build(self, context: VaultContext) -> str:
        summary = context.metrics.get("summary", {})
        communities = context.metrics.get("communities", {})
        top_hubs = context.metrics.get("top_hubs", [])
        god_nodes = context.metrics.get("potential_god_nodes", [])

        lines = [
            "# EX04 Graph Index",
            "",
            f"- **Repository:** `{context.repo_name}` (`{context.repo_path}`)",
            f"- **Phase:** `{context.phase}`",
            "",
            "## Graph Summary",
            "",
            f"- Nodes: **{summary.get('node_count', 0)}**",
            f"- Links: **{summary.get('link_count', 0)}**",
            f"- Communities: **{len(communities)}**",
            f"- Connected components: **{summary.get('connected_component_count', 0)}**",
            "",
            "## Top Hubs (graph centrality)",
            "",
            "| Node | Degree | Wikilink |",
            "| --- | ---: | --- |",
        ]
        for hub in top_hubs[:8]:
            lines.append(
                f"| {hub.get('label', hub.get('id', ''))} | "
                f"{hub.get('total_degree', 0)} | "
                f"{node_wikilink(hub['id'], hub.get('label', hub['id']))} |"
            )

        lines.extend(["", "## Possible God-Node Candidates", ""])
        for node in god_nodes[:8]:
            lines.append(
                f"- {node_wikilink(node['id'], node.get('label', node['id']))} "
                f"(degree {node.get('total_degree', 0)}) — graph suggests high connectivity; "
                "validate in source before drawing architecture conclusions."
            )

        lines.extend(
            [
                "",
                "## Start Here",
                "",
                "- Priority investigation page: [[hot|hot.md]]",
                "- Graph narrative: [[reports/graph_summary|graph_summary]]",
                "",
                "## Top Node Pages",
                "",
            ]
        )
        for hub in top_hubs[:6]:
            lines.append(f"- {node_wikilink(hub['id'], hub.get('label', hub['id']))}")

        lines.extend(
            [
                "",
                "## How to Investigate",
                "",
                "Use the graph reading flow from the course materials:",
                "",
                "1. **OBS** — observe node labels, communities, and degrees in this index.",
                "2. **REL** — follow wikilinks to inspect incoming/outgoing relations on node pages.",
                "3. **CONF** — check link confidence in [[reports/graph_summary|graph_summary]] "
                "(AST-only graph here is EXTRACTED-only).",
                "4. **CTX** — read README and source files cited on each node page.",
                "5. **SRC** — open files under the target repo and confirm behavior manually.",
                "",
                "_Graph evidence ranks candidates; it is not final proof of bugs or design flaws._",
            ]
        )
        content = "\n".join(lines)
        if len(content) > context.index_max_chars:
            content = content[: context.index_max_chars - 3].rstrip() + "..."
        return content + "\n"
