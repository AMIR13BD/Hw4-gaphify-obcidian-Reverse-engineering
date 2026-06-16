"""Base class for EX04 pipeline agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from ex04_agent.shared.config import AppConfig, load_config

if TYPE_CHECKING:
    from ex04_agent.agent_trace.recorder import AgentTraceRecorder
    from ex04_agent.workflow.state import PipelineState


class BaseAgent(ABC):
    """Shared agent interface for LangGraph nodes."""

    name: str = "base"

    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or load_config()

    @property
    def config(self) -> AppConfig:
        """Loaded application configuration."""
        return self._config

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent task."""

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        """Execute as a LangGraph pipeline node (override in pipeline agents)."""
        msg = f"{self.name} does not implement run_pipeline"
        raise NotImplementedError(msg)
