# Graph Summary Report

**Phase:** `before` · **Repository:** `broken-python`

## Metrics Overview

- Nodes: 25
- Links: 19
- Communities: 7
- Connected components: 7
- Low-confidence links: 0

## Relation Counts

- `calls`: 1
- `contains`: 14
- `method`: 1
- `rationale_for`: 3

## Confidence Counts

- `EXTRACTED`: 19

All links in the current AST-only graph are **EXTRACTED** (19/19). No INFERRED or AMBIGUOUS edges were emitted.

## Communities (node counts)

- Community 0: 5 nodes
- Community 1: 8 nodes
- Community 2: 4 nodes
- Community 3: 4 nodes
- Community 5: 2 nodes
- Community 6: 1 nodes
- Community 7: 1 nodes

## Top Hubs

- [[nodes/polygons_polygons|polygons.py]] (degree 6)
- [[nodes/mathsquiz_readme_maths_quiz|Maths Quiz]] (degree 4)
- [[nodes/mathsquiz_mathsquiz_step2|mathsquiz-step2.py]] (degree 3)
- [[nodes/mathsquiz_mathsquiz_step3|mathsquiz-step3.py]] (degree 3)
- [[nodes/polygons_polygons_polygon|Polygon]] (degree 3)
- [[nodes/polygons_polygons_calc_polygon_details|calc_polygon_details()]] (degree 2)
- [[nodes/mathsquiz_mathsquiz_step2_ask_question|ask_question()]] (degree 1)
- [[nodes/mathsquiz_mathsquiz_step2_print_final_scores|print_final_scores()]] (degree 1)

## Low-Confidence / Ambiguous Links

- None in current graph — all links are EXTRACTED.

## GRAPH_REPORT Excerpt

# Graph Report - broken-python  (2026-06-16)

## Corpus Check
- 7 files · ~1,788 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 25 nodes · 19 edges · 7 communities (6 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dfd5ba3e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 5|Community 5]]

## God Nodes (most connected - your core abstractions)
1. `Maths Quiz` - 4 edges
2. `Polygon` - 3 edges
3. `calc_polygon_details()` - 2 edges
4. `# TODO: find a better way to work this stuff out` - 1 edges
5. `# TODO: perhaps I should use the class Polygon instead!` - 1 edges
6. `# TODO: make this work for any type of polygon` - 1 edges
7. `broken-python` - 1 edges
8. `Introduction` - 1 edges
9. `Objectives` - 1 edges
10. `The Files` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (7 total, 1 thin omitted)

_Graph metrics suggest where to look next; source validation is required before architecture or bug conclusions._
