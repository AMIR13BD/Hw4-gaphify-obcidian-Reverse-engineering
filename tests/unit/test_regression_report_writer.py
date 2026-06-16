"""Tests for RegressionReportWriter."""

from __future__ import annotations

import json
from pathlib import Path

from regression_helpers import make_regression_result

from ex04_agent.testing.report_writer import RegressionReportWriter


def test_report_writer_writes_json_and_md(tmp_path: Path) -> None:
    result = make_regression_result()
    writer = RegressionReportWriter()
    json_path = tmp_path / "regression.json"
    md_path = tmp_path / "regression.md"
    writer.write(result, json_path=json_path, md_path=md_path)
    assert json_path.is_file()
    assert md_path.is_file()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["phase"] == "before"
    assert "Summary" in md_path.read_text(encoding="utf-8")


def test_report_writer_writes_latest(tmp_path: Path) -> None:
    result = make_regression_result()
    writer = RegressionReportWriter()
    latest = tmp_path / "latest.json"
    writer.write(result, json_path=tmp_path / "r.json", md_path=tmp_path / "r.md", latest_path=latest)
    assert latest.is_file()
