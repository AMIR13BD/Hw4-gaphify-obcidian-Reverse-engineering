"""Orchestrate deterministic architecture detection."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ex04_agent.detection.detectors import run_all_detectors
from ex04_agent.detection.finding import ArchitectureFinding
from ex04_agent.detection.report_writer import FindingsSummary, ReportWriter
from ex04_agent.detection.source_scanner import SourceScanner
from ex04_agent.shared.config import AppConfig


@dataclass
class DetectionInputs:
    """Resolved input paths for detection."""

    phase: str
    graph_path: Path
    metrics_path: Path
    hotmd_path: Path
    story_path: Path
    repo_root: Path


class ArchitectureDetectionEngine:
    """Run detectors and write findings reports."""

    def __init__(self, config: AppConfig, writer: ReportWriter | None = None) -> None:
        self._config = config
        self._writer = writer or ReportWriter()

    def run(self, *, phase: str = "before") -> FindingsSummary:
        inputs = self._resolve_inputs(phase)
        self._require_file(inputs.metrics_path, "metrics")
        self._require_file(inputs.graph_path, "graph")
        metrics = json.loads(inputs.metrics_path.read_text(encoding="utf-8"))
        scanner = SourceScanner(inputs.repo_root)
        findings = run_all_detectors(metrics, scanner, inputs.repo_root)
        json_path = self._findings_json_path(phase)
        md_path = self._findings_md_path(phase)
        latest = self._config.project_root / "reports" / "architecture" / "findings.json"
        return self._writer.write(
            findings,
            phase=phase,
            json_path=json_path,
            markdown_path=md_path,
            latest_json_path=latest,
        )

    def findings_as_dicts(self, findings: list[ArchitectureFinding]) -> list[dict[str, Any]]:
        return [item.to_dict() for item in findings]

    def _resolve_inputs(self, phase: str) -> DetectionInputs:
        root = self._config.project_root
        return DetectionInputs(
            phase=phase,
            graph_path=root / "artifacts" / "graph" / phase / "graph.json",
            metrics_path=root / "reports" / "architecture" / f"metrics_{phase}.json",
            hotmd_path=root / "obsidian" / "hot.md",
            story_path=root / "reports" / "architecture" / f"story_{phase}.md",
            repo_root=self._config.target_repo_path,
        )

    def _findings_json_path(self, phase: str) -> Path:
        return self._config.project_root / "reports" / "architecture" / f"findings_{phase}.json"

    def _findings_md_path(self, phase: str) -> Path:
        return self._config.project_root / "reports" / "architecture" / f"findings_{phase}.md"

    @staticmethod
    def _require_file(path: Path, label: str) -> None:
        if not path.is_file():
            msg = f"Required {label} file not found: {path}"
            raise FileNotFoundError(msg)
