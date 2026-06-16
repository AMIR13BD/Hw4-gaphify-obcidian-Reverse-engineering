"""Phase 10 safe patch agent."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.patching.engine import PatchEngine
from ex04_agent.patching.report_writer import PatchSummary
from ex04_agent.workflow.state import PipelineState, merge_completed, merge_skipped


class PatchAgent(BaseAgent):
    """Apply safe deterministic patches when allow_patches is enabled."""

    name = "patch"

    def __init__(self, config=None, engine: PatchEngine | None = None) -> None:
        super().__init__(config)
        self._engine = engine or PatchEngine(self.config)

    def run(self, *, phase: str = "before", allow_patches: bool = False) -> PatchSummary:
        return self._engine.run(phase=phase, allow_patches=allow_patches)

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        phase = str(state.get("phase", "before"))
        allow = bool(self.config.allow_patches) and not bool(state.get("dry_run", True))

        if not allow:
            msg = "Patching disabled in dry-run and planned for Phase 10."
            recorder.record(
                self.name, "skipped",
                inputs={"dry_run": state.get("dry_run"), "allow_patches": self.config.allow_patches},
                outputs={"message": msg},
            )
            return merge_skipped(state, self.name, msg)

        try:
            summary = self.run(phase=phase, allow_patches=True)
            recorder.record(
                self.name, "completed",
                inputs={"phase": phase, "allow_patches": True},
                outputs=summary.to_dict(),
            )
            return merge_completed(
                state, self.name,
                patch_result_path=summary.json_path,
                patch_applied_count=summary.applied_count,
            )
        except Exception as exc:
            recorder.record(self.name, "failed", errors=[str(exc)])
            errors = list(state.get("errors", []))
            errors.append(str(exc))
            return {"errors": errors}
