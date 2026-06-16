"""Compute finding deltas between before and after phases."""

from __future__ import annotations

from collections import Counter

from ex04_agent.comparison.model import FindingDelta


def _finding_key(item: dict) -> str:
    fid = str(item.get("id", ""))
    if fid:
        return fid
    files = ",".join(sorted(item.get("affected_files", [])))
    title = str(item.get("title", ""))[:40]
    return f"{item.get('category', '')}|{files}|{title}"


def compute_finding_delta(findings_before: dict, findings_after: dict) -> FindingDelta:
    before_list = findings_before.get("findings", [])
    after_list = findings_after.get("findings", [])
    before_keys = {_finding_key(f): f for f in before_list}
    after_keys = {_finding_key(f): f for f in after_list}
    resolved = tuple(
        before_keys[k].get("title", k)
        for k in sorted(set(before_keys) - set(after_keys))
    )
    remaining = tuple(
        after_keys[k].get("title", k)
        for k in sorted(set(after_keys))
    )
    cat_b = Counter(f.get("category", "unknown") for f in before_list)
    cat_a = Counter(f.get("category", "unknown") for f in after_list)
    sev_b = Counter(f.get("severity", "unknown") for f in before_list)
    sev_a = Counter(f.get("severity", "unknown") for f in after_list)
    health_b = sum(1 for f in before_list if f.get("category") == "code_health_blocker")
    health_a = sum(1 for f in after_list if f.get("category") == "code_health_blocker")
    return FindingDelta(
        before_count=len(before_list),
        after_count=len(after_list),
        resolved_or_removed=resolved,
        remaining=remaining,
        category_before=dict(sorted(cat_b.items())),
        category_after=dict(sorted(cat_a.items())),
        severity_before=dict(sorted(sev_b.items())),
        severity_after=dict(sorted(sev_a.items())),
        code_health_before=health_b,
        code_health_after=health_a,
    )
