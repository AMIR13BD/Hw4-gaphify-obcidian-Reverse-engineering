# Token Efficiency Report

## Context Problem

Naive reverse engineering loads entire repositories and raw graph dumps into an LLM context.
Graph-guided retrieval uses Obsidian navigation, hot.md ranking, and metrics to focus agents.

## Estimation Method

- Rule: `estimated_tokens = ceil(character_count / 4)`
- Character-based estimate only; not provider billing or tokenizer-accurate counts.

## Context Bundles

| Bundle | Files | Estimated tokens | Description |
| --- | ---: | ---: | --- |
| naive_full_context | 7 | 2900 | All target .py and .md files |
| naive_source_only | 5 | 2545 | All target .py files |
| naive_evidence_dump | 41 | 78646 | Raw graphs + architecture/comparison/test reports |
| graph_guided_minimal | 8 | 6643 | Obsidian index/hot + top node pages + metrics |
| graph_guided_after | 4 | 9820 | After metrics/findings/recommendations + comparison md |
| agent_detection | 12 | 8369 | Metrics + hot.md + hub sources for detection |
| agent_recommendation | 7 | 9422 | Findings JSON + affected source files |
| agent_comparison | 8 | 24777 | Phase-specific before/after metrics/findings/recs + patch/regression |

## Scenario Comparison

| Scenario | Baseline tokens | Graph-guided tokens | Saved | % saved |
| --- | ---: | ---: | ---: | ---: |
| architecture_detection | 81546 | 8369 | +73177 | 89.7% |
| recommendation_generation | 81546 | 9422 | +72124 | 88.4% |
| before_after_comparison | 48440 | 24777 | +23663 | 48.9% |

## Savings Result

- Total baseline (scenarios): **211532**
- Total graph-guided (scenarios): **42568**
- Total tokens saved: **168964** (79.9%)

## Graph-Guided Retrieval

Graphify produced metrics and hub candidates; Obsidian index/hot.md and node pages steer agents to high-centrality files instead of reading every source file.

## Limitations

- Estimates only — not provider billing or tokenizer-accurate counts.
- Small teaching repo — raw graph/report dumps can exceed source-only context.
- Token efficiency is more meaningful on larger repositories.
- Primary benefit here may be focus and traceability, not only raw token reduction.
- No real provider token logs were available for this phase.

## Course Requirement Support

Demonstrates whether graph/wiki context reduces estimated tokens versus naive full dumps for detection, recommendation, and comparison tasks.

## Notes for README

Include estimation disclaimer, scenario table, and honest note if savings are small.
