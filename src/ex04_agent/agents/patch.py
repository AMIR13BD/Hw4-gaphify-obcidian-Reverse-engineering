"""Placeholder for Phase 10 safe patching."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.workflow.state import PipelineState, merge_skipped


class PatchAgent(BaseAgent):
    """Always skipped in Phase 7 — never edits the target repo."""

    name = "patch"

    def run(self) -> dict[str, str]:
        return {"status": "skipped", "message": "Patching disabled."}

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        message = "Patching disabled in dry-run and planned for Phase 10."
        recorder.record(
            self.name,
            "skipped",
            inputs={"dry_run": state.get("dry_run"), "allow_patches": self.config.allow_patches},
            outputs={"message": message},
        )
        return merge_skipped(state, self.name, message)
