# Phase 1 Environment Report

**Date:** 2026-06-16  
**Scope:** Clone and inspect `martinpeck/broken-python` only (no agent implementation)

---

## 1. Is the target repo cloned?

**Yes.**

| Field | Value |
|-------|-------|
| URL | https://github.com/martinpeck/broken-python.git |
| Local path | `data/target_repo/broken-python/` |
| Branch | `master` |
| Commit | `fc222e2431035de82e35fc8e07f85bd294ca0c58` |

**Layout:**
- `mathsquiz/` — 4 Python scripts (step1–3 + main), README
- `polygons/polygons.py` — polygon exercise
- Root `README.md` (minimal), `LICENSE.txt`

**Size:** 5 Python files, ~321 lines total.

---

## 2. Can tests run?

**No — not in the target repository.**

| Check | Result |
|-------|--------|
| `test_*.py` files | None |
| `tests/` directory | None |
| `pytest.ini` / `pyproject.toml` | None |
| `python -m pytest` | Fails — pytest not installed globally |

**Workaround for later phases:** Our EX04 project will add wrapper tests under `tests/` (Phase 2 + Phase 11). The target repo is intentionally a manual debugging exercise without automated tests.

**Manual note:** `mathsquiz.py` uses invalid Python 3 syntax (Python 2-style `print`, `if answer = 55:`). Running it on Python 3.13 fails with `SyntaxError` — expected for this repo.

---

## 3. Can Graphify run?

**Yes — after installing `graphifyy`.**

| Stage | Result |
|-------|--------|
| Initial CLI check | `graphify` not found |
| After `python -m pip install graphifyy` | `graphify 0.8.40` works |
| `graphify extract .` | Failed — needs LLM API key for 3 README/doc files |
| `graphify update .` | **Success** — AST-only, no API key |

**Smoke outputs** (copied to `artifacts/graph/before/`):
- `graph.json` — 26 nodes, 20 links, 8 communities
- `graph.html`
- `GRAPH_REPORT.md`

**Not produced by Graphify:** `index.md`, `hot.md` (we generate these in Phases 5–6).

**Course note:** `uv` is not on PATH yet. Long-term install should be `uv tool install graphifyy` per course guidelines.

---

## 4. Environment inventory

| Item | Finding |
|------|---------|
| Python (system) | 3.13.13 |
| Target repo Python version declared | None (code looks Python 2-era) |
| Dependency files | None |
| Documentation | Root README + `mathsquiz/README.md` |
| Setup complexity | **Simple clone** — no install step for target repo |
| `uv` | **Not installed** — blocker for Phase 2 course scaffold |
| Graphify | Installed globally via pip (Phase 1 probe only) |

---

## 5. Is this repo sufficient for the assignment?

**Yes, with caveats — recommend staying on `broken-python` unless you want a richer graph.**

### Strengths
- Official EX04 base repo; matches planning docs
- Intentionally buggy code → clear debugging / improvement story
- Graphify produced a usable graph (god nodes: `Polygon`, `Maths Quiz`; isolated doc nodes; TODO community)
- Easy local control on Windows

### Risks (small repo)
| Risk | Severity | Mitigation |
|------|----------|------------|
| Only ~321 LOC | Medium | Rich Obsidian narrative; focus on graph *reading* not scale |
| No target tests | Medium | Wrapper tests in our project |
| Thin token-efficiency delta | Medium | Report honestly; compare README dump vs index+hot |
| AST-only graph (no semantic edges on docs) | Low | Optional LLM key for full `extract` later |
| Python 2 syntax in scripts | Low | Patch/fix is part of assignment story |

### Graphify's own verdict
`GRAPH_REPORT.md` states: *"corpus is large enough that graph structure adds value"* — 26 nodes, 8 communities.

### Switch repo?
**Do not switch automatically.** If you want more architecture depth (more modules, real test suite), `andela/buggy-python` or `BugsInPy` are alternatives — but require your explicit approval per planning rules.

---

## 6. Phase 1 blockers for Phase 2

| Blocker | Status | Action needed |
|---------|--------|---------------|
| Target repo clone | Resolved | — |
| Graphify CLI | Resolved (pip); prefer uv tool | Install `uv` + `uv tool install graphifyy` |
| `uv` not installed | **Open** | Install uv before Phase 2 |
| No target tests | Expected | Plan wrapper tests in Phase 11 |
| No fake graph outputs | OK | Real artifacts in `artifacts/graph/before/` |

---

## 7. Artifacts produced in Phase 1

- `reports/architecture/repo_metadata.json`
- `reports/architecture/phase1_environment_report.md` (this file)
- `reports/tests/baseline_test_output.txt`
- `reports/graphify/graphify_cli_check.txt`
- `artifacts/graph/before/{graph.json, graph.html, GRAPH_REPORT.md, ...}`

---

## 8. Approval before Phase 2

Please confirm:
1. Proceed with Phase 2 (`uv` project scaffold) — includes installing `uv` on this machine.
2. Keep `broken-python` as target repo.
3. Accept wrapper tests in our project (target repo has none).
4. Graphify install strategy: `uv tool install graphifyy` inside course environment vs global pip used for Phase 1 probe.
