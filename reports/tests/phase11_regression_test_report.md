# Phase 11 — Regression Test Runner and Validation Agent Report

**Date:** 2026-06-16  
**Phase:** 11 — Deterministic regression/validation runner for Phase 10 patches  
**Repair pass:** Ruff status consistency + test file line-limit cleanup

---

## Repair Summary

### What was inconsistent before

- `artifacts/test_runs/before/ruff_stdout.txt` recorded Ruff failures (SIM105, I001).
- `regression_before.json` had the Ruff command with `return_code: 1` and `status: failed`, but top-level `ruff_status` was incorrectly set to `passed`.
- `phase11_regression_test_report.md` claimed Ruff passed despite the saved command output showing failures.
- Root cause: `RegressionEngine` derived `ruff_status` from stdout parsing (`parse_ruff_issues`) instead of the command return code; the parser also did not match Ruff's plural `"Found N errors"` message reliably.
- Two test files exceeded the 150-line limit: `test_regression_engine.py` (161) and `test_workflow.py` (156).

### Fixes applied

- `RegressionEngine` now sets `ruff_status = ruff_cmd.status` (return-code driven).
- `parse_ruff_issues` improved (ANSI strip, plural `errors?`, stderr support) for auxiliary parsing only.
- CLI `run_test` now returns non-zero when Ruff or coverage fails.
- Ruff I001 import-order issues fixed in split test files.
- Oversized test files split into focused modules under 150 lines each.

---

## Files Created

- `src/ex04_agent/testing/__init__.py`
- `src/ex04_agent/testing/model.py`
- `src/ex04_agent/testing/command_runner.py`
- `src/ex04_agent/testing/discovery.py`
- `src/ex04_agent/testing/validators.py`
- `src/ex04_agent/testing/result_parser.py`
- `src/ex04_agent/testing/report_writer.py`
- `src/ex04_agent/testing/engine.py`
- `tests/unit/regression_helpers.py`
- `tests/unit/workflow_helpers.py`
- `tests/unit/test_regression_models.py`
- `tests/unit/test_regression_validators.py`
- `tests/unit/test_regression_report_writer.py`
- `tests/unit/test_regression_cli.py`
- `tests/unit/test_regression_pipeline.py`
- `tests/unit/test_workflow_compile.py`
- `tests/unit/test_workflow_dry_run.py`
- `reports/tests/regression_before.json`
- `reports/tests/regression_before.md`
- `reports/tests/regression.json`
- `artifacts/test_runs/before/` (pytest, coverage, ruff stdout/stderr)

## Files Changed

- `src/ex04_agent/agents/test_runner.py`
- `src/ex04_agent/workflow/state.py`
- `src/ex04_agent/workflow/result.py`
- `src/ex04_agent/cli/handlers.py`
- `src/ex04_agent/cli/parser.py`
- `tests/unit/test_pipeline_cli.py`

## Files Removed (split)

- `tests/unit/test_regression_engine.py` → split into report_writer, cli, pipeline tests
- `tests/unit/test_workflow.py` → split into compile + dry_run tests

---

## CLI Command Result

Command: `uv run ex04-agent test --phase before`

```json
{
  "compile_status": "passed",
  "ast_status": "passed",
  "import_status": "skipped",
  "target_test_status": "skipped",
  "project_test_status": "passed",
  "coverage_status": "passed",
  "ruff_status": "passed",
  "failed_files_count": 0
}
```

Exit code: **0**

---

## Validations Run

| Check | Result | Notes |
|---|---|---|
| Compile validation | **passed** | All 5 target Python files compile |
| AST validation | **passed** | All 5 files parse cleanly |
| Safe import | **skipped** | turtle/input usage — unsafe to auto-import |
| Target repo tests | **skipped** | No `tests/` directory in target repo |
| Project pytest | **passed** | 112 tests passed |
| Coverage | **passed** | 87.45% (threshold: 85%) |
| Ruff | **passed** | return_code 0; stdout: `All checks passed!` |

### Ruff consistency check

- `regression_before.json` → `commands_run[ruff].return_code: 0`, `status: passed`, `ruff_status: passed`
- `regression_before.md` → Ruff row: `passed`
- `artifacts/test_runs/before/ruff_stdout.txt` → `All checks passed!`

All three sources now agree.

---

## Target Repo Test Discovery

No dedicated test suite in `martinpeck/broken-python`.  
`target_test_status: skipped` with warning recorded.

---

## Failed Files

None.

---

## Confirmation: No New Target Repo Source Changes

`git diff -- data/target_repo/broken-python` shows **no changes** after repair.

Note: pipeline dry-run may touch `graphify-out/cache/stat-index.json` (Graphify cache only). That file was restored and is **not** counted as a Phase 11 source-code change. No `.py` files in the target repo were modified during Phase 11.

---

## Pipeline dry-run result

Command: `uv run ex04-agent pipeline --dry-run --phase before`

- `test_runner`: **completed**
- `comparison_report`: **skipped** (Phase 13)
- `patch`: **skipped** (allow_patches not set)

---

## pytest Result

```
112 passed
```

## Coverage Result

```
Total coverage: 87.45%  (required: 85%)
```

## Ruff Result

```
All checks passed!
```

---

## Blockers

None. Phase 11 repair complete and consistent.
