"""Tests for pipeline state helpers."""

from __future__ import annotations

from ex04_agent.shared.config import load_config
from ex04_agent.workflow.state import initial_state, merge_completed, merge_skipped


def test_initial_state_has_required_fields() -> None:
    """Pipeline state initializes with expected defaults."""
    config = load_config()
    state = initial_state(config, phase="before", dry_run=True)
    assert state["phase"] == "before"
    assert state["dry_run"] is True
    assert state["completed_agents"] == []
    assert state["skipped_agents"] == []
    assert state["iteration"] == 1
    assert state["trace_run_id"]


def test_merge_completed_and_skipped() -> None:
    """State merge helpers append agent names."""
    base = {"completed_agents": ["a"], "skipped_agents": []}
    done = merge_completed(base, "b", metrics_path="/tmp/m.json")
    skipped = merge_skipped(base, "patch", "disabled")
    assert done["completed_agents"] == ["a", "b"]
    assert done["metrics_path"] == "/tmp/m.json"
    assert "patch:disabled" in skipped["skipped_agents"][0]
