"""Tests for token estimator."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.token_efficiency.token_estimator import TokenEstimator


def test_estimate_text_uses_ceil_chars_over_four() -> None:
    est = TokenEstimator()
    assert est.estimate_text("") == 0
    assert est.estimate_text("abcd") == 1
    assert est.estimate_text("abcde") == 2


def test_estimate_file_counts_characters(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    path.write_text("hello world", encoding="utf-8")
    result = TokenEstimator().estimate_file(path)
    assert result.characters == 11
    assert result.estimated_tokens == 3
