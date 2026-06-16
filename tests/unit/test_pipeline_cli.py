"""Tests for pipeline CLI command."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ex04_agent.cli.parser import build_parser
from ex04_agent.main import main
from ex04_agent.workflow.result import PipelineResult


def test_cli_pipeline_rejects_invalid_phase() -> None:
    """Parser only accepts before/after phases."""
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["pipeline", "--phase", "middle"])


def test_cli_pipeline_dry_run(monkeypatch, capsys) -> None:
    """Pipeline subcommand prints JSON summary."""
    mock_result = PipelineResult(
        success=True,
        phase="before",
        dry_run=True,
        completed_agents=("repository_setup", "supervisor"),
        skipped_agents=("patch:disabled",),
        stop_reason="dry_run_completed",
        graph_artifacts={},
        metrics_path="metrics.json",
        obsidian_paths={},
        hotmd_path="hot.md",
        story_path="story.md",
        findings_path="findings.json",
        finding_count=3,
        recommendations_path="recommendations.json",
        recommendation_count=3,
        patch_plan_path="patch_plan.json",
        trace_run_id="run1",
        errors=(),
    )
    monkeypatch.setattr(
        "ex04_agent.cli.handlers.Ex04Sdk",
        lambda: MagicMock(run_pipeline=MagicMock(return_value=mock_result)),
    )
    code = main(["pipeline", "--dry-run", "--phase", "before"])
    captured = capsys.readouterr().out
    assert code == 0
    assert "dry_run_completed" in captured
