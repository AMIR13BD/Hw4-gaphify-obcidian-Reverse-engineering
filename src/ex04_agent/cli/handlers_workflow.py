"""CLI handlers for detect, recommend, test, compare, patch, and pipeline."""

from __future__ import annotations

import argparse
import json

from ex04_agent.agents.test_runner import TestRunnerAgent
from ex04_agent.cli.handler_io import run_guarded
from ex04_agent.sdk.sdk import Ex04Sdk


def run_detect(args: argparse.Namespace) -> int:
    def _run() -> int:
        from ex04_agent.agents.architecture_bug import ArchitectureBugAgent

        print(json.dumps(ArchitectureBugAgent().run(phase=args.phase).to_dict(), indent=2))
        return 0

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0


def run_recommend(args: argparse.Namespace) -> int:
    def _run() -> int:
        from ex04_agent.agents.recommendation import RecommendationAgent

        print(json.dumps(RecommendationAgent().run(phase=args.phase).to_dict(), indent=2))
        return 0

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0


def run_test(args: argparse.Namespace) -> int:
    def _run() -> int:
        result = TestRunnerAgent().run(phase=args.phase)
        summary = {
            "compile_status": result.compile_status,
            "ast_status": result.ast_status,
            "import_status": result.import_status,
            "target_test_status": result.target_test_status,
            "project_test_status": result.project_test_status,
            "coverage_status": result.coverage_status,
            "ruff_status": result.ruff_status,
            "failed_files_count": len(result.failed_files),
            "output_paths": result.output_paths,
        }
        print(json.dumps(summary, indent=2))
        checks = (
            result.compile_status, result.ast_status, result.project_test_status,
            result.coverage_status, result.ruff_status,
        )
        return 1 if any(s == "failed" for s in checks) else 0

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0


def run_compare(args: argparse.Namespace) -> int:
    if args.before == args.after:
        print(json.dumps({"success": False, "error": "before and after phases must differ"}, indent=2))
        return 1

    def _run() -> int:
        from ex04_agent.agents.comparison_report import ComparisonReportAgent

        summary = ComparisonReportAgent().run(before_phase=args.before, after_phase=args.after)
        print(json.dumps(summary.to_dict(), indent=2))
        return 0

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0


def run_patch(args: argparse.Namespace) -> int:
    def _run() -> int:
        from ex04_agent.agents.patch import PatchAgent

        summary = PatchAgent().run(phase=args.phase, allow_patches=args.allow_patches)
        print(json.dumps(summary.to_dict(), indent=2))
        return 0

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0


def run_pipeline(args: argparse.Namespace) -> int:
    if not args.dry_run and not Ex04Sdk().config.allow_patches:
        print(json.dumps({"success": False, "error": "Non-dry-run pipeline requires allow_patches in config"}, indent=2))
        return 1

    def _run() -> int:
        result = Ex04Sdk().run_pipeline(dry_run=args.dry_run, phase=args.phase)
        print(json.dumps(result.to_dict(), indent=2))
        return 0 if result.success else 1

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0


def run_token_report(args: argparse.Namespace) -> int:
    def _run() -> int:
        summary = Ex04Sdk().run_token_report(phase=args.phase)
        print(json.dumps(summary.to_dict(), indent=2))
        return 0

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0
