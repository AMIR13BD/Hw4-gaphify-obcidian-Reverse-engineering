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

### Community 0 - "Community 0"
Cohesion: 0.40
Nodes (4): Introduction, Maths Quiz, Objectives, The Files

### Community 1 - "Community 1"
Cohesion: 0.29
Nodes (5): calc_polygon_details(), Polygon, # TODO: find a better way to work this stuff out, # TODO: perhaps I should use the class Polygon instead!, # TODO: make this work for any type of polygon

## Knowledge Gaps
- **4 isolated node(s):** `broken-python`, `Introduction`, `Objectives`, `The Files`
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `# TODO: find a better way to work this stuff out`, `# TODO: perhaps I should use the class Polygon instead!`, `# TODO: make this work for any type of polygon` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._