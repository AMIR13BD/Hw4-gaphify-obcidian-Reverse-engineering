"""Tests for SourceScanner and source/graph detectors."""

from __future__ import annotations

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


def _write(root: Path, name: str, content: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_source_scanner_detects_responsibilities(tmp_path: Path) -> None:
    """Scanner tags mixed responsibilities in fixture file."""
    _write(tmp_path, "polygons/polygons.py", POLYGON_FIXTURE)
    scan = SourceScanner(tmp_path).scan_file("polygons/polygons.py")
    assert scan is not None
    assert "class_definition" in scan.responsibilities
    assert "drawing" in scan.responsibilities
    assert "top_level_execution" in scan.responsibilities


def test_source_scanner_detects_syntax_errors(tmp_path: Path) -> None:
    """Scanner reports syntax validation failures."""
    _write(tmp_path, "mathsquiz/bad.py", SYNTAX_ERROR_FIXTURE)
    scan = SourceScanner(tmp_path).scan_file("mathsquiz/bad.py")
    assert scan is not None
    assert scan.syntax_valid is False
    assert scan.syntax_error


def test_mixed_responsibility_detector(tmp_path: Path) -> None:
    """MixedResponsibilityDetector emits finding for fixture polygons file."""
    _write(tmp_path, "polygons/polygons.py", POLYGON_FIXTURE)
    findings = detect_mixed_responsibility(SourceScanner(tmp_path))
    assert any(item.detector == "MixedResponsibilityDetector" for item in findings)


def test_top_level_side_effect_detector(tmp_path: Path) -> None:
    """TopLevelSideEffectDetector flags module-level execution."""
    _write(tmp_path, "polygons/polygons.py", POLYGON_FIXTURE)
    findings = detect_top_level_side_effects(SourceScanner(tmp_path))
    assert findings


def test_hidden_global_detector(tmp_path: Path) -> None:
    """HiddenGlobalStateDetector finds score/global mismatch."""
    _write(tmp_path, "mathsquiz/mathsquiz-step2.py", HIDDEN_GLOBAL_FIXTURE)
    findings = detect_hidden_globals(SourceScanner(tmp_path))
    assert any("score" in item.title for item in findings)


def test_execution_blocker_detector(tmp_path: Path) -> None:
    """ExecutionBlockerDetector reports syntax blockers."""
    _write(tmp_path, "mathsquiz/mathsquiz.py", SYNTAX_ERROR_FIXTURE)
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
        _write(tmp_path, name, "# step\n")
    findings = detect_duplicate_evolution(SourceScanner(tmp_path), tmp_path)
    assert findings
