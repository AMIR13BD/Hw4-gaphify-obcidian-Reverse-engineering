"""Regression test result models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

CheckStatus = Literal["passed", "failed", "skipped"]


@dataclass
class CommandResult:
    name: str
    command: str
    cwd: str
    return_code: int
    stdout_path: str
    stderr_path: str
    status: CheckStatus
    duration_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RegressionResult:
    phase: str
    target_repo_path: str
    commands_run: tuple[CommandResult, ...]
    compile_status: CheckStatus
    ast_status: CheckStatus
    import_status: CheckStatus
    target_test_status: CheckStatus
    project_test_status: CheckStatus
    coverage_status: CheckStatus
    ruff_status: CheckStatus
    failed_files: tuple[str, ...]
    passed_files: tuple[str, ...]
    skipped_checks: tuple[str, ...]
    warnings: tuple[str, ...]
    output_paths: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "target_repo_path": self.target_repo_path,
            "commands_run": [c.to_dict() for c in self.commands_run],
            "compile_status": self.compile_status,
            "ast_status": self.ast_status,
            "import_status": self.import_status,
            "target_test_status": self.target_test_status,
            "project_test_status": self.project_test_status,
            "coverage_status": self.coverage_status,
            "ruff_status": self.ruff_status,
            "failed_files": list(self.failed_files),
            "passed_files": list(self.passed_files),
            "skipped_checks": list(self.skipped_checks),
            "warnings": list(self.warnings),
            "output_paths": self.output_paths,
        }
