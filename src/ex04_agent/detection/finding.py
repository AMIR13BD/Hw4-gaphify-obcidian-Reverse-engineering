"""Architecture finding models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

Severity = Literal["low", "medium", "high"]
FindingConfidence = Literal["low", "medium", "high"]
FindingStatus = Literal["candidate", "validated_by_source", "needs_manual_validation"]
EvidenceKind = Literal["graph", "metric", "source", "report", "hotmd"]


@dataclass(frozen=True)
class EvidenceItem:
    """Structured evidence supporting a finding."""

    kind: EvidenceKind
    path: str | None
    start_line: int | None
    end_line: int | None
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArchitectureFinding:
    """Deterministic architecture or code-health finding."""

    id: str
    title: str
    detector: str
    category: str
    severity: Severity
    confidence: FindingConfidence
    status: FindingStatus
    observation: str
    relation: str
    confidence_reason: str
    context: str
    affected_nodes: tuple[str, ...]
    affected_files: tuple[str, ...]
    evidence: tuple[EvidenceItem, ...]
    source_validation: str
    next_validation_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence"] = [item.to_dict() for item in self.evidence]
        return payload
