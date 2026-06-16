"""Deterministic local token estimation (no external APIs)."""

from __future__ import annotations

import math
from pathlib import Path

from ex04_agent.token_efficiency.model import FileEstimate

ESTIMATION_RULE = "estimated_tokens = ceil(character_count / 4)"
DISCLAIMER = (
    "Character-based estimate only; not provider billing or tokenizer-accurate counts."
)


class TokenEstimator:
    """Estimate tokens from text using a transparent local rule."""

    def __init__(self, chars_per_token: int = 4) -> None:
        self._chars_per_token = chars_per_token

    @property
    def estimation_rule(self) -> str:
        return ESTIMATION_RULE

    def estimate_text(self, text: str) -> int:
        if not text:
            return 0
        return math.ceil(len(text) / self._chars_per_token)

    def estimate_file(self, path: Path) -> FileEstimate:
        content = path.read_text(encoding="utf-8", errors="replace")
        chars = len(content)
        return FileEstimate(str(path), chars, self.estimate_text(content))

    def estimate_paths(self, paths: list[Path]) -> tuple[FileEstimate, ...]:
        existing = [p for p in paths if p.is_file()]
        return tuple(self.estimate_file(p) for p in sorted(existing, key=lambda x: str(x)))
