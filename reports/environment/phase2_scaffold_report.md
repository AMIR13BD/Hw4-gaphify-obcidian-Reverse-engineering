# Phase 2 Scaffold Report

**Date:** 2026-06-16  
**Scope:** uv project scaffold and configuration only (no agents, GraphParser, Obsidian, patching)

---

## 1. uv

| Item | Value |
|------|-------|
| Installed | Yes (was missing at start of Phase 2) |
| Version | `uv 0.11.21` |
| Path | `C:\Users\ameer\.local\bin\uv.exe` |
| Installer | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Virtual env | `.venv/` created via `uv sync` |
| Lock file | `uv.lock` generated |

Details: `reports/environment/uv_check.txt`

---

## 2. Graphify (uv tool)

| Item | Value |
|------|-------|
| Package | `graphifyy` |
| CLI | `graphify` |
| Version | `0.8.40` |
| Install | `uv tool install graphifyy` |
| Primary path | `C:\Users\ameer\.local\bin\graphify.exe` |

Details: `reports/graphify/graphify_uv_tool_check.txt`

Phase 1 global pip install remains on PATH but **uv tool is the preferred method** going forward.

---

## 3. Files created

### Project manifest & env
- `pyproject.toml`
- `uv.lock`
- `.env-example`
- `.gitignore`
- `README.md` (minimal quick-start)

### Config
- `config/setup.json`
- `config/rate_limits.json`

### Source (`src/ex04_agent/`)
- `__init__.py`
- `main.py` — CLI with `health` subcommand
- `sdk/__init__.py`, `sdk/sdk.py` — `Ex04Sdk.health_check()`
- `shared/__init__.py`, `shared/version.py`, `shared/config.py`

### Tests
- `tests/conftest.py`
- `tests/unit/test_version.py`
- `tests/unit/test_config.py`
- `tests/unit/test_sdk.py`
- `tests/unit/test_cli.py`
- `tests/integration/.gitkeep`

### Reports
- `reports/environment/uv_check.txt`
- `reports/environment/phase2_scaffold_report.md` (this file)

---

## 4. Commands run

```text
uv lock                          # exit 0
uv sync                          # exit 0
uv run pytest -q                 # 5 passed
uv run pytest --cov=src --cov-report=term-missing -q
                                 # 5 passed, 90.11% coverage (>= 85%)
uv run ruff check                # All checks passed (after excluding data/)
uv run ex04-agent health         # JSON health output, exit 0
uv tool install graphifyy        # exit 0
```

---

## 5. Test results

| Check | Result |
|-------|--------|
| pytest | **PASS** — 5 tests |
| coverage | **PASS** — 90.11% (threshold 85%) |
| ruff | **PASS** — 0 violations on `src/` + `tests/` |

**Ruff note:** Initial `ruff check` scanned `data/target_repo/broken-python/` (intentionally broken Python 2-style code) and failed with 72 errors. Fixed by adding `extend-exclude = ["data", "artifacts", "_pdf_extracts"]` in `pyproject.toml`. Target repo is **not** linted by our project.

---

## 6. Scaffold behavior

`uv run ex04-agent health` returns:

```json
{
  "version": "1.00",
  "target_repo": "data/target_repo/broken-python",
  "graphify_cli": "graphify",
  "allow_patches": false,
  "max_iterations": 3
}
```

No pipeline, agents, Graphify runner, or patching implemented yet.

---

## 7. Blockers

| Blocker | Status |
|---------|--------|
| uv missing | **Resolved** |
| Graphify via uv tool | **Resolved** |
| Target repo has no tests | **Expected** — wrapper tests in our project |
| Phase 3+ not started | By design |

---

## 8. Approval before Phase 3

Phase 3 will implement **GraphifyRunner** and artifact collection only. Please confirm:

1. Proceed to Phase 3 (Graphify runner service + artifacts to `artifacts/graph/{phase}/`).
2. Accept ruff `extend-exclude` for `data/` and `artifacts/` (target repo not linted).
3. Keep using `graphify update` for AST-only scans unless you want to configure an LLM key for full `extract`.
