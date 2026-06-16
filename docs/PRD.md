# Product Requirements Document — EX04 Graph-Guided Reverse Engineering Agent

**Project:** Assignment 04 — Reverse Engineering, Debugging, and Token-Efficient Agentic AI  
**Course:** Dr. Yoram Segal — AI Agents (Lecture 07)  
**Version:** 1.0 (Planning)  
**Date:** June 2026

---

## 1. Project Purpose

Build a **local-first, multi-agent Python system** that:

1. Reverse-engineers an unfamiliar Python repository using **Graphify/Grphify** and **Obsidian** as the primary knowledge architecture.
2. Tells the **story of the graph** — what the architecture reveals, how the code was planned, what developers focused on, how code is organized, where architecture bugs live, and what recommendations improve the system.
3. Applies **safe architectural improvements**, validates with **unit tests**, re-runs Graphify, and produces **before/after proof** including **token-efficiency comparison**.
4. Implements an original extension: **dynamic `hot.md` generation** from `graph.json` and `git diff`.

This is **not** a simple bug-fix assignment. The deliverable is evidence of **architectural understanding** mediated by graph knowledge, agent orchestration, and measurable context reduction.

---

## 2. Users and Stakeholders

| Stakeholder | Role | Needs |
|-------------|------|-------|
| **Student (primary operator)** | Builds and submits EX04 | Runnable local pipeline, clear docs, grading-ready artifacts |
| **Dr. Yoram Segal (lecturer)** | Evaluates assignment | Graph story, agent workflow, OOP quality, token metrics, originality |
| **Future maintainers** | Extend the tool | Modular `src/` layout, PRD sub-docs per mechanism, ≥85% test coverage |
| **LLM agents (runtime)** | Execute specialized tasks | Compact `index.md` / `hot.md`, structured `graph.json`, deterministic fallbacks |

---

## 3. Assignment Interpretation (from course PDFs)

### 3.1 EX04 core message

- Clone a **real Python repo** and understand it **architecturally**, not only via README claims.
- Run **Graphify → Obsidian** to create an active knowledge space (`index.md`, `hot.md`, linked wiki pages).
- Build an **agentic AI workflow** (CrewAI or LangGraph) that:
  - Detects architecture issues (god nodes, bottlenecks, mixed responsibilities, isolation, ambiguous edges, docs-without-code, weak traceability, duplicate responsibilities, nodes near failing tests).
  - Recommends and applies **safe** improvements.
  - Re-runs Graphify and compares **before vs after**.
  - Reports **token / context efficiency** (workflow-level and graph-guided retrieval).

### 3.2 Lecture 07 synthesis

- **Three-layer architecture:** Files (raw) → Graphify (structural skeleton) → Obsidian (semantic wiki).
- **Edge types:** Extracted (strong), Inferred (needs validation), Ambiguous (manual review).
- **Reading levels:** Macro (communities, hubs, bridges) → Meso (domains/layers) → Micro (node, relation, confidence, source).
- **Token efficiency:** Prefer graph-guided `index.md` + `hot.md` over dumping full codebase into context; measure signal-to-noise; explain if savings were not achieved.
- **Lost in the Middle:** Critical instructions and evidence must appear at context boundaries (start/end), not buried in middle noise.

### 3.3 Software submission guidelines (mandatory engineering bar)

- `uv` (not `pip`), `pyproject.toml`, `uv.lock`
- `src/`, `tests/`, `docs/`, `config/`, `data/`, `reports/`, `artifacts/`, `obsidian/`
- Python files ≤150 lines; OOP; DRY; SDK-style entry point
- TDD mindset; ≥85% coverage; Ruff zero violations
- `.env-example` only; no secrets in git
- PRD → PLAN → TODO before implementation

---

## 4. Chosen Repository

**Exact base repository:** [`martinpeck/broken-python`](https://github.com/martinpeck/broken-python)

### 4.1 Why this repo was chosen

| Criterion | `martinpeck/broken-python` | Alternatives |
|-----------|------------------------------|--------------|
| Assignment fit | Official EX04 base repo; Python snippets for debugging and improvement | `BugsInPy` — real bugs but heavier Docker/venv setup |
| Local control | Small, clone-friendly, predictable test surface | `andela/buggy-python` — similar but less aligned with “broken snippets” pedagogy |
| Graph story potential | Intentionally imperfect structure → god nodes, mixed responsibilities, traceability gaps | Easier to demonstrate architectural narrative than pure bug-hunt |
| Reverse engineering | README is insufficient; graph + tests reveal true design | Matches lecturer intent |
| Risk | Lower environment friction than BugsInPy on Windows | BugsInPy discouraged without Docker/Python expertise per EX04 “Don’t” |

**Decision rule:** Do not switch repositories unless cloning/installation is impossible. Repository was verified reachable (`git ls-remote` succeeded).

### 4.2 Repository role in the system

- **Target codebase** cloned under `data/target_repo/broken-python/` (or submodule path documented in PLAN).
- **Not merged** into our agent project root; kept isolated for Graphify runs and patch application.
- Our project wraps orchestration around this external repo.

---

## 5. Required Inputs and Outputs

### 5.1 Inputs

| Input | Source | Description |
|-------|--------|-------------|
| Target repo | `martinpeck/broken-python` | Cloned Python project |
| Graphify CLI | Local install / `uv run` | Produces graph artifacts |
| `graph.json` | Graphify export | Canonical graph data |
| `GRAPH_REPORT.md`, `graph.html` | Graphify export | Human interpretation + visualization |
| Git state | `git diff`, `git status` in target repo | Changed files for dynamic `hot.md` |
| Config | `config/setup.json`, `.env` (optional LLM) | Paths, limits, feature flags |
| Unit test command | Target repo + our wrapper | Regression gate |

### 5.2 Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Obsidian vault | `obsidian/` | `index.md`, `hot.md`, per-node/cluster pages |
| Graph artifacts | `artifacts/graph/{before,after}/` | `graph.json`, `graph.html`, `GRAPH_REPORT.md` |
| Agent run logs | `reports/agent_runs/` | Per-agent decisions, timestamps |
| Architecture findings | `reports/architecture/` | Bugs, recommendations, evidence links |
| Patches | `artifacts/patches/` | Safe diffs applied to target repo |
| Test results | `reports/tests/` | Before/after pytest output |
| Comparison report | `reports/comparison/` | Graph metrics + narrative |
| Token report | `reports/token_efficiency/` | Baseline vs graph-guided context sizes |
| Final README | `README.md` (later) | Screenshots, diagrams, graph story, extension |

---

## 6. Functional Requirements

### FR-1 Repository setup
- Clone `martinpeck/broken-python` into workspace.
- Detect Python version, dependencies, and test entry point.
- Create/adapt virtual environment via `uv`.

### FR-2 Graphify execution
- Run Graphify on target repo (before and after improvements).
- Collect `graph.json`, `graph.html`, `GRAPH_REPORT.md`, and any `index.md` / `hot.md` templates Graphify emits.

### FR-3 Graph parsing and metrics
- Parse nodes, edges, labels, confidence, `source_file`.
- Compute centrality, community hints, hub/bottleneck candidates, isolated clusters.

### FR-4 Obsidian vault generation
- Generate `obsidian/index.md` — compact navigation hub (critical files, communities, investigation entry points).
- Generate `obsidian/hot.md` — urgent investigation page (bugs, god nodes, suspicious edges).
- Create linked Markdown pages per significant cluster/node (traceable to `source_file`).

### FR-5 Dynamic `hot.md` (original extension)
- Merge `graph.json` metrics with `git diff` changed files.
- Rank suspicious nodes by centrality and proximity to changed files / failing tests.
- Auto-update `hot.md` with affected files, architecture problem hypothesis, investigation path, before/after notes.

### FR-6 Multi-agent workflow (LangGraph)
- Eleven specialized agents + supervisor loop (see `docs/PRD_agent_workflow.md`).
- Iterative loop: Graphify → analyze → recommend → patch → test → Graphify → compare → continue/stop.

### FR-7 Architecture bug detection
Detect and document (with graph evidence):
- God nodes / hubs with excessive fan-in/out
- Bottlenecks and single points of failure
- Mixed responsibilities
- Isolated components
- Unclear / ambiguous edges
- Docs without code (traceability gaps)
- Weak PRD/requirement → implementation links
- Duplicate / overlapping responsibilities
- Nodes suspicious by centrality or proximity to failing tests

### FR-8 Recommendations
- Produce prioritized, evidence-backed architectural recommendations.
- Classify: safe auto-apply vs human-review vs documentation-only.

### FR-9 Safe patch application
- Apply only **reversible, low-risk** refactors (extract function, split module, add facade, clarify imports).
- Never apply irreversible/destructive changes without explicit approval flag.

### FR-10 Test execution
- Run target repo unit tests before and after each patch cycle.
- Block further patches on regression.

### FR-11 Before/after comparison
- Diff graph metrics (node/edge counts, centrality, cluster cohesion, isolation).
- Diff test status.
- Narrative “graph story” delta.

### FR-12 Token efficiency reporting
- Measure baseline context (full relevant files / naive RAG chunk set).
- Measure graph-guided context (`index.md` + `hot.md` + selected wiki pages).
- Report token/character estimates; explain failure to save tokens if applicable.

---

## 7. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | **Local-first:** entire pipeline runs without paid API keys |
| NFR-2 | **Deterministic fallback:** rule-based findings from `graph.json` when LLM unavailable |
| NFR-3 | **uv-only** dependency management |
| NFR-4 | **File size:** each Python module ≤150 lines |
| NFR-5 | **OOP:** agents as classes; shared logic in services, not duplicated |
| NFR-6 | **Coverage:** ≥85% on public functions in `src/` |
| NFR-7 | **Lint:** Ruff zero violations |
| NFR-8 | **Security:** no real API keys; `.env-example` only |
| NFR-9 | **Traceability:** every finding links to `source_file` + edge type + confidence |
| NFR-10 | **Reproducibility:** versioned artifacts under `artifacts/` and `reports/` |

---

## 8. Acceptance Criteria

- [ ] `martinpeck/broken-python` cloned and tests run locally
- [ ] Graphify produces before/after artifacts stored under `artifacts/graph/`
- [ ] Obsidian vault contains `index.md`, `hot.md`, and linked wiki pages
- [ ] Dynamic `hot.md` updates when `git diff` changes and graph metrics shift
- [ ] LangGraph workflow executes full loop with logged agent handoffs
- [ ] At least one architecture bug identified with graph evidence (god node, bottleneck, etc.)
- [ ] At least one safe improvement applied; tests pass after change
- [ ] Before/after comparison report with metrics and narrative
- [ ] Token efficiency report with baseline vs graph-guided numbers
- [ ] `docs/PRD.md`, `PLAN.md`, `TODO.md`, and mechanism PRDs present
- [ ] (Implementation phase) `pyproject.toml`, `uv.lock`, `src/`, `tests/`, Ruff clean, ≥85% coverage
- [ ] (Submission phase) README with screenshots, diagrams, graph story, extension explanation

---

## 9. Local-Only / Environment Constraints

- **OS:** Windows 10+ (developer machine)
- **Python:** 3.10+ (per course Ruff target)
- **Package manager:** `uv` exclusively (`uv sync`, `uv run`, `uv add`)
- **Graphify:** installed locally; path configured in `config/setup.json`
- **Obsidian:** vault folder generated as Markdown; Obsidian app optional for viewing
- **LLM (optional):** Ollama or local endpoint; if absent, deterministic analyzers only
- **No BugsInPy Docker** unless explicitly approved (EX04 discourages without expertise)

---

## 10. Agent Workflow Requirements

See **`docs/PRD_agent_workflow.md`** for full detail.

Summary:
- **LangGraph** supervisor loop with max iterations and stop conditions
- Agents: RepositorySetup, GraphifyRunner, GraphParser, ObsidianVault, GraphInterpreter, ArchitectureBug, Recommendation, Patch, TestRunner, ComparisonReport, Supervisor
- Shared state object carries artifacts paths, findings, patch queue, metrics
- Guardrails: read-only analysis agents vs write-capable PatchAgent
- Human-in-the-loop flag for irreversible operations

---

## 11. Graphify / Obsidian Requirements

See **`docs/PRD_graphify_pipeline.md`**.

Summary:
- Treat Graphify output as **evidence**, not verdict — validate EXTRACTED vs INFERRED vs AMBIGUOUS
- Read graph at three levels: macro / meso / micro
- `index.md` = guided retrieval hub (LLM Wiki pattern)
- `hot.md` = urgent investigation surface (god nodes, failing-test proximity)
- Wiki pages must cite `source_file` before conclusions

---

## 12. Token-Efficiency Requirements

See **`docs/PRD_token_efficiency.md`**.

Summary:
- Compare **workflow-level** token use (full dump vs agent steps)
- Compare **graph-guided retrieval** (`index.md` + `hot.md` + 2–3 wiki pages vs full repo text)
- Target: demonstrate reduction aligned with Lecture 07 (up to ~71.5× reported for graph-guided code queries — aspirational, not guaranteed)
- If no savings: document why (small repo, redundant index, ambiguous edges requiring full file reads)

---

## 13. Before/After Architecture Proof Requirements

- Side-by-side `graph.json` metrics table
- Screenshots or exported `graph.html` snapshots in `reports/comparison/`
- Narrative sections:
  - **Architecture before** (graph story)
  - **Problem** (evidence chain)
  - **Improvement** (patch description)
  - **Architecture after** (graph story delta)
- Test pass/fail evidence
- Optional: diff visualization of hub centrality changes

---

## 14. Testing Requirements

- **Unit tests** for all public functions in `src/` (graph parser, metrics, hot.md builder, token estimator)
- **Integration tests** for pipeline stages with fixture `graph.json`
- **Coverage:** ≥85% (`fail_under = 85` in `pyproject.toml`)
- **TDD encouraged** for new modules
- Target repo tests invoked via `TestRunnerAgent` / SDK wrapper

---

## 15. Original Extension: Dynamic `hot.md`

See **`docs/PRD_dynamic_hotmd.md`**.

**Minimum extension scope:**
- Input: `graph.json` + `git diff` + optional failing test file list
- Output: ranked suspicious nodes, affected files, problem hypothesis, investigation path, before/after notes in `obsidian/hot.md`
- Trigger: after Graphify run, after patch, and on explicit CLI command

---

## 16. Out of Scope (Planning Phase)

- Implementation code (`src/`, `tests/`, `pyproject.toml`)
- Final README screenshots
- GitHub submission packaging
- Paid cloud LLM integrations

---

## 17. Related Documents

| Document | Purpose |
|----------|---------|
| `docs/PLAN.md` | Technical architecture and diagrams |
| `docs/TODO.md` | Phased implementation checklist |
| `docs/PRD_graphify_pipeline.md` | Graphify/Obsidian mechanism |
| `docs/PRD_agent_workflow.md` | LangGraph agents mechanism |
| `docs/PRD_token_efficiency.md` | Token measurement mechanism |
| `docs/PRD_dynamic_hotmd.md` | Dynamic hot.md mechanism |

---

## 18. Source PDFs (local)

| File | Role |
|------|------|
| `ex04-gaphify-obcidian-Reverse-engineering (1).pdf` | Assignment spec |
| `L07-Lesson-Summary.pdf` | Lecture concepts |
| `Part-A-Active_Knowledge_Architecture.pdf` | (image-only extract; concepts covered in L07/B/C) |
| `PART-B-ארכיטקטורות_ידע_מבוססות_גרפים_...pdf` | Graph + wiki + token theory |
| `PART-C-כיצד_קוראים,_מפרשים_ומסיקים_...pdf` | Graph reading methodology |
| `software_submission_guidelines-V3.pdf` | Engineering standards |
