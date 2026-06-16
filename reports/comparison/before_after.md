# Before/After Comparison

## Executive Summary

- Execution/syntax blockers reduced after Phase 10 safe patches.
- Finding count decreased from 19 to 8; many pre-patch issues no longer detected on patched code.
- The graph became slightly smaller after patching; this may reflect removal of invalid syntax-related structure.

Architecture improvement must be interpreted together with findings and tests.

## Metrics

| Metric | Before | After | Delta | Note |
| --- | ---: | ---: | ---: | --- |
| node_count | 26.0 | 25.0 | -1 | The graph became slightly smaller after patching. |
| link_count | 20.0 | 19.0 | -1 | This supports that one invalid/obsolete relation may have been removed. |
| connected_component_count | 7.0 | 7.0 | +0 | Component count unchanged or shifted. |
| community_count | 8.0 | 7.0 | -1 | Community structure may shift after code changes. |
| low_confidence_link_count | 0.0 | 0.0 | +0 | Low-confidence links are graph evidence only. |

## Findings

- Before: **19** · After: **8**
- Resolved/removed: **6** · Remaining: **8**
- Code-health blockers: 2 → 0

### Category counts

| Category | Before | After |
| --- | ---: | ---: |
| `code_health_blocker` | 2 | 0 |
| `documentation_hub` | 1 | 1 |
| `hidden_global_state` | 7 | 0 |
| `import_script_mixing` | 2 | 0 |
| `mixed_responsibility` | 1 | 1 |
| `navigation_scope` | 1 | 1 |
| `organization` | 1 | 1 |
| `possible_hub` | 4 | 4 |

## Recommendations

- Before: **19** · After: **8**
- Patchable: 11 → 0

## What Improved

- Syntax blocker in mathsquiz/mathsquiz.py
- Syntax blocker in polygons/polygons.py
- Possible hidden global `score` in print_final_scores()
- Possible hidden global `score` in print_final_scores()
- Top-level side effects in mathsquiz/mathsquiz-step2.py
- Top-level side effects in polygons/polygons.py

## What Remains

- Multiple disconnected graph components
- Multiple mathsquiz evolution versions coexist
- Possible code hub candidate: mathsquiz-step2.py
- Possible code hub candidate: mathsquiz-step3.py
- Documentation/knowledge hub candidate: Maths Quiz
- Possible code hub candidate: polygons.py
- Possible code hub candidate: Polygon
- Candidate mixed responsibilities in polygons.py

## Graph Delta

- Top hubs before: polygons.py, Maths Quiz, Polygon, mathsquiz-step2.py, mathsquiz-step3.py
- Top hubs after: polygons.py, Maths Quiz, mathsquiz-step2.py, mathsquiz-step3.py, Polygon
- Removed nodes: object
- Before: graph story described pre-patch connectivity and hub candidates. After: graph story reflects patched code structure. Safe Phase 10 patches changed syntax/globals/main guards; graph metrics shifted accordingly. Architecture improvement must be interpreted together with findings and tests.

## Evidence Paths

- `findings_after`: C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3\reports\architecture\findings_after.json
- `findings_before`: C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3\reports\architecture\findings_before.json
- `metrics_after`: C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3\reports\architecture\metrics_after.json
- `metrics_before`: C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3\reports\architecture\metrics_before.json
- `patch_diffs`: C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3\artifacts\patches\before\diffs
- `patch_result`: C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3\reports\architecture\patch_result_before.json
- `recommendations_after`: C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3\reports\architecture\recommendations_after.json
- `recommendations_before`: C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3\reports\architecture\recommendations_before.json
- `regression`: C:\Users\ameer\OneDrive\Desktop\Ai-wdefe3\reports\tests\regression_before.json

## Notes for README

- Small teaching repo (`martinpeck/broken-python`); graph metrics are evidence, not final proof.
- No dedicated target test suite; regression used compile/AST/project pytest.
- Phase 10 patched 4 whitelisted files with backups/diffs.
- Screenshots will be added in Phase 15.

## Limitations

- Metric decreases are not automatically good.
- Finding matching uses id/category/file heuristics.
- Documentation/navigation findings may remain by design.
