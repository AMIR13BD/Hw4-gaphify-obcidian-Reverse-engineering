"""Tests for GraphifyRunner command execution."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ex04_agent.graph.graphify_runner import GraphifyRunner
from ex04_agent.shared.config import load_config


def _project_setup(tmp_path: Path, monkeypatch) -> tuple[Path, object]:
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
    out = target / "graphify-out"
    out.mkdir()
    (out / "graph.json").write_text("{}", encoding="utf-8")
    (out / "graph.html").write_text("<html></html>", encoding="utf-8")
    (out / "GRAPH_REPORT.md").write_text("# report", encoding="utf-8")

    monkeypatch.setattr(
        "ex04_agent.shared.config.find_project_root",
        lambda start=None: project_root,
    )
    config = load_config(project_root / "config" / "setup.json")
    return project_root, config


def test_graphify_runner_builds_expected_command(tmp_path, monkeypatch) -> None:
    """Runner uses AST-only graphify update in target repo cwd."""
    _, config = _project_setup(tmp_path, monkeypatch)
    runner = GraphifyRunner(config)
    assert runner.build_command() == ["graphify", "update", "."]


def test_graphify_runner_executes_and_collects(tmp_path, monkeypatch) -> None:
    """Successful subprocess run copies artifacts and writes reports."""
    project_root, config = _project_setup(tmp_path, monkeypatch)

    def fake_run(command, cwd, capture_output, text, check):  # noqa: ANN001
        assert command == ["graphify", "update", "."]
        assert cwd == config.target_repo_path
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    runner = GraphifyRunner(config, subprocess_runner=fake_run)
    result = runner.run("before")

    assert result.success is True
    assert result.return_code == 0
    assert "graph.json" in result.copied_artifacts
    assert Path(result.log_path).is_file()
    assert Path(result.metadata_path).is_file()
    assert (project_root / "artifacts" / "graph" / "before" / "graph.json").is_file()


def test_graphify_runner_invalid_phase(tmp_path, monkeypatch) -> None:
    """Invalid phase raises before subprocess execution."""
    _, config = _project_setup(tmp_path, monkeypatch)
    runner = GraphifyRunner(config)

    with pytest.raises(ValueError, match="Invalid phase"):
        runner.run("middle")


def test_graphify_runner_failure_return_code(tmp_path, monkeypatch) -> None:
    """Non-zero Graphify exit marks run as failed."""
    _, config = _project_setup(tmp_path, monkeypatch)

    def fail_run(command, cwd, capture_output, text, check):  # noqa: ANN001
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="boom")

    result = GraphifyRunner(config, subprocess_runner=fail_run).run("before")
    assert result.success is False
    assert result.error is not None
