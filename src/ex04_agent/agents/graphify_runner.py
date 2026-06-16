"""Thin agent wrapper around the Graphify runner service."""

from __future__ import annotations

from ex04_agent.agents.base import BaseAgent
from ex04_agent.graph.graphify_run_result import GraphifyRunResult
from ex04_agent.graph.graphify_runner import GraphifyRunner


class GraphifyRunnerAgent(BaseAgent):
    """Run Graphify and collect artifacts for a pipeline phase."""

    name = "graphify_runner"

    def __init__(self, config=None, runner: GraphifyRunner | None = None) -> None:
        super().__init__(config)
        self._runner = runner or GraphifyRunner(self.config)

    def run(self, phase: str = "before") -> GraphifyRunResult:
        """Execute Graphify for the given phase."""
        return self._runner.run(phase)
