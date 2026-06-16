"""Tests for configuration loading."""

from pathlib import Path

from ex04_agent.shared.config import load_config


def test_load_config_reads_setup_json(config_path: Path) -> None:
    """setup.json loads with expected target repo and graphify CLI."""
    config = load_config(config_path)

    assert config.version == "1.00"
    assert config.target_repo == "data/target_repo/broken-python"
    assert config.graphify_cli == "graphify"
    assert config.max_iterations == 3
    assert config.allow_patches is False
    assert config.index_max_chars == 4000


def test_hotmd_weights_match_plan(config_path: Path) -> None:
    """hot.md weights match docs/PLAN.md defaults."""
    weights = load_config(config_path).hotmd_weights

    assert weights.degree == 0.20
    assert weights.betweenness == 0.25
    assert weights.diff_proximity == 0.30
    assert weights.test_proximity == 0.15
    assert weights.ambiguous == 0.05
    assert weights.god_node == 0.05
