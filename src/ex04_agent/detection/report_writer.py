"""Write architecture findings to JSON and Markdown."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ex04_agent.detection.finding import ArchitectureFinding


@dataclass(frozen=True)
class FindingsSummary:
    """Aggregate counts for findings output."""

    finding_count: int
    by_category: dict[str, int]
    by_severity: dict[str, int]
    high_confidence_count: int
    json_path: str
    markdown_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_count": self.finding_count,
            "by_category": self.by_category,
            "by_severity": self.by_severity,
            "high_confidence_count": self.high_confidence_count,
            "json_path": self.json_path,
            "markdown_path": self.markdown_path,
        }


class ReportWriter:
    """Serialize findings to JSON and Markdown reports."""

    def write(
        self,
        findings: list[ArchitectureFinding],
        *,
        phase: str,
        json_path: Path,
        markdown_path: Path,
        latest_json_path: Path | None = None,
    ) -> FindingsSummary:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "phase": phase,
            "finding_count": len(findings),
            "findings": [item.to_dict() for item in findings],
        }
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if latest_json_path is not None:
            latest_json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        markdown_path.write_text(self._render_markdown(phase, findings), encoding="utf-8")
        categories = Counter(item.category for item in findings)
        severities = Counter(item.severity for item in findings)
        high_conf = sum(1 for item in findings if item.confidence == "high")
        return FindingsSummary(
            finding_count=len(findings),
            by_category=dict(sorted(categories.items())),
            by_severity=dict(sorted(severities.items())),
            high_confidence_count=high_conf,
            json_path=str(json_path),
            markdown_path=str(markdown_path),
        )

    def _render_markdown(self, phase: str, findings: list[ArchitectureFinding]) -> str:
        lines = [
            f"# Architecture Findings — {phase}",
            "",
            "_Candidate architecture issues only. Validate in source before acting._",
            "",
            "## Summary",
            "",
            f"- Total findings: **{len(findings)}**",
            "",
            "| Category | Count |",
            "| --- | ---: |",
        ]
        categories = Counter(item.category for item in findings)
        for category, count in sorted(categories.items()):
            lines.append(f"| `{category}` | {count} |")
        grouped: dict[str, list[ArchitectureFinding]] = {}
        for item in findings:
            grouped.setdefault(item.category, []).append(item)
        for category in sorted(grouped):
            lines.extend(["", f"## {category}", ""])
            for item in grouped[category]:
                lines.extend(self._render_finding(item))
        lines.extend(
            [
                "",
                "## Phase 9 Note",
                "",
                "Recommendations are not included here. Phase 9 should map validated findings to actions.",
            ]
        )
        return "\n".join(lines) + "\n"

    def _render_finding(self, item: ArchitectureFinding) -> list[str]:
        return [
            f"### {item.title}",
            "",
            f"- **Detector:** `{item.detector}`",
            f"- **Severity:** `{item.severity}` · **Confidence:** `{item.confidence}` · **Status:** `{item.status}`",
            "",
            "**Observation**",
            "",
            item.observation,
            "",
            "**Relation**",
            "",
            item.relation,
            "",
            "**Confidence**",
            "",
            item.confidence_reason,
            "",
            "**Context**",
            "",
            item.context,
            "",
            "**Source validation**",
            "",
            item.source_validation,
            "",
            "**Evidence**",
            "",
            *(
                f"- `{ev.kind}` {ev.path or ''} {ev.detail}"
                + (f" (L{ev.start_line})" if ev.start_line else "")
                for ev in item.evidence
            ),
            "",
            "**Next validation steps**",
            "",
            *[f"- {step}" for step in item.next_validation_steps],
            "",
        ]
