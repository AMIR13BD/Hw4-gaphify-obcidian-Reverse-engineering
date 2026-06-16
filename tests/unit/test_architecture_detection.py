"""Tests for architecture detection."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.detection.detectors_graph import detect_low_confidence_edges
from ex04_agent.detection.detectors_source import (
    detect_hidden_globals,
    detect_mixed_responsibility,
    detect_top_level_side_effects,
)
from ex04_agent.detection.detectors_source_extra import (
    detect_duplicate_evolution,
    detect_execution_blockers,
)
from ex04_agent.detection.engine import ArchitectureDetectionEngine
from ex04_agent.detection.finding import ArchitectureFinding, EvidenceItem
from ex04_agent.detection.source_scanner import SourceScanner

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

HIDDEN_GLOBAL_FIXTURE = """
def print_final_scores(final_score):
    print("You scored", score, "points")
"""

SYNTAX_ERROR_FIXTURE = '''
print "bad"
if answer = 5:
    pass
'''


def write_fixture(root: Path, name: str, content: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_finding_serializes_to_json() -> None:
    """ArchitectureFinding converts to JSON-friendly dict."""
    finding = ArchitectureFinding(
        id="x",
        title="t",
        detector="d",
        category="c",
        severity="low",
        confidence="medium",
        status="candidate",
        observation="obs",
        relation="rel",
        confidence_reason="reason",
        context="ctx",
        affected_nodes=(),
        affected_files=("a.py",),
        evidence=(EvidenceItem("source", "a.py", 1, 2, "detail"),),
        source_validation="pending",
        next_validation_steps=("step",),
    )
    payload = finding.to_dict()
    assert payload["id"] == "x"
    assert payload["evidence"][0]["kind"] == "source"


def test_source_scanner_detects_responsibilities(tmp_path: Path) -> None:
    """Scanner tags mixed responsibilities in fixture file."""
    rel = "polygons/polygons.py"
    write_fixture(tmp_path, rel, POLYGON_FIXTURE)
    scan = SourceScanner(tmp_path).scan_file(rel)
    assert scan is not None
    assert "class_definition" in scan.responsibilities
    assert "drawing" in scan.responsibilities
    assert "top_level_execution" in scan.responsibilities


def test_source_scanner_detects_syntax_errors(tmp_path: Path) -> None:
    """Scanner reports syntax validation failures."""
    rel = "mathsquiz/bad.py"
    write_fixture(tmp_path, rel, SYNTAX_ERROR_FIXTURE)
    scan = SourceScanner(tmp_path).scan_file(rel)
    assert scan is not None
    assert scan.syntax_valid is False
    assert scan.syntax_error


def test_mixed_responsibility_detector(tmp_path: Path) -> None:
    """MixedResponsibilityDetector emits finding for fixture polygons file."""
    rel = "polygons/polygons.py"
    write_fixture(tmp_path, rel, POLYGON_FIXTURE)
    findings = detect_mixed_responsibility(SourceScanner(tmp_path))
    assert any(item.detector == "MixedResponsibilityDetector" for item in findings)


def test_top_level_side_effect_detector(tmp_path: Path) -> None:
    """TopLevelSideEffectDetector flags module-level execution."""
    rel = "polygons/polygons.py"
    write_fixture(tmp_path, rel, POLYGON_FIXTURE)
    findings = detect_top_level_side_effects(SourceScanner(tmp_path))
    assert findings


def test_hidden_global_detector(tmp_path: Path) -> None:
    """HiddenGlobalStateDetector finds score/global mismatch."""
    rel = "mathsquiz/mathsquiz-step2.py"
    write_fixture(tmp_path, rel, HIDDEN_GLOBAL_FIXTURE)
    findings = detect_hidden_globals(SourceScanner(tmp_path))
    assert any("score" in item.title for item in findings)


def test_execution_blocker_detector(tmp_path: Path) -> None:
    """ExecutionBlockerDetector reports syntax blockers."""
    rel = "mathsquiz/mathsquiz.py"
    write_fixture(tmp_path, rel, SYNTAX_ERROR_FIXTURE)
    findings = detect_execution_blockers(SourceScanner(tmp_path))
    assert any(item.category == "code_health_blocker" for item in findings)


def test_low_confidence_detector_no_fake_findings() -> None:
    """LowConfidenceEdgeDetector returns empty list when no low-confidence links."""
    assert detect_low_confidence_edges({"low_confidence_links": []}) == []


def test_duplicate_evolution_detector(tmp_path: Path) -> None:
    """DuplicateEvolutionDetector finds step-style filenames."""
    for name in (
        "mathsquiz/mathsquiz-step1.py",
        "mathsquiz/mathsquiz-step2.py",
        "mathsquiz/mathsquiz-step3.py",
    ):
        write_fixture(tmp_path, name, "# step\n")
    findings = detect_duplicate_evolution(SourceScanner(tmp_path), tmp_path)
    assert findings


def test_detection_engine_writes_json_and_markdown(tmp_path, monkeypatch) -> None:
    """Engine writes findings JSON and Markdown using project fixtures."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(
        setup_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    metrics_dir = project_root / "reports" / "architecture"
    graph_dir = project_root / "artifacts" / "graph" / "before"
    metrics_dir.mkdir(parents=True)
    graph_dir.mkdir(parents=True)
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    (metrics_dir / "metrics_before.json").write_text(
        fixtures.joinpath("metrics_sample.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (graph_dir / "graph.json").write_text(
        fixtures.joinpath("graph_sample.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    target = project_root / "data" / "target_repo" / "broken-python"
    write_fixture(target, "polygons/polygons.py", POLYGON_FIXTURE)
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
