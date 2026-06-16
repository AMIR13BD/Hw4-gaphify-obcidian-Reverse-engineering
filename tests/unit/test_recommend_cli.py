"""Tests for recommend CLI command."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ex04_agent.cli.parser import build_parser
from ex04_agent.main import main
from ex04_agent.recommendation.report_writer import RecommendationSummary


def test_cli_recommend_rejects_invalid_phase() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["recommend", "--phase", "middle"])


def test_cli_recommend_prints_summary(monkeypatch, capsys) -> None:
    summary = RecommendationSummary(
        recommendation_count=4,
        by_action_type={"review_required": 3, "docs_only": 1},
        by_priority={"high": 2, "medium": 2},
        patchable_count=2,
        recommendations_json_path="recommendations.json",
        recommendations_markdown_path="recommendations.md",
        patch_plan_json_path="patch_plan.json",
        patch_plan_markdown_path="patch_plan.md",
    )
    monkeypatch.setattr(
        "ex04_agent.agents.recommendation.RecommendationAgent",
        lambda *args, **kwargs: MagicMock(run=MagicMock(return_value=summary)),
    )
    code = main(["recommend", "--phase", "before"])
    assert code == 0
    assert "recommendation_count" in capsys.readouterr().out
