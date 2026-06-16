"""Tests for GraphifyRunnerAgent wrapper."""

from ex04_agent.agents.graphify_runner import GraphifyRunnerAgent
from ex04_agent.graph.graphify_runner import GraphifyRunResult


def test_agent_delegates_to_runner(monkeypatch) -> None:
    """Agent run forwards to GraphifyRunner service."""

    class FakeRunner:
        def run(self, phase: str) -> GraphifyRunResult:
            assert phase == "after"
            return GraphifyRunResult(
                success=True,
                phase=phase,
                command=("graphify", "update", "."),
                cwd="cwd",
                return_code=0,
                graphify_cli="graphify",
                graphify_cli_path="graphify",
                target_repo_path="cwd",
                stdout="",
                stderr="",
                copied_artifacts=("graph.json",),
                missing_required_artifacts=(),
                missing_optional_artifacts=(),
                artifact_dest_dir="dest",
                log_path="log",
                metadata_path="meta",
                timestamp="t",
            )

    agent = GraphifyRunnerAgent(runner=FakeRunner())
    result = agent.run("after")
    assert result.phase == "after"
    assert result.success is True
