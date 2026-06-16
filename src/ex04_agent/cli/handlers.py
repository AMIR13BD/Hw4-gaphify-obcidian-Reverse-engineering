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
    """Execute the health subcommand."""
    status = Ex04Sdk().health_check()
    print(json.dumps(status.to_dict(), indent=2))
    return 0


def run_graphify(args: argparse.Namespace) -> int:
    """Execute the graphify subcommand."""
    try:
        result = GraphifyRunnerAgent().run(phase=args.phase)
    except ValueError as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result.to_dict(), indent=2))
    if not result.success:
        message = result.error or "Graphify run failed"
        print(message, file=sys.stderr)
        return 1
    return 0


def run_parse(args: argparse.Namespace) -> int:
    """Execute the parse subcommand."""
    try:
        agent = GraphParserAgent()
        report = agent.run(
            phase=args.phase,
            graph_path=args.graph_path,
            output_path=args.output_path,
        )
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1

    print(agent.terminal_summary(report))
    return 0


def run_obsidian(args: argparse.Namespace) -> int:
    """Execute the obsidian subcommand."""
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
    """Execute the hotmd subcommand."""
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
    """Execute the detect subcommand."""
    from ex04_agent.agents.architecture_bug import ArchitectureBugAgent

    try:
        summary = ArchitectureBugAgent().run(phase=args.phase)
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(summary.to_dict(), indent=2))
    return 0


def run_pipeline(args: argparse.Namespace) -> int:
    """Execute the pipeline subcommand."""
    dry_run = args.dry_run
    if not dry_run and not Ex04Sdk().config.allow_patches:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": "Non-dry-run pipeline requires allow_patches in config",
                },
                indent=2,
            )
        )
        return 1
    try:
        result = Ex04Sdk().run_pipeline(dry_run=dry_run, phase=args.phase)
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.success else 1
