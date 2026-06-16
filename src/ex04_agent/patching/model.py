"""Patch result models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

PatchStatus = Literal["applied", "skipped", "failed", "rolled_back"]


@dataclass
class PatchItemResult:
    recommendation_id: str
    finding_id: str
    affected_file: str
    status: PatchStatus
    reason: str
    backup_path: str
    diff_path: str
    validation_command: str
    validation_output: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PatchResult:
    phase: str
    allow_patches: bool
    changed_files: list[str]
    applied_items: list[PatchItemResult]
    skipped_items: list[PatchItemResult]
    failed_items: list[PatchItemResult]
    rolled_back_items: list[PatchItemResult]
    backup_dir: str
    diff_dir: str
    validation_status: str
    validation_errors: list[str]
    output_paths: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "allow_patches": self.allow_patches,
            "changed_files": self.changed_files,
            "applied_items": [i.to_dict() for i in self.applied_items],
            "skipped_items": [i.to_dict() for i in self.skipped_items],
            "failed_items": [i.to_dict() for i in self.failed_items],
            "rolled_back_items": [i.to_dict() for i in self.rolled_back_items],
            "backup_dir": self.backup_dir,
            "diff_dir": self.diff_dir,
            "validation_status": self.validation_status,
            "validation_errors": self.validation_errors,
            "output_paths": self.output_paths,
        }
