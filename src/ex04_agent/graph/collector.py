"""Copy Graphify output files into project artifact directories."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from ex04_agent.shared.config import AppConfig

REQUIRED_ARTIFACTS = ("graph.json", "graph.html", "GRAPH_REPORT.md")
OPTIONAL_ARTIFACTS = ("manifest.json", ".graphify_labels.json", ".graphify_root")
ALL_ARTIFACTS = REQUIRED_ARTIFACTS + OPTIONAL_ARTIFACTS


@dataclass(frozen=True)
class CollectResult:
    """Outcome of copying Graphify artifacts."""

    source_dir: Path
    dest_dir: Path
    copied: tuple[str, ...]
    missing_required: tuple[str, ...]
    missing_optional: tuple[str, ...]

    @property
    def success(self) -> bool:
        """True when all required artifacts were copied."""
        return not self.missing_required


class GraphCollector:
    """Normalize Graphify outputs into artifacts/graph/{phase}/."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def artifact_dir(self, phase: str) -> Path:
        """Destination directory for a run phase."""
        return (self._config.project_root / "artifacts" / "graph" / phase).resolve()

    def graphify_out_dir(self, target_repo: Path | None = None) -> Path:
        """Default Graphify output folder inside the target repository."""
        repo = target_repo or self._config.target_repo_path
        return (repo / "graphify-out").resolve()

    def collect(
        self,
        phase: str,
        source_dir: Path | None = None,
        dest_dir: Path | None = None,
    ) -> CollectResult:
        """Copy known Graphify artifacts from source_dir to dest_dir."""
        src = (source_dir or self.graphify_out_dir()).resolve()
        dst = (dest_dir or self.artifact_dir(phase)).resolve()
        dst.mkdir(parents=True, exist_ok=True)

        copied: list[str] = []
        missing_required: list[str] = []
        missing_optional: list[str] = []

        for name in ALL_ARTIFACTS:
            source = src / name
            if not source.is_file():
                if name in REQUIRED_ARTIFACTS:
                    missing_required.append(name)
                else:
                    missing_optional.append(name)
                continue
            shutil.copy2(source, dst / name)
            copied.append(name)

        return CollectResult(
            source_dir=src,
            dest_dir=dst,
            copied=tuple(copied),
            missing_required=tuple(missing_required),
            missing_optional=tuple(missing_optional),
        )
