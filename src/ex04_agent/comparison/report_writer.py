"""Write comparison JSON and Markdown reports."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.comparison.model import ComparisonResult


class ComparisonReportWriter:
    def write(
        self,
        result: ComparisonResult,
        *,
        json_path: Path,
        md_path: Path,
        latest_json: Path | None = None,
        latest_md: Path | None = None,
    ) -> None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        md_text = self._render_md(result)
        md_path.write_text(md_text, encoding="utf-8")
        if latest_json:
            latest_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if latest_md:
            latest_md.write_text(md_text, encoding="utf-8")

    def _render_md(self, r: ComparisonResult) -> str:
        fd = r.findings_delta
        rd = r.recommendations_delta
        lines = [
            "# Before/After Comparison",
            "",
            "## Executive Summary",
            "",
            *([f"- {s}" for s in r.improvement_summary] or ["- No summary available."]),
            "",
            "Architecture improvement must be interpreted together with findings and tests.",
            "",
            "## Metrics",
            "",
            "| Metric | Before | After | Delta | Note |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
        for m in r.metrics_delta:
            lines.append(f"| {m.name} | {m.before} | {m.after} | {m.delta:+.0f} | {m.note} |")
        lines += ["", "## Findings", "",
                  f"- Before: **{fd.before_count}** · After: **{fd.after_count}**",
                  f"- Resolved/removed: **{len(fd.resolved_or_removed)}** · Remaining: **{len(fd.remaining)}**",
                  f"- Code-health blockers: {fd.code_health_before} → {fd.code_health_after}", "",
                  "### Category counts", "",
                  "| Category | Before | After |",
                  "| --- | ---: | ---: |"]
        all_cats = sorted(set(fd.category_before) | set(fd.category_after))
        for cat in all_cats:
            lines.append(f"| `{cat}` | {fd.category_before.get(cat, 0)} | {fd.category_after.get(cat, 0)} |")
        lines += ["", "## Recommendations", "",
                  f"- Before: **{rd.before_count}** · After: **{rd.after_count}**",
                  f"- Patchable: {rd.patchable_before} → {rd.patchable_after}", ""]
        lines += ["## What Improved", ""]
        for item in fd.resolved_or_removed[:15]:
            lines.append(f"- {item}")
        if not fd.resolved_or_removed:
            lines.append("- (none matched by id/category)")
        lines += ["", "## What Remains", ""]
        for item in fd.remaining[:15]:
            lines.append(f"- {item}")
        lines += ["", "## Graph Delta", "",
                  f"- Top hubs before: {', '.join(r.graph_delta.top_hubs_before[:5]) or 'n/a'}",
                  f"- Top hubs after: {', '.join(r.graph_delta.top_hubs_after[:5]) or 'n/a'}",
                  f"- Removed nodes: {', '.join(r.graph_delta.removed_nodes) or 'none detected'}",
                  f"- {r.graph_delta.story_summary}", ""]
        lines += ["## Evidence Paths", ""]
        for key, path in sorted(r.evidence_paths.items()):
            lines.append(f"- `{key}`: {path}")
        lines += ["", "## Notes for README", "",
                  "- Small teaching repo (`martinpeck/broken-python`); graph metrics are evidence, not final proof.",
                  "- No dedicated target test suite; regression used compile/AST/project pytest.",
                  "- Phase 10 patched 4 whitelisted files with backups/diffs.",
                  "- Screenshots will be added in Phase 15.", "",
                  "## Limitations", "",
                  "- Metric decreases are not automatically good.",
                  "- Finding matching uses id/category/file heuristics.",
                  "- Documentation/navigation findings may remain by design."]
        return "\n".join(lines) + "\n"
