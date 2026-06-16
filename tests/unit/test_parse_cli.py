"""Tests for parse CLI command."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.main import main


def test_cli_parse_with_fixture(tmp_path, monkeypatch) -> None:
    """Parse subcommand writes metrics JSON from a fixture graph."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(
        setup_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    graph_dir = project_root / "artifacts" / "graph" / "before"
    graph_dir.mkdir(parents=True)
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "graph_sample.json"
    (graph_dir / "graph.json").write_text(fixture.read_text(encoding="utf-8"), encoding="utf-8")

    monkeypatch.setattr(
        "ex04_agent.shared.config.find_project_root",
        lambda start=None: project_root,
    )

    exit_code = main(["parse", "--phase", "before"])
    output = project_root / "reports" / "architecture" / "metrics_before.json"

    assert exit_code == 0
    assert output.is_file()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["phase"] == "before"
    assert payload["summary"]["node_count"] == 5


def test_cli_parse_failure_on_missing_graph(tmp_path, monkeypatch) -> None:
    """Parse returns non-zero when graph.json is missing."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(
        setup_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "ex04_agent.shared.config.find_project_root",
        lambda start=None: project_root,
    )

    exit_code = main(["parse", "--phase", "before"])
    assert exit_code == 1
