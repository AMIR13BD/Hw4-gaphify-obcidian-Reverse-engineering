"""Tests for token-efficiency bundles, comparator, and report writer."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_agent.token_efficiency.collector import TokenEfficiencyCollector
from ex04_agent.token_efficiency.comparator import compare_scenario
from ex04_agent.token_efficiency.context_bundle import ContextBundleBuilder
from ex04_agent.token_efficiency.model import ContextBundle, FileEstimate
from ex04_agent.token_efficiency.report_writer import TokenEfficiencyReportWriter


def test_context_bundle_builder_collects_files(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("print('a')", encoding="utf-8")
    (tmp_path / "b.py").write_text("print('b')", encoding="utf-8")
    bundle = ContextBundleBuilder().build("test", "two files", [tmp_path / "a.py", tmp_path / "b.py"])
    assert len(bundle.files) == 2
    assert bundle.total_tokens > 0


def test_comparator_computes_absolute_and_percent_savings() -> None:
    base = ContextBundle("b", "", (FileEstimate("a", 40, 10),))
    guided = ContextBundle("g", "", (FileEstimate("c", 8, 2),))
    result = compare_scenario("s", "t", base, guided, quality_note="q", risk_note="r")
    assert result.tokens_saved == 8
    assert result.percent_saved == 80.0


def test_comparator_handles_zero_baseline() -> None:
    base = ContextBundle("b", "", ())
    guided = ContextBundle("g", "", (FileEstimate("c", 4, 1),))
    result = compare_scenario("s", "t", base, guided, quality_note="q", risk_note="r")
    assert result.percent_saved == 0.0


def test_report_writer_writes_json_and_md(tmp_path: Path) -> None:
    from ex04_agent.token_efficiency.model import TokenEfficiencyResult

    bundle = ContextBundle("b", "desc", (FileEstimate("f", 8, 2),))
    scenario = compare_scenario("s", "t", bundle, bundle, quality_note="q", risk_note="r")
    result = TokenEfficiencyResult(
        estimation_method="ceil/4", phase="before", bundles=(bundle,),
        scenarios=(scenario,), total_baseline_tokens=2, total_graph_guided_tokens=2,
        total_tokens_saved=0, percent_saved=0.0, output_paths={},
    )
    paths = TokenEfficiencyReportWriter().write(result, tmp_path / "out")
    assert Path(paths["json"]).is_file()
    assert "Estimation Method" in Path(paths["md"]).read_text(encoding="utf-8")


def test_collector_fails_on_missing_required_files(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "p"
    project.mkdir()
    (project / "config").mkdir()
    setup = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project / "config" / "setup.json").write_text(setup.read_text(encoding="utf-8"), encoding="utf-8")
    (project / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    monkeypatch.setattr("ex04_agent.shared.config.find_project_root", lambda start=None: project)
    from ex04_agent.shared.config import load_config

    with pytest.raises(FileNotFoundError, match="Required token-efficiency files missing"):
        TokenEfficiencyCollector(load_config()).require_inputs()
