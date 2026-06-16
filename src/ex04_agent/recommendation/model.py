"""Recommendation and patch-plan models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

ActionType = Literal["safe_auto", "review_required", "docs_only", "defer"]
Priority = Literal["low", "medium", "high", "critical"]
Confidence = Literal["low", "medium", "high"]
RiskLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class ArchitectureRecommendation:
    id: str
    finding_id: str
    title: str
    category: str
    action_type: ActionType
    priority: Priority
    confidence: Confidence
    rationale: str
    proposed_change: str
    affected_files: tuple[str, ...]
    risk_level: RiskLevel
    preconditions: tuple[str, ...]
    validation_steps: tuple[str, ...]
    blocked_by: tuple[str, ...]
    phase10_patchable: bool
    evidence_summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PatchPlanItem:
    recommendation_id: str
    finding_id: str
    action_type: ActionType
    affected_files: tuple[str, ...]
    planned_operation: str
    safety_level: RiskLevel
    requires_manual_review: bool
    rollback_notes: str
    validation_command: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
