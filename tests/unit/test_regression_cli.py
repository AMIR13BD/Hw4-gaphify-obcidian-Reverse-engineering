"""Tests for regression CLI and TestRunnerAgent."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from regression_helpers import make_regression_result

from ex04_agent.cli.parser import build_parser
from ex04_agent.main import main


def test_cli_test_rejects_invalid_phase() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["test", "--phase", "invalid"])


def test_cli_test_prints_summary(monkeypatch, capsys) -> None:
    mock_result = make_regression_result()
    monkeypatch.setattr(
        "ex04_agent.cli.handlers_workflow.TestRunnerAgent",
        lambda *a, **kw: MagicMock(run=MagicMock(return_value=mock_result)),
    )
    code = main(["test", "--phase", "before"])
    assert code == 0
    out = capsys.readouterr().out
    assert "compile_status" in out


def test_test_runner_agent_completes_in_pipeline(tmp_path: Path) -> None:
    from ex04_agent.agent_trace.recorder import AgentTraceRecorder
    from ex04_agent.agents.test_runner import TestRunnerAgent
    from ex04_agent.shared.config import load_config
    from ex04_agent.workflow.state import initial_state

    config = load_config()
    mock_engine = MagicMock()
    mock_engine.run.return_value = make_regression_result()
    agent = TestRunnerAgent(config, engine=mock_engine)
    state = initial_state(config, phase="before", dry_run=True)
    recorder = AgentTraceRecorder(tmp_path, "test")
    updates = agent.run_pipeline(state, recorder)
    assert "test_runner" in updates.get("completed_agents", [])
