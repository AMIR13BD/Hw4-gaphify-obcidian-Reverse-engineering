# Recommendations (Phase 9)

Phase 9 does not modify the target repository.

- Total recommendations: **19**

| Action type | Count |
| --- | ---: |
| `docs_only` | 3 |
| `review_required` | 16 |

## Top priorities

- `critical` Recommendation for Syntax blocker in mathsquiz/mathsquiz.py (mathsquiz/mathsquiz.py)
- `critical` Recommendation for Syntax blocker in polygons/polygons.py (polygons/polygons.py)
- `high` Recommendation for Candidate mixed responsibilities in polygons.py (polygons/polygons.py)
- `high` Recommendation for Top-level side effects in polygons/polygons.py (polygons/polygons.py)
- `high` Recommendation for Top-level side effects in mathsquiz/mathsquiz-step2.py (mathsquiz/mathsquiz-step2.py)

## review_required

### Recommendation for Syntax blocker in mathsquiz/mathsquiz.py

- Rationale: Mapped from category `code_health_blocker` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz.py
- Validation steps:
  - Fix syntax before automated refactor.

### Recommendation for Syntax blocker in polygons/polygons.py

- Rationale: Mapped from category `code_health_blocker` with deterministic phase-9 policy.
- Affected files: polygons/polygons.py
- Validation steps:
  - Fix syntax before automated refactor.

### Recommendation for Candidate mixed responsibilities in polygons.py

- Rationale: Mapped from category `mixed_responsibility` with deterministic phase-9 policy.
- Affected files: polygons/polygons.py
- Validation steps:
  - Split drawing, domain logic, and CLI entry point.
  - Phase 9 may consider safe extraction recommendations.

### Recommendation for Top-level side effects in polygons/polygons.py

- Rationale: Mapped from category `import_script_mixing` with deterministic phase-9 policy.
- Affected files: polygons/polygons.py
- Validation steps:
  - Try importing module without running side effects.

### Recommendation for Top-level side effects in mathsquiz/mathsquiz-step2.py

- Rationale: Mapped from category `import_script_mixing` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step2.py
- Validation steps:
  - Try importing module without running side effects.

### Recommendation for Possible hidden global `score` in print_final_scores()

- Rationale: Mapped from category `hidden_global_state` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step2.py
- Validation steps:
  - Confirm intended parameter usage in source.

### Recommendation for Possible hidden global `score` in print_final_scores()

- Rationale: Mapped from category `hidden_global_state` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step2.py
- Validation steps:
  - Confirm intended parameter usage in source.

### Recommendation for Possible hidden global `score` in print_final_scores()

- Rationale: Mapped from category `hidden_global_state` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step2.py
- Validation steps:
  - Confirm intended parameter usage in source.

### Recommendation for Possible hidden global `score` in print_final_scores()

- Rationale: Mapped from category `hidden_global_state` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step2.py
- Validation steps:
  - Confirm intended parameter usage in source.

### Recommendation for Possible hidden global `score` in print_final_scores()

- Rationale: Mapped from category `hidden_global_state` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step2.py
- Validation steps:
  - Confirm intended parameter usage in source.

### Recommendation for Possible hidden global `score` in print_final_scores()

- Rationale: Mapped from category `hidden_global_state` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step3.py
- Validation steps:
  - Confirm intended parameter usage in source.

### Recommendation for Possible hidden global `score` in print_final_scores()

- Rationale: Mapped from category `hidden_global_state` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step3.py
- Validation steps:
  - Confirm intended parameter usage in source.

### Recommendation for Possible code hub candidate: mathsquiz-step2.py

- Rationale: Mapped from category `possible_hub` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step2.py
- Validation steps:
  - Open source file and confirm responsibilities.
  - Compare with obsidian/hot.md ranking.

### Recommendation for Possible code hub candidate: mathsquiz-step3.py

- Rationale: Mapped from category `possible_hub` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step3.py
- Validation steps:
  - Open source file and confirm responsibilities.
  - Compare with obsidian/hot.md ranking.

### Recommendation for Possible code hub candidate: polygons.py

- Rationale: Mapped from category `possible_hub` with deterministic phase-9 policy.
- Affected files: polygons/polygons.py
- Validation steps:
  - Open source file and confirm responsibilities.
  - Compare with obsidian/hot.md ranking.

### Recommendation for Possible code hub candidate: Polygon

- Rationale: Mapped from category `possible_hub` with deterministic phase-9 policy.
- Affected files: polygons/polygons.py
- Validation steps:
  - Open source file and confirm responsibilities.
  - Compare with obsidian/hot.md ranking.


## safe_auto


## docs_only

### Recommendation for Documentation/knowledge hub candidate: Maths Quiz

- Rationale: Mapped from category `documentation_hub` with deterministic phase-9 policy.
- Affected files: mathsquiz/README.md
- Validation steps:
  - Open source file and confirm responsibilities.
  - Compare with obsidian/hot.md ranking.

### Recommendation for Multiple disconnected graph components

- Rationale: Mapped from category `navigation_scope` with deterministic phase-9 policy.
- Affected files: N/A
- Validation steps:
  - Map each component to a tutorial module in README.

### Recommendation for Multiple mathsquiz evolution versions coexist

- Rationale: Mapped from category `organization` with deterministic phase-9 policy.
- Affected files: mathsquiz/mathsquiz-step1.py, mathsquiz/mathsquiz-step2.py, mathsquiz/mathsquiz-step3.py, mathsquiz/mathsquiz.py
- Validation steps:
  - Confirm which file is canonical for execution.


## defer

