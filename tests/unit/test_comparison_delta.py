"""Tests for comparison loader and delta computation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ex04_agent.comparison.finding_delta import compute_finding_delta
from ex04_agent.comparison.loader import ComparisonLoader
from ex04_agent.comparison.metrics_delta import compute_metrics_delta
from ex04_agent.comparison.recommendation_delta import compute_recommendation_delta
from ex04_agent.shared.config import load_config


def _write_arch(root: Path, phase: str, nodes: int, findings: int) -> None:
    arch = root / "reports" / "architecture"
    arch.mkdir(parents=True, exist_ok=True)
    (arch / f"metrics_{phase}.json").write_text(json.dumps({
        "summary": {"node_count": nodes, "link_count": nodes - 1,
                    "connected_component_count": 7, "low_confidence_link_count": 0, "nodes": []},
        "top_hubs": [], "potential_god_nodes": [], "communities": {"1": 3},
    }), encoding="utf-8")
    flist = [{"id": f"f{i}", "title": f"Finding {i}", "category": "possible_hub",
              "severity": "medium", "affected_files": []} for i in range(findings)]
    (arch / f"findings_{phase}.json").write_text(json.dumps({
        "findings": flist,
    }), encoding="utf-8")
    (arch / f"recommendations_{phase}.json").write_text(json.dumps({
        "recommendations": [{"action_type": "review_required", "priority": "medium",
                             "phase10_patchable": i == 0} for i in range(findings)],
    }), encoding="utf-8")


def test_loader_fails_on_missing_files(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "config").mkdir()
    (project / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project / "config" / "setup.json").write_text(setup.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr("ex04_agent.shared.config.find_project_root", lambda start=None: project)
    with pytest.raises(FileNotFoundError, match="Required comparison files missing"):
        ComparisonLoader(load_config()).load()


def test_metrics_delta_computes_node_link_change() -> None:
    mb = {"summary": {"node_count": 26, "link_count": 20, "connected_component_count": 7,
                      "low_confidence_link_count": 0}, "communities": {"1": 1, "2": 2}}
    ma = {"summary": {"node_count": 25, "link_count": 19, "connected_component_count": 7,
                      "low_confidence_link_count": 0}, "communities": {"1": 1, "2": 2}}
    deltas = compute_metrics_delta(mb, ma)
    nodes = next(m for m in deltas if m.name == "node_count")
    assert nodes.before == 26 and nodes.after == 25 and nodes.delta == -1


def test_finding_delta_detects_reduction() -> None:
    before = {"findings": [{"id": "a", "title": "A", "category": "x", "severity": "low",
                            "affected_files": []}, {"id": "b", "title": "B", "category": "y",
                            "severity": "high", "affected_files": []}]}
    after = {"findings": [{"id": "b", "title": "B", "category": "y", "severity": "high",
                           "affected_files": []}]}
    delta = compute_finding_delta(before, after)
    assert delta.before_count == 2 and delta.after_count == 1
    assert "A" in delta.resolved_or_removed[0]


def test_recommendation_delta_detects_reduction() -> None:
    before = {"recommendations": [{"action_type": "review_required", "priority": "high",
                                     "phase10_patchable": True}] * 19}
    after = {"recommendations": [{"action_type": "docs_only", "priority": "low",
                                  "phase10_patchable": False}] * 8}
    delta = compute_recommendation_delta(before, after)
    assert delta.before_count == 19 and delta.after_count == 8
