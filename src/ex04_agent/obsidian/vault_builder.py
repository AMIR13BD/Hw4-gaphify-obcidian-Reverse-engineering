"""Orchestrate Obsidian vault file generation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ex04_agent.graph.indexer import GraphIndexer
from ex04_agent.graph.parser import GraphParser
from ex04_agent.obsidian.hot_md_builder import HotMdBuilder
from ex04_agent.obsidian.index_builder import IndexBuilder
from ex04_agent.obsidian.node_page_builder import NodePageBuilder
from ex04_agent.obsidian.report_builder import ReportBuilder
from ex04_agent.obsidian.vault_context import VaultContext
from ex04_agent.shared.config import AppConfig


@dataclass(frozen=True)
class VaultBuildResult:
    """Outcome of a vault generation run."""

    success: bool
    phase: str
    vault_dir: str
    index_path: str
    hot_path: str
    report_path: str
    node_pages_created: int
    files_written: tuple[str, ...]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VaultBuilder:
    """Create and refresh the Obsidian vault from metrics and graph artifacts."""

    def __init__(
        self,
        config: AppConfig,
        parser: GraphParser | None = None,
        index_builder: IndexBuilder | None = None,
        hot_builder: HotMdBuilder | None = None,
        node_builder: NodePageBuilder | None = None,
        report_builder: ReportBuilder | None = None,
    ) -> None:
        self._config = config
        self._parser = parser or GraphParser()
        self._index_builder = index_builder or IndexBuilder()
        self._hot_builder = hot_builder or HotMdBuilder()
        self._node_builder = node_builder or NodePageBuilder()
        self._report_builder = report_builder or ReportBuilder()

    def build(
        self,
        *,
        phase: str,
        metrics_path: Path,
        graph_path: Path,
        graph_report_path: Path,
        vault_dir: Path,
    ) -> VaultBuildResult:
        self._validate_phase(phase)
        self._require_file(metrics_path, "metrics")
        self._require_file(graph_path, "graph")

        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        document = self._parser.load(graph_path)
        indexer = GraphIndexer(document)
        report_text = (
            graph_report_path.read_text(encoding="utf-8") if graph_report_path.is_file() else None
        )
        context = VaultContext(
            phase=phase,
            repo_name=self._config.target_repo_path.name,
            repo_path=str(self._config.target_repo),
            metrics=metrics,
            indexer=indexer,
            graph_report_text=report_text,
            index_max_chars=self._config.index_max_chars,
        )

        nodes_dir = vault_dir / "nodes"
        reports_dir = vault_dir / "reports"
        nodes_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)

        written: list[str] = []
        index_path = vault_dir / "index.md"
        hot_path = vault_dir / "hot.md"
        report_path = reports_dir / "graph_summary.md"

        index_path.write_text(self._index_builder.build(context), encoding="utf-8")
        hot_path.write_text(self._hot_builder.build(context), encoding="utf-8")
        report_path.write_text(self._report_builder.build(context), encoding="utf-8")
        written.extend([str(index_path), str(hot_path), str(report_path)])

        node_pages = 0
        nodes_by_id = indexer.nodes_by_id
        for node_id in self._node_builder.select_node_ids(context):
            node = nodes_by_id.get(node_id)
            if node is None:
                continue
            page_path = nodes_dir / self._node_builder.filename_for(node_id)
            page_path.write_text(self._node_builder.build_page(context, node), encoding="utf-8")
            written.append(str(page_path))
            node_pages += 1

        return VaultBuildResult(
            success=True,
            phase=phase,
            vault_dir=str(vault_dir),
            index_path=str(index_path),
            hot_path=str(hot_path),
            report_path=str(report_path),
            node_pages_created=node_pages,
            files_written=tuple(written),
        )

    @staticmethod
    def _validate_phase(phase: str) -> None:
        if phase not in {"before", "after"}:
            msg = f"Invalid phase {phase!r}; expected 'before' or 'after'"
            raise ValueError(msg)

    @staticmethod
    def _require_file(path: Path, label: str) -> None:
        if not path.is_file():
            msg = f"Required {label} file not found: {path}"
            raise FileNotFoundError(msg)
