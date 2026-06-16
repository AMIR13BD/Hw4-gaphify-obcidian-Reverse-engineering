"""Thin agent wrapper for Obsidian vault generation."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.agents.base import BaseAgent
from ex04_agent.obsidian.dynamic_hotmd_builder import DynamicHotMdBuilder, DynamicHotMdResult
from ex04_agent.obsidian.vault_builder import VaultBuilder, VaultBuildResult
from ex04_agent.shared.config import AppConfig


class ObsidianVaultAgent(BaseAgent):
    """Future-ready wrapper around vault builders."""

    name = "obsidian_vault"

    def __init__(
        self,
        config: AppConfig | None = None,
        builder: VaultBuilder | None = None,
        hotmd_builder: DynamicHotMdBuilder | None = None,
    ) -> None:
        super().__init__(config)
        self._builder = builder or VaultBuilder(self.config)
        self._hotmd_builder = hotmd_builder or DynamicHotMdBuilder(self.config)

    def run(
        self,
        phase: str = "before",
        metrics_path: Path | str | None = None,
        graph_path: Path | str | None = None,
        graph_report_path: Path | str | None = None,
        vault_dir: Path | str | None = None,
        dynamic_hot: bool = False,
    ) -> VaultBuildResult:
        vault = Path(vault_dir or self._default_vault_dir())
        result = self._builder.build(
            phase=phase,
            metrics_path=Path(metrics_path or self._default_metrics_path(phase)),
            graph_path=Path(graph_path or self._default_graph_path(phase)),
            graph_report_path=Path(
                graph_report_path or self._default_graph_report_path(phase)
            ),
            vault_dir=vault,
        )
        if dynamic_hot:
            self.run_dynamic_hotmd(
                phase=phase,
                metrics_path=metrics_path,
                graph_path=graph_path,
                hot_path=vault / "hot.md",
            )
        return result

    def run_dynamic_hotmd(
        self,
        phase: str = "before",
        metrics_path: Path | str | None = None,
        graph_path: Path | str | None = None,
        hot_path: Path | str | None = None,
        snapshot_dir: Path | str | None = None,
        failing_test_files: tuple[str, ...] = (),
    ) -> DynamicHotMdResult:
        return self._hotmd_builder.build(
            phase=phase,
            metrics_path=Path(metrics_path or self._default_metrics_path(phase)),
            graph_path=Path(graph_path or self._default_graph_path(phase)),
            hot_path=Path(hot_path or self._default_vault_dir() / "hot.md"),
            snapshot_dir=Path(snapshot_dir or self._default_snapshot_dir()),
            failing_test_files=failing_test_files,
        )

    def _default_metrics_path(self, phase: str) -> Path:
        return self.config.project_root / "reports" / "architecture" / f"metrics_{phase}.json"

    def _default_graph_path(self, phase: str) -> Path:
        return self.config.project_root / "artifacts" / "graph" / phase / "graph.json"

    def _default_graph_report_path(self, phase: str) -> Path:
        return self.config.project_root / "artifacts" / "graph" / phase / "GRAPH_REPORT.md"

    def _default_vault_dir(self) -> Path:
        return self.config.project_root / "obsidian"

    def _default_snapshot_dir(self) -> Path:
        return self.config.project_root / "artifacts" / "hotmd"
