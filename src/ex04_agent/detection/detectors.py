"""Architecture detector registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ex04_agent.detection.detectors_graph import (
    detect_disconnected_components,
    detect_god_nodes,
    detect_low_confidence_edges,
)
from ex04_agent.detection.detectors_source import (
    detect_hidden_globals,
    detect_mixed_responsibility,
    detect_top_level_side_effects,
)
from ex04_agent.detection.detectors_source_extra import (
    detect_duplicate_evolution,
    detect_execution_blockers,
)
from ex04_agent.detection.finding import ArchitectureFinding
from ex04_agent.detection.source_scanner import SourceScanner


def run_all_detectors(
    metrics: dict[str, Any],
    scanner: SourceScanner,
    repo_root: Path,
) -> list[ArchitectureFinding]:
    """Run all deterministic detectors and return findings."""
    findings: list[ArchitectureFinding] = []
    findings.extend(detect_god_nodes(metrics))
    findings.extend(detect_disconnected_components(metrics))
    findings.extend(detect_low_confidence_edges(metrics))
    findings.extend(detect_mixed_responsibility(scanner))
    findings.extend(detect_top_level_side_effects(scanner))
    findings.extend(detect_hidden_globals(scanner))
    findings.extend(detect_execution_blockers(scanner))
    findings.extend(detect_duplicate_evolution(scanner, repo_root))
    return findings
