"""Load application configuration from config/setup.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HotMdWeights:
    """Weights for dynamic hot.md node ranking."""

    degree: float
    betweenness: float
    diff_proximity: float
    test_proximity: float
    ambiguous: float
    god_node: float


@dataclass(frozen=True)
class AppConfig:
    """Application settings loaded from config/setup.json."""

    version: str
    target_repo: str
    graphify_cli: str
    max_iterations: int
    allow_patches: bool
    index_max_chars: int
    hotmd_weights: HotMdWeights
    project_root: Path
    config_path: Path

    @property
    def target_repo_path(self) -> Path:
        """Absolute path to the target repository."""
        return (self.project_root / self.target_repo).resolve()


def find_project_root(start: Path | None = None) -> Path:
    """Locate project root by searching for pyproject.toml."""
    current = (start or Path(__file__)).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    msg = "Could not find project root (pyproject.toml not found)"
    raise FileNotFoundError(msg)


def _parse_hotmd_weights(raw: dict[str, Any]) -> HotMdWeights:
    required = (
        "degree",
        "betweenness",
        "diff_proximity",
        "test_proximity",
        "ambiguous",
        "god_node",
    )
    missing = [key for key in required if key not in raw]
    if missing:
        msg = f"hotmd_weights missing keys: {', '.join(missing)}"
        raise ValueError(msg)
    return HotMdWeights(
        degree=float(raw["degree"]),
        betweenness=float(raw["betweenness"]),
        diff_proximity=float(raw["diff_proximity"]),
        test_proximity=float(raw["test_proximity"]),
        ambiguous=float(raw["ambiguous"]),
        god_node=float(raw["god_node"]),
    )


def load_config(config_path: Path | None = None) -> AppConfig:
    """Load and validate config/setup.json."""
    project_root = find_project_root()
    path = config_path or (project_root / "config" / "setup.json")
    if not path.is_file():
        msg = f"Configuration file not found: {path}"
        raise FileNotFoundError(msg)

    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    required_keys = (
        "version",
        "target_repo",
        "graphify_cli",
        "max_iterations",
        "allow_patches",
        "index_max_chars",
        "hotmd_weights",
    )
    missing = [key for key in required_keys if key not in data]
    if missing:
        msg = f"setup.json missing keys: {', '.join(missing)}"
        raise ValueError(msg)

    return AppConfig(
        version=str(data["version"]),
        target_repo=str(data["target_repo"]),
        graphify_cli=str(data["graphify_cli"]),
        max_iterations=int(data["max_iterations"]),
        allow_patches=bool(data["allow_patches"]),
        index_max_chars=int(data["index_max_chars"]),
        hotmd_weights=_parse_hotmd_weights(data["hotmd_weights"]),
        project_root=project_root,
        config_path=path.resolve(),
    )
