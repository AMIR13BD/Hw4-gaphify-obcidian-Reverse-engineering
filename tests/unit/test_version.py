"""Tests for project version."""

from ex04_agent.shared.version import VERSION


def test_version_is_expected() -> None:
    """Package version matches course scaffold requirement."""
    assert VERSION == "1.00"
