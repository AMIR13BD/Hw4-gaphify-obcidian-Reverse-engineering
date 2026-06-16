"""Architecture bug detection agent."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.detection.engine import ArchitectureDetectionEngine
from ex04_agent.detection.report_writer import FindingsSummary
from ex04_agent.workflow.state import PipelineState, merge_completed


class ArchitectureBugAgent(BaseAgent):
    """Run deterministic architecture finding detectors."""

    name = "architecture_bug"

    def __init__(self, config=None, engine: ArchitectureDetectionEngine | None = None) -> None:
        super().__init__(config)
        self._engine = engine or ArchitectureDetectionEngine(self.config)

    def run(self, phase: str = "before") -> FindingsSummary:
        return self._engine.run(phase=phase)

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        phase = str(state.get("phase", "before"))
        try:
            summary = self.run(phase=phase)
            recorder.record(
                self.name,
                "completed",
                inputs={"phase": phase, "metrics_path": state.get("metrics_path")},
                outputs=summary.to_dict(),
            )
            return merge_completed(
                state,
                self.name,
                findings_path=summary.json_path,
                finding_count=summary.finding_count,
                findings=[],
            )
        except Exception as exc:
            recorder.record(self.name, "failed", errors=[str(exc)])
            errors = list(state.get("errors", []))
            errors.append(str(exc))
            return {"errors": errors}
