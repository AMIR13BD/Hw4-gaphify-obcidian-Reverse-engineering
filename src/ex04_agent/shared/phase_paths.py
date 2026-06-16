"""Phase-scoped report paths and write guards."""

from __future__ import annotations

from pathlib import Path


def architecture_report_path(root: Path, stem: str, phase: str, ext: str) -> Path:
    """Return reports/architecture/{stem}_{phase}.{ext}."""
    if phase not in {"before", "after"}:
        msg = f"Invalid phase {phase!r}; expected 'before' or 'after'"
        raise ValueError(msg)
    return root / "reports" / "architecture" / f"{stem}_{phase}.{ext}"


def ensure_phase_write_path(path: Path, phase: str) -> None:
    """Refuse after-phase writes that would overwrite before artifacts."""
    if phase == "after" and "_before." in path.name:
        msg = f"After-phase run must not write before artifact: {path.name}"
        raise ValueError(msg)
    expected_token = f"_{phase}."
    if expected_token not in path.name:
        msg = f"Path {path.name} does not match phase {phase!r}"
        raise ValueError(msg)
