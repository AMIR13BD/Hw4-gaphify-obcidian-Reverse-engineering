"""Write token-efficiency JSON, Markdown, and CSV reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from ex04_agent.token_efficiency.model import TokenEfficiencyResult
from ex04_agent.token_efficiency.token_estimator import DISCLAIMER, ESTIMATION_RULE


class TokenEfficiencyReportWriter:
    def write(self, result: TokenEfficiencyResult, out_dir: Path) -> dict[str, str]:
        out_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "json": out_dir / "token_efficiency.json",
            "md": out_dir / "token_efficiency.md",
            "bundles_json": out_dir / "context_bundles.json",
            "bundles_md": out_dir / "context_bundles.md",
            "csv": out_dir / "token_comparison.csv",
        }
        payload = result.to_dict()
        paths["json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
        paths["md"].write_text(self._render_main(result), encoding="utf-8")
        bundles_payload = {"bundles": [b.to_dict() for b in result.bundles]}
        paths["bundles_json"].write_text(json.dumps(bundles_payload, indent=2), encoding="utf-8")
        paths["bundles_md"].write_text(self._render_bundles(result), encoding="utf-8")
        self._write_csv(result, paths["csv"])
        return {k: str(v) for k, v in paths.items()}

    def _write_csv(self, result: TokenEfficiencyResult, path: Path) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["scenario", "baseline_tokens", "graph_guided_tokens", "tokens_saved", "percent_saved"])
            for s in result.scenarios:
                writer.writerow([s.name, s.baseline.total_tokens, s.graph_guided.total_tokens, s.tokens_saved, f"{s.percent_saved:.2f}"])

    def _render_main(self, r: TokenEfficiencyResult) -> str:
        lines = [
            "# Token Efficiency Report",
            "",
            "## Context Problem",
            "",
            "Naive reverse engineering loads entire repositories and raw graph dumps into an LLM context.",
            "Graph-guided retrieval uses Obsidian navigation, hot.md ranking, and metrics to focus agents.",
            "",
            "## Estimation Method",
            "",
            f"- Rule: `{ESTIMATION_RULE}`",
            f"- {DISCLAIMER}",
            "",
            "## Context Bundles",
            "",
            "| Bundle | Files | Estimated tokens | Description |",
            "| --- | ---: | ---: | --- |",
        ]
        for b in r.bundles:
            lines.append(f"| {b.name} | {len(b.files)} | {b.total_tokens} | {b.description} |")
        lines += ["", "## Scenario Comparison", "",
                  "| Scenario | Baseline tokens | Graph-guided tokens | Saved | % saved |",
                  "| --- | ---: | ---: | ---: | ---: |"]
        for s in r.scenarios:
            sign = "+" if s.tokens_saved >= 0 else ""
            lines.append(
                f"| {s.name} | {s.baseline.total_tokens} | {s.graph_guided.total_tokens} | "
                f"{sign}{s.tokens_saved} | {s.percent_saved:.1f}% |"
            )
        lines += [
            "", "## Savings Result", "",
            f"- Total baseline (scenarios): **{r.total_baseline_tokens}**",
            f"- Total graph-guided (scenarios): **{r.total_graph_guided_tokens}**",
            f"- Total tokens saved: **{r.total_tokens_saved}** ({r.percent_saved:.1f}%)",
            "", "## Graph-Guided Retrieval", "",
            "Graphify produced metrics and hub candidates; Obsidian index/hot.md and node pages "
            "steer agents to high-centrality files instead of reading every source file.",
            "", "## Limitations", "",
        ]
        lines.extend(f"- {note}" for note in r.limitations)
        lines += [
            "", "## Course Requirement Support", "",
            "Demonstrates whether graph/wiki context reduces estimated tokens versus naive full dumps "
            "for detection, recommendation, and comparison tasks.",
            "", "## Notes for README", "",
            "Include estimation disclaimer, scenario table, and honest note if savings are small.",
        ]
        return "\n".join(lines) + "\n"

    def _render_bundles(self, r: TokenEfficiencyResult) -> str:
        lines = ["# Context Bundles", ""]
        for b in r.bundles:
            lines += [f"## {b.name}", "", b.description, "",
                      f"Files: {len(b.files)} · Tokens: {b.total_tokens}", ""]
            for f in b.files:
                lines.append(f"- `{f.path}` ({f.estimated_tokens} tokens)")
            lines.append("")
        return "\n".join(lines)
