"""Orchestrate dynamic hot.md generation."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ex04_agent.git.diff_reader import GitDiffReader
from ex04_agent.graph.indexer import GraphIndexer
from ex04_agent.graph.parser import GraphParser
from ex04_agent.obsidian.hotmd_renderer import HotMdRenderContext, HotMdRenderer
from ex04_agent.obsidian.node_ranker import NodeRanker
from ex04_agent.shared.config import AppConfig


@dataclass(frozen=True)
class DynamicHotMdResult:
    """Outcome of dynamic hot.md generation."""

    success: bool
    phase: str
    hot_path: str
    snapshot_path: str
    changed_files_count: int
    ranked_nodes_count: int
    top_labels: tuple[str, ...]
    warning: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DynamicHotMdBuilder:
    """Build dynamic hot.md from metrics, graph, and git diff."""

    def __init__(
        self,
        config: AppConfig,
        diff_reader: GitDiffReader | None = None,
        ranker: NodeRanker | None = None,
        renderer: HotMdRenderer | None = None,
        parser: GraphParser | None = None,
    ) -> None:
        self._config = config
        self._diff_reader = diff_reader or GitDiffReader()
        self._ranker = ranker or NodeRanker()
        self._renderer = renderer or HotMdRenderer()
        self._parser = parser or GraphParser()

    def build(
        self,
        *,
        phase: str,
        metrics_path: Path,
        graph_path: Path,
        hot_path: Path,
        snapshot_dir: Path,
        failing_test_files: tuple[str, ...] = (),
    ) -> DynamicHotMdResult:
        self._validate_phase(phase)
        self._require_file(metrics_path, "metrics")
        self._require_file(graph_path, "graph")

        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        indexer = GraphIndexer(self._parser.load(graph_path))
        diff = self._diff_reader.read(self._config.target_repo_path)
        ranked = self._ranker.rank(
            metrics,
            indexer,
            changed_files=diff.changed_files,
            failing_test_files=failing_test_files,
            weights=self._config.hotmd_weights,
        )

        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        previous_excerpt = self._previous_excerpt(hot_path)
        previous_snapshot = self._latest_snapshot_name(snapshot_dir, phase)
        content = self._renderer.render(
            HotMdRenderContext(
                phase=phase,
                timestamp=timestamp,
                repo_path=str(self._config.target_repo),
                commit=diff.commit,
                diff=diff,
                ranked_nodes=ranked,
                previous_hot_excerpt=previous_excerpt,
                previous_snapshot_name=previous_snapshot,
            )
        )

        hot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = snapshot_dir / f"hot_{phase}_{timestamp}.md"
        hot_path.write_text(content, encoding="utf-8")
        snapshot_path.write_text(content, encoding="utf-8")

        top_labels = tuple(node.label for node in ranked[:5])
        return DynamicHotMdResult(
            success=True,
            phase=phase,
            hot_path=str(hot_path),
            snapshot_path=str(snapshot_path),
            changed_files_count=len(diff.changed_files),
            ranked_nodes_count=len(ranked),
            top_labels=top_labels,
            warning=diff.warning,
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

    @staticmethod
    def _previous_excerpt(hot_path: Path, lines: int = 8) -> str | None:
        if not hot_path.is_file():
            return None
        excerpt = hot_path.read_text(encoding="utf-8").splitlines()[:lines]
        return "\n".join(excerpt) if excerpt else None

    @staticmethod
    def _latest_snapshot_name(snapshot_dir: Path, phase: str) -> str | None:
        if not snapshot_dir.is_dir():
            return None
        pattern = re.compile(rf"^hot_{re.escape(phase)}_.*\.md$")
        matches = sorted(p.name for p in snapshot_dir.iterdir() if pattern.match(p.name))
        return matches[-1] if matches else None
