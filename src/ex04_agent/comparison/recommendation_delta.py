"""Compute recommendation deltas between before and after phases."""

from __future__ import annotations

from collections import Counter

from ex04_agent.comparison.model import RecommendationDelta


def compute_recommendation_delta(rec_before: dict, rec_after: dict) -> RecommendationDelta:
    before_list = rec_before.get("recommendations", [])
    after_list = rec_after.get("recommendations", [])
    act_b = Counter(r.get("action_type", "unknown") for r in before_list)
    act_a = Counter(r.get("action_type", "unknown") for r in after_list)
    pri_b = Counter(r.get("priority", "unknown") for r in before_list)
    pri_a = Counter(r.get("priority", "unknown") for r in after_list)
    patch_b = sum(1 for r in before_list if r.get("phase10_patchable"))
    patch_a = sum(1 for r in after_list if r.get("phase10_patchable"))
    return RecommendationDelta(
        before_count=len(before_list),
        after_count=len(after_list),
        action_before=dict(sorted(act_b.items())),
        action_after=dict(sorted(act_a.items())),
        priority_before=dict(sorted(pri_b.items())),
        priority_after=dict(sorted(pri_a.items())),
        patchable_before=patch_b,
        patchable_after=patch_a,
    )
