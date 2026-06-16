# PRD — Token Efficiency Measurement Mechanism

**Parent:** `docs/PRD.md`  
**Mechanism:** Context size estimation and before/after comparison  
**Version:** 1.0 (Planning)

---

## 1. Purpose

Demonstrate EX04 Section 5.5 and Lecture 07 token-efficiency goals: compare **naive full-context** approaches with **graph-guided retrieval** (`index.md`, `hot.md`, selected wiki pages) at both workflow and agent-prompt levels.

---

## 2. Background (Course Concepts)

- **Context window bottleneck:** more tokens ≠ better answers (Context Rot, Attention Dilution)
- **Naive RAG:** chunking adds noise; hierarchy lost
- **LLM Wiki / Guided retrieval:** read small `index.md` first, then 2–3 relevant pages
- **Graphify claim:** up to ~71.5× token reduction for code queries (community reports — use as aspirational benchmark)
- **Lost in the Middle:** place critical content at context start/end

---

## 3. Measurement Goals

| Level | What we measure | EX04 alignment |
|-------|-----------------|----------------|
| **Workflow** | Total tokens/chars across all agent steps | Section 5.5 — workflow comparison |
| **Retrieval** | Context per agent task: baseline vs graph-guided | Section 5.5 — Graphify/index/hot/Obsidian |
| **Before/after** | Context size after architectural improvement | Fewer nodes/edges? smaller hot.md? |

---

## 4. Baseline Context (Control)

Define reproducible baselines:

### B1 — Full repo text
- All `.py` files in target repo concatenated
- Measure: character count, estimated tokens (`chars / 4` heuristic or `tiktoken` if available locally)

### B2 — Naive RAG simulation
- Split repo into fixed-size chunks (e.g., 512 tokens)
- For a standard investigation query, retrieve top-k chunks by keyword overlap
- Measure total chars loaded

### B3 — README + tree
- README + `os.walk` file listing + first 50 lines per file
- Common weak baseline students might use

---

## 5. Graph-Guided Context (Treatment)

### G1 — Index-first
- `obsidian/index.md` only

### G2 — Index + hot
- `index.md` + `hot.md`

### G3 — Guided investigation (recommended)
- `index.md` + `hot.md` + up to 3 linked wiki pages selected by:
  - Nodes ranked in hot.md
  - Changed files from git diff
  - Failing test modules

### G4 — Post-improvement
- Same as G3 after refactor — expect equal or smaller context for same task

---

## 6. Workflow Token Accounting

Track per agent invocation:

| Agent | Typical context inputs |
|-------|------------------------|
| GraphInterpreter | metrics JSON + GRAPH_REPORT excerpt |
| ArchitectureBug | metrics + top N node summaries |
| Recommendation | findings list + 2 wiki pages |
| ComparisonReport | before/after metrics only |

**Metrics to record:**
- `input_chars`, `output_chars` (if LLM used)
- `estimated_input_tokens`, `estimated_output_tokens`
- `cumulative_workflow_tokens`

Store in `reports/token_efficiency/run_{timestamp}.json`

---

## 7. Estimation Methods

### Primary (no external API)
```text
estimated_tokens = ceil(character_count / 4)
```
Document assumption in report.

### Optional (if `tiktoken` added via uv)
- Use `cl100k_base` or model-appropriate encoding
- Fallback to char heuristic on failure

### File-based (deterministic mode)
- No LLM calls → workflow tokens = sum of files read by agents
- Still compare B1 vs G3 file-read totals

---

## 8. Comparison Outputs

`reports/token_efficiency/summary.md` must include:

| Metric | Baseline (B1/B2) | Graph-guided (G3) | Delta % |
|--------|------------------|-------------------|---------|
| Chars for "find god node" task | | | |
| Chars for "explain auth flow" task | | | |
| Chars for full pipeline | | | |
| Wiki pages loaded | N/A | count | |

**Narrative section:**
- Did token savings occur? Yes/no
- If no: explain (repo too small, index larger than code, ambiguous edges forced full file reads, etc.)

---

## 9. Functional Requirements

- TEF-1: `TokenEstimator` service with `estimate_text`, `estimate_files`
- TEF-2: `ContextBundleBuilder` builds B1, B2, G1–G3 bundles for standard tasks
- TEF-3: `WorkflowTokenRecorder` hooks agent execution
- TEF-4: `TokenComparisonReport` writes markdown + JSON
- TEF-5: Integrate with ComparisonReportAgent final output

---

## 10. Standard Evaluation Tasks (Fixed for Reproducibility)

1. **T1:** "Identify the highest-centrality node and explain why it is risky."  
2. **T2:** "List architecture bugs visible in the graph."  
3. **T3:** "What changed after the patch, and did modularity improve?"

Each task runs against B1 and G3; record sizes.

---

## 11. Non-Functional Requirements

- No paid API required for measurement
- Deterministic: same inputs → same token counts
- Unit tests for estimator and bundle builder

---

## 12. Acceptance Criteria

- [ ] Baseline and graph-guided bundles measured for T1–T3
- [ ] Workflow cumulative tokens logged per run
- [ ] Before/after token comparison included in final report
- [ ] Explicit explanation if savings < 10% or negative

---

## 13. Success Interpretation

| Outcome | Interpretation |
|---------|----------------|
| G3 << B1 | Strong EX04 evidence |
| G3 ≈ B1 | Small repo; document honestly |
| G3 > B1 | Index too verbose; compaction needed — valid learning outcome |
| After < Before | Improvement reduced graph complexity or hot.md size |

---

## 14. Risks

| Risk | Mitigation |
|------|------------|
| Token counts misleading without real LLM | Measure file-read proxy + note limitation |
| tiktoken optional dep fails on Windows | Char heuristic default |
| Student inflates baseline | Use fixed B1/B2 definitions in config |
