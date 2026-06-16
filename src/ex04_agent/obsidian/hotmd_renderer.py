"""Render dynamic obsidian/hot.md Markdown."""

from __future__ import annotations

from dataclasses import dataclass

from ex04_agent.git.diff_reader import GitDiffResult
from ex04_agent.obsidian.node_ranker import RankedNode
from ex04_agent.obsidian.vault_context import node_wikilink


@dataclass(frozen=True)
class HotMdRenderContext:
    """Inputs for dynamic hot.md rendering."""

    phase: str
    timestamp: str
    repo_path: str
    commit: str | None
    diff: GitDiffResult
    ranked_nodes: list[RankedNode]
    previous_hot_excerpt: str | None
    previous_snapshot_name: str | None


class HotMdRenderer:
    """Render Markdown for dynamic investigation hot.md."""

    def render(self, context: HotMdRenderContext) -> str:
        lines = [
            "# hot — Dynamic Investigation List",
            "",
            f"- **Phase:** `{context.phase}`",
            f"- **Generated:** `{context.timestamp}`",
            f"- **Target repo:** `{context.repo_path}`",
            f"- **Commit:** `{context.commit or 'unknown'}`",
            "",
            "> **Warning:** Do not auto-patch from this page alone. "
            "Ranked entries are investigation candidates — validate in source and tests.",
            "",
            "## Changed Files (git diff)",
            "",
        ]
        if context.diff.changed_files:
            for path in context.diff.changed_files:
                lines.append(f"- `{path}`")
            if context.diff.stat_text:
                lines.extend(["", "```", context.diff.stat_text, "```"])
        else:
            note = context.diff.warning or "No working-tree changes detected."
            lines.append(f"- _{note}_")

        lines.extend(["", "## Suspicious Nodes (ranked)", ""])
        lines.extend(
            [
                "| Rank | Node | Score | Degree | Diff | Reasons |",
                "| ---: | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for index, node in enumerate(context.ranked_nodes[:15], start=1):
            link = node_wikilink(node.node_id, node.label)
            reasons = "; ".join(node.reasons)
            lines.append(
                f"| {index} | {link} | {node.score} | {node.total_degree} | "
                f"{node.diff_score} | {reasons} |"
            )

        source_files = sorted(
            {node.source_file for node in context.ranked_nodes[:10] if node.source_file}
        )
        lines.extend(["", "## Affected Source Files", ""])
        if source_files:
            for path in source_files:
                lines.append(f"- `{path}`")
        else:
            lines.append("- _No source files in top ranked nodes._")

        lines.extend(["", "## Possible Architecture Problems (graph suggests)", ""])
        problems: list[str] = []
        for node in context.ranked_nodes[:5]:
            if node.god_node_score or node.diff_score >= 0.6 or node.total_degree >= 3:
                problems.append(
                    f"- **{node.label}** — possible hub/candidate; "
                    f"graph suggests review ({'; '.join(node.reasons)})."
                )
        if problems:
            lines.extend(problems)
        else:
            lines.append("- _No strong architecture signals beyond baseline centrality._")

        lines.extend(
            [
                "",
                "## Recommended Investigation Path",
                "",
                "1. Review changed files above (if any).",
                "2. Open top-ranked node pages via wikilinks.",
                "3. Read [[reports/graph_summary|graph_summary]] for relation/confidence context.",
                "4. Follow **OBS → REL → CONF → CTX → SRC** before drawing conclusions.",
                "5. Compare with [[index|index]] for community context.",
                "",
                "## Before / After Notes",
                "",
            ]
        )
        if context.previous_snapshot_name:
            lines.append(
                f"- Previous snapshot: `artifacts/hotmd/{context.previous_snapshot_name}`"
            )
        if context.previous_hot_excerpt:
            lines.append("- Previous `hot.md` opening lines:")
            lines.append("```")
            lines.append(context.previous_hot_excerpt)
            lines.append("```")
        else:
            lines.append("- No previous `hot.md` content captured (first dynamic run).")

        lines.extend(
            [
                "",
                "_Dynamic ranking blends graph centrality, git diff proximity, test proximity, "
                "ambiguous links, and god-node flags. This is the original EX04 extension._",
            ]
        )
        return "\n".join(lines) + "\n"
