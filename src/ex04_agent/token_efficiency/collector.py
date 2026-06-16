"""Collect file paths for token-efficiency bundles and scenarios."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.shared.config import AppConfig
from ex04_agent.shared.phase_paths import architecture_report_path
from ex04_agent.token_efficiency.collector_utils import (
    affected_source_files,
    hub_source_files,
    required_input_paths,
    top_node_pages,
)


class TokenEfficiencyCollector:
    """Resolve paths for naive, graph-guided, and agent-focused bundles."""

    def __init__(self, config: AppConfig) -> None:
        self._root = config.project_root
        self._repo = config.target_repo_path
        self._arch = self._root / "reports" / "architecture"
        self._obsidian = self._root / "obsidian"

    def require_inputs(self, phase: str = "before") -> None:
        missing = [str(p) for p in required_input_paths(self._root, self._obsidian, phase) if not p.is_file()]
        if missing:
            msg = "Required token-efficiency files missing:\n" + "\n".join(f"  - {p}" for p in missing)
            raise FileNotFoundError(msg)

    def target_py_files(self) -> list[Path]:
        return sorted(self._repo.rglob("*.py"), key=lambda p: str(p))

    def target_md_files(self) -> list[Path]:
        return sorted(
            (p for p in self._repo.rglob("*.md") if "graphify-out" not in p.parts),
            key=lambda p: str(p),
        )

    def naive_full_context(self) -> list[Path]:
        return self.target_py_files() + self.target_md_files()

    def naive_source_only(self) -> list[Path]:
        return self.target_py_files()

    def naive_evidence_dump(self) -> list[Path]:
        paths = [
            self._root / "artifacts" / "graph" / "before" / "graph.json",
            self._root / "artifacts" / "graph" / "after" / "graph.json",
        ]
        for pattern in ("*.json", "*.md"):
            paths.extend(self._arch.glob(pattern))
            paths.extend((self._root / "reports" / "comparison").glob(pattern))
            paths.extend((self._root / "reports" / "tests").glob(pattern))
        return sorted({p for p in paths if p.is_file()}, key=lambda x: str(x))

    def graph_guided_minimal(self, phase: str = "before") -> list[Path]:
        paths = [
            self._obsidian / "index.md",
            self._obsidian / "hot.md",
            architecture_report_path(self._root, "metrics", phase, "json"),
        ]
        paths.extend(top_node_pages(self._root, self._obsidian, phase))
        return [p for p in paths if p.is_file()]

    def graph_guided_after(self) -> list[Path]:
        paths = [
            architecture_report_path(self._root, "metrics", "after", "json"),
            architecture_report_path(self._root, "findings", "after", "json"),
            architecture_report_path(self._root, "recommendations", "after", "json"),
            self._root / "reports" / "comparison" / "before_after.md",
        ]
        return [p for p in paths if p.is_file()]

    def detection_baseline(self) -> list[Path]:
        return self.naive_full_context() + self.naive_evidence_dump()

    def detection_guided(self, phase: str = "before") -> list[Path]:
        paths = list(self.graph_guided_minimal(phase))
        paths.extend(hub_source_files(self._root, self._repo, phase))
        return sorted({p for p in paths if p.is_file()}, key=lambda x: str(x))

    def recommendation_baseline(self) -> list[Path]:
        return self.naive_full_context() + self.naive_evidence_dump()

    def recommendation_guided(self, phase: str = "before") -> list[Path]:
        paths = [architecture_report_path(self._root, "findings", phase, "json")]
        paths.extend(affected_source_files(self._root, self._repo, phase))
        return sorted({p for p in paths if p.is_file()}, key=lambda x: str(x))

    def comparison_baseline(self) -> list[Path]:
        paths: list[Path] = []
        for stem in ("metrics", "findings", "recommendations", "patch_plan", "story", "patch_result"):
            for phase in ("before", "after"):
                for ext in ("json", "md"):
                    p = architecture_report_path(self._root, stem, phase, ext)
                    if p.is_file():
                        paths.append(p)
        paths.extend((self._root / "reports" / "comparison").glob("*"))
        return sorted({p for p in paths if p.is_file()}, key=lambda x: str(x))

    def comparison_guided(self) -> list[Path]:
        paths = [
            architecture_report_path(self._root, "metrics", "before", "json"),
            architecture_report_path(self._root, "metrics", "after", "json"),
            architecture_report_path(self._root, "findings", "before", "json"),
            architecture_report_path(self._root, "findings", "after", "json"),
            architecture_report_path(self._root, "recommendations", "before", "json"),
            architecture_report_path(self._root, "recommendations", "after", "json"),
            architecture_report_path(self._root, "patch_result", "before", "json"),
            self._root / "reports" / "tests" / "regression_before.json",
        ]
        return [p for p in paths if p.is_file()]
