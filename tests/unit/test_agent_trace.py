"""Tests for agent trace recorder."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.agent_trace.recorder import AgentTraceRecorder


def test_agent_trace_recorder_writes_files(tmp_path: Path) -> None:
    """Recorder writes per-agent and combined trace files."""
    recorder = AgentTraceRecorder(tmp_path, "run123")
    recorder.record(
        "repository_setup",
        "completed",
        inputs={"phase": "before"},
        outputs={"status": "ready"},
    )
    combined = recorder.write_combined()
    assert combined.is_file()
    assert len(list(recorder.run_dir.glob("*.json"))) == 2
