"""Shared fixtures for regression test modules."""

from __future__ import annotations

from ex04_agent.testing.model import CommandResult, RegressionResult


def make_regression_result(phase: str = "before") -> RegressionResult:
    cmd = CommandResult(
        name="pytest", command="uv run pytest", cwd="/tmp",
        return_code=0, stdout_path="/tmp/out.txt", stderr_path="/tmp/err.txt",
        status="passed", duration_seconds=1.0,
    )
    return RegressionResult(
        phase=phase, target_repo_path="/repo",
        commands_run=(cmd,),
        compile_status="passed", ast_status="passed",
        import_status="skipped", target_test_status="skipped",
        project_test_status="passed", coverage_status="passed",
        ruff_status="passed",
        failed_files=(), passed_files=("a.py",),
        skipped_checks=("import skipped",),
        warnings=("no test suite",),
        output_paths={"json": "out.json", "md": "out.md"},
    )
