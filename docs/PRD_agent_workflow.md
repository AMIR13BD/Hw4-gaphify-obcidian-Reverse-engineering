# PRD — Multi-Agent LangGraph Workflow Mechanism

**Parent:** `docs/PRD.md`  
**Mechanism:** LangGraph orchestration of specialized agents  
**Version:** 1.0 (Planning)

---

## 1. Purpose

Orchestrate reverse engineering and safe architectural improvement through a **LangGraph state machine** with specialized agents — matching EX04's iterative loop and Lecture 07's Graph + Wiki + Skills + Context pattern.

**Framework choice:** LangGraph (not CrewAI) — see Section 12.

---

## 2. Workflow Loop (Assignment-Aligned)

```
Setup → Graphify(before) → Parse → Obsidian → Interpret → Find bugs
  → Recommend → [Patch → Test → Graphify(after) → Compare]*
  → Token report → Final report
```

`*` Supervised iteration with stop conditions.

---

## 3. Shared State Schema (`PipelineState`)

| Field | Type | Description |
|-------|------|-------------|
| `target_repo_path` | str | Path to broken-python clone |
| `phase` | enum | `before` \| `after` \| `complete` |
| `graph_artifacts` | dict | Paths to graph.json, html, report |
| `parsed_graph` | object ref | Serialized graph summary |
| `metrics` | dict | Centrality, clusters, flags |
| `obsidian_paths` | dict | index.md, hot.md paths |
| `findings` | list | ArchitectureBugFinding records |
| `recommendations` | list | Prioritized actions |
| `patch_plan` | list | Safe patches queue |
| `applied_patches` | list | Applied diff metadata |
| `test_results` | dict | pass/fail, output path |
| `comparison` | dict | Before/after delta |
| `token_metrics` | dict | Baseline vs guided sizes |
| `iteration` | int | Loop counter |
| `errors` | list | Non-fatal error log |
| `stop_reason` | str | Why loop ended |

---

## 4. Agents and Responsibilities

### 4.1 RepositorySetupAgent
- Clone or verify `martinpeck/broken-python`
- Detect Python version, dependency files, test command
- Record baseline git commit
- Output: `target_repo_path`, environment metadata

### 4.2 GraphifyRunnerAgent
- Invoke Graphify CLI on target repo
- Store artifacts under `artifacts/graph/{phase}/`
- Output: `graph_artifacts`

### 4.3 GraphParserAgent
- Parse `graph.json` into models
- Run MetricsEngine
- Output: `parsed_graph`, `metrics`

### 4.4 ObsidianVaultAgent
- Build/update `obsidian/` vault
- Generate `index.md`, baseline `hot.md`, wiki pages
- Invoke DynamicHotMdBuilder when diff available
- Output: `obsidian_paths`

### 4.5 GraphInterpreterAgent
- Produce **graph story** narrative:
  - Intended architecture vs observed structure
  - Developer focus areas (dense communities)
  - Organization patterns (layers, folders vs communities)
- Uses metrics + GRAPH_REPORT + deterministic templates
- Optional LLM enrichment if local model available
- Output: `graph_story` in state / `reports/architecture/story_{phase}.md`

### 4.6 ArchitectureBugAgent
- Rule-based detection (always):
  - God nodes (degree/betweenness thresholds)
  - Bottlenecks (betweenness + fan-in/out ratio)
  - Mixed responsibility (node with heterogeneous edge labels)
  - Isolated clusters
  - Ambiguous edge concentration
  - Docs-without-code gaps
  - Duplicate responsibility (semantic similarity + overlapping calls)
  - Failing-test proximity (if test output available)
- Optional LLM validation layer
- Output: `findings` with evidence links

### 4.7 RecommendationAgent
- Map findings → actionable recommendations
- Classify: `safe_auto`, `review_required`, `docs_only`
- Prioritize by severity × centrality × test impact
- Output: `recommendations`, `patch_plan` (safe subset)

### 4.8 PatchAgent
- Apply only `safe_auto` patches
- Use structured edit operations (ast-based or unified diff)
- Write patch records to `artifacts/patches/`
- **Guardrails:** no delete files, no API key changes, no irreversible ops
- Output: `applied_patches`

### 4.9 TestRunnerAgent
- Run `uv run pytest` (or detected test command) in target repo
- Capture junit/xml or stdout
- Parse failures → update failing file list for hot.md
- Output: `test_results`

### 4.10 ComparisonReportAgent
- Compare before/after metrics, graph stories, test status
- Generate `reports/comparison/before_after.md`
- Export metric tables and diagram placeholders
- Output: `comparison`

### 4.11 Supervisor / LoopController
- Decide: continue patch loop vs exit
- Enforce `max_iterations` (default 3)
- Stop if: no safe patches remain, tests fail, no metric improvement, token goal met
- Route to TokenEfficiencyReporter before terminal state

---

## 5. LangGraph Node Topology

**Nodes:** one per agent above + `token_report` + `END`

**Entry:** `repository_setup`

**Linear spine:** setup → graphify → parse → obsidian → interpret → bugs → recommend

**Conditional branch after recommend:**
- If patches available and iteration < max → `patch` → `test` → (fail? → `END` with error) → `graphify_after` → `parse_after` → `obsidian_update` → `compare` → `supervisor`
- Else → `token_report` → `END`

**Supervisor edges:**
- `continue` → `patch` (next recommendation)
- `stop` → `token_report` → `END`

---

## 6. Guardrails (SKILLs Pattern from PART-B)

| Operation | Default policy |
|-----------|----------------|
| Read graph/files | Auto-allowed |
| Write Obsidian/reports | Auto-allowed |
| Modify target repo | Safe patches only; reversible |
| Run tests | Auto-allowed |
| Irreversible git ops | Blocked |

`disable_model_invocation` equivalent: PatchAgent requires explicit `allow_patches=true` in config.

---

## 7. LLM vs Deterministic Mode

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Deterministic** | No `LLM_BASE_URL` / no API key | Template narratives, rule-based bugs |
| **Local LLM** | Ollama or compatible endpoint | Enrich GraphInterpreter, Recommendation |
| **Cloud** | Not required; out of scope for grading bar |

All agents must produce **useful output** in deterministic mode.

---

## 8. Functional Requirements

- FR-AW-1: Single SDK entry (`src/main.py` or `src/ex04_agent/sdk/sdk.py`) runs full pipeline
- FR-AW-2: CLI flags: `--phase`, `--max-iterations`, `--dry-run`, `--allow-patches`
- FR-AW-3: Persist state snapshot after each agent to `reports/agent_runs/`
- FR-AW-4: Resume from last successful agent (optional stretch)
- FR-AW-5: Each agent class ≤150 lines; shared logic in services

---

## 9. Acceptance Criteria

- [ ] LangGraph graph compiles and runs end-to-end in deterministic mode
- [ ] All 11 agents execute in order with logged handoffs
- [ ] Loop stops per configured conditions
- [ ] At least one safe patch cycle completes with passing tests
- [ ] Comparison and token reports generated

---

## 10. Why LangGraph Over CrewAI

| Factor | LangGraph | CrewAI |
|--------|-----------|--------|
| Iterative loop | Native cyclic graph, explicit state | Task chains less natural for cycles |
| Stop conditions | Conditional edges, supervisor node | Requires custom orchestration |
| State passing | Typed `PipelineState` | Context sharing more implicit |
| EX04 / L07 fit | Matches "run Graphify → fix → test → rerun" | Better for role debate, not loop |
| Local debugging | Clear node traces | Harder to trace multi-crew handoffs |
| Course preference | User + lecturer iterative description | Allowed but not preferred |

**Conclusion:** LangGraph is the primary orchestrator; CrewAI not required.

---

## 11. Risks

| Risk | Mitigation |
|------|------------|
| Agent file bloat (>150 lines) | Split into agent + service modules |
| Patch agent breaks tests | Test gate + revert patch |
| Infinite loop | `max_iterations` + supervisor |
| LLM hallucinated bugs | Evidence required from graph.json fields |
