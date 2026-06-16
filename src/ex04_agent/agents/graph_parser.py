"""Thin agent wrapper for graph parsing and metrics."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from ex04_agent.agents.base import BaseAgent
from ex04_agent.graph.indexer import GraphIndexer
from ex04_agent.graph.metrics import MetricsEngine, MetricsReport
from ex04_agent.graph.parser import GraphParser
from ex04_agent.graph.serializer import MetricsSerializer
from ex04_agent.shared.config import AppConfig


class GraphParserAgent(BaseAgent):
    """Future-ready wrapper around parser, indexer, and metrics engine."""

    name = "graph_parser"

    def __init__(
        self,
        config: AppConfig | None = None,
        parser: GraphParser | None = None,
        metrics_engine: MetricsEngine | None = None,
        serializer: MetricsSerializer | None = None,
    ) -> None:
        super().__init__(config)
        self._parser = parser or GraphParser()
        self._metrics_engine = metrics_engine or MetricsEngine()
        self._serializer = serializer or MetricsSerializer()

    def run(
        self,
        phase: str = "before",
        graph_path: Path | str | None = None,
        output_path: Path | str | None = None,
    ) -> MetricsReport:
        self._validate_phase(phase)
        resolved_graph = Path(graph_path or self._default_graph_path(phase))
        resolved_output = Path(output_path or self._default_output_path(phase))
        document = self._parser.load(resolved_graph)
        indexer = GraphIndexer(document)
        generated_at = datetime.now(UTC).isoformat()
        report = self._metrics_engine.compute(
            indexer,
            phase=phase,
            graph_path=str(resolved_graph),
            generated_at=generated_at,
        )
        self._serializer.write(report, resolved_output)
        return report

    def terminal_summary(self, report: MetricsReport) -> str:
        return self._serializer.format_terminal_summary(report)

    def _default_graph_path(self, phase: str) -> Path:
        return self.config.project_root / "artifacts" / "graph" / phase / "graph.json"

    def _default_output_path(self, phase: str) -> Path:
        return self.config.project_root / "reports" / "architecture" / f"metrics_{phase}.json"

    @staticmethod
    def _validate_phase(phase: str) -> None:
        if phase not in {"before", "after"}:
            msg = f"Invalid phase {phase!r}; expected 'before' or 'after'"
            raise ValueError(msg)
