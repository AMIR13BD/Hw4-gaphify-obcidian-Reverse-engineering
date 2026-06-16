"""Build static baseline obsidian/hot.md from metrics only."""

from __future__ import annotations

from ex04_agent.obsidian.vault_context import VaultContext, node_wikilink


class HotMdBuilder:
    """Create a static investigation hot list (Phase 5 baseline, not dynamic)."""

    _NOTES = {
        "polygons_polygons": (
            "Possible **code-level hub** — highest degree in the graph; "
            "polygons module ties classes, calls, and rationale nodes."
        ),
        "polygons_polygons_polygon": (
            "Possible **code-level hub** — central class node with multiple relations; "
            "graph suggests this abstraction anchors the polygons area."
        ),
        "mathsquiz_readme_maths_quiz": (
            "Documentation/knowledge hub from README — not necessarily a code bottleneck. "
            "Use for context before reading step files."
        ),
        "mathsquiz_mathsquiz_step2": (
            "Possible **workflow/function grouping hub** — step file with several child functions."
        ),
        "mathsquiz_mathsquiz_step3": (
            "Possible **workflow/function grouping hub** — parallel step to step2; "
            "compare implementations manually."
        ),
    }

    def build(self, context: VaultContext) -> str:
        candidates = context.metrics.get("potential_god_nodes", [])
        top_hubs = context.metrics.get("top_hubs", [])
        source_files = sorted(
            {
                node.get("source_file")
                for node in context.metrics.get("summary", {}).get("nodes", [])
                if node.get("source_file")
            }
        )

        lines = [
            "# hot — Static Investigation Baseline",
            "",
            f"**Phase:** `{context.phase}` · **Source:** metrics + graph centrality only",
            "",
            "> **Warning:** Do not auto-patch from this page alone. "
            "These are graph-ranked candidates; confirm in source and tests.",
            "",
            "## Candidate Nodes",
            "",
        ]
        seen: set[str] = set()
        for node in candidates + top_hubs:
            node_id = node.get("id")
            if not node_id or node_id in seen:
                continue
            seen.add(node_id)
            note = self._NOTES.get(
                node_id,
                "Graph suggests elevated connectivity — treat as a possible hub until validated.",
            )
            lines.extend(
                [
                    f"### {node_wikilink(node_id, node.get('label', node_id))}",
                    "",
                    f"- Degree: {node.get('total_degree', 0)} "
                    f"(in {node.get('in_degree', '?')} / out {node.get('out_degree', '?')})",
                    f"- Source file: `{node.get('source_file') or 'n/a'}`",
                    f"- Why interesting: {note}",
                    "",
                ]
            )

        lines.extend(
            [
                "## Suggested Investigation Path",
                "",
                "1. Open [[index|index]] for the full graph summary.",
                "2. Read [[reports/graph_summary|graph_summary]] for relation/confidence context.",
                "3. Start with possible code hubs (`polygons.py`, `Polygon`) if code behavior is the goal.",
                "4. Read `Maths Quiz` README context before comparing step2/step3 workflows.",
                "5. Trace relations on linked node pages (OBS → REL → CONF → CTX → SRC).",
                "",
                "## Source Files to Open Manually",
                "",
            ]
        )
        for path in source_files[:12]:
            lines.append(f"- `{path}`")
        lines.extend(
            [
                "",
                "_Dynamic hot.md ranks investigation candidates using graph metrics and git diff._",
            ]
        )
        return "\n".join(lines) + "\n"
