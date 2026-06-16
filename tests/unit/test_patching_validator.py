"""Tests for validator, diff_writer, and safe_patcher."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.patching.diff_writer import make_unified_diff, write_diff
from ex04_agent.patching.safe_patcher import SafePatcher
from ex04_agent.patching.validator import validate_text


def test_validator_passes_valid_python() -> None:
    ok, err = validate_text("x = 1\nprint(x)\n")
    assert ok and err == ""


def test_validator_catches_syntax_error() -> None:
    ok, err = validate_text("print 'hello'\n")
    assert not ok
    assert err


def test_make_unified_diff_shows_changes() -> None:
    diff = make_unified_diff("a\n", "b\n", "test.py")
    assert "-a" in diff
    assert "+b" in diff


def test_write_diff_creates_file(tmp_path: Path) -> None:
    diff_dir = tmp_path / "diffs"
    p = write_diff("diff content", diff_dir, "some/file.py")
    assert p.is_file()
    assert p.read_text(encoding="utf-8") == "diff content"


def test_dry_run_does_not_modify_file(tmp_path: Path) -> None:
    target = tmp_path / "file.py"
    target.write_text("old content\n", encoding="utf-8")
    patcher = SafePatcher(tmp_path / "backups")
    outcome = patcher.apply(target, "new content\n", allow_patches=False)
    assert not outcome.changed
    assert target.read_text(encoding="utf-8") == "old content\n"


def test_patcher_creates_backup_before_change(tmp_path: Path) -> None:
    target = tmp_path / "x.py"
    target.write_text("x = 1\n", encoding="utf-8")
    backup_dir = tmp_path / "backups"
    patcher = SafePatcher(backup_dir)
    patcher.apply(target, "x = 2\n", allow_patches=True)
    baks = list(backup_dir.glob("*.bak"))
    assert baks, "Backup file should exist"


def test_patcher_rollback_on_invalid_output(tmp_path: Path) -> None:
    target = tmp_path / "y.py"
    target.write_text("x = 1\n", encoding="utf-8")
    patcher = SafePatcher(tmp_path / "backups")
    outcome = patcher.apply(target, "print 'bad'\n", allow_patches=True)
    assert not outcome.changed
