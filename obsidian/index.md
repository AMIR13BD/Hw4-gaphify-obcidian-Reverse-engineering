# EX04 Graph Index

- **Repository:** `broken-python` (`data/target_repo/broken-python`)
- **Phase:** `before`

## Graph Summary

- Nodes: **25**
- Links: **19**
- Communities: **7**
- Connected components: **7**

## Top Hubs (graph centrality)

| Node | Degree | Wikilink |
| --- | ---: | --- |
| polygons.py | 6 | [[nodes/polygons_polygons|polygons.py]] |
| Maths Quiz | 4 | [[nodes/mathsquiz_readme_maths_quiz|Maths Quiz]] |
| mathsquiz-step2.py | 3 | [[nodes/mathsquiz_mathsquiz_step2|mathsquiz-step2.py]] |
| mathsquiz-step3.py | 3 | [[nodes/mathsquiz_mathsquiz_step3|mathsquiz-step3.py]] |
| Polygon | 3 | [[nodes/polygons_polygons_polygon|Polygon]] |
| calc_polygon_details() | 2 | [[nodes/polygons_polygons_calc_polygon_details|calc_polygon_details()]] |
| ask_question() | 1 | [[nodes/mathsquiz_mathsquiz_step2_ask_question|ask_question()]] |
| print_final_scores() | 1 | [[nodes/mathsquiz_mathsquiz_step2_print_final_scores|print_final_scores()]] |

## Possible God-Node Candidates

- [[nodes/mathsquiz_mathsquiz_step2|mathsquiz-step2.py]] (degree 3) — graph suggests high connectivity; validate in source before drawing architecture conclusions.
- [[nodes/mathsquiz_mathsquiz_step3|mathsquiz-step3.py]] (degree 3) — graph suggests high connectivity; validate in source before drawing architecture conclusions.
- [[nodes/polygons_polygons|polygons.py]] (degree 6) — graph suggests high connectivity; validate in source before drawing architecture conclusions.
- [[nodes/polygons_polygons_polygon|Polygon]] (degree 3) — graph suggests high connectivity; validate in source before drawing architecture conclusions.
- [[nodes/mathsquiz_readme_maths_quiz|Maths Quiz]] (degree 4) — graph suggests high connectivity; validate in source before drawing architecture conclusions.

## Start Here

- Priority investigation page: [[hot|hot.md]]
- Graph narrative: [[reports/graph_summary|graph_summary]]

## Top Node Pages

- [[nodes/polygons_polygons|polygons.py]]
- [[nodes/mathsquiz_readme_maths_quiz|Maths Quiz]]
- [[nodes/mathsquiz_mathsquiz_step2|mathsquiz-step2.py]]
- [[nodes/mathsquiz_mathsquiz_step3|mathsquiz-step3.py]]
- [[nodes/polygons_polygons_polygon|Polygon]]
- [[nodes/polygons_polygons_calc_polygon_details|calc_polygon_details()]]

## How to Investigate

Use the graph reading flow from the course materials:

1. **OBS** — observe node labels, communities, and degrees in this index.
2. **REL** — follow wikilinks to inspect incoming/outgoing relations on node pages.
3. **CONF** — check link confidence in [[reports/graph_summary|graph_summary]] (AST-only graph here is EXTRACTED-only).
4. **CTX** — read README and source files cited on each node page.
5. **SRC** — open files under the target repo and confirm behavior manually.

_Graph evidence ranks candidates; it is not final proof of bugs or design flaws._
