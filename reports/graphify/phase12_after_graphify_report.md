# Phase 12 — Rerun Graphify After Patches Report

**Date:** 2026-06-16  
**Phase:** 12 — Generate after-phase evidence for Phase 13 comparison  
**Repair pass:** Restore before findings/recommendations; guard after-phase writes

**Note:** After artifacts generated for Phase 13 comparison. No before/after comparison performed.

---

## Repair Summary

### Problem

After-phase pipeline/CLI runs had overwritten phase-specific **before** reports:

- `findings_before.json` / `.md` (reduced from 19 → 8 findings)
- `recommendations_before.json` / `.md` (reduced from 19 → 8)
- `patch_plan_before.json` / `.md` (replaced with after-style plan)

`metrics_before.json` (26 nodes / 20 links) was unaffected. `metrics_after.json` (25 nodes / 19 links) remained correct.

Root cause: re-running detection/recommendation (notably `pipeline --dry-run --phase before` during Phase 11, and subsequent after runs) regenerated **before** artifacts from the patched target repo while using the historical before graph/metrics context inconsistently.

### Repair actions

1. Restored before reports from commit `3eb7e81` (phase 10 done) — the last commit with original Phase 8/9 counts (19 findings / 19 recommendations). Phase 11 HEAD already contained corrupted before counts (8).
2. Added `src/ex04_agent/shared/phase_paths.py` with `ensure_phase_write_path()` — after-phase writes cannot target `*_before.*` paths.
3. Updated detection and recommendation engines to use phase-scoped paths with guards.
4. Added tests in `tests/unit/test_phase_report_guard.py`.

---

## Files Created / Changed

### Code

- `src/ex04_agent/graph/graphify_runner.py` — after phase uses `graphify update . --force`
- `src/ex04_agent/shared/phase_paths.py` — phase path helpers and write guards
- `src/ex04_agent/detection/engine.py` — guarded phase paths
- `src/ex04_agent/recommendation/engine.py` — guarded phase paths

### Tests

- `tests/unit/phase_after_helpers.py`
- `tests/unit/test_phase_after_paths.py`
- `tests/unit/test_phase_after_pipeline.py`
- `tests/unit/test_phase_report_guard.py`

### After artifacts (preserved)

- `artifacts/graph/after/graph.json` (25 nodes, 19 edges)
- `artifacts/graph/after/graph.html`, `GRAPH_REPORT.md`
- `reports/architecture/metrics_after.json`
- `reports/architecture/story_after.md`
- `reports/architecture/findings_after.json` / `.md` (8 findings)
- `reports/architecture/recommendations_after.json` / `.md` (8 recommendations)
- `reports/architecture/patch_plan_after.json` / `.md`
- `artifacts/hotmd/hot_after_*.md`
- `reports/graphify/graphify_after_run.txt`, `graphify_after_metadata.json`

### Before artifacts (restored and preserved)

- `reports/architecture/metrics_before.json` — 26 nodes / 20 links
- `reports/architecture/findings_before.json` / `.md` — **19 findings**
- `reports/architecture/recommendations_before.json` / `.md` — **19 recommendations**
- `reports/architecture/patch_plan_before.json` / `.md` — original Phase 9 plan

Latest copies (`findings.json`, `recommendations.json`, `patch_plan.json`) may reflect after phase — phase-specific before files are protected.

---

## After Graphify Result

Command: `uv run ex04-agent graphify --phase after` — **success** (exit 0, `--force` appended).

---

## Pipeline Dry-Run After

Command: `uv run ex04-agent pipeline --dry-run --phase after`

- `success`: true
- `test_runner`: completed
- `comparison_report`: skipped (Phase 13)
- `findings_before.json`: unchanged at 19 findings after pipeline run

---

## Target Repo Source Changes

No Python source file changes in `data/target_repo/broken-python/`. Graphify may update `graphify-out/` (generated output only).

---

## Quality Gates

| Check | Result |
|---|---|
| pytest | 122 passed |
| coverage | 87.60% (≥ 85%) |
| Ruff | All checks passed |

---

## Blockers

None. After artifacts generated; before artifacts restored and protected for Phase 13 comparison.

Do not interpret metric/finding count differences as confirmed improvement until Phase 13 comparison is approved.
