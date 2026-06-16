"""CLI argument parser for ex04-agent."""

from __future__ import annotations

import argparse

from ex04_agent.cli.handlers import (
    run_detect,
    run_graphify,
    run_health,
    run_hotmd,
    run_obsidian,
    run_parse,
    run_pipeline,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""
    parser = argparse.ArgumentParser(
        prog="ex04-agent",
        description="EX04 graph-guided reverse engineering agent",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    health_parser = subparsers.add_parser("health", help="Print scaffold health check")
    health_parser.set_defaults(func=run_health)

    graphify_parser = subparsers.add_parser(
        "graphify",
        help="Run Graphify update and collect graph artifacts",
    )
    graphify_parser.add_argument(
        "--phase",
        default="before",
        choices=["before", "after"],
        help="Artifact phase directory (default: before)",
    )
    graphify_parser.set_defaults(func=run_graphify)

    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse graph.json and compute architecture metrics",
    )
    parse_parser.add_argument(
        "--phase",
        default="before",
        choices=["before", "after"],
        help="Graph phase directory (default: before)",
    )
    parse_parser.add_argument("--graph-path", default=None, help="Override input graph.json path")
    parse_parser.add_argument("--output-path", default=None, help="Override metrics output JSON path")
    parse_parser.set_defaults(func=run_parse)

    obsidian_parser = subparsers.add_parser(
        "obsidian",
        help="Generate Obsidian vault from graph metrics",
    )
    obsidian_parser.add_argument(
        "--phase",
        default="before",
        choices=["before", "after"],
        help="Artifact phase (default: before)",
    )
    obsidian_parser.add_argument("--metrics-path", default=None, help="Override metrics JSON path")
    obsidian_parser.add_argument("--graph-path", default=None, help="Override graph.json path")
    obsidian_parser.add_argument(
        "--graph-report-path",
        default=None,
        help="Override GRAPH_REPORT.md path",
    )
    obsidian_parser.add_argument("--vault-dir", default=None, help="Override output vault directory")
    obsidian_parser.add_argument(
        "--dynamic-hot",
        action="store_true",
        help="Also regenerate dynamic hot.md after vault build",
    )
    obsidian_parser.set_defaults(func=run_obsidian)

    hotmd_parser = subparsers.add_parser(
        "hotmd",
        help="Generate dynamic hot.md from graph metrics and git diff",
    )
    hotmd_parser.add_argument(
        "--phase",
        default="before",
        choices=["before", "after"],
        help="Artifact phase (default: before)",
    )
    hotmd_parser.add_argument("--metrics-path", default=None, help="Override metrics JSON path")
    hotmd_parser.add_argument("--graph-path", default=None, help="Override graph.json path")
    hotmd_parser.add_argument("--hot-path", default=None, help="Override output hot.md path")
    hotmd_parser.add_argument("--snapshot-dir", default=None, help="Override snapshot directory")
    hotmd_parser.add_argument(
        "--failing-test",
        action="append",
        default=None,
        help="Optional failing test file path (repeatable)",
    )
    hotmd_parser.set_defaults(func=run_hotmd)

    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Run LangGraph multi-agent pipeline",
    )
    pipeline_parser.add_argument(
        "--phase",
        default="before",
        choices=["before", "after"],
        help="Pipeline phase (default: before)",
    )
    pipeline_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Safe dry-run mode (default: true)",
    )
    pipeline_parser.add_argument(
        "--no-dry-run",
        action="store_false",
        dest="dry_run",
        help="Disable dry-run (patching still gated by config)",
    )
    pipeline_parser.set_defaults(func=run_pipeline)

    detect_parser = subparsers.add_parser(
        "detect",
        help="Detect architecture findings from graph and source",
    )
    detect_parser.add_argument(
        "--phase",
        default="before",
        choices=["before", "after"],
        help="Detection phase (default: before)",
    )
    detect_parser.set_defaults(func=run_detect)

    return parser
