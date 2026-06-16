"""Execute Graphify CLI against the target repository."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from ex04_agent.graph.collector import GraphCollector
from ex04_agent.graph.graphify_run_report import build_error, write_log, write_metadata
from ex04_agent.graph.graphify_run_result import GraphifyRunResult
from ex04_agent.shared.config import AppConfig

SubprocessRunner = Callable[..., subprocess.CompletedProcess[str]]


class GraphifyRunner:
    """Run `graphify update .` and collect outputs."""

    def __init__(
        self,
        config: AppConfig,
        collector: GraphCollector | None = None,
        subprocess_runner: SubprocessRunner | None = None,
    ) -> None:
        self._config = config
        self._collector = collector or GraphCollector(config)
        self._subprocess_runner = subprocess_runner or subprocess.run

    def build_command(self) -> list[str]:
        """AST-only Graphify update command (no LLM extract)."""
        return [self._config.graphify_cli, "update", "."]

    def run(self, phase: str) -> GraphifyRunResult:
        """Execute Graphify in the target repo and collect artifacts."""
        self._validate_phase(phase)
        timestamp = datetime.now(UTC).isoformat()
        cwd = self._config.target_repo_path
        command = self.build_command()
        graphify_path = shutil.which(self._config.graphify_cli)

        completed = self._subprocess_runner(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        collect = self._collector.collect(phase)
        success = completed.returncode == 0 and collect.success
        error = build_error(completed.returncode, collect)

        result = GraphifyRunResult(
            success=success,
            phase=phase,
            command=tuple(command),
            cwd=str(cwd),
            return_code=completed.returncode,
            graphify_cli=self._config.graphify_cli,
            graphify_cli_path=graphify_path,
            target_repo_path=str(cwd),
            stdout=completed.stdout,
            stderr=completed.stderr,
            copied_artifacts=collect.copied,
            missing_required_artifacts=collect.missing_required,
            missing_optional_artifacts=collect.missing_optional,
            artifact_dest_dir=str(collect.dest_dir),
            log_path=str(self._log_path(phase)),
            metadata_path=str(self._metadata_path(phase)),
            timestamp=timestamp,
            error=error,
        )
        write_log(result)
        write_metadata(result)
        return result

    @staticmethod
    def _validate_phase(phase: str) -> None:
        if phase not in {"before", "after"}:
            msg = f"Invalid phase {phase!r}; expected 'before' or 'after'"
            raise ValueError(msg)

    def _log_path(self, phase: str) -> Path:
        return self._config.project_root / "reports" / "graphify" / f"graphify_{phase}_run.txt"

    def _metadata_path(self, phase: str) -> Path:
        return self._config.project_root / "reports" / "graphify" / f"graphify_{phase}_metadata.json"
