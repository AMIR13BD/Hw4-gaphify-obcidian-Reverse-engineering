"""Tests for phase report path guards and before/after isolation."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from phase_after_helpers import setup_after_project
from regression_helpers import make_regression_result

from ex04_agent.detection.engine import ArchitectureDetectionEngine
from ex04_agent.recommendation.engine import RecommendationEngine
from ex04_agent.shared.config import load_config
from ex04_agent.shared.phase_paths import ensure_phase_write_path
from ex04_agent.workflow.graph import LangGraphWorkflow
from ex04_agent.workflow.pipeline_nodes import PipelineAgents


def test_ensure_phase_write_path_blocks_after_to_before() -> None:
    with pytest.raises(ValueError, match="must not write before"):
        ensure_phase_write_path(Path("reports/architecture/findings_before.json"), "after")


def test_after_detect_does_not_overwrite_findings_before(tmp_path: Path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    arch = project_root / "reports" / "architecture"
    arch.mkdir(parents=True)
    before = arch / "findings_before.json"
    before.write_text('{"phase":"before","finding_count":19,"findings":[]}', encoding="utf-8")
    graph_dir = project_root / "artifacts" / "graph" / "after"
    graph_dir.mkdir(parents=True)
    (graph_dir / "graph.json").write_text(
        fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    (arch / "metrics_after.json").write_text(
        fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    config = load_config(project_root / "config" / "setup.json")
    ArchitectureDetectionEngine(config).run(phase="after")
    assert json.loads(before.read_text(encoding="utf-8"))["finding_count"] == 19
    assert (arch / "findings_after.json").is_file()


def test_after_recommend_does_not_overwrite_before_plans(tmp_path: Path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    arch = project_root / "reports" / "architecture"
    arch.mkdir(parents=True)
    (arch / "findings_after.json").write_text(
        '{"phase":"after","findings":[{"id":"x","title":"t","detector":"d","category":"c","severity":"low","confidence":"medium","status":"candidate","observation":"o","relation":"r","confidence_reason":"cr","context":"ctx","affected_nodes":[],"affected_files":[],"evidence":[],"source_validation":"pending","next_validation_steps":[]}]}',
        encoding="utf-8",
    )
    (arch / "recommendations_before.json").write_text(
        '{"phase":"before","recommendation_count":19,"recommendations":[]}', encoding="utf-8",
    )
    (arch / "patch_plan_before.json").write_text(
        '{"phase":"before","items":[],"groups":{}}', encoding="utf-8",
    )
    config = load_config(project_root / "config" / "setup.json")
    RecommendationEngine(config).run(phase="after")
    assert json.loads((arch / "recommendations_before.json").read_text(encoding="utf-8"))["recommendation_count"] == 19
    assert (arch / "recommendations_after.json").is_file()
    assert (arch / "patch_plan_after.json").is_file()


def test_pipeline_after_preserves_before_findings(tmp_path: Path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    arch = project_root / "reports" / "architecture"
    graph_dir = project_root / "artifacts" / "graph" / "after"
    graph_dir.mkdir(parents=True)
    arch.mkdir(parents=True)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    (graph_dir / "graph.json").write_text(
        fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    (arch / "metrics_after.json").write_text(
        fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    (arch / "findings_before.json").write_text(
        '{"phase":"before","finding_count":19,"findings":[]}', encoding="utf-8",
    )
    config = load_config(project_root / "config" / "setup.json")
    agents = PipelineAgents(config)
    from ex04_agent.graph.graphify_run_result import GraphifyRunResult
    from ex04_agent.obsidian.dynamic_hotmd_builder import DynamicHotMdResult
    from ex04_agent.obsidian.vault_builder import VaultBuildResult

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
    from ex04_agent.agents.architecture_bug import ArchitectureBugAgent
    from ex04_agent.recommendation.report_writer import RecommendationSummary

    agents.architecture_bug = ArchitectureBugAgent(config)
    agents.recommendation.run = MagicMock(return_value=RecommendationSummary(
        recommendation_count=1, by_action_type={}, by_priority={}, patchable_count=0,
        recommendations_json_path=str(arch / "recommendations_after.json"),
        recommendations_markdown_path=str(arch / "recommendations_after.md"),
        patch_plan_json_path=str(arch / "patch_plan_after.json"),
        patch_plan_markdown_path=str(arch / "patch_plan_after.md"),
    ))
    agents.test_runner.run = MagicMock(return_value=make_regression_result("after"))
    LangGraphWorkflow(config, agents=agents).run(phase="after", dry_run=True)
    assert json.loads((arch / "findings_before.json").read_text(encoding="utf-8"))["finding_count"] == 19
