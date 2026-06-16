"""Before/after comparison report agent."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.comparison.engine import ComparisonEngine, ComparisonSummary
from ex04_agent.comparison.loader import ComparisonLoader
from ex04_agent.workflow.state import PipelineState, merge_completed, merge_skipped


class ComparisonReportAgent(BaseAgent):
    """Run deterministic before/after comparison when artifacts exist."""

    name = "comparison_report"

    def __init__(self, config=None, engine: ComparisonEngine | None = None) -> None:
        super().__init__(config)
        self._engine = engine or ComparisonEngine(self.config)
        self._loader = ComparisonLoader(self.config)

    def run(self, before_phase: str = "before", after_phase: str = "after") -> ComparisonSummary:
        result = self._engine.run(before_phase=before_phase, after_phase=after_phase)
        return self._engine.summary(result)

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        phase = str(state.get("phase", "before"))
        if phase != "after":
            msg = "Comparison requires after-phase pipeline; before-only run skipped."
            recorder.record(self.name, "skipped", inputs={"phase": phase}, outputs={"message": msg})
            return merge_skipped(state, self.name, msg)
        if not self._loader.comparison_ready():
            msg = "Before/after artifacts missing; cannot compare before/after."
            recorder.record(self.name, "skipped", inputs={"phase": phase}, outputs={"message": msg})
            return merge_skipped(state, self.name, msg)
        try:
            summary = self.run(before_phase="before", after_phase="after")
            recorder.record(
                self.name, "completed",
                inputs={"phase": phase},
                outputs=summary.to_dict(),
            )
            return merge_completed(
                state, self.name,
                comparison_path=summary.json_path,
                comparison=dict(summary.to_dict()),
            )
        except Exception as exc:
            recorder.record(self.name, "failed", errors=[str(exc)])
            errors = list(state.get("errors", []))
            errors.append(str(exc))
            return {"errors": errors}
