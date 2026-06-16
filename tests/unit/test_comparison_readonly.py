"""Tests that comparison is read-only on before/after architecture artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from phase_after_helpers import setup_after_project, write_comparison_arch

from ex04_agent.agents.comparison_report import ComparisonReportAgent
from ex04_agent.main import main
from ex04_agent.shared.config import load_config
from ex04_agent.workflow.graph import LangGraphWorkflow


def _snapshot(paths: list[Path]) -> dict[str, str]:
    return {str(p): p.read_text(encoding="utf-8") for p in paths if p.is_file()}


def _before_paths(root: Path) -> list[Path]:
    arch = root / "reports" / "architecture"
    graph = root / "artifacts" / "graph" / "before" / "graph.json"
    return [
        graph,
        arch / "metrics_before.json",
        arch / "findings_before.json",
        arch / "recommendations_before.json",
    ]


def _setup_frozen_before(root: Path) -> None:
    write_comparison_arch(root)
    graph_before = root / "artifacts" / "graph" / "before"
    graph_before.mkdir(parents=True, exist_ok=True)
    graph_after = root / "artifacts" / "graph" / "after"
    graph_after.mkdir(parents=True, exist_ok=True)
    graph_before.joinpath("graph.json").write_text(
        json.dumps({"nodes": [{"id": f"b{i}"} for i in range(26)], "links": [{}] * 20}),
        encoding="utf-8",
    )
    graph_after.joinpath("graph.json").write_text(
        json.dumps({"nodes": [{"id": f"a{i}"} for i in range(25)], "links": [{}] * 19}),
        encoding="utf-8",
    )


def test_compare_does_not_modify_before_artifacts(tmp_path, monkeypatch) -> None:
    root = setup_after_project(tmp_path, monkeypatch)
    _setup_frozen_before(root)
    paths = _before_paths(root)
    before = _snapshot(paths)
    assert main(["compare"]) == 0
    assert _snapshot(paths) == before
    assert (root / "reports" / "comparison" / "before_after.json").is_file()


def test_compare_preserves_before_counts(tmp_path, monkeypatch) -> None:
    root = setup_after_project(tmp_path, monkeypatch)
    _setup_frozen_before(root)
    ComparisonReportAgent(load_config(root / "config" / "setup.json")).run()
    metrics = json.loads((root / "reports" / "architecture" / "metrics_before.json").read_text())
    findings = json.loads((root / "reports" / "architecture" / "findings_before.json").read_text())
    recs = json.loads((root / "reports" / "architecture" / "recommendations_before.json").read_text())
    assert metrics["summary"]["node_count"] == 26
    assert metrics["summary"]["link_count"] == 20
    assert len(findings["findings"]) == 19
    assert len(recs["recommendations"]) == 19


def test_pipeline_after_comparison_only_preserves_before(tmp_path, monkeypatch) -> None:
    root = setup_after_project(tmp_path, monkeypatch)
    _setup_frozen_before(root)
    config = load_config(root / "config" / "setup.json")
    paths = _before_paths(root)
    before = _snapshot(paths)
    result = LangGraphWorkflow(config).run(phase="after", dry_run=True)
    assert _snapshot(paths) == before
    assert "comparison_report" in result.completed_agents
    assert any("graphify_runner:" in s for s in result.skipped_agents)
