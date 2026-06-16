"""LangGraph node handlers for pipeline agents."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.architecture_bug import ArchitectureBugAgent
from ex04_agent.agents.comparison_report import ComparisonReportAgent
from ex04_agent.agents.graph_interpreter import GraphInterpreterAgent
from ex04_agent.agents.graph_parser import GraphParserAgent
from ex04_agent.agents.graphify_runner import GraphifyRunnerAgent
from ex04_agent.agents.obsidian_vault import ObsidianVaultAgent
from ex04_agent.agents.patch import PatchAgent
from ex04_agent.agents.recommendation import RecommendationAgent
from ex04_agent.agents.repository_setup import RepositorySetupAgent
from ex04_agent.agents.supervisor import SupervisorAgent
from ex04_agent.agents.test_runner import TestRunnerAgent
from ex04_agent.shared.config import AppConfig
from ex04_agent.workflow.pipeline_steps import (
    run_dynamic_hotmd,
    run_graph_parser,
    run_graphify,
    run_obsidian_vault,
)
from ex04_agent.workflow.state import PipelineState


class PipelineAgents:
    """Bundle all pipeline agents for LangGraph nodes."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.repository_setup = RepositorySetupAgent(config)
        self.graphify_runner = GraphifyRunnerAgent(config)
        self.graph_parser = GraphParserAgent(config)
        self.obsidian_vault = ObsidianVaultAgent(config)
        self.graph_interpreter = GraphInterpreterAgent(config)
        self.architecture_bug = ArchitectureBugAgent(config)
        self.recommendation = RecommendationAgent(config)
        self.patch = PatchAgent(config)
        self.test_runner = TestRunnerAgent(config)
        self.comparison_report = ComparisonReportAgent(config)
        self.supervisor = SupervisorAgent(config)

    def bind(self, recorder: AgentTraceRecorder) -> dict[str, Any]:
        """Return LangGraph node callables bound to a trace recorder."""

        def step(handler):
            def wrapped(state: PipelineState) -> dict[str, Any]:
                return handler(self, state, recorder)

            wrapped.__name__ = handler.__name__
            return wrapped

        def agent_step(agent, method_name: str):
            method = getattr(agent, method_name)

            def wrapped(state: PipelineState) -> dict[str, Any]:
                return method(state, recorder)

            wrapped.__name__ = method_name
            return wrapped

        return {
            "repository_setup": agent_step(self.repository_setup, "run_pipeline"),
            "graphify_runner": step(run_graphify),
            "graph_parser": step(run_graph_parser),
            "obsidian_vault": step(run_obsidian_vault),
            "dynamic_hotmd": step(run_dynamic_hotmd),
            "graph_interpreter": agent_step(self.graph_interpreter, "run_pipeline"),
            "architecture_bug": agent_step(self.architecture_bug, "run_pipeline"),
            "recommendation": agent_step(self.recommendation, "run_pipeline"),
            "patch": agent_step(self.patch, "run_pipeline"),
            "test_runner": agent_step(self.test_runner, "run_pipeline"),
            "comparison_report": agent_step(self.comparison_report, "run_pipeline"),
            "supervisor": agent_step(self.supervisor, "run_pipeline"),
        }
