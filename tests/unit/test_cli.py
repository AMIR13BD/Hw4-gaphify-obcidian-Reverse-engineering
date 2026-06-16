"""Tests for CLI scaffold."""

import json

from ex04_agent.main import main


def test_cli_health_prints_json(capsys) -> None:
    """Health subcommand prints valid JSON with version."""
    exit_code = main(["health"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["version"] == "1.00"
    assert payload["target_repo"] == "data/target_repo/broken-python"
