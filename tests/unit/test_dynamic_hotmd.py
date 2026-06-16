"""Tests for dynamic hot.md ranking and rendering."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ex04_agent.git.diff_reader import GitDiffResult
from ex04_agent.graph.indexer import GraphIndexer
from ex04_agent.graph.parser import GraphParser
from ex04_agent.obsidian.dynamic_hotmd_builder import DynamicHotMdBuilder
from ex04_agent.obsidian.hotmd_renderer import HotMdRenderContext, HotMdRenderer
from ex04_agent.obsidian.node_ranker import NodeRanker
from ex04_agent.shared.config import HotMdWeights, load_config


@pytest.fixture
def fixture_paths() -> dict[str, Path]:
    base = Path(__file__).resolve().parents[1] / "fixtures"
    return {"graph": base / "graph_sample.json", "metrics": base / "metrics_sample.json"}


@pytest.fixture
def weights() -> HotMdWeights:
    return HotMdWeights(
        degree=0.20,
        betweenness=0.25,
        diff_proximity=0.30,
        test_proximity=0.15,
        ambiguous=0.05,
        god_node=0.05,
    )


def test_node_ranker_prefers_changed_file_node(fixture_paths, weights) -> None:
    """Node on a changed source file ranks above an unchanged isolated node."""
    metrics = json.loads(fixture_paths["metrics"].read_text(encoding="utf-8"))
    indexer = GraphIndexer(GraphParser().load(fixture_paths["graph"]))
    ranked = NodeRanker().rank(
        metrics,
        indexer,
        changed_files=("src/hub.py",),
        weights=weights,
    )
    top = ranked[0]
    assert top.node_id == "hub"
    assert top.diff_score == 1.0


def test_node_ranker_falls_back_to_centrality(fixture_paths, weights) -> None:
    """Empty diff still ranks by centrality/god-node signals."""
    metrics = json.loads(fixture_paths["metrics"].read_text(encoding="utf-8"))
    indexer = GraphIndexer(GraphParser().load(fixture_paths["graph"]))
    ranked = NodeRanker().rank(metrics, indexer, changed_files=(), weights=weights)
    assert ranked[0].node_id == "hub"


def test_hotmd_renderer_includes_warning_and_flow() -> None:
    """Renderer includes safety warning and OBS→SRC reminder."""
    content = HotMdRenderer().render(
        HotMdRenderContext(
            phase="before",
            timestamp="2026-01-01T00:00:00Z",
            repo_path="data/target_repo/broken-python",
            commit="abc",
            diff=GitDiffResult((), "", "", "abc", "No changes", True),
            ranked_nodes=[],
            previous_hot_excerpt=None,
            previous_snapshot_name=None,
        )
    )
    assert "Do not auto-patch" in content
    assert "OBS" in content and "SRC" in content


def test_dynamic_hotmd_builder_writes_hot_and_snapshot(
    fixture_paths, tmp_path, monkeypatch
) -> None:
    """Builder writes obsidian/hot.md and artifacts/hotmd snapshot."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(
        setup_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "ex04_agent.shared.config.find_project_root",
        lambda start=None: project_root,
    )
    config = load_config(project_root / "config" / "setup.json")
    hot_path = project_root / "obsidian" / "hot.md"
    snapshot_dir = project_root / "artifacts" / "hotmd"

    result = DynamicHotMdBuilder(config).build(
        phase="before",
        metrics_path=fixture_paths["metrics"],
        graph_path=fixture_paths["graph"],
        hot_path=hot_path,
        snapshot_dir=snapshot_dir,
    )

    assert result.success is True
    assert hot_path.is_file()
    assert Path(result.snapshot_path).is_file()
    assert "Dynamic Investigation List" in hot_path.read_text(encoding="utf-8")
