"""Tests for comparison engine, report writer, CLI, and pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from phase_after_helpers import setup_after_project, write_comparison_arch
from regression_helpers import make_regression_result

from ex04_agent.comparison.engine import ComparisonSummary
from ex04_agent.comparison.model import (
    ComparisonResult,
    FindingDelta,
    GraphDelta,
    MetricDelta,
    RecommendationDelta,
)
from ex04_agent.comparison.report_writer import ComparisonReportWriter
from ex04_agent.main import main
from ex04_agent.shared.config import load_config
from ex04_agent.workflow.graph import LangGraphWorkflow
from ex04_agent.workflow.pipeline_nodes import PipelineAgents


def _write_full_arch(root: Path) -> None:
    write_comparison_arch(root)


def test_report_writer_writes_json_and_md(tmp_path: Path) -> None:
    fd = FindingDelta(19, 8, ("resolved",), ("remain",), {}, {}, {}, {}, 2, 0)
    rd = RecommendationDelta(19, 8, {}, {}, {}, {}, 0, 0)
    gd = GraphDelta((), (), (), (), (), (), "story")
    result = ComparisonResult("before", "after", [MetricDelta("node_count", 26, 25, -1)], fd, rd, gd, (), (), {}, {"json": "j", "md": "m"})
    jp, mp = tmp_path / "c.json", tmp_path / "c.md"
    ComparisonReportWriter().write(result, json_path=jp, md_path=mp)
    assert jp.is_file() and "Executive Summary" in mp.read_text(encoding="utf-8")


def test_compare_cli_rejects_same_phase() -> None:
    assert main(["compare", "--before", "before", "--after", "before"]) == 1


def test_compare_cli_runs(monkeypatch, capsys) -> None:
    mock = ComparisonSummary(26, 25, 19, 8, 19, 8, 11, 8, "/j", "/m")
    monkeypatch.setattr(
        "ex04_agent.agents.comparison_report.ComparisonReportAgent",
        lambda *a, **k: MagicMock(run=MagicMock(return_value=mock)),
    )
    assert main(["compare"]) == 0
    assert "before_nodes" in capsys.readouterr().out


def test_comparison_agent_completes(tmp_path: Path) -> None:
    from ex04_agent.agent_trace.recorder import AgentTraceRecorder
    from ex04_agent.agents.comparison_report import ComparisonReportAgent
    from ex04_agent.workflow.state import initial_state

    config = load_config()
    agent = ComparisonReportAgent(config)
    agent.run = MagicMock(return_value=ComparisonSummary(
        26, 25, 19, 8, 19, 8, 11, 8, "/j", "/m",
    ))
    state = initial_state(config, phase="after", dry_run=True)
    recorder = AgentTraceRecorder(tmp_path, "t")
    updates = agent.run_pipeline(state, recorder)
    assert "comparison_report" in updates.get("completed_agents", [])


def test_pipeline_after_completes_comparison(tmp_path: Path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    _write_full_arch(project_root)
    config = load_config(project_root / "config" / "setup.json")
    agents = PipelineAgents(config)
    from ex04_agent.agents.architecture_bug import ArchitectureBugAgent
    from ex04_agent.detection.report_writer import FindingsSummary
    from ex04_agent.graph.graphify_run_result import GraphifyRunResult
    from ex04_agent.obsidian.dynamic_hotmd_builder import DynamicHotMdResult
    from ex04_agent.obsidian.vault_builder import VaultBuildResult
    from ex04_agent.recommendation.report_writer import RecommendationSummary

    arch = project_root / "reports" / "architecture"
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
        finding_count=8, by_category={}, by_severity={}, high_confidence_count=0,
        json_path=str(arch / "findings_after.json"), markdown_path=str(arch / "findings_after.md"),
    ))
    agents.recommendation.run = MagicMock(return_value=RecommendationSummary(
        recommendation_count=8, by_action_type={}, by_priority={}, patchable_count=0,
        recommendations_json_path=str(arch / "recommendations_after.json"),
        recommendations_markdown_path=str(arch / "recommendations_after.md"),
        patch_plan_json_path=str(arch / "patch_plan_after.json"),
        patch_plan_markdown_path=str(arch / "patch_plan_after.md"),
    ))
    agents.test_runner.run = MagicMock(return_value=make_regression_result("after"))
    result = LangGraphWorkflow(config, agents=agents).run(phase="after", dry_run=True)
    assert "comparison_report" in result.completed_agents
