"""Phase 11 regression test runner agent."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.testing.engine import RegressionEngine
from ex04_agent.testing.model import RegressionResult
from ex04_agent.workflow.state import PipelineState, merge_completed


class TestRunnerAgent(BaseAgent):
    """Run regression validation after Phase 10 patches."""

    name = "test_runner"

    def __init__(self, config=None, engine: RegressionEngine | None = None) -> None:
        super().__init__(config)
        self._engine = engine or RegressionEngine(self.config)

    def run(self, phase: str = "before") -> RegressionResult:
        return self._engine.run(phase=phase)

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        phase = str(state.get("phase", "before"))
        try:
            result = self.run(phase=phase)
            recorder.record(
                self.name, "completed",
                inputs={"phase": phase},
                outputs={
                    "compile_status": result.compile_status,
                    "project_test_status": result.project_test_status,
                    "failed_files_count": len(result.failed_files),
                },
            )
            return merge_completed(
                state, self.name,
                regression_path=result.output_paths.get("json", ""),
                regression_failed_files=list(result.failed_files),
            )
        except Exception as exc:
            recorder.record(self.name, "failed", errors=[str(exc)])
            errors = list(state.get("errors", []))
            errors.append(str(exc))
            return {"errors": errors}
