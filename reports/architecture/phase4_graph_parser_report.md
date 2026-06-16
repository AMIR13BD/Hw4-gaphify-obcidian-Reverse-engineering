# Phase 4 — Graph Parser and Graph Metrics Report

**Date:** 2026-06-16  
**Target repo:** `data/target_repo/broken-python/` (unchanged)  
**Command:** `uv run ex04-agent parse --phase before`

---

## Files Created

| File | Purpose |
|------|---------|
| `src/ex04_agent/graph/models.py` | `GraphNode`, `GraphLink`, `GraphDocument` dataclasses |
| `src/ex04_agent/graph/parser.py` | `GraphParser` — defensive Graphify JSON parsing |
| `src/ex04_agent/graph/indexer.py` | `GraphIndexer` — id/file/adjacency lookups |
| `src/ex04_agent/graph/metrics.py` | `MetricsEngine`, `MetricsReport` |
| `src/ex04_agent/graph/metrics_topology.py` | Connected components and bridging helpers |
| `src/ex04_agent/graph/serializer.py` | `MetricsSerializer` — JSON export and terminal summary |
| `src/ex04_agent/agents/graph_parser.py` | `GraphParserAgent` thin wrapper |
| `src/ex04_agent/graph/graphify_run_result.py` | Split from `graphify_runner.py` (line-limit cleanup) |
| `src/ex04_agent/graph/graphify_run_report.py` | Split from `graphify_runner.py` (line-limit cleanup) |
| `tests/fixtures/graph_sample.json` | Unit-test fixture with `nodes` + `links` |
| `tests/unit/test_graph_parser.py` | Parser, indexer, metrics unit tests |
| `tests/unit/test_parse_cli.py` | CLI parse command tests |
| `reports/architecture/metrics_before.json` | Generated metrics output |

## Files Changed

| File | Change |
|------|--------|
| `src/ex04_agent/graph/graphify_runner.py` | Reduced to 90 lines; delegates result/report helpers |
| `src/ex04_agent/graph/__init__.py` | Export parser/metrics symbols |
| `src/ex04_agent/agents/__init__.py` | Export `GraphParserAgent` |
| `src/ex04_agent/agents/graphify_runner.py` | Import `GraphifyRunResult` from split module |
| `src/ex04_agent/main.py` | Added `parse --phase before\|after` subcommand |
| `docs/TODO.md` | Phase 4 tasks marked complete |

All Python source files are **≤150 physical lines**.

---

## Graph Schema Confirmed

Graphify `graph.json` uses **`nodes`** and **`links`** (not `edges`).

- **26 nodes**, **20 links** in before-phase graph
- Node fields observed: `id`, `label`, `file_type`, `source_file`, `source_location`, `_origin`, `community`, `norm_label`
- Link fields observed: `source`, `target`, `relation`, `confidence`, `confidence_score`, `source_file`, `source_location`, `weight`

---

## Metrics Generated (`metrics_before.json`)

| Metric | Value |
|--------|-------|
| node_count | 26 |
| link_count | 20 |
| file_node_count | 0 |
| code_node_count | 26 |
| isolated_node_count | 2 |
| connected_component_count | 7 |
| god_node_threshold | 3 |
| low_confidence_link_count | 0 |

### Relation counts

| Relation | Count |
|----------|-------|
| contains | 14 |
| rationale_for | 3 |
| calls | 1 |
| inherits | 1 |
| method | 1 |

### Confidence counts

All 20 links: `EXTRACTED` (confidence_score 1.0).

---

## Top Hubs (by total_degree)

| Label | Degree |
|-------|--------|
| polygons.py | 6 |
| Maths Quiz | 4 |
| Polygon | 4 |
| mathsquiz-step2.py | 3 |
| mathsquiz-step3.py | 3 |

## Potential God Nodes (degree ≥ max(3, 90th percentile))

| Label | Degree | Source file |
|-------|--------|-------------|
| polygons.py | 6 | polygons/polygons.py |
| Polygon | 4 | polygons/polygons.py |
| Maths Quiz | 4 | mathsquiz/README.md |
| mathsquiz-step2.py | 3 | mathsquiz/mathsquiz-step2.py |
| mathsquiz-step3.py | 3 | mathsquiz/mathsquiz-step3.py |

## Low-Confidence Links

**0** — AST-only Graphify run produced only `EXTRACTED` links with score 1.0.

---

## Test Results

```
27 passed in 0.62s
```

New tests cover parser, indexer, metrics (god nodes, low-confidence), and CLI parse with temp fixture.

## Coverage

```
TOTAL: 580 statements, 33 missed, 94.31% (threshold 85%)
```

## Ruff

```
All checks passed!
```

---

## Blockers

None for Phase 4.

**Note for Phase 5+:** Real before graph has no `file`-typed nodes (all `code`); Obsidian vault generation may need to treat `code` file-level nodes separately. Low-confidence link detection is untested on real Graphify LLM-extract output — only fixture coverage for INFERRED/AMBIGUOUS.

---

## Approval Gate for Phase 5

Before starting Obsidian vault generation, confirm:

1. Metrics output shape (`metrics_before.json`) is acceptable for downstream agents.
2. God-node threshold rule (`degree ≥ max(3, 90th percentile)`) is reasonable for `hot.md` weighting.
3. Proceed with static `index.md` / `hot.md` vault (no dynamic hot.md yet — Phase 6).
