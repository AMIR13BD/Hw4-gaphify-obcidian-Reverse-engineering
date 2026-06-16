# PRD — Graphify / Obsidian Pipeline Mechanism

**Parent:** `docs/PRD.md`  
**Mechanism:** Graphify runner, graph parsing, Obsidian vault generation  
**Version:** 1.0 (Planning)

---

## 1. Purpose

Define how the system runs **Graphify (Grphify)** on `martinpeck/broken-python`, parses outputs, and materializes an **Obsidian-compatible knowledge vault** that supports graph-guided reverse engineering and token-efficient agent context.

---

## 2. Problem Statement

Raw codebase text overwhelms LLM context (noise, Lost in the Middle). Graphify produces a **structural skeleton**; Obsidian adds a **semantic wiki layer**. Together they enable guided retrieval via `index.md` and urgent focus via `hot.md` — core EX04 and Lecture 07 requirements.

---

## 3. Graphify Outputs (Source of Truth)

| Artifact | Required | Use |
|----------|----------|-----|
| `graph.json` | Yes | Machine parsing, metrics, hot.md ranking |
| `graph.html` | Yes | Human visualization, README screenshots |
| `GRAPH_REPORT.md` | Yes | Narrative graph story, anomalies |
| `index.md` | Yes (generated or templated) | Navigation hub |
| `hot.md` | Yes (generated + dynamic extension) | Urgent investigation |

Graphify may also emit `wiki/` pages — merge or regenerate under `obsidian/`.

---

## 4. Three Evidence Layers (PART-C)

Interpret every conclusion across layers:

1. **Files** — raw code, docs, media inputs  
2. **Code** — deterministic AST edges (`imports`, `calls`)  
3. **Semantic** — inferred rationale, `semantically_similar_to`, ambiguous links  

**Rule:** Ask which layer supports each edge before claiming an architecture bug.

---

## 5. Edge Types and Confidence

| Type | Meaning | Agent action |
|------|---------|--------------|
| **EXTRACTED** | Direct from source (import/call) | Strong evidence; cite in reports |
| **INFERRED** | LLM/semantic inference | Validate against `source_file` |
| **AMBIGUOUS** | Uncertain direction/meaning | Flag for manual review; do not auto-patch |

Fields to parse per edge: `label`, `direction`, `confidence`, `source_file`, `rationale_for` (if present).

---

## 6. Graph Reading Protocol (OBS → REL → CONF → CTX → SRC)

1. **Observation** — note hubs, isolated clusters, missing paths (no conclusion yet)  
2. **Relation** — read edge label and direction  
3. **Confidence** — EXTRACTED vs INFERRED vs AMBIGUOUS  
4. **Context** — community, layer, tests, rationale nodes  
5. **Source validation** — open `source_file` before final wording  

---

## 7. Architecture Signals to Detect

| Signal | Graph indicator | Interpretation caution |
|--------|-----------------|------------------------|
| God node / hub | High degree, high betweenness | May be legitimate facade — check alternatives |
| Bottleneck | Most paths through one node | Small change → wide impact |
| Isolated cluster | Low external connectivity | May be adapter, legacy, or parser gap |
| Docs without code | Doc community, no `implements` edges | Traceability gap, not proof of missing feature |
| Semantic similarity | `semantically_similar_to` | Not duplicate — verify call sites |
| Ambiguous edge | Low confidence | Investigation required |

---

## 8. Functional Requirements

### GPF-1 GraphifyRunner
- Execute Graphify CLI against configurable target path
- Support `before` and `after` output directories
- Capture stdout/stderr to `reports/graphify/`
- Fail gracefully with actionable error if CLI missing

### GPF-2 ArtifactCollector
- Normalize outputs into `artifacts/graph/{phase}/`
- Verify required files exist; warn on partial runs
- Store run metadata (timestamp, graphify version, commit hash)

### GPF-3 GraphParser
- Load `graph.json` into typed models (`GraphNode`, `GraphEdge`, `GraphDocument`)
- Index nodes by `id`, `source_file`, `type`
- Build adjacency lists for directed analysis

### GPF-4 MetricsEngine
- Degree centrality, betweenness (approximate for large graphs)
- Community/cluster detection (connected components + label grouping)
- Hub candidate scoring
- Isolation score per cluster
- Docs-without-code detector (doc nodes without code edges)

### GPF-5 ObsidianVaultBuilder
- Write `obsidian/index.md`:
  - Portfolio/domain summary
  - Top communities with links
  - Entry points for investigation
  - Links to `hot.md`, `GRAPH_REPORT` summary
- Write per-entity pages under `obsidian/nodes/`, `obsidian/clusters/`
- Use `[[wikilinks]]` compatible with Obsidian
- Include `source_file` backlinks on every page

### GPF-6 hot.md (static baseline)
- List top N suspicious nodes from metrics
- Link to detail pages
- Section: "Investigation queue" with prioritized bullets

---

## 9. Obsidian Vault Structure

```
obsidian/
├── index.md              # Navigation hub (guided retrieval)
├── hot.md                # Urgent issues (+ dynamic updates)
├── log.md                # Run log / decisions (optional)
├── clusters/
│   └── {cluster_id}.md
├── nodes/
│   └── {node_id}.md
└── reports/
    └── graph_summary.md  # Distilled GRAPH_REPORT.md
```

---

## 10. index.md Content Requirements

Per EX04 and LLM Wiki pattern:

- **Compact** — suitable for start-of-context placement (avoid Lost in the Middle)
- Sections:
  - Repository overview (1 paragraph)
  - Critical files (bulleted, linked)
  - Community map (table or list)
  - Known architecture risks (from metrics)
  - How to investigate (link to `hot.md`)
- Token budget target: configurable max chars (default 4000) with truncation strategy

---

## 11. hot.md Content Requirements

Per EX04:

- Urgent bug investigation focus
- Markdown pages for critical nodes/edges
- Links to architecture investigation progress
- **Extended by dynamic mechanism** (`PRD_dynamic_hotmd.md`)

---

## 12. Non-Functional Requirements

- Parser must handle missing optional fields without crash
- All public parser/metrics functions unit-tested
- No network calls during parse/metrics
- Deterministic output for same `graph.json` input

---

## 13. Acceptance Criteria

- [ ] Graphify runs twice (before/after) with artifacts stored
- [ ] `graph.json` parsed into internal models
- [ ] Metrics JSON written to `reports/architecture/metrics_{phase}.json`
- [ ] `obsidian/index.md` and baseline `hot.md` generated
- [ ] At least 3 wiki pages with `source_file` citations
- [ ] GRAPH_REPORT key findings mirrored in `obsidian/reports/graph_summary.md`

---

## 14. Risks

| Risk | Mitigation |
|------|------------|
| Graphify not installed on Windows | Document install; verify in Phase 1 |
| `graph.json` schema drift | Schema version check; defensive parsing |
| Over-trusting INFERRED edges | Confidence gates in bug agent |
| Huge graph slows metrics | Limit expensive metrics; sample large graphs |

---

## 15. Dependencies

- Graphify CLI (local)
- Target repo: `martinpeck/broken-python`
- Downstream: ArchitectureBugAgent, DynamicHotMdBuilder
