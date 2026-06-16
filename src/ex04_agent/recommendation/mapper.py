"""Deterministic finding-to-recommendation mapping."""

from __future__ import annotations

from ex04_agent.recommendation.model import ArchitectureRecommendation


def map_finding(finding: dict, index: int) -> ArchitectureRecommendation:
    category = str(finding.get("category", "unknown"))
    base = _rules(category, finding)
    return ArchitectureRecommendation(
        id=f"rec_{index:03d}_{finding['id']}",
        finding_id=str(finding["id"]),
        title=base["title"],
        category=category,
        action_type=base["action_type"],
        priority=base["priority"],
        confidence=str(finding.get("confidence", "medium")),
        rationale=base["rationale"],
        proposed_change=base["proposed_change"],
        affected_files=tuple(finding.get("affected_files", ())),
        risk_level=base["risk_level"],
        preconditions=tuple(base["preconditions"]),
        validation_steps=tuple(base["validation_steps"]),
        blocked_by=tuple(base["blocked_by"]),
        phase10_patchable=base["phase10_patchable"],
        evidence_summary=str(finding.get("source_validation", "")),
    )


def _rules(category: str, finding: dict) -> dict:
    if category == "code_health_blocker":
        return _build("review_required", "critical", True, "high", finding, "Remove compile blocker with minimal syntax modernization.")
    if category == "mixed_responsibility":
        return _build("review_required", "high", False, "high", finding, "Separate domain logic from drawing/input and top-level execution.")
    if category == "import_script_mixing":
        return _build("review_required", "high", True, "medium", finding, "Add safe main guard or move top-level calls into entrypoint.")
    if category == "hidden_global_state":
        return _build("review_required", "medium", True, "medium", finding, "Use function parameters consistently instead of global variables.")
    if category == "possible_hub":
        return _build("review_required", "medium", False, "medium", finding, "Inspect responsibility boundaries before structural refactor.")
    if category == "documentation_hub":
        return _build("docs_only", "low", False, "low", finding, "Document this as a knowledge hub, not a code bottleneck.")
    if category == "navigation_scope":
        return _build("docs_only", "low", False, "low", finding, "Document disconnected components as expected tutorial scope.")
    if category == "organization":
        return _build("docs_only", "low", False, "low", finding, "Document tutorial versioning or move variants under examples.")
    return _build("defer", "low", False, "low", finding, "No deterministic mapping rule; defer to manual review.")


def _build(action: str, priority: str, patchable: bool, risk: str, finding: dict, change: str) -> dict:
    return {
        "title": f"Recommendation for {finding['title']}",
        "action_type": action,
        "priority": priority,
        "risk_level": risk,
        "rationale": f"Mapped from category `{finding.get('category')}` with deterministic phase-9 policy.",
        "proposed_change": change,
        "preconditions": ("Phase 9 does not modify the target repository.",),
        "validation_steps": tuple(finding.get("next_validation_steps", ())),
        "blocked_by": () if patchable else ("Needs manual approval for Phase 10 changes.",),
        "phase10_patchable": patchable,
    }
