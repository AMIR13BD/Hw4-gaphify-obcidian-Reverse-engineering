"""Shared fixtures for after-phase test modules."""

from __future__ import annotations

from pathlib import Path


def setup_after_project(tmp_path: Path, monkeypatch) -> Path:
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
    out = target / "graphify-out"
    out.mkdir()
    for name in ("graph.json", "graph.html", "GRAPH_REPORT.md"):
        (out / name).write_text("{}" if name.endswith(".json") else "# x", encoding="utf-8")
    monkeypatch.setattr("ex04_agent.shared.config.find_project_root", lambda start=None: project_root)
    return project_root
