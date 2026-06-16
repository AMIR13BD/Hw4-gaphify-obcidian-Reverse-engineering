"""Pipeline run result model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ex04_agent.workflow.state import PipelineState


@dataclass(frozen=True)
class PipelineResult:
    success: bool
    phase: str
    dry_run: bool
    completed_agents: tuple[str, ...]
    skipped_agents: tuple[str, ...]
    stop_reason: str | None
    graph_artifacts: dict[str, str]
    metrics_path: str
    obsidian_paths: dict[str, str]
    hotmd_path: str
    story_path: str
    findings_path: str
    finding_count: int
    recommendations_path: str
    recommendation_count: int
    patch_plan_path: str
    patch_result_path: str
    patch_applied_count: int
    regression_path: str
    regression_failed_files: tuple[str, ...]
    comparison_path: str
    comparison: dict[str, Any]
    trace_run_id: str
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_state(cls, state: PipelineState) -> PipelineResult:
        errors = tuple(state.get("errors", []))
        return cls(
            success=not errors,
            phase=str(state.get("phase", "")),
            dry_run=bool(state.get("dry_run", True)),
            completed_agents=tuple(state.get("completed_agents", [])),
            skipped_agents=tuple(state.get("skipped_agents", [])),
            stop_reason=state.get("stop_reason"),
            graph_artifacts=dict(state.get("graph_artifacts", {})),
            metrics_path=str(state.get("metrics_path", "")),
            obsidian_paths=dict(state.get("obsidian_paths", {})),
            hotmd_path=str(state.get("hotmd_path", "")),
            story_path=str(state.get("story_path", "")),
            findings_path=str(state.get("findings_path", "")),
            finding_count=int(state.get("finding_count", 0)),
            recommendations_path=str(state.get("recommendations_path", "")),
            recommendation_count=int(state.get("recommendation_count", 0)),
            patch_plan_path=str(state.get("patch_plan_path", "")),
            patch_result_path=str(state.get("patch_result_path", "")),
            patch_applied_count=int(state.get("patch_applied_count", 0)),
            regression_path=str(state.get("regression_path", "")),
            regression_failed_files=tuple(state.get("regression_failed_files", [])),
            comparison_path=str(state.get("comparison_path", "")),
            comparison=dict(state.get("comparison", {})),
            trace_run_id=str(state.get("trace_run_id", "")),
            errors=errors,
        )
