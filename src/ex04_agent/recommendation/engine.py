"""Recommendation engine for Phase 9."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.recommendation.mapper import map_finding
from ex04_agent.recommendation.patch_plan import build_patch_plan
from ex04_agent.recommendation.prioritizer import sort_recommendations
from ex04_agent.recommendation.report_writer import (
    RecommendationReportWriter,
    RecommendationSummary,
)
from ex04_agent.shared.config import AppConfig
from ex04_agent.shared.phase_paths import architecture_report_path, ensure_phase_write_path


class RecommendationEngine:
    def __init__(self, config: AppConfig, writer: RecommendationReportWriter | None = None) -> None:
        self._config = config
        self._writer = writer or RecommendationReportWriter()

    def run(self, phase: str = "before", findings_path: Path | None = None) -> RecommendationSummary:
        if phase not in {"before", "after"}:
            msg = f"Invalid phase {phase!r}; expected 'before' or 'after'"
            raise ValueError(msg)
        inputs = findings_path or architecture_report_path(self._config.project_root, "findings", phase, "json")
        if not inputs.is_file():
            raise FileNotFoundError(f"Required findings file not found: {inputs}")
        findings = json.loads(inputs.read_text(encoding="utf-8")).get("findings", [])
        by_id = {str(item.get("id")): item for item in findings}
        recs = [map_finding(item, i + 1) for i, item in enumerate(findings)]
        ordered = sort_recommendations(recs, by_id)
        plan_items, groups = build_patch_plan(ordered)
        rec_json = architecture_report_path(self._config.project_root, "recommendations", phase, "json")
        rec_md = architecture_report_path(self._config.project_root, "recommendations", phase, "md")
        plan_json = architecture_report_path(self._config.project_root, "patch_plan", phase, "json")
        plan_md = architecture_report_path(self._config.project_root, "patch_plan", phase, "md")
        for path in (rec_json, rec_md, plan_json, plan_md):
            ensure_phase_write_path(path, phase)
        rec_json.parent.mkdir(parents=True, exist_ok=True)
        self._writer.write_recommendations(
            ordered, phase, rec_json, rec_md,
            self._config.project_root / "reports" / "architecture" / "recommendations.json",
        )
        self._writer.write_patch_plan(
            plan_items, groups, phase, plan_json, plan_md,
            self._config.project_root / "reports" / "architecture" / "patch_plan.json",
        )
        return self._writer.build_summary(ordered, rec_json, rec_md, plan_json, plan_md)
