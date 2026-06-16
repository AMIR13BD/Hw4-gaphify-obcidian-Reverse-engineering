"""Tests for PatchItemResult and PatchResult models."""

from __future__ import annotations

from ex04_agent.patching.model import PatchItemResult, PatchResult


def test_patch_item_result_serializes() -> None:
    item = PatchItemResult("rec1", "f1", "x.py", "applied", "ok", "/bak", "/diff", "pytest", "")
    d = item.to_dict()
    assert d["status"] == "applied"
    assert d["affected_file"] == "x.py"


def test_patch_result_serializes() -> None:
    result = PatchResult(
        phase="before", allow_patches=True, changed_files=["x.py"],
        applied_items=[], skipped_items=[], failed_items=[], rolled_back_items=[],
        backup_dir="/bak", diff_dir="/diff", validation_status="pass",
        validation_errors=[], output_paths={"json": "out.json"},
    )
    d = result.to_dict()
    assert d["allow_patches"] is True
    assert d["validation_status"] == "pass"
