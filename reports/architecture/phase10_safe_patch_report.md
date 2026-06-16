# Phase 10 — Safe Patch / Refactor Implementation Report

**Date:** 2026-06-16  
**Phase:** 10 — Deterministic safe patching of broken-python target files

---

## Files created

- `src/ex04_agent/patching/__init__.py`
- `src/ex04_agent/patching/model.py`
- `src/ex04_agent/patching/validator.py`
- `src/ex04_agent/patching/diff_writer.py`
- `src/ex04_agent/patching/safe_patcher.py`
- `src/ex04_agent/patching/recipes.py`
- `src/ex04_agent/patching/report_writer.py`
- `src/ex04_agent/patching/engine.py`
- `tests/unit/test_patching.py`
- `reports/architecture/patch_result_before.json`
- `reports/architecture/patch_result_before.md`
- `reports/architecture/patch_result.json`
- `artifacts/patches/before/diffs/` (4 diff files)
- `artifacts/patches/before/backups/` (4 backup files)

## Files changed

- `src/ex04_agent/agents/patch.py` — replaced placeholder with real `PatchAgent`
- `src/ex04_agent/workflow/state.py` — added `patch_result_path`, `patch_applied_count`
- `src/ex04_agent/workflow/result.py` — added `patch_result_path`, `patch_applied_count`
- `src/ex04_agent/cli/handlers.py` — added `run_patch` handler
- `src/ex04_agent/cli/parser.py` — added `patch` subcommand with `--allow-patches` flag
- `tests/unit/test_pipeline_cli.py` — updated `PipelineResult` mock with new fields
- `docs/TODO.md` — Phase 10 tasks marked complete

---

## Dry-run patch command result

Command: `uv run ex04-agent patch --phase before`

```json
{
  "allow_patches": false,
  "changed_files": 0,
  "applied_count": 0,
  "skipped_count": 4,
  "failed_count": 0,
  "rolled_back_count": 0,
  "validation_status": "pass"
}
```

Result: **success** — dry-run printed what would be patched; **no target files modified**.

---

## Real patch command with `--allow-patches`

Command: `uv run ex04-agent patch --phase before --allow-patches`

```json
{
  "allow_patches": true,
  "changed_files": 4,
  "applied_count": 4,
  "skipped_count": 0,
  "failed_count": 0,
  "rolled_back_count": 0,
  "validation_status": "pass"
}
```

Result: **success** — all 4 whitelisted files patched, 0 failed.

---

## Changed target repo files

| File | Changes applied |
|------|----------------|
| `mathsquiz/mathsquiz.py` | Python 2 `print "..."` → `print(...)`, `if answer = N:` → `if int(answer) == N:`, `score += 1` added in each correct block, `else if` → `elif`, `else if score = 10:` → `elif score == 10:` |
| `polygons/polygons.py` | `class Polygon(Object):` → `class Polygon:`, `poly = new Polygon(` → `poly = Polygon(`, bare top-level execution wrapped in `if __name__ == "__main__":` guard |
| `mathsquiz/mathsquiz-step2.py` | Global `score` replaced with `final_score` parameter in `print_final_scores` function body; top-level execution wrapped in `if __name__ == "__main__":` |
| `mathsquiz/mathsquiz-step3.py` | Global `score` replaced with `final_score` parameter and `percentage` calculation fixed in `print_final_scores` function body; top-level execution wrapped in `if __name__ == "__main__":` |

---

## Patch counts

- Applied: **4**
- Skipped: **0**
- Failed: **0**
- Rolled back: **0**

---

## Backup and diff folders

- Backups: `artifacts/patches/before/backups/` — 4 `.bak` files, all from the same clean run
- Diffs: `artifacts/patches/before/diffs/` — 4 `.diff` files, all from the same clean run

No leftover artifacts from prior failed runs.

---

## Compile validation result

`python -m compileall data/target_repo/broken-python`:

```
Compiling 'mathsquiz/mathsquiz-step1.py'...
Compiling 'mathsquiz/mathsquiz-step2.py'...
Compiling 'mathsquiz/mathsquiz-step3.py'...
Compiling 'mathsquiz/mathsquiz.py'...
Compiling 'polygons/polygons.py'...
```

All files compile cleanly. Exit code 0.

---

## Git diff confirmation — only whitelisted files changed

```
data/target_repo/broken-python/mathsquiz/mathsquiz-step2.py
data/target_repo/broken-python/mathsquiz/mathsquiz-step3.py
data/target_repo/broken-python/mathsquiz/mathsquiz.py
data/target_repo/broken-python/polygons/polygons.py
```

No other files in the target repo were touched.

---

## pytest result

```
96 passed in 1.60s
```

## Coverage result

```
Total coverage: 89.67%  (required: 85%)
```

## Ruff result

```
All checks passed!
```

---

## Consistency between JSON and Markdown

`reports/architecture/patch_result_before.json`:
- `changed_files`: 4 files
- `applied_items`: 4 items (one per whitelisted file)
- `skipped_items`: 0
- `failed_items`: 0
- `rolled_back_items`: 0

`reports/architecture/patch_result_before.md`: matches

---

## Blockers

None. Phase 10 completed with all 4 whitelisted files patched, reports consistent, artifacts clean.

All patches were:
- Deterministic (no LLM)
- Whitelisted files only
- Backed up before modification
- Validated after modification (compile + ast)
- Recorded with unified diffs and full item status
