"""Write patch result JSON and Markdown reports."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ex04_agent.patching.model import PatchResult


@dataclass(frozen=True)
class PatchSummary:
    allow_patches: bool
    changed_files: int
    applied_count: int
    skipped_count: int
    failed_count: int
    rolled_back_count: int
    validation_status: str
    json_path: str
    markdown_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PatchReportWriter:
    def write(
        self,
        result: PatchResult,
        *,
        json_path: Path,
        markdown_path: Path,
        latest_path: Path | None = None,
    ) -> PatchSummary:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if latest_path:
            latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        markdown_path.write_text(self._render_md(result), encoding="utf-8")
        return PatchSummary(
            allow_patches=result.allow_patches,
            changed_files=len(result.changed_files),
            applied_count=len(result.applied_items),
            skipped_count=len(result.skipped_items),
            failed_count=len(result.failed_items),
            rolled_back_count=len(result.rolled_back_items),
            validation_status=result.validation_status,
            json_path=str(json_path),
            markdown_path=str(markdown_path),
        )

    def _render_md(self, result: PatchResult) -> str:
        lines = [
            f"# Patch Result — {result.phase}",
            "",
            f"- allow_patches: **{result.allow_patches}**",
            f"- applied: {len(result.applied_items)}, skipped: {len(result.skipped_items)},"
            f" failed: {len(result.failed_items)}, rolled_back: {len(result.rolled_back_items)}",
            f"- validation_status: `{result.validation_status}`",
            "",
            "## Applied",
            "",
        ]
        for item in result.applied_items:
            lines.append(f"- `{item.affected_file}` — {item.reason}")
        lines += ["", "## Skipped", ""]
        for item in result.skipped_items:
            lines.append(f"- `{item.affected_file}` — {item.reason}")
        lines += ["", "## Failed", ""]
        for item in result.failed_items:
            lines.append(f"- `{item.affected_file}` — {item.reason}")
        if result.rolled_back_items:
            lines += ["", "## Rolled back", ""]
            for item in result.rolled_back_items:
                lines.append(f"- `{item.affected_file}` — {item.reason}")
        return "\n".join(lines) + "\n"
