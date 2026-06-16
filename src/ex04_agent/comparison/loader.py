"""Load before/after artifacts for comparison."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ex04_agent.shared.config import AppConfig
from ex04_agent.shared.phase_paths import architecture_report_path


@dataclass(frozen=True)
class ComparisonInputs:
    before_phase: str
    after_phase: str
    metrics_before: dict
    metrics_after: dict
    findings_before: dict
    findings_after: dict
    recommendations_before: dict
    recommendations_after: dict
    story_before: str
    story_after: str
    patch_result: dict
    regression: dict
    evidence_paths: dict[str, str]


REQUIRED = (
    ("metrics", "json"),
    ("findings", "json"),
    ("recommendations", "json"),
)


class ComparisonLoader:
    def __init__(self, config: AppConfig) -> None:
        self._root = config.project_root

    def load(self, before_phase: str = "before", after_phase: str = "after") -> ComparisonInputs:
        missing: list[str] = []
        paths: dict[str, Path] = {}
        for phase in (before_phase, after_phase):
            for stem, ext in REQUIRED:
                path = architecture_report_path(self._root, stem, phase, ext)
                paths[f"{stem}_{phase}"] = path
                if not path.is_file():
                    missing.append(str(path))
        if missing:
            msg = "Required comparison files missing:\n" + "\n".join(f"  - {p}" for p in missing)
            raise FileNotFoundError(msg)

        def _read(key: str) -> dict:
            return json.loads(paths[key].read_text(encoding="utf-8"))

        evidence = {k: str(v) for k, v in paths.items()}
        return ComparisonInputs(
            before_phase=before_phase,
            after_phase=after_phase,
            metrics_before=_read(f"metrics_{before_phase}"),
            metrics_after=_read(f"metrics_{after_phase}"),
            findings_before=_read(f"findings_{before_phase}"),
            findings_after=_read(f"findings_{after_phase}"),
            recommendations_before=_read(f"recommendations_{before_phase}"),
            recommendations_after=_read(f"recommendations_{after_phase}"),
            story_before=self._read_text(architecture_report_path(self._root, "story", before_phase, "md")),
            story_after=self._read_text(architecture_report_path(self._root, "story", after_phase, "md")),
            patch_result=self._read_json_optional(architecture_report_path(self._root, "patch_result", before_phase, "json")),
            regression=self._read_json_optional(self._root / "reports" / "tests" / f"regression_{before_phase}.json"),
            evidence_paths={
                **evidence,
                "patch_result": str(architecture_report_path(self._root, "patch_result", before_phase, "json")),
                "patch_diffs": str(self._root / "artifacts" / "patches" / before_phase / "diffs"),
                "regression": str(self._root / "reports" / "tests" / f"regression_{before_phase}.json"),
            },
        )

    @staticmethod
    def _read_text(path: Path) -> str:
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    @staticmethod
    def _read_json_optional(path: Path) -> dict:
        if not path.is_file():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def after_artifacts_exist(self, after_phase: str = "after") -> bool:
        return self._phase_artifacts_exist(after_phase)

    def before_artifacts_exist(self, before_phase: str = "before") -> bool:
        return self._phase_artifacts_exist(before_phase)

    def comparison_ready(
        self,
        before_phase: str = "before",
        after_phase: str = "after",
    ) -> bool:
        return (
            self.before_artifacts_exist(before_phase)
            and self.after_artifacts_exist(after_phase)
        )

    def _phase_artifacts_exist(self, phase: str) -> bool:
        for stem, ext in REQUIRED:
            if not architecture_report_path(self._root, stem, phase, ext).is_file():
                return False
        return True
