"""Orchestrate token-efficiency analysis."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ex04_agent.shared.config import AppConfig
from ex04_agent.token_efficiency.collector import TokenEfficiencyCollector
from ex04_agent.token_efficiency.comparator import compare_scenario
from ex04_agent.token_efficiency.context_bundle import ContextBundleBuilder
from ex04_agent.token_efficiency.model import TokenEfficiencyResult
from ex04_agent.token_efficiency.report_writer import TokenEfficiencyReportWriter
from ex04_agent.token_efficiency.token_estimator import ESTIMATION_RULE, TokenEstimator

LIMITATIONS = (
    "Estimates only — not provider billing or tokenizer-accurate counts.",
    "Small teaching repo — raw graph/report dumps can exceed source-only context.",
    "Token efficiency is more meaningful on larger repositories.",
    "Primary benefit here may be focus and traceability, not only raw token reduction.",
    "No real provider token logs were available for this phase.",
)


@dataclass(frozen=True)
class TokenEfficiencySummary:
    scenarios_count: int
    total_baseline_tokens: int
    total_graph_guided_tokens: int
    total_tokens_saved: int
    percent_saved: float
    output_paths: dict[str, str]

    def to_dict(self) -> dict:
        return {
            "scenarios_count": self.scenarios_count,
            "total_baseline_tokens": self.total_baseline_tokens,
            "total_graph_guided_tokens": self.total_graph_guided_tokens,
            "total_tokens_saved": self.total_tokens_saved,
            "percent_saved": round(self.percent_saved, 2),
            "output_paths": self.output_paths,
        }


class TokenEfficiencyEngine:
    def __init__(
        self,
        config: AppConfig,
        collector: TokenEfficiencyCollector | None = None,
        builder: ContextBundleBuilder | None = None,
        writer: TokenEfficiencyReportWriter | None = None,
    ) -> None:
        self._config = config
        self._collector = collector or TokenEfficiencyCollector(config)
        self._builder = builder or ContextBundleBuilder(TokenEstimator())
        self._writer = writer or TokenEfficiencyReportWriter()

    def run(self, phase: str = "before") -> TokenEfficiencyResult:
        self._collector.require_inputs(phase)
        bundles = self._build_bundles(phase)
        scenarios = self._build_scenarios(phase)
        base_total = sum(s.baseline.total_tokens for s in scenarios)
        guided_total = sum(s.graph_guided.total_tokens for s in scenarios)
        saved = base_total - guided_total
        pct = (saved / base_total * 100.0) if base_total > 0 else 0.0
        out_dir = self._config.project_root / "reports" / "token_efficiency"
        result = TokenEfficiencyResult(
            estimation_method=ESTIMATION_RULE,
            phase=phase,
            bundles=tuple(bundles),
            scenarios=tuple(scenarios),
            total_baseline_tokens=base_total,
            total_graph_guided_tokens=guided_total,
            total_tokens_saved=saved,
            percent_saved=pct,
            output_paths={},
            limitations=LIMITATIONS,
        )
        paths = self._writer.write(result, out_dir)
        return replace(result, output_paths=paths)

    def summary(self, result: TokenEfficiencyResult) -> TokenEfficiencySummary:
        return TokenEfficiencySummary(
            scenarios_count=len(result.scenarios),
            total_baseline_tokens=result.total_baseline_tokens,
            total_graph_guided_tokens=result.total_graph_guided_tokens,
            total_tokens_saved=result.total_tokens_saved,
            percent_saved=result.percent_saved,
            output_paths=result.output_paths,
        )

    def _build_bundles(self, phase: str) -> list:
        c, b = self._collector, self._builder
        return [
            b.build("naive_full_context", "All target .py and .md files", c.naive_full_context()),
            b.build("naive_source_only", "All target .py files", c.naive_source_only()),
            b.build("naive_evidence_dump", "Raw graphs + architecture/comparison/test reports", c.naive_evidence_dump()),
            b.build("graph_guided_minimal", "Obsidian index/hot + top node pages + metrics", c.graph_guided_minimal(phase)),
            b.build("graph_guided_after", "After metrics/findings/recommendations + comparison md", c.graph_guided_after()),
            b.build("agent_detection", "Metrics + hot.md + hub sources for detection", c.detection_guided(phase)),
            b.build("agent_recommendation", "Findings JSON + affected source files", c.recommendation_guided(phase)),
            b.build("agent_comparison", "Phase-specific before/after metrics/findings/recs + patch/regression", c.comparison_guided()),
        ]

    def _build_scenarios(self, phase: str) -> list:
        c, b = self._collector, self._builder
        det_base = b.merge("detection_baseline", "Full repo + evidence dump", b.build("x", "", c.naive_full_context()), b.build("y", "", c.naive_evidence_dump()))
        det_guided = b.build("detection_guided", "Graph-guided detection bundle", c.detection_guided(phase))
        rec_base = b.merge("recommendation_baseline", "Full repo + evidence", b.build("x", "", c.naive_full_context()), b.build("y", "", c.naive_evidence_dump()))
        rec_guided = b.build("recommendation_guided", "Findings + affected files", c.recommendation_guided(phase))
        cmp_base = b.build("comparison_baseline", "All architecture reports", c.comparison_baseline())
        cmp_guided = b.build("comparison_guided", "Focused before/after comparison inputs", c.comparison_guided())
        return [
            compare_scenario(
                "architecture_detection", "T1: Architecture detection",
                det_base, det_guided,
                quality_note="Preserves hub metrics, hot.md ranking, and top hub source files.",
                risk_note="May miss findings in low-centrality files not linked in graph.",
            ),
            compare_scenario(
                "recommendation_generation", "T2: Recommendation generation",
                rec_base, rec_guided,
                quality_note="Preserves structured findings and directly affected source paths.",
                risk_note="Cross-file refactor context may be incomplete without full repo scan.",
            ),
            compare_scenario(
                "before_after_comparison", "T3: Before/after comparison",
                cmp_base, cmp_guided,
                quality_note="Preserves phase-specific metrics, findings, recommendations, patch and regression evidence.",
                risk_note="Omits narrative story markdown and duplicate latest copies.",
            ),
        ]
