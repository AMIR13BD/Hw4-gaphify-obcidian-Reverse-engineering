"""Placeholder for Phase 11 test runner."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.workflow.state import PipelineState, merge_skipped


class TestRunnerAgent(BaseAgent):
    """Phase 11 placeholder — does not run target tests yet."""

    name = "test_runner"

    def run(self) -> dict[str, str]:
        return {"status": "pending", "message": "Phase 11 not implemented yet."}

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        message = "Test runner regression checks are planned for Phase 11."
        recorder.record(
            self.name,
            "skipped",
            inputs={"phase": state.get("phase")},
            outputs={"message": message},
        )
        return merge_skipped(state, self.name, message)
