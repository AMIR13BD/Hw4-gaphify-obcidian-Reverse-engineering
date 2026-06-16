"""Deterministic recommendation ordering."""

from __future__ import annotations

from ex04_agent.recommendation.model import ArchitectureRecommendation

PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
STATUS_RANK = {"validated_by_source": 0, "needs_manual_validation": 1, "candidate": 2}
CATEGORY_RANK = {"code_health_blocker": 0}


def sort_recommendations(items: list[ArchitectureRecommendation], finding_by_id: dict[str, dict]) -> list[ArchitectureRecommendation]:
    def key(item: ArchitectureRecommendation) -> tuple:
        finding = finding_by_id.get(item.finding_id, {})
        docs_penalty = 1 if item.action_type == "docs_only" else 0
        return (
            PRIORITY_RANK.get(item.priority, 9),
            SEVERITY_RANK.get(str(finding.get("severity", "medium")), 9),
            STATUS_RANK.get(str(finding.get("status", "needs_manual_validation")), 9),
            CATEGORY_RANK.get(str(finding.get("category", "")), 5),
            docs_penalty,
            item.id,
        )

    return sorted(items, key=key)
