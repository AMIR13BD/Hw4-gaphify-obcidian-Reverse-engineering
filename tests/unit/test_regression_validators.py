"""Tests for discovery and validator modules."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.testing.discovery import discover_target
from ex04_agent.testing.validators import ast_validate, compile_validate

VALID_PY = "x = 1\nprint(x)\n"
BROKEN_PY = "print 'bad'\nif answer = 5:\n    pass\n"


def test_discovery_no_tests(tmp_path: Path) -> None:
    """Discovery reports no tests when repo has only source files."""
    (tmp_path / "main.py").write_text(VALID_PY, encoding="utf-8")
    result = discover_target(tmp_path)
    assert not result.has_tests
    assert result.test_command is None
    assert "no dedicated test suite" in result.reason.lower()


def test_discovery_finds_tests_dir(tmp_path: Path) -> None:
    """Discovery detects tests/ directory with test files."""
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text("def test_x(): pass\n", encoding="utf-8")
    result = discover_target(tmp_path)
    assert result.has_tests
    assert result.test_command is not None


def test_compile_validator_passes_valid(tmp_path: Path) -> None:
    f = tmp_path / "good.py"
    f.write_text(VALID_PY, encoding="utf-8")
    passed, failed = compile_validate([f])
    assert str(f) in passed
    assert not failed


def test_compile_validator_catches_syntax_error(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text(BROKEN_PY, encoding="utf-8")
    passed, failed = compile_validate([f])
    assert str(f) in failed
    assert not passed


def test_ast_validator_passes_valid(tmp_path: Path) -> None:
    f = tmp_path / "good.py"
    f.write_text(VALID_PY, encoding="utf-8")
    passed, failed = ast_validate([f])
    assert str(f) in passed
    assert not failed


def test_ast_validator_catches_syntax_error(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text(BROKEN_PY, encoding="utf-8")
    passed, failed = ast_validate([f])
    assert str(f) in failed
    assert not passed


def test_parse_ruff_issues_counts_plural_errors(tmp_path: Path) -> None:
    from ex04_agent.testing.result_parser import parse_ruff_issues

    out = tmp_path / "ruff.txt"
    out.write_text("Found 4 errors.\n", encoding="utf-8")
    assert parse_ruff_issues(str(out)) == 4


def test_parse_ruff_issues_passes_on_clean_output(tmp_path: Path) -> None:
    from ex04_agent.testing.result_parser import parse_ruff_issues

    out = tmp_path / "ruff.txt"
    out.write_text("All checks passed!\n", encoding="utf-8")
    assert parse_ruff_issues(str(out)) == 0
