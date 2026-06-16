"""Tests for LangGraph workflow."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ex04_agent.graph.graphify_run_result import GraphifyRunResult
from ex04_agent.obsidian.dynamic_hotmd_builder import DynamicHotMdResult
from ex04_agent.obsidian.vault_builder import VaultBuildResult
from ex04_agent.shared.config import load_config
from ex04_agent.workflow.graph import NODE_ORDER, LangGraphWorkflow
from ex04_agent.workflow.pipeline_nodes import PipelineAgents


def _graphify_result() -> GraphifyRunResult:
    return GraphifyRunResult(
        success=True,
        phase="before",
        command=("graphify", "update", "."),
        cwd="/tmp/repo",
        return_code=0,
        graphify_cli="graphify",
        graphify_cli_path="/bin/graphify",
        target_repo_path="/tmp/repo",
        stdout="ok",
        stderr="",
        copied_artifacts=("graph.json",),
        missing_required_artifacts=(),
        missing_optional_artifacts=(),
        artifact_dest_dir="/tmp/artifacts/graph/before",
        log_path="/tmp/log.txt",
        metadata_path="/tmp/meta.json",
        timestamp="2026-01-01T00:00:00+00:00",
    )


def test_langgraph_workflow_compiles(tmp_path: Path) -> None:
    """Workflow graph compiles with all expected nodes."""
    config = load_config()
    workflow = LangGraphWorkflow(config)
    from ex04_agent.agent_trace.recorder import AgentTraceRecorder

    rec = AgentTraceRecorder(tmp_path, "compile_test")
    compiled = workflow.compile(rec)
    assert compiled is not None
    assert len(NODE_ORDER) == 12


def test_pipeline_dry_run_with_mocked_services(tmp_path, monkeypatch) -> None:
    """Dry-run pipeline completes with mocked heavy agents."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(
        setup_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    target = project_root / "data" / "target_repo" / "broken-python"
    target.mkdir(parents=True)
    graph_dir = project_root / "artifacts" / "graph" / "before"
    graph_dir.mkdir(parents=True)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    (graph_dir / "graph.json").write_text(
        fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    metrics_dir = project_root / "reports" / "architecture"
    metrics_dir.mkdir(parents=True)
    (metrics_dir / "metrics_before.json").write_text(
        fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "ex04_agent.shared.config.find_project_root",
        lambda start=None: project_root,
    )
    config = load_config(project_root / "config" / "setup.json")
    agents = PipelineAgents(config)
    agents.graphify_runner.run = MagicMock(return_value=_graphify_result())
    agents.graph_parser.run = MagicMock(return_value=MagicMock())
    agents.obsidian_vault.run = MagicMock(
        return_value=VaultBuildResult(
            success=True,
            phase="before",
            vault_dir=str(project_root / "obsidian"),
            index_path=str(project_root / "obsidian" / "index.md"),
            hot_path=str(project_root / "obsidian" / "hot.md"),
            report_path=str(project_root / "obsidian" / "reports" / "graph_summary.md"),
            node_pages_created=3,
            files_written=(),
        )
    )
    agents.obsidian_vault.run_dynamic_hotmd = MagicMock(
        return_value=DynamicHotMdResult(
            success=True,
            phase="before",
            hot_path=str(project_root / "obsidian" / "hot.md"),
            snapshot_path=str(project_root / "artifacts" / "hotmd" / "hot.md"),
            changed_files_count=0,
            ranked_nodes_count=5,
            top_labels=("hub",),
        )
    )
    from ex04_agent.agents.architecture_bug import ArchitectureBugAgent
    from ex04_agent.detection.report_writer import FindingsSummary

    agents.architecture_bug = ArchitectureBugAgent(config)
    agents.architecture_bug.run = MagicMock(
        return_value=FindingsSummary(
            finding_count=2,
            by_category={"possible_hub": 2},
            by_severity={"medium": 2},
            high_confidence_count=1,
            json_path=str(metrics_dir / "findings_before.json"),
            markdown_path=str(metrics_dir / "findings_before.md"),
        )
    )

    result = LangGraphWorkflow(config, agents=agents).run(phase="before", dry_run=True)
    assert result.stop_reason == "dry_run_completed"
    assert "repository_setup" in result.completed_agents
    assert "supervisor" in result.completed_agents
    assert "architecture_bug" in result.completed_agents
    assert any("patch:" in item for item in result.skipped_agents)
