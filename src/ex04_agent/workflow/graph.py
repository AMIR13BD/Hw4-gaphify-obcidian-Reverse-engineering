"""LangGraph workflow assembly and execution."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.shared.config import AppConfig
from ex04_agent.workflow.pipeline_nodes import PipelineAgents
from ex04_agent.workflow.result import PipelineResult
from ex04_agent.workflow.state import PipelineState, initial_state

NODE_ORDER = (
    "repository_setup",
    "graphify_runner",
    "graph_parser",
    "obsidian_vault",
    "dynamic_hotmd",
    "graph_interpreter",
    "architecture_bug",
    "recommendation",
    "patch",
    "test_runner",
    "comparison_report",
    "supervisor",
)


class LangGraphWorkflow:
    """Linear multi-agent pipeline using LangGraph."""

    def __init__(
        self,
        config: AppConfig,
        agents: PipelineAgents | None = None,
    ) -> None:
        self._config = config
        self._agents = agents or PipelineAgents(config)

    def compile(self, recorder: AgentTraceRecorder):
        """Build and compile the LangGraph workflow."""
        nodes = self._agents.bind(recorder)
        graph: StateGraph = StateGraph(PipelineState)
        for name in NODE_ORDER:
            graph.add_node(name, nodes[name])
        graph.add_edge(START, "repository_setup")
        for left, right in zip(NODE_ORDER, NODE_ORDER[1:], strict=False):
            graph.add_edge(left, right)
        graph.add_edge("supervisor", END)
        return graph.compile()

    def run(self, *, phase: str = "before", dry_run: bool = True) -> PipelineResult:
        """Execute the compiled pipeline."""
        state = initial_state(self._config, phase=phase, dry_run=dry_run)
        recorder = AgentTraceRecorder(
            self._config.project_root / "reports" / "agent_runs",
            state["trace_run_id"],
        )
        compiled = self.compile(recorder)
        final_state = compiled.invoke(state)
        recorder.write_combined()
        return PipelineResult.from_state(final_state)
