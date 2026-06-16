"""Patch plan builder for Phase 9 outputs."""

from __future__ import annotations

from collections import defaultdict

from ex04_agent.recommendation.model import ArchitectureRecommendation, PatchPlanItem


def build_patch_plan(recommendations: list[ArchitectureRecommendation]) -> tuple[list[PatchPlanItem], dict[str, list[PatchPlanItem]]]:
    items = [_to_item(rec) for rec in recommendations]
    groups: dict[str, list[PatchPlanItem]] = defaultdict(list)
    for item, rec in zip(items, recommendations, strict=True):
        key = "deferred"
        if rec.action_type == "docs_only":
            key = "docs_only_items"
        elif rec.action_type == "review_required":
            key = "safe_candidates_phase10" if rec.phase10_patchable else "review_required_items"
        elif rec.action_type == "safe_auto":
            key = "safe_candidates_phase10"
        groups[key].append(item)
    return items, dict(groups)


def _to_item(rec: ArchitectureRecommendation) -> PatchPlanItem:
    command = "uv run pytest -q" if rec.action_type != "docs_only" else "uv run ruff check"
    return PatchPlanItem(
        recommendation_id=rec.id,
        finding_id=rec.finding_id,
        action_type=rec.action_type,
        affected_files=rec.affected_files,
        planned_operation=rec.proposed_change,
        safety_level=rec.risk_level,
        requires_manual_review=rec.action_type == "review_required",
        rollback_notes="Revert planned file edits and re-run detection/recommendation.",
        validation_command=command,
    )
