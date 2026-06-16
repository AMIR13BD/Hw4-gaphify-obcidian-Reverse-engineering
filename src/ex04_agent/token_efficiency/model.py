"""Data models for token-efficiency analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class FileEstimate:
    path: str
    characters: int
    estimated_tokens: int


@dataclass(frozen=True)
class ContextBundle:
    name: str
    description: str
    files: tuple[FileEstimate, ...]

    @property
    def total_characters(self) -> int:
        return sum(f.characters for f in self.files)

    @property
    def total_tokens(self) -> int:
        return sum(f.estimated_tokens for f in self.files)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "file_count": len(self.files),
            "total_characters": self.total_characters,
            "total_tokens": self.total_tokens,
            "files": [asdict(f) for f in self.files],
        }


@dataclass(frozen=True)
class ScenarioComparison:
    name: str
    task: str
    baseline: ContextBundle
    graph_guided: ContextBundle
    tokens_saved: int
    percent_saved: float
    quality_note: str
    risk_note: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "task": self.task,
            "baseline_tokens": self.baseline.total_tokens,
            "graph_guided_tokens": self.graph_guided.total_tokens,
            "tokens_saved": self.tokens_saved,
            "percent_saved": round(self.percent_saved, 2),
            "baseline_files": [f.path for f in self.baseline.files],
            "graph_guided_files": [f.path for f in self.graph_guided.files],
            "quality_note": self.quality_note,
            "risk_note": self.risk_note,
        }


@dataclass(frozen=True)
class TokenEfficiencyResult:
    estimation_method: str
    phase: str
    bundles: tuple[ContextBundle, ...]
    scenarios: tuple[ScenarioComparison, ...]
    total_baseline_tokens: int
    total_graph_guided_tokens: int
    total_tokens_saved: int
    percent_saved: float
    output_paths: dict[str, str]
    limitations: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "estimation_method": self.estimation_method,
            "phase": self.phase,
            "bundles": [b.to_dict() for b in self.bundles],
            "scenarios": [s.to_dict() for s in self.scenarios],
            "total_baseline_tokens": self.total_baseline_tokens,
            "total_graph_guided_tokens": self.total_graph_guided_tokens,
            "total_tokens_saved": self.total_tokens_saved,
            "percent_saved": round(self.percent_saved, 2),
            "output_paths": self.output_paths,
            "limitations": list(self.limitations),
        }
