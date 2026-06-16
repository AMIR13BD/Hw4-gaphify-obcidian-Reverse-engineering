# Phase 13 — Before/After Comparison Report (Repaired)

**Date:** 2026-06-16  
**Phase:** 13 — Deterministic before/after comparison (read-only on architecture artifacts)

---

## Repair Summary

### Problem

Phase 13 validation runs (`pipeline --dry-run --phase before` and full after pipeline) regenerated **before** artifacts from the patched target repo, overwriting the frozen Phase 12 baseline:

- `artifacts/graph/before/graph.json` — 25 nodes / 19 links (wrong)
- `reports/architecture/metrics_before.json` — 25 / 19 (wrong)
- `reports/architecture/findings_before.*` — 8 findings (wrong)
- `reports/architecture/recommendations_before.*` — 8 recommendations (wrong)
- `reports/architecture/patch_plan_before.*` — after-style plan (wrong)

Root cause: `pipeline --dry-run --phase before` re-ran graphify/detect/recommend against the patched repo. After dry-run also re-ran artifact generators unnecessarily.

### Repair actions

1. Restored all before artifacts from commit `3e33309` (Phase 12 done).
2. Added `src/ex04_agent/workflow/comparison_mode.py` — **comparison-only** after dry-run skips graphify, parse, obsidian, detect, recommend, patch, and test_runner when both before/after artifact sets exist.
3. Extended `ComparisonLoader` with `before_artifacts_exist()` and `comparison_ready()`.
4. Added `tests/unit/test_comparison_readonly.py` — compare and pipeline after must not modify before architecture files.

---

## Files Created / Changed

### Comparison module (Phase 13)

- `src/ex04_agent/comparison/` — engine, loader, deltas, report writer
- `src/ex04_agent/workflow/comparison_mode.py` — comparison-only pipeline guard
- `src/ex04_agent/agents/comparison_report.py` — wired to comparison engine
- `src/ex04_agent/workflow/pipeline_nodes.py` — skip artifact steps in comparison-only mode
- Tests: `test_comparison_delta.py`, `test_comparison_engine.py`, `test_comparison_pipeline.py`, `test_comparison_readonly.py`

### Reports (comparison output only)

- `reports/comparison/before_after.json`
- `reports/comparison/before_after.md`
- `reports/comparison/comparison.json`
- `reports/comparison/comparison.md`

**Target repo:** No Phase 13 source changes.

---

## Verified Artifact Counts

| Artifact | Before | After |
| --- | ---: | ---: |
| Graph nodes | 26 | 25 |
| Graph links | 20 | 19 |
| Findings | 19 | 8 |
| Recommendations | 19 | 8 |
| Patch plan items (before) | 19 | — |

---

## Compare CLI

`uv run ex04-agent compare` — exit 0, writes only to `reports/comparison/`.

---

## Pipeline After (Comparison-Only)

`uv run ex04-agent pipeline --dry-run --phase after`:

- **Completed:** `repository_setup`, `comparison_report`, `supervisor`
- **Skipped:** `graphify_runner`, `graph_parser`, `obsidian_vault`, `dynamic_hotmd`, `graph_interpreter`, `architecture_bug`, `recommendation`, `patch`, `test_runner`
- Before artifacts unchanged after run

---

## Validation

| Check | Result |
| --- | --- |
| `uv run pytest` | 135 passed |
| Coverage | 88.49% (≥ 85%) |
| `uv run ruff check` | Clean |
| Target repo diff | Empty |

---

## Blockers

None. Phase 13 repaired and safe to commit.

**Next:** Phase 14 — Token-Efficiency Report (requires approval).
