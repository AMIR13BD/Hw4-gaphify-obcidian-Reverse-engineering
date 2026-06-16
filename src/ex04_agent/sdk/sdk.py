"""SDK facade for the EX04 agent project."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ex04_agent.shared.config import AppConfig, load_config
from ex04_agent.shared.version import VERSION
from ex04_agent.workflow.graph import LangGraphWorkflow
from ex04_agent.workflow.result import PipelineResult


@dataclass(frozen=True)
class HealthStatus:
    """Result of a scaffold health check."""

    version: str
    project_root: str
    config_path: str
    config_version: str
    target_repo: str
    target_repo_path: str
    graphify_cli: str
    allow_patches: bool
    max_iterations: int

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable health report."""
        return asdict(self)


class Ex04Sdk:
    """Single entry point for EX04 agent operations."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or load_config()
        self._workflow = LangGraphWorkflow(self._config)

    @property
    def config(self) -> AppConfig:
        """Loaded application configuration."""
        return self._config

    def health_check(self) -> HealthStatus:
        """Return basic project paths and configuration summary."""
        cfg = self._config
        return HealthStatus(
            version=VERSION,
            project_root=str(cfg.project_root),
            config_path=str(cfg.config_path),
            config_version=cfg.version,
            target_repo=cfg.target_repo,
            target_repo_path=str(cfg.target_repo_path),
            graphify_cli=cfg.graphify_cli,
            allow_patches=cfg.allow_patches,
            max_iterations=cfg.max_iterations,
        )

    def run_pipeline(self, *, dry_run: bool = True, phase: str = "before") -> PipelineResult:
        """Run the LangGraph multi-agent pipeline."""
        if phase not in {"before", "after"}:
            msg = f"Invalid phase {phase!r}; expected 'before' or 'after'"
            raise ValueError(msg)
        return self._workflow.run(phase=phase, dry_run=dry_run)
