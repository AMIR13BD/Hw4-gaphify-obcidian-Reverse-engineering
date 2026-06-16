"""Placeholder for Phase 9 recommendation generation."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.workflow.state import PipelineState, merge_skipped


class RecommendationAgent(BaseAgent):
    """Phase 9 placeholder — no recommendations yet."""

    name = "recommendation"

    def run(self) -> dict[str, str]:
        return {"status": "pending", "message": "Phase 9 not implemented yet."}

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        message = "Recommendation generation is planned for Phase 9."
        recorder.record(
            self.name,
            "skipped",
            inputs={"phase": state.get("phase")},
            outputs={"message": message},
        )
        return merge_skipped(state, self.name, message)
