"""Tests for after-phase pipeline integration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from phase_after_helpers import setup_after_project, write_comparison_arch
from regression_helpers import make_regression_result

from ex04_agent.agents.architecture_bug import ArchitectureBugAgent
from ex04_agent.detection.report_writer import FindingsSummary
from ex04_agent.graph.graphify_run_result import GraphifyRunResult
from ex04_agent.obsidian.dynamic_hotmd_builder import DynamicHotMdResult
from ex04_agent.obsidian.vault_builder import VaultBuildResult
from ex04_agent.recommendation.report_writer import RecommendationSummary
from ex04_agent.shared.config import load_config
from ex04_agent.workflow.graph import LangGraphWorkflow
from ex04_agent.workflow.pipeline_nodes import PipelineAgents


def test_pipeline_after_completes_comparison_report(tmp_path: Path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    write_comparison_arch(project_root)
    graph_dir = project_root / "artifacts" / "graph" / "after"
    metrics_dir = project_root / "reports" / "architecture"
    graph_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    (graph_dir / "graph.json").write_text(
        fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    (metrics_dir / "metrics_after.json").write_text(
        fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    config = load_config(project_root / "config" / "setup.json")
    agents = PipelineAgents(config)
    agents.graphify_runner.run = MagicMock(return_value=GraphifyRunResult(
        success=True, phase="after", command=("g",), cwd="/tmp", return_code=0,
        graphify_cli="g", graphify_cli_path="/g", target_repo_path="/t",
        stdout="ok", stderr="", copied_artifacts=(), missing_required_artifacts=(),
        missing_optional_artifacts=(), artifact_dest_dir="/a", log_path="/l",
        metadata_path="/m", timestamp="2026-01-01T00:00:00+00:00",
    ))
    agents.graph_parser.run = MagicMock(return_value=MagicMock())
    agents.obsidian_vault.run = MagicMock(return_value=VaultBuildResult(
        success=True, phase="after", vault_dir="/v", index_path="/i",
        hot_path="/h", report_path="/r", node_pages_created=1, files_written=(),
    ))
    agents.obsidian_vault.run_dynamic_hotmd = MagicMock(return_value=DynamicHotMdResult(
        success=True, phase="after", hot_path="/h", snapshot_path="/s",
        changed_files_count=0, ranked_nodes_count=3, top_labels=(),
    ))
    agents.architecture_bug = ArchitectureBugAgent(config)
    agents.architecture_bug.run = MagicMock(return_value=FindingsSummary(
        finding_count=1, by_category={}, by_severity={}, high_confidence_count=0,
        json_path=str(metrics_dir / "findings_after.json"),
        markdown_path=str(metrics_dir / "findings_after.md"),
    ))
    agents.recommendation.run = MagicMock(return_value=RecommendationSummary(
        recommendation_count=1, by_action_type={}, by_priority={}, patchable_count=0,
        recommendations_json_path=str(metrics_dir / "recommendations_after.json"),
        recommendations_markdown_path=str(metrics_dir / "recommendations_after.md"),
        patch_plan_json_path=str(metrics_dir / "patch_plan_after.json"),
        patch_plan_markdown_path=str(metrics_dir / "patch_plan_after.md"),
    ))
    agents.test_runner.run = MagicMock(return_value=make_regression_result("after"))
    result = LangGraphWorkflow(config, agents=agents).run(phase="after", dry_run=True)
    assert result.stop_reason == "dry_run_completed"
    assert "comparison_report" in result.completed_agents
    assert any("graphify_runner:" in s for s in result.skipped_agents)
    assert "test_runner" not in result.completed_agents
