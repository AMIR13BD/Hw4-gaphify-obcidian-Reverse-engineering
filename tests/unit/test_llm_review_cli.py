"""Tests for llm-review CLI."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from ex04_agent.cli.parser import build_parser
from ex04_agent.llm_review.model import LlmReviewMetadata, LlmReviewResult
from ex04_agent.main import main


def test_cli_llm_review_rejects_invalid_phase() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["llm-review", "--phase", "invalid"])


def test_cli_llm_review_missing_api_key(monkeypatch, capsys) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert main(["llm-review", "--phase", "before"]) == 1
    err = capsys.readouterr().out
    payload = json.loads(err)
    assert payload["success"] is False
    assert "OPENAI_API_KEY" in payload["error"]


def test_cli_llm_review_prints_summary(monkeypatch, capsys) -> None:
    metadata = LlmReviewMetadata(
        model_name="test-model",
        input_files_used=["obsidian/hot.md"],
        character_count=100,
        estimated_input_tokens=25,
        provider_prompt_tokens=10,
        provider_completion_tokens=5,
        provider_total_tokens=15,
        timestamp="2026-06-17T00:00:00+00:00",
        llm_calls=1,
        phase="before",
    )
    review = LlmReviewResult(
        response_text="ok",
        metadata=metadata,
        markdown_path="/tmp/review.md",
        json_path="/tmp/review.json",
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "ex04_agent.llm_review.engine.LlmReviewEngine.run",
        MagicMock(return_value=review),
    )
    assert main(["llm-review", "--phase", "before"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["metadata"]["llm_calls"] == 1
    assert out["markdown_path"] == "/tmp/review.md"
