"""Verify target repository is present for the pipeline."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.workflow.state import PipelineState, merge_completed


class RepositorySetupAgent(BaseAgent):
    """Confirm target repo exists and record metadata."""

    name = "repository_setup"

    def run(self) -> dict[str, str]:
        path = self.config.target_repo_path
        if not path.is_dir():
            msg = f"Target repository not found: {path}"
            raise FileNotFoundError(msg)
        return {"target_repo_path": str(path), "status": "ready"}

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        try:
            info = self.run()
            recorder.record(
                self.name,
                "completed",
                inputs={"phase": state.get("phase")},
                outputs=info,
            )
            return merge_completed(
                state,
                self.name,
                target_repo_path=info["target_repo_path"],
            )
        except Exception as exc:
            recorder.record(
                self.name,
                "failed",
                inputs={"phase": state.get("phase")},
                errors=[str(exc)],
            )
            errors = list(state.get("errors", []))
            errors.append(str(exc))
            return {"errors": errors}
