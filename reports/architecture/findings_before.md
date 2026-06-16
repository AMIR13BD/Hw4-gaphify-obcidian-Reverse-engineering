# Architecture Findings — before

_Candidate architecture issues only. Validate in source before acting._

## Summary

- Total findings: **19**

| Category | Count |
| --- | ---: |
| `code_health_blocker` | 2 |
| `documentation_hub` | 1 |
| `hidden_global_state` | 7 |
| `import_script_mixing` | 2 |
| `mixed_responsibility` | 1 |
| `navigation_scope` | 1 |
| `organization` | 1 |
| `possible_hub` | 4 |

## code_health_blocker

### Syntax blocker in mathsquiz/mathsquiz.py

- **Detector:** `ExecutionBlockerDetector`
- **Severity:** `high` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Source validation proves the file does not compile under Python 3.

**Relation**

Blocks safe AST analysis, testing, and patching.

**Confidence**

Missing parentheses in call to 'print'. Did you mean print(...)? (mathsquiz/mathsquiz.py, line 3)

**Context**

Separate from pure architecture; affects analysis workflow.

**Source validation**

Validated by compile().

**Evidence**

- `source` mathsquiz/mathsquiz.py Missing parentheses in call to 'print'. Did you mean print(...)? (mathsquiz/mathsquiz.py, line 3)

**Next validation steps**

- Fix syntax before automated refactor.

### Syntax blocker in polygons/polygons.py

- **Detector:** `ExecutionBlockerDetector`
- **Severity:** `high` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Source validation proves the file does not compile under Python 3.

**Relation**

Blocks safe AST analysis, testing, and patching.

**Confidence**

invalid syntax (polygons/polygons.py, line 29)

**Context**

Separate from pure architecture; affects analysis workflow.

**Source validation**

Validated by compile().

**Evidence**

- `source` polygons/polygons.py invalid syntax (polygons/polygons.py, line 29)

**Next validation steps**

- Fix syntax before automated refactor.


## documentation_hub

### Documentation/knowledge hub candidate: Maths Quiz

- **Detector:** `GodNodeCandidateDetector`
- **Severity:** `medium` · **Confidence:** `medium` · **Status:** `needs_manual_validation`

**Observation**

The graph suggests `Maths Quiz` is a documentation/knowledge hub, not necessarily a code bottleneck.

**Relation**

High total degree in metrics; graph suggests central role.

**Confidence**

Derived from potential_god_nodes in metrics JSON.

**Context**

OBS: hub list in metrics. REL: inspect node links. CONF: AST graph is EXTRACTED.

**Source validation**

Graph centrality only; needs manual confirmation in source.

**Evidence**

- `metric` reports/architecture/metrics_before.json total_degree=4

**Next validation steps**

- Open source file and confirm responsibilities.
- Compare with obsidian/hot.md ranking.


## hidden_global_state

### Possible hidden global `score` in print_final_scores()

- **Detector:** `HiddenGlobalStateDetector`
- **Severity:** `medium` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Function `print_final_scores` appears to use global `score` instead of its parameters.

**Relation**

Parameter/global mismatch increases coupling.

**Confidence**

AST or text scan of function body.

**Context**

Example: print_final_scores(final_score) prints global score.

**Source validation**

Validated by source scan.

**Evidence**

- `source` mathsquiz/mathsquiz-step2.py uses global `score` (L25)

**Next validation steps**

- Confirm intended parameter usage in source.

### Possible hidden global `score` in print_final_scores()

- **Detector:** `HiddenGlobalStateDetector`
- **Severity:** `medium` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Function `print_final_scores` appears to use global `score` instead of its parameters.

**Relation**

Parameter/global mismatch increases coupling.

**Confidence**

AST or text scan of function body.

**Context**

Example: print_final_scores(final_score) prints global score.

**Source validation**

Validated by source scan.

**Evidence**

- `source` mathsquiz/mathsquiz-step2.py uses global `score` (L26)

**Next validation steps**

- Confirm intended parameter usage in source.

### Possible hidden global `score` in print_final_scores()

- **Detector:** `HiddenGlobalStateDetector`
- **Severity:** `medium` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Function `print_final_scores` appears to use global `score` instead of its parameters.

**Relation**

Parameter/global mismatch increases coupling.

**Confidence**

AST or text scan of function body.

**Context**

Example: print_final_scores(final_score) prints global score.

**Source validation**

Validated by source scan.

**Evidence**

- `source` mathsquiz/mathsquiz-step2.py uses global `score` (L28)

**Next validation steps**

- Confirm intended parameter usage in source.

### Possible hidden global `score` in print_final_scores()

- **Detector:** `HiddenGlobalStateDetector`
- **Severity:** `medium` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Function `print_final_scores` appears to use global `score` instead of its parameters.

**Relation**

Parameter/global mismatch increases coupling.

**Confidence**

AST or text scan of function body.

**Context**

Example: print_final_scores(final_score) prints global score.

**Source validation**

Validated by source scan.

**Evidence**

- `source` mathsquiz/mathsquiz-step2.py uses global `score` (L30)

**Next validation steps**

- Confirm intended parameter usage in source.

### Possible hidden global `score` in print_final_scores()

- **Detector:** `HiddenGlobalStateDetector`
- **Severity:** `medium` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Function `print_final_scores` appears to use global `score` instead of its parameters.

**Relation**

Parameter/global mismatch increases coupling.

**Confidence**

AST or text scan of function body.

**Context**

Example: print_final_scores(final_score) prints global score.

**Source validation**

Validated by source scan.

**Evidence**

- `source` mathsquiz/mathsquiz-step2.py uses global `score` (L32)

**Next validation steps**

- Confirm intended parameter usage in source.

### Possible hidden global `score` in print_final_scores()

- **Detector:** `HiddenGlobalStateDetector`
- **Severity:** `medium` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Function `print_final_scores` appears to use global `score` instead of its parameters.

**Relation**

Parameter/global mismatch increases coupling.

**Confidence**

AST or text scan of function body.

**Context**

Example: print_final_scores(final_score) prints global score.

**Source validation**

Validated by source scan.

**Evidence**

- `source` mathsquiz/mathsquiz-step3.py uses global `score` (L30)

**Next validation steps**

- Confirm intended parameter usage in source.

### Possible hidden global `score` in print_final_scores()

- **Detector:** `HiddenGlobalStateDetector`
- **Severity:** `medium` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Function `print_final_scores` appears to use global `score` instead of its parameters.

**Relation**

Parameter/global mismatch increases coupling.

**Confidence**

AST or text scan of function body.

**Context**

Example: print_final_scores(final_score) prints global score.

**Source validation**

Validated by source scan.

**Evidence**

- `source` mathsquiz/mathsquiz-step3.py uses global `score` (L32)

**Next validation steps**

- Confirm intended parameter usage in source.


## import_script_mixing

### Top-level side effects in polygons/polygons.py

- **Detector:** `TopLevelSideEffectDetector`
- **Severity:** `medium` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Graph suggests importable code and runnable script behavior may be mixed.

**Relation**

Module-level input/print/calls run on import.

**Confidence**

Top-level execution tags and line matches.

**Context**

Not a confirmed bug unless import fails; needs manual confirmation.

**Source validation**

Validated by source line scan.

**Evidence**

- `source` polygons/polygons.py top-level execution (L3)
- `source` polygons/polygons.py top-level execution (L13)
- `source` polygons/polygons.py top-level execution (L41)
- `source` polygons/polygons.py top-level execution (L58)
- `source` polygons/polygons.py top-level execution (L60)

**Next validation steps**

- Try importing module without running side effects.

### Top-level side effects in mathsquiz/mathsquiz-step2.py

- **Detector:** `TopLevelSideEffectDetector`
- **Severity:** `medium` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Graph suggests importable code and runnable script behavior may be mixed.

**Relation**

Module-level input/print/calls run on import.

**Confidence**

Top-level execution tags and line matches.

**Context**

Not a confirmed bug unless import fails; needs manual confirmation.

**Source validation**

Validated by source line scan.

**Evidence**

- `source` mathsquiz/mathsquiz-step2.py top-level execution (L3)
- `source` mathsquiz/mathsquiz-step2.py top-level execution (L8)
- `source` mathsquiz/mathsquiz-step2.py top-level execution (L23)
- `source` mathsquiz/mathsquiz-step2.py top-level execution (L39)
- `source` mathsquiz/mathsquiz-step2.py top-level execution (L45)

**Next validation steps**

- Try importing module without running side effects.


## mixed_responsibility

### Candidate mixed responsibilities in polygons.py

- **Detector:** `MixedResponsibilityDetector`
- **Severity:** `high` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

Source scan suggests multiple responsibilities in one file: calculation, class_definition, drawing, global_state, input, output, top_level_execution.

**Relation**

Class/model, calculation, drawing, I/O, and top-level execution coexist.

**Confidence**

Responsibility tags detected in source file.

**Context**

SRC: polygons.py combines tutorial script and reusable module patterns.

**Source validation**

Validated by source responsibility scan.

**Evidence**

- `source` polygons/polygons.py responsibility=calculation (L1)
- `source` polygons/polygons.py responsibility=class_definition (L1)
- `source` polygons/polygons.py responsibility=drawing (L1)
- `source` polygons/polygons.py responsibility=global_state (L1)
- `source` polygons/polygons.py responsibility=input (L1)
- `source` polygons/polygons.py responsibility=output (L1)
- `source` polygons/polygons.py responsibility=top_level_execution (L1)

**Next validation steps**

- Split drawing, domain logic, and CLI entry point.
- Phase 9 may consider safe extraction recommendations.


## navigation_scope

### Multiple disconnected graph components

- **Detector:** `DisconnectedComponentsDetector`
- **Severity:** `low` · **Confidence:** `high` · **Status:** `validated_by_source`

**Observation**

The graph shows 7 disconnected components. This may be expected in a tutorial repo with separate exercises.

**Relation**

Weakly connected subgraphs increase navigation scope.

**Confidence**

connected_component_count from metrics.

**Context**

CTX: tutorial repos often split steps into isolated files.

**Source validation**

Validated by metrics component analysis.

**Evidence**

- `metric`  connected_component_count=7

**Next validation steps**

- Map each component to a tutorial module in README.


## organization

### Multiple mathsquiz evolution versions coexist

- **Detector:** `DuplicateEvolutionDetector`
- **Severity:** `low` · **Confidence:** `high` · **Status:** `needs_manual_validation`

**Observation**

Tutorial step files and a combined mathsquiz.py live together. This may be intentional for teaching.

**Relation**

Parallel versions of the same feature increase maintenance surface.

**Confidence**

Found files: mathsquiz/mathsquiz-step1.py, mathsquiz/mathsquiz-step2.py, mathsquiz/mathsquiz-step3.py, mathsquiz/mathsquiz.py

**Context**

Do not treat as automatically bad; teaching repos often keep all steps.

**Source validation**

File inventory validated; intent needs manual confirmation.

**Evidence**

- `source` mathsquiz/mathsquiz-step1.py step/evolution file present
- `source` mathsquiz/mathsquiz-step2.py step/evolution file present
- `source` mathsquiz/mathsquiz-step3.py step/evolution file present
- `source` mathsquiz/mathsquiz.py step/evolution file present

**Next validation steps**

- Confirm which file is canonical for execution.


## possible_hub

### Possible code hub candidate: mathsquiz-step2.py

- **Detector:** `GodNodeCandidateDetector`
- **Severity:** `medium` · **Confidence:** `medium` · **Status:** `needs_manual_validation`

**Observation**

The graph suggests `mathsquiz-step2.py` is a possible hub with elevated connectivity.

**Relation**

High total degree in metrics; graph suggests central role.

**Confidence**

Derived from potential_god_nodes in metrics JSON.

**Context**

OBS: hub list in metrics. REL: inspect node links. CONF: AST graph is EXTRACTED.

**Source validation**

Graph centrality only; needs manual confirmation in source.

**Evidence**

- `metric` reports/architecture/metrics_before.json total_degree=3

**Next validation steps**

- Open source file and confirm responsibilities.
- Compare with obsidian/hot.md ranking.

### Possible code hub candidate: mathsquiz-step3.py

- **Detector:** `GodNodeCandidateDetector`
- **Severity:** `medium` · **Confidence:** `medium` · **Status:** `needs_manual_validation`

**Observation**

The graph suggests `mathsquiz-step3.py` is a possible hub with elevated connectivity.

**Relation**

High total degree in metrics; graph suggests central role.

**Confidence**

Derived from potential_god_nodes in metrics JSON.

**Context**

OBS: hub list in metrics. REL: inspect node links. CONF: AST graph is EXTRACTED.

**Source validation**

Graph centrality only; needs manual confirmation in source.

**Evidence**

- `metric` reports/architecture/metrics_before.json total_degree=3

**Next validation steps**

- Open source file and confirm responsibilities.
- Compare with obsidian/hot.md ranking.

### Possible code hub candidate: polygons.py

- **Detector:** `GodNodeCandidateDetector`
- **Severity:** `medium` · **Confidence:** `medium` · **Status:** `needs_manual_validation`

**Observation**

The graph suggests `polygons.py` is a possible hub with elevated connectivity.

**Relation**

High total degree in metrics; graph suggests central role.

**Confidence**

Derived from potential_god_nodes in metrics JSON.

**Context**

OBS: hub list in metrics. REL: inspect node links. CONF: AST graph is EXTRACTED.

**Source validation**

Graph centrality only; needs manual confirmation in source.

**Evidence**

- `metric` reports/architecture/metrics_before.json total_degree=6

**Next validation steps**

- Open source file and confirm responsibilities.
- Compare with obsidian/hot.md ranking.

### Possible code hub candidate: Polygon

- **Detector:** `GodNodeCandidateDetector`
- **Severity:** `medium` · **Confidence:** `medium` · **Status:** `needs_manual_validation`

**Observation**

The graph suggests `Polygon` is a possible hub with elevated connectivity.

**Relation**

High total degree in metrics; graph suggests central role.

**Confidence**

Derived from potential_god_nodes in metrics JSON.

**Context**

OBS: hub list in metrics. REL: inspect node links. CONF: AST graph is EXTRACTED.

**Source validation**

Graph centrality only; needs manual confirmation in source.

**Evidence**

- `metric` reports/architecture/metrics_before.json total_degree=4

**Next validation steps**

- Open source file and confirm responsibilities.
- Compare with obsidian/hot.md ranking.


## Phase 9 Note

Recommendations are not included here. Phase 9 should map validated findings to actions.
