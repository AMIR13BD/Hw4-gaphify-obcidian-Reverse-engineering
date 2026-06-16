# PRD — Dynamic `hot.md` from `graph.json` and Git Diff

**Parent:** `docs/PRD.md`  
**Mechanism:** Original EX04 extension  
**Version:** 1.0 (Planning)

---

## 1. Purpose

Automatically generate and update `obsidian/hot.md` by combining:

- **Graph metrics** from `graph.json` (centrality, proximity, edge confidence)
- **Git diff** changed files in `martinpeck/broken-python`
- **Optional:** failing test file paths from TestRunnerAgent

This focuses agent and human attention on the highest-risk architecture surface during iterative improvement.

---

## 2. Problem Statement

Static `hot.md` becomes stale after patches and test runs. Investigators waste context re-scanning the full graph. Dynamic `hot.md` implements Lecture 07's **hot investigation surface** tied to **current code churn** — a unique extension beyond EX04 minimum.

---

## 3. Inputs

| Input | Source | Required |
|-------|--------|----------|
| `graph.json` | Graphify artifact | Yes |
| Parsed metrics | GraphParserAgent / MetricsEngine | Yes |
| `git diff --name-only` | Target repo | Yes (empty diff OK) |
| `git diff` hunks | Target repo | Optional (for line-level proximity) |
| Failing tests | pytest output | Optional |
| Phase label | `before` / `after` | Yes |
| Previous `hot.md` | obsidian/ | Optional (for before/after notes) |

---

## 4. Outputs

**File:** `obsidian/hot.md` (overwrite with version header)

**Sections (required):**

1. **Metadata** — timestamp, phase, commit short SHA, graph artifact path  
2. **Changed files** — from git diff, linked to node pages if mapped  
3. **Suspicious nodes ranked** — table: rank, node, score, centrality, proximity reason  
4. **Affected files** — union of changed files + nodes' `source_file`  
5. **Possible architecture problems** — templated hypotheses per top node  
6. **Recommended investigation path** — ordered wiki links (OBS→REL→CONF→SRC)  
7. **Before/after notes** — delta from previous hot.md if exists  

---

## 5. Ranking Algorithm

### 5.1 Score formula (deterministic)

```text
score(node) =
  w1 * normalized_degree(node)
+ w2 * normalized_betweenness(node)
+ w3 * proximity_to_changed_files(node)
+ w4 * proximity_to_failing_tests(node)
+ w5 * ambiguous_edge_ratio(node)
+ w6 * god_node_flag(node)
```

**Default weights** (configurable in `config/setup.json`):

| Weight | Default | Meaning |
|--------|---------|---------|
| w1 | 0.20 | Degree centrality |
| w2 | 0.25 | Betweenness |
| w3 | 0.30 | Changed file proximity |
| w4 | 0.15 | Failing test proximity |
| w5 | 0.05 | Ambiguous edges |
| w6 | 0.05 | God node threshold bonus |

### 5.2 Proximity to changed files

- If `node.source_file` in changed files → proximity = 1.0  
- Else if same directory as changed file → 0.6  
- Else if edge (EXTRACTED) to node in changed file → 0.4  
- Else → 0.0  

### 5.3 God node flag

- `degree > p90` AND `betweenness > p75` → flag = 1  

### 5.4 Tie-breaking

1. Higher EXTRACTED edge count  
2. Alphabetic node id  

---

## 6. Architecture Problem Templates

| Pattern | Template hypothesis |
|---------|---------------------|
| God node + changed | "Central node `{id}` changed — regression may propagate widely" |
| Bottleneck + changed | "Bottleneck `{id}` edited — verify callers in {affected_files}" |
| Isolated + changed | "Isolated cluster changed — check if integration was intended" |
| Docs proximity | "Docs near change without code edge — traceability gap" |
| Ambiguous edges | "Node has ambiguous edges — validate before patch" |
| Test failure proximity | "Node near failing test `{test}` — likely investigation entry" |

---

## 7. Investigation Path Generation

For top K nodes (default K=5):

1. Link to `obsidian/nodes/{id}.md`  
2. List incoming/outgoing EXTRACTED edges  
3. Suggest micro-read order: node → edges → `source_file` → related tests  
4. Link to `index.md` community section  

Output as numbered list in `hot.md`.

---

## 8. Before/After Notes

When previous `hot.md` exists:

| Compare | Note |
|---------|------|
| Rank changes | "Node X rose from #7 to #2 after patch" |
| New changed files | List newly appeared paths |
| Score delta | Top node score before vs after |
| Resolved flags | God node flag cleared? |

Store snapshot: `artifacts/hotmd/hot_{phase}_{timestamp}.md`

---

## 9. Triggers

| Event | Action |
|-------|--------|
| After GraphifyRunnerAgent (before) | Generate initial hot.md |
| After PatchAgent | Regenerate with git diff |
| After TestRunnerAgent (failures) | Boost failing-test proximity |
| After GraphifyRunnerAgent (after) | Final hot.md + before/after section |
| CLI: `uv run python -m ex04_agent hotmd` | Manual regeneration |

---

## 10. Functional Requirements

- DH-1: `DynamicHotMdBuilder` class in `src/` (≤150 lines; helpers in service)  
- DH-2: `GitDiffReader` — changed files, optional hunks  
- DH-3: `NodeRanker` — implements score formula  
- DH-4: `HotMdRenderer` — Markdown template rendering  
- DH-5: Unit tests with fixture graph + fixture diff  

---

## 11. hot.md Example Structure

```markdown
# hot.md — Urgent Investigation

**Phase:** after | **Commit:** abc1234 | **Updated:** 2026-06-16T12:00:00

## Changed files
- `src/foo.py` [[nodes/foo_py]]
- `tests/test_foo.py`

## Suspicious nodes (ranked)
| Rank | Node | Score | Why |
|------|------|-------|-----|
| 1 | func_process | 0.87 | god node + direct change |

## Possible architecture problems
- ...

## Recommended investigation path
1. [[nodes/func_process]] → check callers ...

## Before/after notes
- Top suspect unchanged; betweenness dropped 12% after extract-method refactor.
```

---

## 12. Non-Functional Requirements

- Regeneration < 5s for graphs up to 500 nodes  
- Deterministic ranking for same inputs  
- No LLM required  
- Wikilink paths compatible with Obsidian  

---

## 13. Acceptance Criteria

- [ ] `hot.md` generated after before-phase Graphify  
- [ ] Regenerates when `git diff` non-empty  
- [ ] Top 5 nodes include at least one with changed-file proximity when diff exists  
- [ ] Before/after section populated after second run  
- [ ] Unit tests cover ranker, diff reader, renderer  
- [ ] Documented in final README as original extension  

---

## 14. Risks

| Risk | Mitigation |
|------|------------|
| Node `source_file` mismatch paths | Normalize paths relative to repo root |
| Empty git diff | Fall back to pure centrality ranking |
| Overwriting manual edits | Snapshot to `artifacts/hotmd/`; optional `--merge` flag later |

---

## 15. Integration Points

- **ObsidianVaultAgent** — calls builder after vault scaffold  
- **PatchAgent / TestRunnerAgent** — trigger refresh  
- **TokenEfficiency** — measure `hot.md` size before/after  
- **ComparisonReportAgent** — cite hot.md rank changes in narrative
