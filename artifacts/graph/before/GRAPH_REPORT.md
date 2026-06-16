# Graph Report - broken-python  (2026-06-16)

## Corpus Check
- 7 files · ~1,763 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 26 nodes · 20 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fc222e24`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]

## God Nodes (most connected - your core abstractions)
1. `Polygon` - 4 edges
2. `Maths Quiz` - 4 edges
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

## Communities (8 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.40
Nodes (4): Introduction, Maths Quiz, Objectives, The Files

### Community 1 - "Community 1"
Cohesion: 0.40
Nodes (3): # TODO: find a better way to work this stuff out, # TODO: perhaps I should use the class Polygon instead!, # TODO: make this work for any type of polygon

### Community 4 - "Community 4"
Cohesion: 0.50
Nodes (3): Object, calc_polygon_details(), Polygon

## Knowledge Gaps
- **4 isolated node(s):** `broken-python`, `Introduction`, `Objectives`, `The Files`
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Polygon` connect `Community 4` to `Community 1`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **What connects `# TODO: find a better way to work this stuff out`, `# TODO: perhaps I should use the class Polygon instead!`, `# TODO: make this work for any type of polygon` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._