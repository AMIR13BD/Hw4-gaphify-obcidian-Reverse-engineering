"""CLI handlers for graph, parse, and Obsidian commands."""

from __future__ import annotations

import argparse
import json
import sys

from ex04_agent.agents.graph_parser import GraphParserAgent
from ex04_agent.agents.graphify_runner import GraphifyRunnerAgent
from ex04_agent.agents.obsidian_vault import ObsidianVaultAgent
from ex04_agent.cli.handler_io import print_error, run_guarded
from ex04_agent.sdk.sdk import Ex04Sdk


def run_health(_: argparse.Namespace) -> int:
    print(json.dumps(Ex04Sdk().health_check().to_dict(), indent=2))
    return 0


def run_graphify(args: argparse.Namespace) -> int:
    try:
        result = GraphifyRunnerAgent().run(phase=args.phase)
    except ValueError as exc:
        print_error(exc)
        return 1
    print(json.dumps(result.to_dict(), indent=2))
    if not result.success:
        print(result.error or "Graphify run failed", file=sys.stderr)
        return 1
    return 0


def run_parse(args: argparse.Namespace) -> int:
    def _run() -> int:
        agent = GraphParserAgent()
        print(agent.terminal_summary(agent.run(
            phase=args.phase, graph_path=args.graph_path, output_path=args.output_path,
        )))
        return 0

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0


def run_obsidian(args: argparse.Namespace) -> int:
    def _run() -> int:
        result = ObsidianVaultAgent().run(
            phase=args.phase,
            metrics_path=args.metrics_path,
            graph_path=args.graph_path,
            graph_report_path=args.graph_report_path,
            vault_dir=args.vault_dir,
            dynamic_hot=args.dynamic_hot,
        )
        print(json.dumps(result.to_dict(), indent=2))
        return 0 if result.success else 1

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0


def run_hotmd(args: argparse.Namespace) -> int:
    def _run() -> int:
        result = ObsidianVaultAgent().run_dynamic_hotmd(
            phase=args.phase,
            metrics_path=args.metrics_path,
            graph_path=args.graph_path,
            hot_path=args.hot_path,
            snapshot_dir=args.snapshot_dir,
            failing_test_files=tuple(args.failing_test or ()),
        )
        print(json.dumps(result.to_dict(), indent=2))
        return 0 if result.success else 1

    result = run_guarded(_run)
    return result if isinstance(result, int) else 0
