"""Backup-apply-validate-rollback safe file patcher."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from ex04_agent.patching.validator import validate_text


@dataclass
class ApplyOutcome:
    """Result of a single file patch attempt."""

    changed: bool
    rolled_back: bool
    backup_path: str
    diff_content: str
    validation_ok: bool
    validation_error: str
    reason: str


class SafePatcher:
    """Apply recipe transforms with backup and automatic rollback on failure."""

    def __init__(self, backup_dir: Path) -> None:
        self._backup_dir = backup_dir

    def apply(
        self,
        target_file: Path,
        new_content: str,
        *,
        allow_patches: bool,
    ) -> ApplyOutcome:
        """Attempt to write new_content to target_file safely.

        Returns ApplyOutcome. If allow_patches is False the file is never touched.
        """
        original = target_file.read_text(encoding="utf-8") if target_file.is_file() else ""

        if new_content == original:
            return ApplyOutcome(
                changed=False, rolled_back=False, backup_path="",
                diff_content="", validation_ok=True, validation_error="",
                reason="already correct — no change needed",
            )

        ok, err = validate_text(new_content, str(target_file))
        if not ok:
            return ApplyOutcome(
                changed=False, rolled_back=False, backup_path="",
                diff_content="", validation_ok=False, validation_error=err,
                reason=f"recipe produced invalid Python: {err}",
            )

        if not allow_patches:
            return ApplyOutcome(
                changed=False, rolled_back=False, backup_path="",
                diff_content="", validation_ok=True, validation_error="",
                reason="dry-run: would apply patch but --allow-patches not set",
            )

        backup_path = self._backup(target_file, original)

        try:
            target_file.write_text(new_content, encoding="utf-8")
        except OSError as exc:
            return ApplyOutcome(
                changed=False, rolled_back=False,
                backup_path=str(backup_path),
                diff_content="", validation_ok=False, validation_error=str(exc),
                reason=f"write failed: {exc}",
            )

        re_ok, re_err = validate_text(new_content, str(target_file))
        if not re_ok:
            shutil.copy2(backup_path, target_file)
            return ApplyOutcome(
                changed=False, rolled_back=True,
                backup_path=str(backup_path),
                diff_content="", validation_ok=False, validation_error=re_err,
                reason=f"post-write validation failed; rolled back: {re_err}",
            )

        return ApplyOutcome(
            changed=True, rolled_back=False,
            backup_path=str(backup_path),
            diff_content="", validation_ok=True, validation_error="",
            reason="patch applied and validated",
        )

    def _backup(self, target_file: Path, content: str) -> Path:
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        safe_name = str(target_file.name) + ".bak"
        backup_path = self._backup_dir / safe_name
        backup_path.write_text(content, encoding="utf-8")
        return backup_path
