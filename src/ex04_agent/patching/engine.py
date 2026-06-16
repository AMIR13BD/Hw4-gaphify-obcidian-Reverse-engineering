"""Phase 10 patch engine: read plan, apply safe recipes, write report."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.patching.diff_writer import make_unified_diff, write_diff
from ex04_agent.patching.model import PatchItemResult, PatchResult
from ex04_agent.patching.recipes import WHITELIST, get_recipe
from ex04_agent.patching.report_writer import PatchReportWriter, PatchSummary
from ex04_agent.patching.safe_patcher import SafePatcher
from ex04_agent.shared.config import AppConfig

SKIP_CATEGORIES = {"docs_only", "mixed_responsibility", "possible_hub", "documentation_hub", "navigation_scope", "organization"}


class PatchEngine:
    def __init__(self, config: AppConfig, writer: PatchReportWriter | None = None) -> None:
        self._config = config
        self._writer = writer or PatchReportWriter()

    def run(self, *, phase: str = "before", allow_patches: bool = False) -> PatchSummary:
        if phase not in {"before", "after"}:
            msg = f"Invalid phase {phase!r}"
            raise ValueError(msg)
        plan_path = self._rpath(f"patch_plan_{phase}.json")
        if not plan_path.is_file():
            raise FileNotFoundError(f"Patch plan not found: {plan_path}")

        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        candidates = plan.get("groups", {}).get("safe_candidates_phase10", [])
        repo_root = self._config.target_repo_path
        backup_dir = self._config.project_root / "artifacts" / "patches" / phase / "backups"
        diff_dir = self._config.project_root / "artifacts" / "patches" / phase / "diffs"
        patcher = SafePatcher(backup_dir)

        applied, skipped, failed, rolled = [], [], [], []
        changed_files: list[str] = []
        seen: set[str] = set()

        for plan_item in candidates:
            for rel in plan_item.get("affected_files", []):
                if rel in seen:
                    continue
                seen.add(rel)
                item_result = self._process(
                    rel, plan_item, repo_root, patcher, diff_dir, allow_patches
                )
                if item_result.status == "applied":
                    applied.append(item_result)
                    changed_files.append(rel)
                elif item_result.status == "skipped":
                    skipped.append(item_result)
                elif item_result.status == "rolled_back":
                    rolled.append(item_result)
                else:
                    failed.append(item_result)

        val_status = "pass" if not failed and not rolled else "fail"
        result = PatchResult(
            phase=phase, allow_patches=allow_patches,
            changed_files=changed_files,
            applied_items=applied, skipped_items=skipped,
            failed_items=failed, rolled_back_items=rolled,
            backup_dir=str(backup_dir), diff_dir=str(diff_dir),
            validation_status=val_status, validation_errors=[],
            output_paths={
                "json": str(self._rpath(f"patch_result_{phase}.json")),
                "md": str(self._rpath(f"patch_result_{phase}.md")),
            },
        )
        return self._writer.write(
            result,
            json_path=self._rpath(f"patch_result_{phase}.json"),
            markdown_path=self._rpath(f"patch_result_{phase}.md"),
            latest_path=self._rpath("patch_result.json"),
        )

    def _process(self, rel: str, plan_item: dict, repo_root: Path, patcher: SafePatcher, diff_dir: Path, allow_patches: bool) -> PatchItemResult:
        rec_id = plan_item.get("recommendation_id", "")
        finding_id = plan_item.get("finding_id", "")

        if rel not in WHITELIST:
            return PatchItemResult(rec_id, finding_id, rel, "skipped", "not in whitelist", "", "", "", "")

        recipe = get_recipe(rel)
        if recipe is None:
            return PatchItemResult(rec_id, finding_id, rel, "skipped", "no recipe available", "", "", "", "")

        target = repo_root / rel
        if not target.is_file():
            return PatchItemResult(rec_id, finding_id, rel, "skipped", "file not found in repo", "", "", "", "")

        original = target.read_text(encoding="utf-8")
        new_content = recipe(original)
        if new_content is None:
            return PatchItemResult(rec_id, finding_id, rel, "skipped", "already correct — no change needed", "", "", "", "")

        diff = make_unified_diff(original, new_content, rel)
        diff_path = write_diff(diff, diff_dir, rel)

        outcome = patcher.apply(target, new_content, allow_patches=allow_patches)
        status: str
        if outcome.rolled_back:
            status = "rolled_back"
        elif not outcome.validation_ok:
            status = "failed"
        elif outcome.changed:
            status = "applied"
        else:
            status = "skipped"

        return PatchItemResult(
            rec_id, finding_id, rel, status,  # type: ignore[arg-type]
            outcome.reason, outcome.backup_path, str(diff_path), "uv run pytest -q",
            outcome.validation_error,
        )

    def _rpath(self, name: str) -> Path:
        return self._config.project_root / "reports" / "architecture" / name
