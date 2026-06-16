"""CLI entry point for the EX04 agent."""

from __future__ import annotations

import sys

from ex04_agent.cli.parser import build_parser


def main(argv: list[str] | None = None) -> int:
    """CLI main entry."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
