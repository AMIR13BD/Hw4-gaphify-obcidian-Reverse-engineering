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


class RecommendationEngine:
    def __init__(self, config: AppConfig, writer: RecommendationReportWriter | None = None) -> None:
        self._config = config
        self._writer = writer or RecommendationReportWriter()

    def run(self, phase: str = "before", findings_path: Path | None = None) -> RecommendationSummary:
        if phase not in {"before", "after"}:
            msg = f"Invalid phase {phase!r}; expected 'before' or 'after'"
            raise ValueError(msg)
        inputs = findings_path or self._path(f"findings_{phase}.json")
        if not inputs.is_file():
            raise FileNotFoundError(f"Required findings file not found: {inputs}")
        findings = json.loads(inputs.read_text(encoding="utf-8")).get("findings", [])
        by_id = {str(item.get("id")): item for item in findings}
        recs = [map_finding(item, i + 1) for i, item in enumerate(findings)]
        ordered = sort_recommendations(recs, by_id)
        plan_items, groups = build_patch_plan(ordered)
        rec_json = self._path(f"recommendations_{phase}.json")
        rec_md = self._path(f"recommendations_{phase}.md")
        plan_json = self._path(f"patch_plan_{phase}.json")
        plan_md = self._path(f"patch_plan_{phase}.md")
        rec_json.parent.mkdir(parents=True, exist_ok=True)
        self._writer.write_recommendations(ordered, phase, rec_json, rec_md, self._path("recommendations.json"))
        self._writer.write_patch_plan(plan_items, groups, phase, plan_json, plan_md, self._path("patch_plan.json"))
        return self._writer.build_summary(ordered, rec_json, rec_md, plan_json, plan_md)

    def _path(self, name: str) -> Path:
        return self._config.project_root / "reports" / "architecture" / name
