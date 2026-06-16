"""Write RegressionResult to JSON and Markdown."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.testing.model import RegressionResult


class RegressionReportWriter:
    def write(
        self,
        result: RegressionResult,
        *,
        json_path: Path,
        md_path: Path,
        latest_path: Path | None = None,
    ) -> None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if latest_path:
            latest_path.parent.mkdir(parents=True, exist_ok=True)
            latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        md_path.write_text(self._render_md(result), encoding="utf-8")

    def _render_md(self, r: RegressionResult) -> str:
        lines = [
            f"# Regression Report — {r.phase}",
            "",
            "## Summary",
            "",
            "| Check | Status |",
            "| --- | --- |",
            f"| Compile | `{r.compile_status}` |",
            f"| AST parse | `{r.ast_status}` |",
            f"| Safe import | `{r.import_status}` |",
            f"| Target repo tests | `{r.target_test_status}` |",
            f"| Project pytest | `{r.project_test_status}` |",
            f"| Coverage | `{r.coverage_status}` |",
            f"| Ruff | `{r.ruff_status}` |",
            "",
        ]
        if r.target_test_status == "skipped":
            lines += [
                "## Target Repository Tests",
                "",
                "> No dedicated test suite found in target repository.",
                "> Running fallback validation only.",
                "",
            ]
        if r.failed_files:
            lines += ["## Failed Files", ""]
            for f in r.failed_files:
                lines.append(f"- `{f}`")
            lines.append("")
        if r.warnings:
            lines += ["## Warnings", ""]
            for w in r.warnings:
                lines.append(f"- {w}")
            lines.append("")
        if r.skipped_checks:
            lines += ["## Skipped Checks", ""]
            for s in r.skipped_checks:
                lines.append(f"- {s}")
            lines.append("")
        lines += ["## Commands Run", ""]
        for cmd in r.commands_run:
            lines.append(f"- `{cmd.name}`: {cmd.status} ({cmd.duration_seconds}s)")
        return "\n".join(lines) + "\n"
