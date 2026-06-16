# Phase 6 — Dynamic hot.md Report

**Date:** 2026-06-16  
**Target repo:** `data/target_repo/broken-python/` (unchanged, not modified)  
**Command:** `uv run ex04-agent hotmd --phase before`

---

## Files Created

| File | Purpose |
|------|---------|
| `src/ex04_agent/git/__init__.py` | Git package exports |
| `src/ex04_agent/git/diff_reader.py` | `GitDiffReader`, `GitDiffResult` |
| `src/ex04_agent/obsidian/node_ranker.py` | `NodeRanker`, `RankedNode` |
| `src/ex04_agent/obsidian/rank_proximity.py` | Diff/test proximity scoring |
| `src/ex04_agent/obsidian/dynamic_hotmd_builder.py` | Orchestrates dynamic hot.md + snapshots |
| `src/ex04_agent/obsidian/hotmd_renderer.py` | `HotMdRenderer` Markdown output |
| `src/ex04_agent/cli/__init__.py` | CLI package |
| `src/ex04_agent/cli/handlers.py` | Subcommand handlers |
| `src/ex04_agent/cli/parser.py` | Argument parser |
| `tests/unit/test_git_diff_reader.py` | Git diff unit tests |
| `tests/unit/test_dynamic_hotmd.py` | Ranker, renderer, builder tests |
| `tests/unit/test_hotmd_cli.py` | hotmd CLI tests |

## Files Changed

| File | Change |
|------|--------|
| `src/ex04_agent/main.py` | Slim entry point (18 lines); delegates to `cli/` |
| `src/ex04_agent/agents/obsidian_vault.py` | Added `run_dynamic_hotmd`, optional `--dynamic-hot` hook |
| `src/ex04_agent/obsidian/__init__.py` | Export dynamic hot.md symbols |
| `src/ex04_agent/obsidian/hot_md_builder.py` | Updated static footer text |
| `tests/unit/test_graphify_cli.py` | Patch path updated for CLI refactor |
| `docs/TODO.md` | Phase 6 tasks marked complete |

All Python source files remain **≤150 physical lines**.

---

## CLI Result

```json
{
  "success": true,
  "phase": "before",
  "hot_path": "obsidian/hot.md",
  "snapshot_path": "artifacts/hotmd/hot_before_20260616T113637Z.md",
  "changed_files_count": 0,
  "ranked_nodes_count": 26,
  "top_labels": [
    "polygons.py",
    "Maths Quiz",
    "Polygon",
    "mathsquiz-step2.py",
    "mathsquiz-step3.py"
  ],
  "warning": "No changed files in working tree diff."
}
```

Exit code: **0**

---

## Outputs

| Artifact | Status |
|----------|--------|
| `obsidian/hot.md` | **Generated** (dynamic version replaces static baseline) |
| `artifacts/hotmd/hot_before_20260616T113637Z.md` | **Snapshot saved** |

### Changed files (live target repo)

**0** — working tree is clean at commit `fc222e2431035de82e35fc8e07f85bd294ca0c58`. Ranking fell back to centrality + god-node weights as designed.

### Top ranked nodes

| Rank | Node | Score | Why |
|------|------|------:|-----|
| 1 | polygons.py | 0.50 | possible god-node candidate + highest degree |
| 2 | Maths Quiz | 0.29 | possible god-node candidate (README doc hub) |
| 3 | Polygon | 0.27 | possible god-node candidate |
| 4 | mathsquiz-step2.py | 0.20 | possible god-node candidate |
| 5 | mathsquiz-step3.py | 0.20 | possible god-node candidate |

---

## How Dynamic hot.md Supports the Original Extension

The dynamic `hot.md` blends **graph metrics** (degree, bridging, god-node flags, ambiguous links) with **git diff proximity** (exact file, same directory, connected node) and optional **failing test paths**. When a developer edits files in the target repo and reruns `uv run ex04-agent hotmd`, changed-file nodes rise in the ranked table — prioritizing investigation without claiming confirmed bugs.

Snapshots under `artifacts/hotmd/` preserve before/after history for comparison across iterations.

Scoring weights from `config/setup.json`:

- degree 0.20 · betweenness 0.25 · diff_proximity 0.30 · test_proximity 0.15 · ambiguous 0.05 · god_node 0.05

---

## Test Results

```
45 passed in 2.34s
```

## Coverage

```
TOTAL: 1201 statements, 65 missed, 94.59% (threshold 85%)
```

## Ruff

```
All checks passed!
```

---

## Blockers

None for Phase 6.

**Note:** To see diff-weighted ranking on the live repo, make a local unstaged edit in `data/target_repo/broken-python/` and rerun `hotmd` — do not commit that change to the course submission.

---

## Approval Gate for Phase 7

Before LangGraph multi-agent workflow:

1. Confirm dynamic hot.md ranking behavior is acceptable.
2. Approve `PipelineState` design and agent list for Phase 7.
3. Decide whether `pipeline --dry-run` should invoke graphify → parse → obsidian → hotmd in sequence.
