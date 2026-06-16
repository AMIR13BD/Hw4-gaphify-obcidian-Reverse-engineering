"""Tests for PatchEngine, CLI, and PatchAgent pipeline integration."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ex04_agent.cli.parser import build_parser
from ex04_agent.main import main
from ex04_agent.patching.engine import PatchEngine


def _setup_project(tmp_path: Path, plan: dict) -> Path:
    """Create minimal project layout with a given patch plan."""
    project_root = tmp_path / "project"
    (project_root / "config").mkdir(parents=True)
    (project_root / "reports" / "architecture").mkdir(parents=True)
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(
        setup_src.read_text(encoding="utf-8"), encoding="utf-8",
    )
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (project_root / "reports" / "architecture" / "patch_plan_before.json").write_text(
        json.dumps(plan), encoding="utf-8",
    )
    return project_root


def test_patch_engine_skips_docs_only(tmp_path: Path, monkeypatch) -> None:
    """Engine skips items in docs-only / deferred groups."""
    plan = {
        "phase": "before",
        "groups": {
            "docs_only_items": [{"recommendation_id": "r1", "finding_id": "f1", "affected_files": ["README.md"], "action_type": "docs_only"}],
            "safe_candidates_phase10": [],
        },
    }
    project_root = _setup_project(tmp_path, plan)
    monkeypatch.setattr("ex04_agent.shared.config.find_project_root", lambda start=None: project_root)
    from ex04_agent.shared.config import load_config
    summary = PatchEngine(load_config()).run(phase="before", allow_patches=False)
    assert summary.applied_count == 0


def test_patch_engine_skips_non_whitelist(tmp_path: Path, monkeypatch) -> None:
    """Engine skips files not in the whitelist."""
    plan = {
        "phase": "before",
        "groups": {"safe_candidates_phase10": [{"recommendation_id": "r1", "finding_id": "f1", "affected_files": ["other/not_whitelisted.py"], "action_type": "review_required"}]},
    }
    project_root = _setup_project(tmp_path, plan)
    monkeypatch.setattr("ex04_agent.shared.config.find_project_root", lambda start=None: project_root)
    from ex04_agent.shared.config import load_config
    summary = PatchEngine(load_config()).run(phase="before", allow_patches=False)
    assert summary.applied_count == 0
    assert summary.skipped_count >= 1


def test_cli_patch_rejects_invalid_phase() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["patch", "--phase", "invalid"])


def test_cli_patch_dry_run_does_not_write(monkeypatch) -> None:
    from ex04_agent.patching.report_writer import PatchSummary
    mock_summary = PatchSummary(
        allow_patches=False, changed_files=0, applied_count=0,
        skipped_count=2, failed_count=0, rolled_back_count=0,
        validation_status="pass", json_path="out.json", markdown_path="out.md",
    )
    monkeypatch.setattr(
        "ex04_agent.agents.patch.PatchAgent",
        lambda *a, **kw: MagicMock(run=MagicMock(return_value=mock_summary)),
    )
    code = main(["patch", "--phase", "before"])
    assert code == 0


def test_patch_agent_skipped_when_allow_patches_false(tmp_path: Path) -> None:
    from ex04_agent.agent_trace.recorder import AgentTraceRecorder
    from ex04_agent.agents.patch import PatchAgent
    from ex04_agent.shared.config import load_config
    from ex04_agent.workflow.state import initial_state
    config = load_config()
    state = initial_state(config, phase="before", dry_run=True)
    recorder = AgentTraceRecorder(tmp_path, "test")
    updates = PatchAgent(config).run_pipeline(state, recorder)
    assert "skipped_agents" in updates
    assert any("patch:" in s for s in updates["skipped_agents"])
