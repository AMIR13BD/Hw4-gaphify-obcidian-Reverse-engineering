"""Tests for LangGraph pipeline dry-run execution."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from workflow_helpers import graphify_result, regression_result

from ex04_agent.agents.architecture_bug import ArchitectureBugAgent
from ex04_agent.detection.report_writer import FindingsSummary
from ex04_agent.obsidian.dynamic_hotmd_builder import DynamicHotMdResult
from ex04_agent.obsidian.vault_builder import VaultBuildResult
from ex04_agent.recommendation.report_writer import RecommendationSummary
from ex04_agent.shared.config import load_config
from ex04_agent.workflow.graph import LangGraphWorkflow
from ex04_agent.workflow.pipeline_nodes import PipelineAgents


def test_pipeline_dry_run_with_mocked_services(tmp_path, monkeypatch) -> None:
    """Dry-run pipeline completes with mocked heavy agents."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(
        setup_src.read_text(encoding="utf-8"), encoding="utf-8",
    )
    target = project_root / "data" / "target_repo" / "broken-python"
    target.mkdir(parents=True)
    graph_dir = project_root / "artifacts" / "graph" / "before"
    graph_dir.mkdir(parents=True)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    (graph_dir / "graph.json").write_text(
        fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    metrics_dir = project_root / "reports" / "architecture"
    metrics_dir.mkdir(parents=True)
    (metrics_dir / "metrics_before.json").write_text(
        fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    monkeypatch.setattr(
        "ex04_agent.shared.config.find_project_root",
        lambda start=None: project_root,
    )
    config = load_config(project_root / "config" / "setup.json")
    agents = PipelineAgents(config)
    agents.graphify_runner.run = MagicMock(return_value=graphify_result())
    agents.graph_parser.run = MagicMock(return_value=MagicMock())
    agents.obsidian_vault.run = MagicMock(
        return_value=VaultBuildResult(
            success=True, phase="before",
            vault_dir=str(project_root / "obsidian"),
            index_path=str(project_root / "obsidian" / "index.md"),
            hot_path=str(project_root / "obsidian" / "hot.md"),
            report_path=str(project_root / "obsidian" / "reports" / "graph_summary.md"),
            node_pages_created=3, files_written=(),
        )
    )
    agents.obsidian_vault.run_dynamic_hotmd = MagicMock(
        return_value=DynamicHotMdResult(
            success=True, phase="before",
            hot_path=str(project_root / "obsidian" / "hot.md"),
            snapshot_path=str(project_root / "artifacts" / "hotmd" / "hot.md"),
            changed_files_count=0, ranked_nodes_count=5, top_labels=("hub",),
        )
    )
    agents.architecture_bug = ArchitectureBugAgent(config)
    agents.architecture_bug.run = MagicMock(
        return_value=FindingsSummary(
            finding_count=2, by_category={"possible_hub": 2},
            by_severity={"medium": 2}, high_confidence_count=1,
            json_path=str(metrics_dir / "findings_before.json"),
            markdown_path=str(metrics_dir / "findings_before.md"),
        )
    )
    agents.recommendation.run = MagicMock(
        return_value=RecommendationSummary(
            recommendation_count=2, by_action_type={"review_required": 2},
            by_priority={"high": 1, "medium": 1}, patchable_count=1,
            recommendations_json_path=str(metrics_dir / "recommendations_before.json"),
            recommendations_markdown_path=str(metrics_dir / "recommendations_before.md"),
            patch_plan_json_path=str(metrics_dir / "patch_plan_before.json"),
            patch_plan_markdown_path=str(metrics_dir / "patch_plan_before.md"),
        )
    )
    agents.test_runner.run = MagicMock(return_value=regression_result(metrics_dir))

    result = LangGraphWorkflow(config, agents=agents).run(phase="before", dry_run=True)
    assert result.stop_reason == "dry_run_completed"
    assert "repository_setup" in result.completed_agents
    assert "supervisor" in result.completed_agents
    assert "architecture_bug" in result.completed_agents
    assert "recommendation" in result.completed_agents
    assert "test_runner" in result.completed_agents
    assert any("patch:" in item for item in result.skipped_agents)
    assert any("comparison_report:" in item for item in result.skipped_agents)
