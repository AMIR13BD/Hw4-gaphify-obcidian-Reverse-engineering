"""Tests for detect CLI command."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ex04_agent.cli.parser import build_parser
from ex04_agent.detection.report_writer import FindingsSummary
from ex04_agent.main import main


def test_cli_detect_rejects_invalid_phase() -> None:
    """Parser only accepts before/after phases."""
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["detect", "--phase", "middle"])


def test_cli_detect_prints_summary(monkeypatch, capsys) -> None:
    """Detect subcommand prints JSON summary."""
    summary = FindingsSummary(
        finding_count=3,
        by_category={"possible_hub": 1},
        by_severity={"medium": 3},
        high_confidence_count=2,
        json_path="findings.json",
        markdown_path="findings.md",
    )
    monkeypatch.setattr(
        "ex04_agent.agents.architecture_bug.ArchitectureBugAgent",
        lambda *args, **kwargs: MagicMock(run=MagicMock(return_value=summary)),
    )
    code = main(["detect", "--phase", "before"])
    assert code == 0
    assert "finding_count" in capsys.readouterr().out
