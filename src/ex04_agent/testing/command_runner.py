"""Run shell commands and capture output to artifact files."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from ex04_agent.testing.model import CommandResult


def run_command(
    name: str,
    args: list[str],
    *,
    cwd: Path,
    artifact_dir: Path,
    timeout: int = 120,
) -> CommandResult:
    """Run a command, write stdout/stderr to files, return CommandResult."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stem = name.replace(" ", "_")
    stdout_path = artifact_dir / f"{stem}_stdout.txt"
    stderr_path = artifact_dir / f"{stem}_stderr.txt"
    start = time.monotonic()
    try:
        proc = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        rc = proc.returncode
        stdout_path.write_text(proc.stdout or "", encoding="utf-8")
        stderr_path.write_text(proc.stderr or "", encoding="utf-8")
    except subprocess.TimeoutExpired:
        rc = -1
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(f"Command timed out after {timeout}s", encoding="utf-8")
    except OSError as exc:
        rc = -1
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(str(exc), encoding="utf-8")
    elapsed = round(time.monotonic() - start, 2)
    status = "passed" if rc == 0 else "failed"
    return CommandResult(
        name=name,
        command=" ".join(args),
        cwd=str(cwd),
        return_code=rc,
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        status=status,
        duration_seconds=elapsed,
    )
