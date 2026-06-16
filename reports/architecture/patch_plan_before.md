# Patch Plan (Phase 9)

Phase 9 does not modify the target repository.

## safe_candidates_phase10

- `rec_017_execution_blocker_mathsquiz_mathsquiz.py` Remove compile blocker with minimal syntax modernization.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_018_execution_blocker_polygons_polygons.py` Remove compile blocker with minimal syntax modernization.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_008_top_level_polygons_polygons_py` Add safe main guard or move top-level calls into entrypoint.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_009_top_level_mathsquiz_mathsquiz-step2_py` Add safe main guard or move top-level calls into entrypoint.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_010_hidden_global_mathsquiz_mathsquiz-step2.py_print_final_scores` Use function parameters consistently instead of global variables.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_011_hidden_global_mathsquiz_mathsquiz-step2.py_print_final_scores` Use function parameters consistently instead of global variables.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_012_hidden_global_mathsquiz_mathsquiz-step2.py_print_final_scores` Use function parameters consistently instead of global variables.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_013_hidden_global_mathsquiz_mathsquiz-step2.py_print_final_scores` Use function parameters consistently instead of global variables.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_014_hidden_global_mathsquiz_mathsquiz-step2.py_print_final_scores` Use function parameters consistently instead of global variables.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_015_hidden_global_mathsquiz_mathsquiz-step3.py_print_final_scores` Use function parameters consistently instead of global variables.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_016_hidden_global_mathsquiz_mathsquiz-step3.py_print_final_scores` Use function parameters consistently instead of global variables.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.

## review_required_items

- `rec_007_mixed_responsibility_polygons` Separate domain logic from drawing/input and top-level execution.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_001_god_node_mathsquiz_mathsquiz_step2` Inspect responsibility boundaries before structural refactor.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_002_god_node_mathsquiz_mathsquiz_step3` Inspect responsibility boundaries before structural refactor.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_003_god_node_polygons_polygons` Inspect responsibility boundaries before structural refactor.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_004_god_node_polygons_polygons_polygon` Inspect responsibility boundaries before structural refactor.
  - validation: `uv run pytest -q`
  - rollback: Revert planned file edits and re-run detection/recommendation.

## docs_only_items

- `rec_005_god_node_mathsquiz_readme_maths_quiz` Document this as a knowledge hub, not a code bottleneck.
  - validation: `uv run ruff check`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_006_disconnected_components` Document disconnected components as expected tutorial scope.
  - validation: `uv run ruff check`
  - rollback: Revert planned file edits and re-run detection/recommendation.
- `rec_019_duplicate_evolution_mathsquiz` Document tutorial versioning or move variants under examples.
  - validation: `uv run ruff check`
  - rollback: Revert planned file edits and re-run detection/recommendation.

## deferred

- None
