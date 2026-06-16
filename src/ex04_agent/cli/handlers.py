"""CLI command handlers for ex04-agent."""

from __future__ import annotations

import argparse
import json
import sys

from ex04_agent.agents.graph_parser import GraphParserAgent
from ex04_agent.agents.graphify_runner import GraphifyRunnerAgent
from ex04_agent.agents.obsidian_vault import ObsidianVaultAgent
from ex04_agent.sdk.sdk import Ex04Sdk


def run_health(_: argparse.Namespace) -> int:
    print(json.dumps(Ex04Sdk().health_check().to_dict(), indent=2))
    return 0


def run_graphify(args: argparse.Namespace) -> int:
    try:
        result = GraphifyRunnerAgent().run(phase=args.phase)
    except ValueError as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result.to_dict(), indent=2))
    if not result.success:
        print(result.error or "Graphify run failed", file=sys.stderr)
        return 1
    return 0


def run_parse(args: argparse.Namespace) -> int:
    try:
        agent = GraphParserAgent()
        print(agent.terminal_summary(agent.run(phase=args.phase, graph_path=args.graph_path, output_path=args.output_path)))
        return 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1


def run_obsidian(args: argparse.Namespace) -> int:
    try:
        result = ObsidianVaultAgent().run(
            phase=args.phase,
            metrics_path=args.metrics_path,
            graph_path=args.graph_path,
            graph_report_path=args.graph_report_path,
            vault_dir=args.vault_dir,
            dynamic_hot=args.dynamic_hot,
        )
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.success else 1


def run_hotmd(args: argparse.Namespace) -> int:
    try:
        result = ObsidianVaultAgent().run_dynamic_hotmd(
            phase=args.phase,
            metrics_path=args.metrics_path,
            graph_path=args.graph_path,
            hot_path=args.hot_path,
            snapshot_dir=args.snapshot_dir,
            failing_test_files=tuple(args.failing_test or ()),
        )
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.success else 1


def run_detect(args: argparse.Namespace) -> int:
    from ex04_agent.agents.architecture_bug import ArchitectureBugAgent

    try:
        print(json.dumps(ArchitectureBugAgent().run(phase=args.phase).to_dict(), indent=2))
        return 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1


def run_recommend(args: argparse.Namespace) -> int:
    from ex04_agent.agents.recommendation import RecommendationAgent

    try:
        print(json.dumps(RecommendationAgent().run(phase=args.phase).to_dict(), indent=2))
        return 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1


def run_test(args: argparse.Namespace) -> int:
    from ex04_agent.agents.test_runner import TestRunnerAgent

    try:
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
        checks = (result.compile_status, result.ast_status, result.project_test_status, result.coverage_status, result.ruff_status)
        return 1 if any(s == "failed" for s in checks) else 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1


def run_patch(args: argparse.Namespace) -> int:
    from ex04_agent.agents.patch import PatchAgent

    try:
        summary = PatchAgent().run(phase=args.phase, allow_patches=args.allow_patches)
        print(json.dumps(summary.to_dict(), indent=2))
        return 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1


def run_pipeline(args: argparse.Namespace) -> int:
    if not args.dry_run and not Ex04Sdk().config.allow_patches:
        print(json.dumps({"success": False, "error": "Non-dry-run pipeline requires allow_patches in config"}, indent=2))
        return 1
    try:
        result = Ex04Sdk().run_pipeline(dry_run=args.dry_run, phase=args.phase)
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.success else 1
