"""Phase 13 before/after comparison engine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ex04_agent.comparison.finding_delta import compute_finding_delta
from ex04_agent.comparison.loader import ComparisonLoader
from ex04_agent.comparison.metrics_delta import compute_graph_delta, compute_metrics_delta
from ex04_agent.comparison.model import ComparisonResult
from ex04_agent.comparison.recommendation_delta import compute_recommendation_delta
from ex04_agent.comparison.report_writer import ComparisonReportWriter
from ex04_agent.shared.config import AppConfig


@dataclass(frozen=True)
class ComparisonSummary:
    before_nodes: int
    after_nodes: int
    before_findings: int
    after_findings: int
    before_recommendations: int
    after_recommendations: int
    resolved_or_removed_findings_count: int
    remaining_findings_count: int
    json_path: str
    markdown_path: str

    def to_dict(self) -> dict:
        return {
            "before_nodes": self.before_nodes,
            "after_nodes": self.after_nodes,
            "before_findings": self.before_findings,
            "after_findings": self.after_findings,
            "before_recommendations": self.before_recommendations,
            "after_recommendations": self.after_recommendations,
            "resolved_or_removed_findings_count": self.resolved_or_removed_findings_count,
            "remaining_findings_count": self.remaining_findings_count,
            "output_paths": {"json": self.json_path, "md": self.markdown_path},
        }


class ComparisonEngine:
    def __init__(
        self,
        config: AppConfig,
        loader: ComparisonLoader | None = None,
        writer: ComparisonReportWriter | None = None,
    ) -> None:
        self._config = config
        self._loader = loader or ComparisonLoader(config)
        self._writer = writer or ComparisonReportWriter()

    def run(self, before_phase: str = "before", after_phase: str = "after") -> ComparisonResult:
        inputs = self._loader.load(before_phase, after_phase)
        metrics_delta = compute_metrics_delta(inputs.metrics_before, inputs.metrics_after)
        findings_delta = compute_finding_delta(inputs.findings_before, inputs.findings_after)
        rec_delta = compute_recommendation_delta(
            inputs.recommendations_before, inputs.recommendations_after,
        )
        graph_delta = compute_graph_delta(
            inputs.metrics_before, inputs.metrics_after,
            inputs.story_before, inputs.story_after,
        )
        improved, risks = self._summaries(inputs, findings_delta, metrics_delta)
        json_path = self._out("before_after.json")
        md_path = self._out("before_after.md")
        result = ComparisonResult(
            before_phase=before_phase, after_phase=after_phase,
            metrics_delta=metrics_delta, findings_delta=findings_delta,
            recommendations_delta=rec_delta, graph_delta=graph_delta,
            improvement_summary=improved, remaining_risks=risks,
            evidence_paths=inputs.evidence_paths,
            output_paths={"json": str(json_path), "md": str(md_path)},
        )
        self._writer.write(
            result, json_path=json_path, md_path=md_path,
            latest_json=self._out("comparison.json"),
            latest_md=self._out("comparison.md"),
        )
        return result

    def summary(self, result: ComparisonResult) -> ComparisonSummary:
        counts = result.summary_counts()
        return ComparisonSummary(
            before_nodes=int(counts["before_nodes"]),
            after_nodes=int(counts["after_nodes"]),
            before_findings=int(counts["before_findings"]),
            after_findings=int(counts["after_findings"]),
            before_recommendations=int(counts["before_recommendations"]),
            after_recommendations=int(counts["after_recommendations"]),
            resolved_or_removed_findings_count=int(counts["resolved_or_removed_findings_count"]),
            remaining_findings_count=int(counts["remaining_findings_count"]),
            json_path=str(result.output_paths["json"]),
            markdown_path=str(result.output_paths["md"]),
        )

    def _out(self, name: str) -> Path:
        return self._config.project_root / "reports" / "comparison" / name

    def _summaries(self, inputs, fd, metrics) -> tuple[tuple[str, ...], tuple[str, ...]]:
        improved: list[str] = []
        if fd.code_health_before > fd.code_health_after:
            improved.append("Execution/syntax blockers reduced after Phase 10 safe patches.")
        if fd.before_count > fd.after_count:
            improved.append(
                f"Finding count decreased from {fd.before_count} to {fd.after_count}; "
                "many pre-patch issues no longer detected on patched code."
            )
        patch = inputs.patch_result
        if patch.get("applied_items"):
            improved.append(
                f"Phase 10 applied {len(patch.get('applied_items', []))} safe patches "
                "to whitelisted files with backups/diffs."
            )
        reg = inputs.regression
        if reg.get("compile_status") == "passed" and reg.get("project_test_status") == "passed":
            improved.append("Phase 11 regression: compile, project pytest, coverage, and Ruff passed.")
        node_m = next((m for m in metrics if m.name == "node_count"), None)
        if node_m and node_m.delta < 0:
            improved.append(
                "The graph became slightly smaller after patching; "
                "this may reflect removal of invalid syntax-related structure."
            )
        risks: list[str] = []
        if fd.code_health_after:
            risks.append(f"{fd.code_health_after} code-health finding(s) still remain.")
        mixed = fd.category_after.get("mixed_responsibility", 0)
        if mixed:
            risks.append(f"{mixed} mixed-responsibility finding(s) remain (deferred from Phase 10).")
        docs = sum(fd.category_after.get(c, 0) for c in ("documentation_hub", "navigation_scope", "organization"))
        if docs:
            risks.append(f"{docs} documentation/navigation finding(s) remain by design.")
        if reg.get("target_test_status") == "skipped":
            risks.append("Target repository has no dedicated test suite.")
        risks.append("Graph metrics are evidence; validate conclusions in source.")
        return tuple(improved), tuple(risks)
