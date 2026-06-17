"""Load only graph-guided context files for LLM review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GraphGuidedContext:
    """Bundled graph-guided context for one LLM prompt."""

    phase: str
    files: tuple[tuple[str, str], ...]
    combined_text: str
    character_count: int


def context_paths(root: Path, phase: str) -> tuple[Path, ...]:
    """Return the only files allowed for graph-guided LLM review."""
    if phase not in {"before", "after"}:
        msg = f"Invalid phase {phase!r}; expected 'before' or 'after'"
        raise ValueError(msg)
    return (
        root / "obsidian" / "hot.md",
        root / "obsidian" / "index.md",
        root / "reports" / "architecture" / f"findings_{phase}.md",
        root / "reports" / "architecture" / f"recommendations_{phase}.md",
    )


def load_graph_guided_context(root: Path, phase: str) -> GraphGuidedContext:
    """Read graph-guided files only; fail if any required file is missing."""
    paths = context_paths(root, phase)
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        msg = f"Missing graph-guided context file(s): {', '.join(missing)}"
        raise FileNotFoundError(msg)

    parts: list[tuple[str, str]] = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        parts.append((rel, path.read_text(encoding="utf-8", errors="replace")))

    combined = "\n\n".join(f"## File: {rel}\n\n{body}" for rel, body in parts)
    return GraphGuidedContext(
        phase=phase,
        files=tuple(parts),
        combined_text=combined,
        character_count=len(combined),
    )
