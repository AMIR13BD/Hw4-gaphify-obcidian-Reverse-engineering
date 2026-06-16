"""Tests for git diff reader."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ex04_agent.git.diff_reader import GitDiffReader


def test_git_diff_reader_empty_diff(tmp_path: Path) -> None:
    """Clean git repo with no unstaged changes returns empty file list."""
    repo = _init_git_repo(tmp_path)
    result = GitDiffReader().read(repo)
    assert result.is_git_repo is True
    assert result.changed_files == ()
    assert result.warning is not None


def test_git_diff_reader_detects_changed_file(tmp_path: Path) -> None:
    """Unstaged modification appears in changed files."""
    repo = _init_git_repo(tmp_path)
    (repo / "module.py").write_text("print('changed')\n", encoding="utf-8")
    result = GitDiffReader().read(repo)
    assert "module.py" in result.changed_files
    assert result.stat_text


def test_git_diff_reader_non_git_folder(tmp_path: Path) -> None:
    """Non-git directory returns warning without raising."""
    folder = tmp_path / "plain"
    folder.mkdir()
    result = GitDiffReader().read(folder)
    assert result.is_git_repo is False
    assert result.changed_files == ()
    assert result.warning is not None


def _init_git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=repo, check=True)
    target = repo / "module.py"
    target.write_text("print('v1')\n", encoding="utf-8")
    subprocess.run(["git", "add", "module.py"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    return repo
