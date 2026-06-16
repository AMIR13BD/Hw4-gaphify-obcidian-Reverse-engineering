"""Tests for LangGraph workflow compilation."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.shared.config import load_config
from ex04_agent.workflow.graph import NODE_ORDER, LangGraphWorkflow


def test_langgraph_workflow_compiles(tmp_path: Path) -> None:
    """Workflow graph compiles with all expected nodes."""
    config = load_config()
    workflow = LangGraphWorkflow(config)
    rec = AgentTraceRecorder(tmp_path, "compile_test")
    compiled = workflow.compile(rec)
    assert compiled is not None
    assert len(NODE_ORDER) == 12
