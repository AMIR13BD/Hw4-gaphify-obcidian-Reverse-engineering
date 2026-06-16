"""Tests for ArchitectureDetectionEngine."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.detection.engine import ArchitectureDetectionEngine

POLYGON_FIXTURE = """import turtle

class Polygon(Object):
    def __init__(self, sides):
        self.sides = sides

def calc_polygon_details(sides):
    print("calc")
    return {"sides": sides}

def draw_polygon(details):
    scr = turtle.Screen()
    t = turtle.Turtle()
    t.forward(10)

sides = int(input("sides? "))
print(calc_polygon_details(sides))
draw_polygon({})
"""


def _write(root: Path, name: str, content: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_detection_engine_writes_json_and_markdown(tmp_path: Path, monkeypatch) -> None:
    """Engine writes findings JSON and Markdown using project fixtures."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(
        setup_src.read_text(encoding="utf-8"), encoding="utf-8",
    )
    metrics_dir = project_root / "reports" / "architecture"
    graph_dir = project_root / "artifacts" / "graph" / "before"
    metrics_dir.mkdir(parents=True)
    graph_dir.mkdir(parents=True)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    (metrics_dir / "metrics_before.json").write_text(
        fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    (graph_dir / "graph.json").write_text(
        fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"), encoding="utf-8",
    )
    target = project_root / "data" / "target_repo" / "broken-python"
    _write(target, "polygons/polygons.py", POLYGON_FIXTURE)
    monkeypatch.setattr(
        "ex04_agent.shared.config.find_project_root",
        lambda start=None: project_root,
    )
    from ex04_agent.shared.config import load_config

    summary = ArchitectureDetectionEngine(load_config()).run(phase="before")
    assert summary.finding_count >= 1
    assert Path(summary.json_path).is_file()
    assert Path(summary.markdown_path).is_file()
    payload = json.loads(Path(summary.json_path).read_text(encoding="utf-8"))
    assert "findings" in payload
