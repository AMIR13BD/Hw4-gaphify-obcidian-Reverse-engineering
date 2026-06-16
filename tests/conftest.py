"""Shared pytest fixtures for the EX04 agent project."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_agent.shared.config import find_project_root


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the repository root containing pyproject.toml."""
    return find_project_root()


@pytest.fixture(scope="session")
def config_path(project_root: Path) -> Path:
    """Return the path to config/setup.json."""
    return project_root / "config" / "setup.json"
