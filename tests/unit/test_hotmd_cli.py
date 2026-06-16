"""Tests for hotmd CLI command."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_agent.cli.parser import build_parser
from ex04_agent.main import main


def _setup_project(tmp_path: Path, monkeypatch) -> Path:
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
    return project_root


def test_cli_hotmd_rejects_invalid_phase() -> None:
    """Parser only accepts before/after phases."""
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["hotmd", "--phase", "middle"])


def test_cli_hotmd_with_fixture(tmp_path, monkeypatch) -> None:
    """Hotmd subcommand writes dynamic hot.md from fixtures."""
    project_root = _setup_project(tmp_path, monkeypatch)
    phase_dir = project_root / "artifacts" / "graph" / "before"
    phase_dir.mkdir(parents=True)
    metrics_dir = project_root / "reports" / "architecture"
    metrics_dir.mkdir(parents=True)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    (phase_dir / "graph.json").write_text(
        fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (metrics_dir / "metrics_before.json").write_text(
        fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    exit_code = main(["hotmd", "--phase", "before"])
    hot_path = project_root / "obsidian" / "hot.md"

    assert exit_code == 0
    assert hot_path.is_file()
    assert "Dynamic Investigation List" in hot_path.read_text(encoding="utf-8")


def test_cli_hotmd_missing_metrics_fails(tmp_path, monkeypatch) -> None:
    """Hotmd returns non-zero when metrics file is missing."""
    _setup_project(tmp_path, monkeypatch)
    assert main(["hotmd", "--phase", "before"]) == 1
