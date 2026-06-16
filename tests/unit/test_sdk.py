"""Tests for the public SDK scaffold."""

from pathlib import Path

from ex04_agent.sdk.sdk import Ex04Sdk


def test_health_check_returns_version_and_target_repo(project_root: Path) -> None:
    """Health check exposes version and configured target repo path."""
    status = Ex04Sdk().health_check()

    assert status.version == "1.00"
    assert status.config_version == "1.00"
    assert status.target_repo == "data/target_repo/broken-python"
    assert status.graphify_cli == "graphify"
    assert Path(status.project_root) == project_root
    assert Path(status.target_repo_path) == (project_root / "data/target_repo/broken-python").resolve()
