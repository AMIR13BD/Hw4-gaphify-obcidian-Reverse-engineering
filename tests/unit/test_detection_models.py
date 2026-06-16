"""Tests for ArchitectureFinding / EvidenceItem models."""

from __future__ import annotations

from ex04_agent.detection.finding import ArchitectureFinding, EvidenceItem


def test_finding_serializes_to_json() -> None:
    """ArchitectureFinding converts to JSON-friendly dict."""
    finding = ArchitectureFinding(
        id="x",
        title="t",
        detector="d",
        category="c",
        severity="low",
        confidence="medium",
        status="candidate",
        observation="obs",
        relation="rel",
        confidence_reason="reason",
        context="ctx",
        affected_nodes=(),
        affected_files=("a.py",),
        evidence=(EvidenceItem("source", "a.py", 1, 2, "detail"),),
        source_validation="pending",
        next_validation_steps=("step",),
    )
    payload = finding.to_dict()
    assert payload["id"] == "x"
    assert payload["evidence"][0]["kind"] == "source"
