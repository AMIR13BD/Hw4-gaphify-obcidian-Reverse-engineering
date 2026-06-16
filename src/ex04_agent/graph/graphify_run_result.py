"""Graphify CLI run result model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class GraphifyRunResult:
    """Full outcome of a Graphify CLI run and artifact collection."""

    success: bool
    phase: str
    command: tuple[str, ...]
    cwd: str
    return_code: int
    graphify_cli: str
    graphify_cli_path: str | None
    target_repo_path: str
    stdout: str
    stderr: str
    copied_artifacts: tuple[str, ...]
    missing_required_artifacts: tuple[str, ...]
    missing_optional_artifacts: tuple[str, ...]
    artifact_dest_dir: str
    log_path: str
    metadata_path: str
    timestamp: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable summary."""
        return asdict(self)
