"""Tests for token-report CLI."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ex04_agent.cli.parser import build_parser
from ex04_agent.main import main
from ex04_agent.token_efficiency.engine import TokenEfficiencySummary


def test_cli_token_report_rejects_invalid_phase() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["token-report", "--phase", "invalid"])


def test_cli_token_report_prints_summary(monkeypatch, capsys) -> None:
    mock = TokenEfficiencySummary(3, 1000, 400, 600, 60.0, {"json": "/j", "md": "/m"})
    monkeypatch.setattr(
        "ex04_agent.sdk.sdk.Ex04Sdk",
        lambda *a, **kw: MagicMock(run_token_report=MagicMock(return_value=mock)),
    )
    assert main(["token-report"]) == 0
    out = capsys.readouterr().out
    assert "scenarios_count" in out
    assert "total_baseline_tokens" in out
