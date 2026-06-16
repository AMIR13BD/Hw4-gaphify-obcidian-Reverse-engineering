"""Tests for after-phase artifact paths and isolation."""

from __future__ import annotations

import json
from pathlib import Path

from phase_after_helpers import setup_after_project

from ex04_agent.agents.graph_parser import GraphParserAgent
from ex04_agent.detection.engine import ArchitectureDetectionEngine
from ex04_agent.graph.collector import GraphCollector
from ex04_agent.graph.graphify_runner import GraphifyRunner
from ex04_agent.main import main
from ex04_agent.recommendation.engine import RecommendationEngine
from ex04_agent.shared.config import load_config


def test_graphify_after_artifact_dir(tmp_path: Path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    config = load_config(project_root / "config" / "setup.json")
    dest = GraphCollector(config).artifact_dir("after")
    assert dest == project_root / "artifacts" / "graph" / "after"
    assert GraphifyRunner(config).build_command("after")[-1] == "--force"


def test_parse_after_output_path(tmp_path: Path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    config = load_config(project_root / "config" / "setup.json")
    agent = GraphParserAgent(config)
    graph = project_root / "artifacts" / "graph" / "after" / "graph.json"
    graph.parent.mkdir(parents=True, exist_ok=True)
    graph.write_text(
        '{"directed":false,"multigraph":false,"graph":{},"nodes":[],"links":[]}',
        encoding="utf-8",
    )
    report = agent.run(phase="after", graph_path=graph)
    out = project_root / "reports" / "architecture" / "metrics_after.json"
    assert out.is_file()
    assert report.phase == "after"


def test_detection_recommendation_after_paths(tmp_path: Path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    graph_dir = project_root / "artifacts" / "graph" / "after"
    graph_dir.mkdir(parents=True)
    metrics_dir = project_root / "reports" / "architecture"
    metrics_dir.mkdir(parents=True)
    (graph_dir / "graph.json").write_text(
        fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    (metrics_dir / "metrics_after.json").write_text(
        fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    config = load_config(project_root / "config" / "setup.json")
    det = ArchitectureDetectionEngine(config).run(phase="after")
    assert det.json_path.endswith("findings_after.json")
    rec = RecommendationEngine(config).run(phase="after")
    assert rec.patch_plan_json_path.endswith("patch_plan_after.json")


def test_collect_after_does_not_overwrite_before(tmp_path: Path, monkeypatch) -> None:
    project_root = setup_after_project(tmp_path, monkeypatch)
    config = load_config(project_root / "config" / "setup.json")
    before_dir = project_root / "artifacts" / "graph" / "before"
    before_dir.mkdir(parents=True)
    (before_dir / "graph.json").write_text('{"marker":"before"}', encoding="utf-8")
    GraphCollector(config).collect("after")
    assert json.loads((before_dir / "graph.json").read_text(encoding="utf-8"))["marker"] == "before"


def test_cli_accepts_phase_after(monkeypatch) -> None:
    from ex04_agent.graph.graphify_run_result import GraphifyRunResult

    class FakeAgent:
        def run(self, phase: str) -> GraphifyRunResult:
            return GraphifyRunResult(
                success=True, phase=phase, command=("graphify", "update", ".", "--force"),
                cwd="/tmp", return_code=0, graphify_cli="graphify", graphify_cli_path="/g",
                target_repo_path="/tmp", stdout="", stderr="", copied_artifacts=("graph.json",),
                missing_required_artifacts=(), missing_optional_artifacts=(),
                artifact_dest_dir="/a/after", log_path="/l", metadata_path="/m",
                timestamp="2026-01-01T00:00:00+00:00",
            )

    monkeypatch.setattr("ex04_agent.cli.handlers.GraphifyRunnerAgent", FakeAgent)
    assert main(["graphify", "--phase", "after"]) == 0
