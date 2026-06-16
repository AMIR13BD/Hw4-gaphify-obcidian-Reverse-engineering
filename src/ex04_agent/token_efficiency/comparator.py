"""Compare baseline vs graph-guided context bundles."""

from __future__ import annotations

from ex04_agent.token_efficiency.model import ContextBundle, ScenarioComparison


def compare_scenario(
    name: str,
    task: str,
    baseline: ContextBundle,
    graph_guided: ContextBundle,
    *,
    quality_note: str,
    risk_note: str,
) -> ScenarioComparison:
    base_t = baseline.total_tokens
    guided_t = graph_guided.total_tokens
    saved = base_t - guided_t
    pct = _percent_saved(base_t, saved)
    return ScenarioComparison(
        name=name,
        task=task,
        baseline=baseline,
        graph_guided=graph_guided,
        tokens_saved=saved,
        percent_saved=pct,
        quality_note=quality_note,
        risk_note=risk_note,
    )


def _percent_saved(baseline_tokens: int, tokens_saved: int) -> float:
    if baseline_tokens <= 0:
        return 0.0 if tokens_saved <= 0 else -100.0
    return (tokens_saved / baseline_tokens) * 100.0
