# Patch Plan (Phase 9)

Phase 9 does not modify the target repository.

## safe_candidates_phase10

- None

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
- `rec_008_duplicate_evolution_mathsquiz` Document tutorial versioning or move variants under examples.
  - validation: `uv run ruff check`
  - rollback: Revert planned file edits and re-run detection/recommendation.

## deferred

- None
