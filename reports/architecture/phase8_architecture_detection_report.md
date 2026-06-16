# Phase 8 — Architecture Detection Report

**Date:** 2026-06-16  
**Phase:** 8 — Architecture Bug / Architecture Smell Detection  
**Target repo:** `data/target_repo/broken-python` (unchanged)

---

## Files Created

| Path | Purpose |
| --- | --- |
| `src/ex04_agent/detection/__init__.py` | Package exports |
| `src/ex04_agent/detection/finding.py` | `ArchitectureFinding`, `EvidenceItem` |
| `src/ex04_agent/detection/source_scanner.py` | Read-only source scan and validation |
| `src/ex04_agent/detection/detectors_graph.py` | Graph/metrics detectors |
| `src/ex04_agent/detection/detectors_source.py` | Mixed responsibility, side effects, globals |
| `src/ex04_agent/detection/detectors_source_extra.py` | Execution blockers, duplicate evolution |
| `src/ex04_agent/detection/detectors.py` | Detector registry |
| `src/ex04_agent/detection/report_writer.py` | JSON + Markdown reports |
| `src/ex04_agent/detection/engine.py` | `ArchitectureDetectionEngine` |
| `tests/unit/test_architecture_detection.py` | Detector and engine unit tests |
| `tests/unit/test_detect_cli.py` | Detect CLI tests |
| `reports/architecture/findings_before.json` | Before-phase findings |
| `reports/architecture/findings_before.md` | Before-phase Markdown report |
| `reports/architecture/findings.json` | Latest findings copy |

## Files Updated

| Path | Change |
| --- | --- |
| `src/ex04_agent/agents/architecture_bug.py` | Runs detection engine |
| `src/ex04_agent/workflow/state.py` | `findings_path`, `finding_count` |
| `src/ex04_agent/workflow/result.py` | Pipeline result fields |
| `src/ex04_agent/cli/handlers.py` | `run_detect` handler |
| `src/ex04_agent/cli/parser.py` | `detect` subcommand |
| `tests/unit/test_pipeline_agents.py` | Architecture bug agent tests |
| `tests/unit/test_pipeline_cli.py` | Updated `PipelineResult` fields |
| `tests/unit/test_workflow.py` | `architecture_bug` completed in dry-run |
| `docs/TODO.md` | Phase 8 marked complete |

---

## Detectors Implemented (8)

1. **GodNodeCandidateDetector** — metrics `potential_god_nodes`; README/docs hubs labeled separately
2. **MixedResponsibilityDetector** — responsibility tags from source scan
3. **TopLevelSideEffectDetector** — import/script mixing at module level
4. **HiddenGlobalStateDetector** — parameter vs global mismatch (AST + text fallback)
5. **DisconnectedComponentsDetector** — navigation/scope finding from component count
6. **LowConfidenceEdgeDetector** — returns empty when no low-confidence links (0 in current graph)
7. **ExecutionBlockerDetector** — `compile()` syntax blockers (`code_health_blocker`)
8. **DuplicateEvolutionDetector** — mathsquiz step files coexistence

---

## Real Finding Summary

| Metric | Value |
| --- | ---: |
| **Total findings** | 19 |
| **High confidence** | 14 |
| **High severity** | 3 |
| **Medium severity** | 14 |
| **Low severity** | 2 |

### By category

| Category | Count |
| --- | ---: |
| `possible_hub` | 4 |
| `documentation_hub` | 1 |
| `mixed_responsibility` | 1 |
| `import_script_mixing` | 2 |
| `hidden_global_state` | 7 |
| `navigation_scope` | 1 |
| `code_health_blocker` | 2 |
| `organization` | 1 |

### Top 3 findings (by severity / impact)

1. **Candidate mixed responsibilities in polygons.py** (`MixedResponsibilityDetector`, high) — class/model, calculation, drawing, I/O, and top-level execution coexist; validated by source.
2. **Syntax blocker in mathsquiz/mathsquiz.py** (`ExecutionBlockerDetector`, high) — Python 2 syntax prevents Python 3 compile; validated by `compile()`.
3. **Syntax blocker in polygons/polygons.py** (`ExecutionBlockerDetector`, high) — invalid `Object` base / `new` usage blocks safe AST analysis; validated by `compile()`.

---

## CLI: `detect --phase before`

```json
{
  "finding_count": 19,
  "by_category": {
    "code_health_blocker": 2,
    "documentation_hub": 1,
    "hidden_global_state": 7,
    "import_script_mixing": 2,
    "mixed_responsibility": 1,
    "navigation_scope": 1,
    "organization": 1,
    "possible_hub": 4
  },
  "by_severity": { "high": 3, "low": 2, "medium": 14 },
  "high_confidence_count": 14
}
```

Exit code: **0**

---

## Pipeline dry-run

`architecture_bug` is now **completed** (not skipped). Future agents remain honestly skipped:

- `recommendation` — Phase 9
- `patch` — Phase 10
- `test_runner` — Phase 11
- `comparison_report` — Phase 13

`finding_count`: 19 · `findings_path`: `reports/architecture/findings_before.json`

---

## Target Repo Safety

`git status` in `data/target_repo/broken-python` shows no tracked file modifications. Only pre-existing untracked `graphify-out/` directory.

---

## Quality Gates

| Check | Result |
| --- | --- |
| `uv run pytest` | **67 passed** |
| `uv run pytest --cov=src` | **92.12%** (≥85% required) |
| `uv run ruff check` | **All checks passed** |
| Python files ≤150 lines | **Pass** (all `src/` files) |

---

## Blockers

None for Phase 8 completion.

---

## Phase 9 Approval Gate

Before Phase 9 (Recommendation Generation):

- Review `reports/architecture/findings_before.md` for wording and evidence quality
- Confirm high-severity findings (`polygons.py`, `mathsquiz.py`) match expected teaching-repo context
- Approve mapping findings → `safe_auto` / `review_required` / `docs_only` recommendations
