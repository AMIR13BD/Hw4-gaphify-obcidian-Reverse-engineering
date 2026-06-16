"""Phase 11 regression test engine."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.shared.config import AppConfig
from ex04_agent.testing.command_runner import run_command
from ex04_agent.testing.discovery import discover_target
from ex04_agent.testing.model import CommandResult, RegressionResult
from ex04_agent.testing.report_writer import RegressionReportWriter
from ex04_agent.testing.result_parser import parse_coverage_percent, parse_pytest_summary
from ex04_agent.testing.validators import ast_validate, compile_validate, import_validate


class RegressionEngine:
    def __init__(self, config: AppConfig, writer: RegressionReportWriter | None = None) -> None:
        self._config = config
        self._writer = writer or RegressionReportWriter()

    def run(self, phase: str = "before") -> RegressionResult:
        if phase not in {"before", "after"}:
            msg = f"Invalid phase {phase!r}"
            raise ValueError(msg)
        repo = self._config.target_repo_path
        project = self._config.project_root
        artifact_dir = project / "artifacts" / "test_runs" / phase
        artifact_dir.mkdir(parents=True, exist_ok=True)

        discovery = discover_target(repo)
        py_files = [repo / f for f in discovery.python_files]
        warnings: list[str] = []
        skipped: list[str] = []
        commands: list[CommandResult] = []
        failed_files: list[str] = []

        # 1. Compile validation
        c_passed, c_failed = compile_validate(py_files)
        compile_status = "passed" if not c_failed else "failed"
        failed_files.extend(c_failed)

        # 2. AST validation
        a_passed, a_failed = ast_validate(py_files)
        ast_status = "passed" if not a_failed else "failed"
        for f in a_failed:
            if f not in failed_files:
                failed_files.append(f)

        # 3. Import safety check
        _imp_passed, _imp_failed, imp_skip = import_validate(py_files)
        import_status = "skipped" if imp_skip else "passed"
        if imp_skip:
            skipped.append(f"safe import skipped for {len(imp_skip)} file(s) requiring GUI/input")

        # 4. Target repo test discovery
        if not discovery.has_tests:
            target_test_status = "skipped"
            warnings.append("target repository has no dedicated test suite")
        else:
            cmd = run_command("target_pytest", discovery.test_command or [], cwd=repo, artifact_dir=artifact_dir)
            commands.append(cmd)
            target_test_status = cmd.status

        # 5. Project pytest
        pytest_cmd = run_command("pytest", ["uv", "run", "pytest"], cwd=project, artifact_dir=artifact_dir)
        commands.append(pytest_cmd)
        _p, _f, pytest_failed = parse_pytest_summary(pytest_cmd.stdout_path)
        failed_files.extend(f for f in pytest_failed if f not in failed_files)
        project_test_status = pytest_cmd.status

        # 6. Coverage
        cov_cmd = run_command("coverage", ["uv", "run", "pytest", "--cov=src", "--cov-report=term-missing"], cwd=project, artifact_dir=artifact_dir)
        commands.append(cov_cmd)
        cov_pct = parse_coverage_percent(cov_cmd.stdout_path)
        coverage_status = "passed" if cov_pct is not None and cov_pct >= 85.0 else "failed"

        # 7. Ruff
        ruff_cmd = run_command("ruff", ["uv", "run", "ruff", "check"], cwd=project, artifact_dir=artifact_dir)
        commands.append(ruff_cmd)
        ruff_status = ruff_cmd.status

        all_passed = list({*c_passed, *a_passed} - set(c_failed) - set(a_failed))
        json_path = self._rpath(f"regression_{phase}.json")
        md_path = self._rpath(f"regression_{phase}.md")
        result = RegressionResult(
            phase=phase, target_repo_path=str(repo),
            commands_run=tuple(commands),
            compile_status=compile_status, ast_status=ast_status,
            import_status=import_status, target_test_status=target_test_status,
            project_test_status=project_test_status,
            coverage_status=coverage_status, ruff_status=ruff_status,
            failed_files=tuple(failed_files), passed_files=tuple(all_passed),
            skipped_checks=tuple(skipped), warnings=tuple(warnings),
            output_paths={"json": str(json_path), "md": str(md_path)},
        )
        self._writer.write(result, json_path=json_path, md_path=md_path, latest_path=self._rpath("regression.json"))
        return result

    def _rpath(self, name: str) -> Path:
        return self._config.project_root / "reports" / "tests" / name
