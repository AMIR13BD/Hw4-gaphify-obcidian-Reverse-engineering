# TODO — EX04 Implementation Phases

**Parent:** `docs/PRD.md`, `docs/PLAN.md`  
**Status:** Planning complete — implementation not started  
**Legend:** `[ ]` pending · `[x]` done · `[-]` cancelled

---

## Phase 0: Locate PDFs and Summarize Requirements

- [x] Search `C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3` for assignment PDFs
- [x] Identify key files:
  - `ex04-gaphify-obcidian-Reverse-engineering (1).pdf` — EX04 assignment
  - `L07-Lesson-Summary.pdf` — Lecture 07 concepts
  - `Part-A-Active_Knowledge_Architecture.pdf` — (image-only; concepts in L07/B/C)
  - `PART-B-ארכיטקטורות_ידע_מבוססות_גרפים_...pdf` — Graph/wiki/token theory
  - `PART-C-כיצד_קוראים,_מפרשים_ומסיקים_...pdf` — Graph reading methodology
  - `software_submission_guidelines-V3.pdf` — Engineering standards
- [x] Extract PDF text to `_pdf_extracts/` for reference
- [x] Confirm base repo choice: `martinpeck/broken-python`
- [x] Create planning documents (`docs/PRD*.md`, `PLAN.md`, `TODO.md`)
- [x] **Approval gate:** Review planning docs before Phase 1

**Phase 0 definition of done:** All planning docs committed; requirements traceable to PDFs.

---

## Phase 1: Clone `martinpeck/broken-python` and Inspect Environment

- [x] Clone repo to `data/target_repo/broken-python/`
- [x] Record commit SHA in `reports/architecture/repo_metadata.json`
- [x] Inventory: Python version, `requirements.txt` / `pyproject.toml`, test layout
- [x] Run existing tests; capture baseline pass/fail (no tests in target repo — documented)
- [x] Document install steps in scratch notes for README (`reports/architecture/phase1_environment_report.md`)
- [x] Verify Graphify CLI install (`graphify --version` or equivalent)
- [x] Manual smoke: run Graphify once on cloned repo; note output paths (`artifacts/graph/before/`)
- [x] Flag blockers (`uv` not installed; no target tests — see phase1 report)

**Definition of done:** Target repo cloned; Graphify produces artifacts. Met (via `graphify update` after `pip install graphifyy`).

---

## Phase 2: Create Project Scaffold and UV Setup

- [x] `uv init` / configure `pyproject.toml` (package name `ex04-agent`)
- [x] Add dependencies: `langgraph`, `langchain-core` (minimal), `pytest`, `pytest-cov`, `ruff`
- [x] Create directory scaffold per `docs/PLAN.md`
- [x] Add `config/setup.json`, `config/rate_limits.json`
- [x] Add `.env-example`, `.gitignore`
- [x] `uv lock` && `uv sync`
- [x] Stub `src/ex04_agent/sdk/sdk.py` and `main.py`
- [x] Configure Ruff and coverage (`fail_under = 85`) in `pyproject.toml`
- [x] Empty `tests/conftest.py` with fixture paths
- [x] Install uv (`uv 0.11.21`) and Graphify via `uv tool install graphifyy`
- [x] Minimal unit tests (version, config, SDK, CLI health)
- [x] Phase 2 report: `reports/environment/phase2_scaffold_report.md`

**Definition of done:** `uv run pytest` passes; `uv run ruff check` clean. Met (5 tests, 90.11% coverage).

---

## Phase 3: Graphify Runner and Artifact Collection

- [x] Implement `GraphCollector` / `GraphifyRunner` service
- [x] Implement `GraphifyRunnerAgent`
- [x] Write artifacts to `artifacts/graph/{before,after}/`
- [x] Capture logs to `reports/graphify/`
- [x] Unit test: mock CLI returns fixture files
- [x] CLI: `uv run ex04-agent graphify --phase before|after`
- [x] Phase 3 report: `reports/graphify/phase3_graphify_runner_report.md`

**Definition of done:** `uv run ex04-agent graphify --phase before` populates artifacts. Met.

---

## Phase 4: Graph Parser and Graph Metrics

- [x] Implement `GraphDocument`, `GraphNode`, `GraphLink` models
- [x] Implement `GraphParser`, `GraphIndexer`
- [x] Implement `MetricsEngine` (degree, betweenness, clusters, god-node flags)
- [x] Implement `GraphParserAgent`
- [x] Export `metrics_{phase}.json`
- [x] Unit tests: fixture `graph.json` in `tests/fixtures/`
- [x] Test edge types EXTRACTED / INFERRED / AMBIGUOUS parsing
- [x] CLI: `uv run ex04-agent parse --phase before|after`
- [x] Phase 4 report: `reports/architecture/phase4_graph_parser_report.md`

**Definition of done:** Metrics JSON generated from before-phase graph. Met.

---

## Phase 5: Obsidian Vault Generation with `index.md` and `hot.md`

- [x] Implement `IndexBuilder`, `VaultBuilder`
- [x] Implement `NodePageBuilder`, `ReportBuilder`
- [x] Implement `ObsidianVaultAgent`
- [x] Generate `obsidian/index.md`
- [x] Generate static baseline `obsidian/hot.md` (centrality-only)
- [x] Generate `obsidian/nodes/{id}.md` for top hubs and sourced nodes
- [x] Generate `obsidian/reports/graph_summary.md` from GRAPH_REPORT
- [x] Unit tests: index content, hot wording, filename sanitization, vault output
- [x] CLI: `uv run ex04-agent obsidian --phase before|after`
- [x] Phase 5 report: `reports/obsidian/phase5_obsidian_vault_report.md`

**Definition of done:** Open `obsidian/` in Obsidian (optional) and navigate index → nodes. Met.

---

## Phase 6: Dynamic `hot.md` from `graph.json` and Git Diff

- [x] Implement `GitDiffReader`
- [x] Implement `NodeRanker` with configurable weights
- [x] Implement `HotMdRenderer` / `DynamicHotMdBuilder`
- [x] Wire into `ObsidianVaultAgent` (`run_dynamic_hotmd`, optional `--dynamic-hot` on obsidian)
- [x] Snapshot to `artifacts/hotmd/`
- [x] Implement before/after notes section
- [x] Unit tests: ranking with fixture diff + graph
- [x] CLI: `uv run ex04-agent hotmd`
- [x] Refactor CLI handlers into `src/ex04_agent/cli/`
- [x] Phase 6 report: `reports/obsidian/phase6_dynamic_hotmd_report.md`

**Definition of done:** Edit file in target repo → regenerate hot.md → changed file appears in ranking. Met (ranking logic verified in unit tests; live repo has clean working tree).

---

## Phase 7: Multi-Agent LangGraph Workflow

- [x] Define `PipelineState` typed dict or dataclass
- [x] Extend `BaseAgent` with `run_pipeline` interface
- [x] Implement all 12 pipeline agents (7 active + 5 placeholders)
- [x] Build `LangGraphWorkflow` with linear edges
- [x] Implement `SupervisorAgent` stop logic (`dry_run_completed`)
- [x] Persist `reports/agent_runs/` traces
- [x] SDK: `Ex04Sdk.run_pipeline()`
- [x] CLI: `uv run ex04-agent pipeline --dry-run --phase before`
- [x] Integration test: dry-run full graph (mocked heavy services)
- [x] Phase 7 report: `reports/agent_runs/phase7_langgraph_workflow_report.md`

**Definition of done:** `uv run ex04-agent pipeline --dry-run` completes all nodes. Met.

---

## Phase 8: Architecture Bug Detection

- [x] Create `ArchitectureFinding` and `EvidenceItem` models (`detection/finding.py`)
- [x] Implement `SourceScanner` (read-only responsibilities, syntax, globals)
- [x] Implement deterministic detectors (`detection/detectors*.py`):
  - [x] `GodNodeCandidateDetector` (metrics hubs; docs vs code)
  - [x] `MixedResponsibilityDetector`
  - [x] `TopLevelSideEffectDetector`
  - [x] `HiddenGlobalStateDetector`
  - [x] `DisconnectedComponentsDetector`
  - [x] `LowConfidenceEdgeDetector` (no fake findings when count is 0)
  - [x] `ExecutionBlockerDetector` (`code_health_blocker`)
  - [x] `DuplicateEvolutionDetector`
- [x] Implement `ArchitectureDetectionEngine` and `ReportWriter`
- [x] Wire `ArchitectureBugAgent` to detection engine
- [x] Output `reports/architecture/findings_{phase}.json` and `.md`
- [x] Output latest `reports/architecture/findings.json`
- [x] CLI: `uv run ex04-agent detect --phase before|after`
- [x] Pipeline dry-run: `architecture_bug` completed (not skipped)
- [x] Unit tests per detector and CLI integration
- [x] Phase 8 report: `reports/architecture/phase8_architecture_detection_report.md`

**Definition of done:** ≥3 finding types fire on broken-python before graph. Met (19 findings, 8 categories).

---

## Phase 9: Recommendation Generation

- [x] Implement deterministic recommendation engine (finding → action mapping)
- [x] Classify `safe_auto` / `review_required` / `docs_only` / `defer`
- [x] Implement `RecommendationAgent`
- [x] Output `recommendations_{phase}.json`/`.md` and `patch_plan_{phase}.json`/`.md`
- [x] Output latest `recommendations.json` and `patch_plan.json`
- [x] Unit tests: mapping, prioritization, patch-plan grouping, engine, CLI, pipeline
- [x] CLI: `uv run ex04-agent recommend --phase before|after`
- [x] Pipeline dry-run: `recommendation` completed; patch/test/comparison still skipped
- [x] Phase 9 report: `reports/architecture/phase9_recommendation_report.md`

**Definition of done:** Recommendations and patch plan generated without modifying target repo. Met.

---

## Phase 10: Safe Patch / Refactor Implementation

- [x] Implement `SafePatcher` (whitelist operations) (`patching/safe_patcher.py`)
- [x] Implement `PatchAgent` with `allow_patches` guard
- [x] Implement deterministic recipes for 4 target files
- [x] Store diffs in `artifacts/patches/{phase}/diffs/`
- [x] Store backups in `artifacts/patches/{phase}/backups/`
- [x] Rollback on apply failure with compile-time validation
- [x] Output `reports/architecture/patch_result_{phase}.json` and `.md`
- [x] CLI: `uv run ex04-agent patch --phase before|after [--allow-patches]`
- [x] Pipeline: `PatchAgent` skipped unless `allow_patches=True`
- [x] Unit tests: model, validator, recipes, diff_writer, safe_patcher, engine, CLI, pipeline
- [x] Phase 10 report: `reports/architecture/phase10_safe_patch_report.md`

**Definition of done:** Safe patches apply cleanly to broken-python with backup/diff/validation. Met (2 files patched, both validate, 96 tests pass).

---

## Phase 11: Regression Test Runner and Validation Agent

- [x] Create `src/ex04_agent/testing/` package (model, command_runner, discovery, validators, result_parser, report_writer, engine)
- [x] Implement `TestRunnerAgent` using `RegressionEngine`
- [x] Detect target repo test suite (no tests found — skipped with warning)
- [x] Compile + AST validation on all target Python files
- [x] Safe import validation (turtle/input files skipped)
- [x] Project pytest + coverage + Ruff validation
- [x] Write `reports/tests/regression_before.json` and `.md`
- [x] CLI: `uv run ex04-agent test --phase before|after`
- [x] Pipeline: `TestRunnerAgent` runs in dry-run pipeline (no longer skipped)
- [x] Unit tests: models, validators, discovery, report writer, CLI, agent, pipeline integration
- [x] Coverage ≥ 85% (achieved 87%)
- [x] `uv run ruff check` — zero violations

**Definition of done:** Regression report generated; compile/AST pass; project tests pass (110); coverage 87%; Ruff clean. Met.

---

## Phase 12: Rerun Graphify After Improvement

- [x] Add `--force` to after-phase Graphify command (`graphify update . --force`)
- [x] Run `uv run ex04-agent graphify --phase after`
- [x] Run parse, obsidian, detect, recommend for after phase
- [x] Generate `artifacts/graph/after/` (graph.json, graph.html, GRAPH_REPORT.md)
- [x] Generate `reports/architecture/metrics_after.json`, `story_after.md`
- [x] Generate `findings_after` and `recommendations_after` (+ patch_plan_after)
- [x] Generate `artifacts/hotmd/hot_after_<timestamp>.md` snapshot
- [x] Pipeline: `uv run ex04-agent pipeline --dry-run --phase after` completes test_runner
- [x] Unit tests: after-phase paths, before isolation, pipeline skips comparison_report
- [x] Phase 12 report: `reports/graphify/phase12_after_graphify_report.md`

**Definition of done:** After artifacts generated for Phase 13 comparison; before artifacts preserved. Met.

---

## Phase 13: Before/After Comparison

- [x] Implement `ComparisonService` / comparison module (metrics, findings, recommendations, graph deltas)
- [x] Implement `ComparisonReportAgent` wired to comparison engine
- [x] CLI: `uv run ex04-agent compare [--before before] [--after after]`
- [x] Pipeline: `comparison_report` completes on after dry-run; skips on before-only
- [x] Write `reports/comparison/before_after.json` and `.md`
- [x] Include graph story delta and patch/regression evidence paths
- [x] Placeholder paths for screenshots (`assets/` noted in report)
- [x] Comparison read-only: compare writes only to `reports/comparison/`
- [x] Comparison-only after dry-run skips artifact regeneration when before/after exist
- [x] Restored frozen before artifacts (26/20, 19 findings, 19 recommendations) from Phase 12
- [x] Read-only tests: compare and pipeline after do not modify before architecture files

**Definition of done:** Comparison report shows measurable before/after table. Met.

---

## Phase 14: Token-Efficiency Report

- [x] Implement `TokenEstimator` (ceil(chars/4), no external APIs)
- [x] Implement `ContextBundleBuilder` and `TokenEfficiencyCollector`
- [x] Build 8 context bundles (naive, graph-guided, agent-focused)
- [x] Compare 3 task scenarios (detection, recommendation, comparison)
- [x] CLI: `uv run ex04-agent token-report [--phase before|after]`
- [x] SDK: `Ex04Sdk.run_token_report()`
- [x] Write `reports/token_efficiency/token_efficiency.json` and `.md`
- [x] Write `context_bundles.json`, `context_bundles.md`, `token_comparison.csv`
- [x] Honest limitations documented (estimates, small repo, focus vs raw savings)
- [x] Unit tests: estimator, bundles, comparator, report writer, CLI, missing files
- [x] Phase 14 report: `reports/token_efficiency/phase14_token_efficiency_report.md`

**Definition of done:** Token summary shows naive vs graph-guided comparison. Met.

---

## Phase 15: README and Final Submission Packaging

- [x] Write `README.md` per EX04 Section 8 (repo choice, RQ, architecture, workflow, findings, patches, comparison, tokens, extension, how-to-run, evidence map, limitations)
- [x] Add `assets/screenshots/README.md` with Obsidian capture instructions
- [x] Screenshot placeholder paths in README (manual capture TODO)
- [x] `reports/final/final_submission_checklist.md`
- [x] `reports/final/final_summary.md`
- [x] Verify deliverables checklist against EX04 Section 7
- [x] Final `uv run pytest` && coverage && Ruff (144 passed, 89.86%, clean)
- [ ] GitHub push (when ready — includes manual screenshots optional)
- [ ] Manual Obsidian screenshots → `assets/screenshots/`
- [ ] Manual clean zip (exclude `.venv/`, caches)

**Definition of done:** Submission-ready repo matching course guidelines V3. Met (pending manual screenshots/zip).

---

## Cross-Cutting Checklist (All Phases)

- [x] No Python file >150 lines
- [x] OOP — no duplicated logic across agents
- [x] No secrets in git — `.env-example` only
- [x] All public functions have tests
- [x] No LLM API for detection/recommendation/patching (deterministic only)
- [ ] Prompt engineering log (N/A — no LLM used)

---

## Current Status Summary

| Phase | Status |
|-------|--------|
| 0 | Complete |
| 1 | Complete |
| 2 | Complete |
| 3 | Complete |
| 4 | Complete |
| 5 | Complete |
| 6 | Complete |
| 7 | Complete |
| 8 | Complete |
| 9 | Complete |
| 10 | Complete |
| 11 | Complete |
| 12 | Complete |
| 13 | Complete |
| 14 | Complete |
| 15 | Complete |

**Next action:** Manual Obsidian screenshots + final clean zip + GitHub push when ready.


