"""Tests for regression engine pipeline integration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from regression_helpers import make_regression_result

from ex04_agent.detection.report_writer import FindingsSummary
from ex04_agent.graph.graphify_run_result import GraphifyRunResult
from ex04_agent.obsidian.dynamic_hotmd_builder import DynamicHotMdResult
from ex04_agent.obsidian.vault_builder import VaultBuildResult
from ex04_agent.recommendation.report_writer import RecommendationSummary
from ex04_agent.shared.config import load_config
from ex04_agent.workflow.graph import LangGraphWorkflow
from ex04_agent.workflow.pipeline_nodes import PipelineAgents


def test_pipeline_dry_run_marks_test_runner_completed(tmp_path: Path, monkeypatch) -> None:
    """Dry-run pipeline completes test_runner and still skips comparison_report."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(setup_src.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr("ex04_agent.shared.config.find_project_root", lambda start=None: project_root)

    config = load_config(project_root / "config" / "setup.json")
    graph_dir = project_root / "artifacts" / "graph" / "before"
    graph_dir.mkdir(parents=True)
    metrics_dir = project_root / "reports" / "architecture"
    metrics_dir.mkdir(parents=True)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    (graph_dir / "graph.json").write_text(fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"), encoding="utf-8")
    (metrics_dir / "metrics_before.json").write_text(fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"), encoding="utf-8")

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
        changed_files_count=0, ranked_nodes_count=3, top_labels=(),
    ))
    from ex04_agent.agents.architecture_bug import ArchitectureBugAgent

    agents.architecture_bug = ArchitectureBugAgent(config)
    agents.architecture_bug.run = MagicMock(return_value=FindingsSummary(
        finding_count=1, by_category={}, by_severity={}, high_confidence_count=0,
        json_path=str(metrics_dir / "findings_before.json"),
        markdown_path=str(metrics_dir / "findings_before.md"),
    ))
    agents.recommendation.run = MagicMock(return_value=RecommendationSummary(
        recommendation_count=1, by_action_type={}, by_priority={}, patchable_count=0,
        recommendations_json_path=str(metrics_dir / "recommendations_before.json"),
        recommendations_markdown_path=str(metrics_dir / "recommendations_before.md"),
        patch_plan_json_path=str(metrics_dir / "patch_plan_before.json"),
        patch_plan_markdown_path=str(metrics_dir / "patch_plan_before.md"),
    ))
    agents.test_runner.run = MagicMock(return_value=make_regression_result())

    result = LangGraphWorkflow(config, agents=agents).run(phase="before", dry_run=True)
    assert result.stop_reason == "dry_run_completed"
    assert "test_runner" in result.completed_agents
    assert any("comparison_report:" in s for s in result.skipped_agents)
