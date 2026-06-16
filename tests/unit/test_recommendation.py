"""Tests for recommendation generation."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.recommendation.engine import RecommendationEngine
from ex04_agent.recommendation.mapper import map_finding
from ex04_agent.recommendation.patch_plan import build_patch_plan
from ex04_agent.recommendation.prioritizer import sort_recommendations
from ex04_agent.recommendation.report_writer import RecommendationReportWriter
from ex04_agent.shared.config import load_config


def _finding(fid: str, category: str, severity: str = "medium", status: str = "validated_by_source") -> dict:
    return {
        "id": fid,
        "title": fid,
        "category": category,
        "severity": severity,
        "status": status,
        "confidence": "high",
        "affected_files": ["x.py"],
        "next_validation_steps": ["step"],
        "source_validation": "validated by source",
    }


def test_recommendation_model_serializes() -> None:
    rec = map_finding(_finding("f1", "code_health_blocker"), 1)
    payload = rec.to_dict()
    assert payload["id"].startswith("rec_")
    assert payload["action_type"] == "review_required"


def test_mapper_blocker_to_review_required() -> None:
    rec = map_finding(_finding("f1", "code_health_blocker"), 1)
    assert rec.action_type == "review_required"
    assert rec.priority in {"critical", "high"}


def test_mapper_docs_categories() -> None:
    assert map_finding(_finding("f2", "documentation_hub"), 2).action_type == "docs_only"
    assert map_finding(_finding("f3", "navigation_scope"), 3).action_type == "docs_only"


def test_prioritizer_orders_blockers_before_docs() -> None:
    findings = {"a": _finding("a", "documentation_hub", "low"), "b": _finding("b", "code_health_blocker", "high")}
    recs = [map_finding(findings["a"], 1), map_finding(findings["b"], 2)]
    ordered = sort_recommendations(recs, findings)
    assert ordered[0].finding_id == "b"


def test_patch_plan_groups_items() -> None:
    recs = [map_finding(_finding("a", "hidden_global_state"), 1), map_finding(_finding("b", "documentation_hub"), 2)]
    items, groups = build_patch_plan(recs)
    assert items
    assert "safe_candidates_phase10" in groups or "review_required_items" in groups
    assert "docs_only_items" in groups


def test_recommendation_engine_writes_reports(tmp_path, monkeypatch) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "reports" / "architecture").mkdir(parents=True)
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(setup_src.read_text(encoding="utf-8"), encoding="utf-8")
    findings_path = project_root / "reports" / "architecture" / "findings_before.json"
    findings_path.write_text(json.dumps({"phase": "before", "findings": [_finding("a", "code_health_blocker", "high")]}), encoding="utf-8")
    monkeypatch.setattr("ex04_agent.shared.config.find_project_root", lambda start=None: project_root)
    summary = RecommendationEngine(load_config(), writer=RecommendationReportWriter()).run("before")
    assert summary.recommendation_count == 1
    assert Path(summary.recommendations_json_path).is_file()
    assert Path(summary.patch_plan_markdown_path).is_file()
