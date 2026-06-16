"""Tests for regression test result models."""

from __future__ import annotations

from ex04_agent.testing.model import CommandResult, RegressionResult


def _make_cmd(status: str = "passed") -> CommandResult:
    return CommandResult(
        name="pytest", command="uv run pytest", cwd="/tmp",
        return_code=0 if status == "passed" else 1,
        stdout_path="/tmp/out.txt", stderr_path="/tmp/err.txt",
        status=status, duration_seconds=1.5,  # type: ignore[arg-type]
    )


def test_command_result_serializes() -> None:
    cmd = _make_cmd("passed")
    d = cmd.to_dict()
    assert d["name"] == "pytest"
    assert d["status"] == "passed"
    assert d["duration_seconds"] == 1.5


def test_regression_result_serializes() -> None:
    result = RegressionResult(
        phase="before",
        target_repo_path="/repo",
        commands_run=(_make_cmd("passed"),),
        compile_status="passed",
        ast_status="passed",
        import_status="skipped",
        target_test_status="skipped",
        project_test_status="passed",
        coverage_status="passed",
        ruff_status="passed",
        failed_files=(),
        passed_files=("a.py",),
        skipped_checks=("safe import skipped",),
        warnings=("no test suite",),
        output_paths={"json": "out.json", "md": "out.md"},
    )
    d = result.to_dict()
    assert d["phase"] == "before"
    assert d["compile_status"] == "passed"
    assert d["target_test_status"] == "skipped"
    assert d["warnings"] == ["no test suite"]
    assert len(d["commands_run"]) == 1
