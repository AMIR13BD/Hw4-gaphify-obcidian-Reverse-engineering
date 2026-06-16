"""Skip artifact regeneration when comparison inputs already exist."""

from __future__ import annotations

from ex04_agent.comparison.loader import ComparisonLoader
from ex04_agent.shared.config import AppConfig
from ex04_agent.workflow.state import PipelineState

_ARTIFACT_AGENTS = frozenset({
    "graphify_runner",
    "graph_parser",
    "obsidian_vault",
    "dynamic_hotmd",
    "graph_interpreter",
    "architecture_bug",
    "recommendation",
    "patch",
    "test_runner",
})

_SKIP_REASON = (
    "Comparison-only after dry-run; existing before/after artifacts preserved "
    "(no graphify/detect/recommend regeneration)."
)


def comparison_only_skip_reason(
    state: PipelineState,
    config: AppConfig,
    agent_name: str,
) -> str | None:
    if agent_name not in _ARTIFACT_AGENTS:
        return None
    if str(state.get("phase", "before")) != "after":
        return None
    if not bool(state.get("dry_run", True)):
        return None
    if ComparisonLoader(config).comparison_ready():
        return _SKIP_REASON
    return None
