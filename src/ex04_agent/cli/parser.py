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
    run_patch,
    run_pipeline,
    run_recommend,
    run_test,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ex04-agent", description="EX04 graph-guided reverse engineering agent")
    sp = parser.add_subparsers(dest="command", required=True)
    sp.add_parser("health", help="Print scaffold health check").set_defaults(func=run_health)
    _phase_only(sp.add_parser("graphify", help="Run Graphify update and collect graph artifacts"), run_graphify)

    parse = sp.add_parser("parse", help="Parse graph.json and compute architecture metrics")
    _add_phase(parse)
    parse.add_argument("--graph-path", default=None, help="Override input graph.json path")
    parse.add_argument("--output-path", default=None, help="Override metrics output JSON path")
    parse.set_defaults(func=run_parse)

    obsidian = sp.add_parser("obsidian", help="Generate Obsidian vault from graph metrics")
    _add_phase(obsidian)
    obsidian.add_argument("--metrics-path", default=None)
    obsidian.add_argument("--graph-path", default=None)
    obsidian.add_argument("--graph-report-path", default=None)
    obsidian.add_argument("--vault-dir", default=None)
    obsidian.add_argument("--dynamic-hot", action="store_true")
    obsidian.set_defaults(func=run_obsidian)

    hotmd = sp.add_parser("hotmd", help="Generate dynamic hot.md from graph metrics and git diff")
    _add_phase(hotmd)
    hotmd.add_argument("--metrics-path", default=None)
    hotmd.add_argument("--graph-path", default=None)
    hotmd.add_argument("--hot-path", default=None)
    hotmd.add_argument("--snapshot-dir", default=None)
    hotmd.add_argument("--failing-test", action="append", default=None)
    hotmd.set_defaults(func=run_hotmd)

    _phase_only(sp.add_parser("detect", help="Detect architecture findings from graph and source"), run_detect)
    _phase_only(sp.add_parser("recommend", help="Generate recommendations from findings"), run_recommend)
    _phase_only(sp.add_parser("test", help="Run regression validation on patched target files"), run_test)
    patch = sp.add_parser("patch", help="Apply safe patches from patch plan")
    _add_phase(patch)
    patch.add_argument("--allow-patches", action="store_true", default=False,
                       help="Actually modify target repo files (default: dry-run)")
    patch.set_defaults(func=run_patch)
    pipe = sp.add_parser("pipeline", help="Run LangGraph multi-agent pipeline")
    _add_phase(pipe)
    pipe.add_argument("--dry-run", action="store_true", default=True)
    pipe.add_argument("--no-dry-run", action="store_false", dest="dry_run")
    pipe.set_defaults(func=run_pipeline)
    return parser


def _phase_only(parser: argparse.ArgumentParser, handler) -> None:
    _add_phase(parser)
    parser.set_defaults(func=handler)


def _add_phase(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--phase", default="before", choices=["before", "after"])
