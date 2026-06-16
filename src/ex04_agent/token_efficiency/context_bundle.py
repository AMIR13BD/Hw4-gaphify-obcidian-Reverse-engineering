"""Build named context bundles from file paths."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.token_efficiency.model import ContextBundle
from ex04_agent.token_efficiency.token_estimator import TokenEstimator


class ContextBundleBuilder:
    """Assemble context bundles with deterministic token estimates."""

    def __init__(self, estimator: TokenEstimator | None = None) -> None:
        self._estimator = estimator or TokenEstimator()

    def build(self, name: str, description: str, paths: list[Path]) -> ContextBundle:
        files = self._estimator.estimate_paths(paths)
        return ContextBundle(name=name, description=description, files=files)

    def merge(self, name: str, description: str, *bundles: ContextBundle) -> ContextBundle:
        seen: set[str] = set()
        merged: list = []
        for bundle in bundles:
            for f in bundle.files:
                if f.path not in seen:
                    seen.add(f.path)
                    merged.append(f)
        merged.sort(key=lambda f: f.path)
        return ContextBundle(name=name, description=description, files=tuple(merged))
