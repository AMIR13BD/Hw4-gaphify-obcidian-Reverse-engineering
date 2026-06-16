"""Shared fixtures for after-phase test modules."""

from __future__ import annotations

import json
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


def write_comparison_arch(root: Path) -> None:
    for phase, nodes, findings in (("before", 26, 19), ("after", 25, 8)):
        arch = root / "reports" / "architecture"
        arch.mkdir(parents=True, exist_ok=True)
        (arch / f"metrics_{phase}.json").write_text(json.dumps({
            "summary": {"node_count": nodes, "link_count": nodes - 6,
                        "connected_component_count": 7, "low_confidence_link_count": 0, "nodes": []},
            "top_hubs": [{"label": "hub.py", "id": "h"}], "potential_god_nodes": [],
            "communities": {"1": 3},
        }), encoding="utf-8")
        (arch / f"findings_{phase}.json").write_text(json.dumps({
            "findings": [{"id": f"f{i}_{phase}", "title": f"F{i}", "category": "possible_hub",
                          "severity": "medium", "affected_files": []} for i in range(findings)],
        }), encoding="utf-8")
        (arch / f"recommendations_{phase}.json").write_text(json.dumps({
            "recommendations": [{"action_type": "review_required", "priority": "medium",
                                 "phase10_patchable": False} for _ in range(findings)],
        }), encoding="utf-8")
