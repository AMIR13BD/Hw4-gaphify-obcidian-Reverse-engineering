"""Tests for pipeline agents."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.graph_interpreter import GraphInterpreterAgent
from ex04_agent.agents.patch import PatchAgent
from ex04_agent.agents.repository_setup import RepositorySetupAgent
from ex04_agent.agents.supervisor import SupervisorAgent
from ex04_agent.shared.config import load_config
from ex04_agent.workflow.state import initial_state


@pytest.fixture
def recorder(tmp_path: Path) -> AgentTraceRecorder:
    return AgentTraceRecorder(tmp_path, "test_run")


def test_repository_setup_detects_target_repo(recorder) -> None:
    """Repository setup succeeds when target repo exists."""
    config = load_config()
    state = initial_state(config, phase="before", dry_run=True)
    updates = RepositorySetupAgent(config).run_pipeline(state, recorder)
    assert "repository_setup" in updates["completed_agents"]


def test_graph_interpreter_writes_story(tmp_path, recorder) -> None:
    """Graph interpreter writes story markdown from metrics fixture."""
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
    metrics_dir.mkdir(parents=True)
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "metrics_sample.json"
    (metrics_dir / "metrics_before.json").write_text(
        fixture.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    import ex04_agent.shared.config as config_mod

    original = config_mod.find_project_root
    config_mod.find_project_root = lambda start=None: project_root
    try:
        config = load_config(project_root / "config" / "setup.json")
        state = initial_state(config, phase="before", dry_run=True)
        state["metrics_path"] = str(metrics_dir / "metrics_before.json")
        updates = GraphInterpreterAgent(config).run_pipeline(state, recorder)
        story = Path(updates["story_path"])
        assert story.is_file()
        text = story.read_text(encoding="utf-8")
        assert "graph suggests" in text
        assert "validation in source" in text
    finally:
        config_mod.find_project_root = original


def test_placeholder_agents_return_skipped(recorder) -> None:
    """Future-phase agents record skipped status without fake outputs."""
    config = load_config()
    state = initial_state(config, phase="before", dry_run=True)

    updates = PatchAgent(config).run_pipeline(state, recorder)
    assert updates["skipped_agents"]
    assert SupervisorAgent(config).run_pipeline(state, recorder)["stop_reason"] == "dry_run_completed"
