"""Supervisor agent — pipeline stop logic."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.workflow.state import PipelineState, merge_completed


class SupervisorAgent(BaseAgent):
    """Set final stop reason after pipeline stages complete."""

    name = "supervisor"

    def run(self, dry_run: bool = True) -> dict[str, str]:
        reason = "dry_run_completed" if dry_run else "pipeline_completed"
        return {"stop_reason": reason}

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        dry_run = bool(state.get("dry_run", True))
        reason = "dry_run_completed" if dry_run else "pipeline_completed"
        recorder.record(
            self.name,
            "completed",
            inputs={
                "iteration": state.get("iteration"),
                "errors": state.get("errors", []),
            },
            outputs={"stop_reason": reason},
        )
        return merge_completed(state, self.name, stop_reason=reason)
