"""Shared CLI output helpers."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def print_error(exc: BaseException) -> None:
    print(json.dumps({"success": False, "error": str(exc)}, indent=2))


def run_guarded(action: Callable[[], T], *, errors: tuple[type[BaseException], ...] = (ValueError, FileNotFoundError, OSError)) -> T | int:
    try:
        return action()
    except errors as exc:
        print_error(exc)
        return 1
