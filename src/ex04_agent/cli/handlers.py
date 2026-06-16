"""CLI command handler exports for ex04-agent."""

from __future__ import annotations

from ex04_agent.cli.handlers_graph import (
    run_graphify,
    run_health,
    run_hotmd,
    run_obsidian,
    run_parse,
)
from ex04_agent.cli.handlers_workflow import (
    run_compare,
    run_detect,
    run_patch,
    run_pipeline,
    run_recommend,
    run_test,
)

__all__ = (
    "run_compare",
    "run_detect",
    "run_graphify",
    "run_health",
    "run_hotmd",
    "run_obsidian",
    "run_parse",
    "run_patch",
    "run_pipeline",
    "run_recommend",
    "run_test",
)
