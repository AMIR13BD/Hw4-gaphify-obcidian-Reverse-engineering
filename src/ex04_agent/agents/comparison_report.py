"""Placeholder for Phase 13 before/after comparison."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.workflow.state import PipelineState, merge_skipped


class ComparisonReportAgent(BaseAgent):
    """Phase 13 placeholder — no comparison report yet."""

    name = "comparison_report"

    def run(self) -> dict[str, str]:
        return {"status": "pending", "message": "Phase 13 not implemented yet."}

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        message = "Before/after comparison is planned for Phase 13."
        recorder.record(
            self.name,
            "skipped",
            inputs={"phase": state.get("phase")},
            outputs={"message": message},
        )
        return merge_skipped(state, self.name, message)
