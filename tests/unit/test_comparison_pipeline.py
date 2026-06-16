"""Tests for pipeline before-phase comparison skip."""

from __future__ import annotations

from unittest.mock import MagicMock

from phase_after_helpers import setup_after_project
from regression_helpers import make_regression_result

from ex04_agent.detection.report_writer import FindingsSummary
from ex04_agent.graph.graphify_run_result import GraphifyRunResult
from ex04_agent.obsidian.dynamic_hotmd_builder import DynamicHotMdResult
from ex04_agent.obsidian.vault_builder import VaultBuildResult
from ex04_agent.recommendation.report_writer import RecommendationSummary
from ex04_agent.shared.config import load_config
from ex04_agent.workflow.graph import LangGraphWorkflow
from ex04_agent.workflow.pipeline_nodes import PipelineAgents


def test_pipeline_before_skips_comparison(tmp_path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    config = load_config(project_root / "config" / "setup.json")

    agents = PipelineAgents(config)
    agents.graphify_runner.run = MagicMock(return_value=GraphifyRunResult(
        success=True, phase="before", command=("g",), cwd="/tmp", return_code=0,
        graphify_cli="g", graphify_cli_path="/g", target_repo_path="/t",
        stdout="ok", stderr="", copied_artifacts=(), missing_required_artifacts=(),
        missing_optional_artifacts=(), artifact_dest_dir="/a", log_path="/l",
        metadata_path="/m", timestamp="2026-01-01T00:00:00+00:00",
    ))
    agents.graph_parser.run = MagicMock(return_value=MagicMock())
    agents.obsidian_vault.run = MagicMock(return_value=VaultBuildResult(
        success=True, phase="before", vault_dir="/v", index_path="/i",
        hot_path="/h", report_path="/r", node_pages_created=1, files_written=(),
    ))
    agents.obsidian_vault.run_dynamic_hotmd = MagicMock(return_value=DynamicHotMdResult(
        success=True, phase="before", hot_path="/h", snapshot_path="/s",
        changed_files_count=0, ranked_nodes_count=1, top_labels=(),
    ))
    agents.architecture_bug.run = MagicMock(return_value=FindingsSummary(
        finding_count=1, by_category={}, by_severity={}, high_confidence_count=0,
        json_path="/f", markdown_path="/fm",
    ))
    agents.recommendation.run = MagicMock(return_value=RecommendationSummary(
        recommendation_count=1, by_action_type={}, by_priority={}, patchable_count=0,
        recommendations_json_path="/r", recommendations_markdown_path="/rm",
        patch_plan_json_path="/p", patch_plan_markdown_path="/pm",
    ))
    agents.test_runner.run = MagicMock(return_value=make_regression_result("before"))
    result = LangGraphWorkflow(config, agents=agents).run(phase="before", dry_run=True)
    assert any("comparison_report:" in s for s in result.skipped_agents)
