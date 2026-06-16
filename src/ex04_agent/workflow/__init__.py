"""LangGraph multi-agent pipeline."""

from ex04_agent.workflow.result import PipelineResult
from ex04_agent.workflow.state import PipelineState, initial_state

__all__ = [
    "LangGraphWorkflow",
    "NODE_ORDER",
    "PipelineResult",
    "PipelineState",
    "initial_state",
]


def __getattr__(name: str):
    if name in {"LangGraphWorkflow", "NODE_ORDER"}:
        from ex04_agent.workflow.graph import NODE_ORDER, LangGraphWorkflow

        return LangGraphWorkflow if name == "LangGraphWorkflow" else NODE_ORDER
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
