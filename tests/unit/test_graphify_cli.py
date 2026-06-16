"""Tests for Graphify CLI subcommand."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from ex04_agent.graph.graphify_runner import GraphifyRunResult
from ex04_agent.main import main


def _sample_result(phase: str = "before", success: bool = True) -> GraphifyRunResult:
    return GraphifyRunResult(
        success=success,
        phase=phase,
        command=("graphify", "update", "."),
        cwd="/tmp/repo",
        return_code=0 if success else 1,
        graphify_cli="graphify",
        graphify_cli_path="/bin/graphify",
        target_repo_path="/tmp/repo",
        stdout="ok",
        stderr="",
        copied_artifacts=("graph.json", "graph.html", "GRAPH_REPORT.md"),
        missing_required_artifacts=(),
        missing_optional_artifacts=(".graphify_root",),
        artifact_dest_dir="/tmp/artifacts/graph/before",
        log_path="/tmp/reports/graphify/graphify_before_run.txt",
        metadata_path="/tmp/reports/graphify/graphify_before_metadata.json",
        timestamp="2026-06-16T00:00:00+00:00",
        error=None if success else "failed",
    )


def test_cli_rejects_invalid_phase() -> None:
    """argparse rejects phases other than before/after."""
    with pytest.raises(SystemExit):
        main(["graphify", "--phase", "middle"])


def test_cli_graphify_success(monkeypatch, capsys) -> None:
    """graphify subcommand prints JSON summary on success."""

    class FakeAgent:
        def run(self, phase: str) -> GraphifyRunResult:
            assert phase == "before"
            return _sample_result()

    monkeypatch.setattr("ex04_agent.cli.handlers_graph.GraphifyRunnerAgent", FakeAgent)
    code = main(["graphify", "--phase", "before"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["success"] is True
    assert payload["phase"] == "before"


def test_cli_graphify_failure(monkeypatch, capsys) -> None:
    """graphify subcommand returns non-zero when run fails."""

    class FakeAgent:
        def run(self, phase: str) -> GraphifyRunResult:
            return replace(_sample_result(success=False), return_code=2)

    monkeypatch.setattr("ex04_agent.cli.handlers_graph.GraphifyRunnerAgent", FakeAgent)
    code = main(["graphify"])
    captured = capsys.readouterr()

    assert code == 1
    assert json.loads(captured.out)["success"] is False
    assert captured.err
