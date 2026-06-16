"""Pipeline state for LangGraph workflow."""

from __future__ import annotations

from typing import Any, TypedDict

from ex04_agent.shared.config import AppConfig


class PipelineState(TypedDict, total=False):
    phase: str
    dry_run: bool
    target_repo_path: str
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
    regression_failed_files: list[str]
    comparison_path: str
    comparison: dict[str, Any]
    findings: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    applied_patches: list[dict[str, Any]]
    test_results: dict[str, Any]
    iteration: int
    max_iterations: int
    errors: list[str]
    completed_agents: list[str]
    skipped_agents: list[str]
    stop_reason: str | None
    trace_run_id: str


def initial_state(config: AppConfig, *, phase: str, dry_run: bool) -> PipelineState:
    from datetime import UTC, datetime

    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return PipelineState(
        phase=phase,
        dry_run=dry_run,
        target_repo_path=str(config.target_repo_path),
        graph_artifacts={},
        metrics_path="",
        obsidian_paths={},
        hotmd_path="",
        story_path="",
        findings_path="",
        finding_count=0,
        recommendations_path="",
        recommendation_count=0,
        patch_plan_path="",
        patch_result_path="",
        patch_applied_count=0,
        regression_path="",
        regression_failed_files=[],
        comparison_path="",
        comparison={},
        findings=[],
        recommendations=[],
        applied_patches=[],
        test_results={},
        iteration=1,
        max_iterations=config.max_iterations,
        errors=[],
        completed_agents=[],
        skipped_agents=[],
        stop_reason=None,
        trace_run_id=run_id,
    )


def merge_completed(state: PipelineState, agent_name: str, **updates: Any) -> dict[str, Any]:
    completed = list(state.get("completed_agents", []))
    if agent_name not in completed:
        completed.append(agent_name)
    return {"completed_agents": completed, **updates}


def merge_skipped(state: PipelineState, agent_name: str, reason: str) -> dict[str, Any]:
    skipped = list(state.get("skipped_agents", []))
    entry = f"{agent_name}:{reason}"
    if entry not in skipped:
        skipped.append(entry)
    return {"skipped_agents": skipped}
