"""Write recommendation and patch plan reports."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ex04_agent.recommendation.model import ArchitectureRecommendation, PatchPlanItem


@dataclass(frozen=True)
class RecommendationSummary:
    recommendation_count: int
    by_action_type: dict[str, int]
    by_priority: dict[str, int]
    patchable_count: int
    recommendations_json_path: str
    recommendations_markdown_path: str
    patch_plan_json_path: str
    patch_plan_markdown_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RecommendationReportWriter:
    def write_recommendations(self, recs: list[ArchitectureRecommendation], phase: str, json_path: Path, md_path: Path, latest_path: Path | None) -> None:
        payload = {"phase": phase, "recommendation_count": len(recs), "recommendations": [r.to_dict() for r in recs]}
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if latest_path:
            latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        md_path.write_text(self._recommendations_md(recs), encoding="utf-8")

    def write_patch_plan(self, items: list[PatchPlanItem], groups: dict[str, list[PatchPlanItem]], phase: str, json_path: Path, md_path: Path, latest_path: Path | None) -> None:
        payload = {"phase": phase, "note": "Phase 9 does not modify the target repository.", "items": [i.to_dict() for i in items], "groups": {k: [i.to_dict() for i in v] for k, v in groups.items()}}
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if latest_path:
            latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        md_path.write_text(self._patch_plan_md(groups), encoding="utf-8")

    def build_summary(self, recs: list[ArchitectureRecommendation], rec_json: Path, rec_md: Path, plan_json: Path, plan_md: Path) -> RecommendationSummary:
        return RecommendationSummary(
            recommendation_count=len(recs),
            by_action_type=dict(sorted(Counter(r.action_type for r in recs).items())),
            by_priority=dict(sorted(Counter(r.priority for r in recs).items())),
            patchable_count=sum(1 for r in recs if r.phase10_patchable),
            recommendations_json_path=str(rec_json),
            recommendations_markdown_path=str(rec_md),
            patch_plan_json_path=str(plan_json),
            patch_plan_markdown_path=str(plan_md),
        )

    def _recommendations_md(self, recs: list[ArchitectureRecommendation]) -> str:
        lines = ["# Recommendations (Phase 9)", "", "Phase 9 does not modify the target repository.", "", f"- Total recommendations: **{len(recs)}**", "", "| Action type | Count |", "| --- | ---: |"]
        for action, count in sorted(Counter(r.action_type for r in recs).items()):
            lines.append(f"| `{action}` | {count} |")
        top = [r for r in recs if r.priority in {"critical", "high"}][:5]
        lines.extend(["", "## Top priorities", ""])
        for rec in top:
            lines.extend([f"- `{rec.priority}` {rec.title} ({', '.join(rec.affected_files) or 'no file'})"])
        for action in ("review_required", "safe_auto", "docs_only", "defer"):
            lines.extend(["", f"## {action}", ""])
            for rec in [r for r in recs if r.action_type == action]:
                lines.extend([f"### {rec.title}", "", f"- Rationale: {rec.rationale}", f"- Affected files: {', '.join(rec.affected_files) or 'N/A'}", "- Validation steps:"])
                lines.extend([f"  - {step}" for step in rec.validation_steps] or ["  - needs manual confirmation"])
                lines.append("")
        return "\n".join(lines) + "\n"

    def _patch_plan_md(self, groups: dict[str, list[PatchPlanItem]]) -> str:
        lines = ["# Patch Plan (Phase 9)", "", "Phase 9 does not modify the target repository.", ""]
        sections = ("safe_candidates_phase10", "review_required_items", "docs_only_items", "deferred")
        for section in sections:
            lines.extend([f"## {section}", ""])
            for item in groups.get(section, []):
                lines.extend([f"- `{item.recommendation_id}` {item.planned_operation}", f"  - validation: `{item.validation_command}`", f"  - rollback: {item.rollback_notes}"])
            if not groups.get(section):
                lines.append("- None")
            lines.append("")
        return "\n".join(lines)
