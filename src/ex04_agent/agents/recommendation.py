"""Recommendation generation agent."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.recommendation.engine import RecommendationEngine
from ex04_agent.recommendation.report_writer import RecommendationSummary
from ex04_agent.workflow.state import PipelineState, merge_completed


class RecommendationAgent(BaseAgent):
    """Run deterministic recommendation mapping from findings."""

    name = "recommendation"

    def __init__(self, config=None, engine: RecommendationEngine | None = None) -> None:
        super().__init__(config)
        self._engine = engine or RecommendationEngine(self.config)

    def run(self, phase: str = "before") -> RecommendationSummary:
        return self._engine.run(phase=phase)

    def run_pipeline(self, state: PipelineState, recorder: AgentTraceRecorder) -> dict[str, Any]:
        phase = str(state.get("phase", "before"))
        try:
            summary = self.run(phase=phase)
            recorder.record(self.name, "completed", inputs={"phase": phase, "findings_path": state.get("findings_path")}, outputs=summary.to_dict())
            return merge_completed(
                state,
                self.name,
                recommendations_path=summary.recommendations_json_path,
                recommendation_count=summary.recommendation_count,
                patch_plan_path=summary.patch_plan_json_path,
                recommendations=[],
            )
        except Exception as exc:
            recorder.record(self.name, "failed", errors=[str(exc)])
            errors = list(state.get("errors", []))
            errors.append(str(exc))
            return {"errors": errors}
