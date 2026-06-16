"""Git diff inspection for the target repository."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

SubprocessRunner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class GitDiffResult:
    """Read-only git diff snapshot from the target repo."""

    changed_files: tuple[str, ...]
    stat_text: str
    raw_diff: str
    commit: str | None
    warning: str | None
    is_git_repo: bool


class GitDiffReader:
    """Run read-only git diff commands inside the target repository."""

    def __init__(self, subprocess_runner: SubprocessRunner | None = None) -> None:
        self._subprocess_runner = subprocess_runner or subprocess.run

    def read(self, repo_path: Path | str, *, include_raw_diff: bool = True) -> GitDiffResult:
        """Collect changed files and diff text without modifying the repo."""
        cwd = Path(repo_path)
        if not (cwd / ".git").exists():
            return GitDiffResult(
                changed_files=(),
                stat_text="",
                raw_diff="",
                commit=None,
                warning=f"Not a git repository: {cwd}",
                is_git_repo=False,
            )

        names = self._run_git(cwd, ["git", "diff", "--name-only"])
        stat = self._run_git(cwd, ["git", "diff", "--stat"])
        raw = self._run_git(cwd, ["git", "diff"]) if include_raw_diff else ""
        commit = self._run_git(cwd, ["git", "rev-parse", "HEAD"]).strip() or None
        changed = tuple(line.strip() for line in names.splitlines() if line.strip())
        warning = None if changed else "No changed files in working tree diff."
        return GitDiffResult(
            changed_files=changed,
            stat_text=stat.strip(),
            raw_diff=raw.strip(),
            commit=commit,
            warning=warning,
            is_git_repo=True,
        )

    def _run_git(self, cwd: Path, command: list[str]) -> str:
        completed = self._subprocess_runner(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return completed.stderr.strip()
        return completed.stdout
