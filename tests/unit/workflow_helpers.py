"""Shared fixtures for workflow test modules."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.graph.graphify_run_result import GraphifyRunResult
from ex04_agent.testing.model import CommandResult, RegressionResult


def graphify_result() -> GraphifyRunResult:
    return GraphifyRunResult(
        success=True,
        phase="before",
        command=("graphify", "update", "."),
        cwd="/tmp/repo",
        return_code=0,
        graphify_cli="graphify",
        graphify_cli_path="/bin/graphify",
        target_repo_path="/tmp/repo",
        stdout="ok",
        stderr="",
        copied_artifacts=("graph.json",),
        missing_required_artifacts=(),
        missing_optional_artifacts=(),
        artifact_dest_dir="/tmp/artifacts/graph/before",
        log_path="/tmp/log.txt",
        metadata_path="/tmp/meta.json",
        timestamp="2026-01-01T00:00:00+00:00",
    )


def regression_result(metrics_dir: Path) -> RegressionResult:
    return RegressionResult(
        phase="before", target_repo_path="/repo",
        commands_run=(CommandResult("p", "pytest", "/", 0, "/o", "/e", "passed", 1.0),),
        compile_status="passed", ast_status="passed", import_status="skipped",
        target_test_status="skipped", project_test_status="passed",
        coverage_status="passed", ruff_status="passed",
        failed_files=(), passed_files=(), skipped_checks=(), warnings=(),
        output_paths={
            "json": str(metrics_dir / "regression_before.json"),
            "md": str(metrics_dir / "regression_before.md"),
        },
    )
