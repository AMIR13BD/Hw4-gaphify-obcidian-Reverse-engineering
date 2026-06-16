"""Tests for Obsidian vault builders."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ex04_agent.graph.indexer import GraphIndexer
from ex04_agent.graph.parser import GraphParser
from ex04_agent.obsidian.hot_md_builder import HotMdBuilder
from ex04_agent.obsidian.index_builder import IndexBuilder
from ex04_agent.obsidian.node_page_builder import NodePageBuilder
from ex04_agent.obsidian.report_builder import ReportBuilder
from ex04_agent.obsidian.vault_builder import VaultBuilder
from ex04_agent.obsidian.vault_context import VaultContext, sanitize_filename
from ex04_agent.shared.config import load_config


@pytest.fixture
def fixture_paths() -> dict[str, Path]:
    base = Path(__file__).resolve().parents[1] / "fixtures"
    return {
        "graph": base / "graph_sample.json",
        "metrics": base / "metrics_sample.json",
    }


@pytest.fixture
def vault_context(fixture_paths: dict[str, Path], tmp_path, monkeypatch):
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
    metrics = json.loads(fixture_paths["metrics"].read_text(encoding="utf-8"))
    document = GraphParser().load(fixture_paths["graph"])
    indexer = GraphIndexer(document)
    return VaultContext(
        phase="before",
        repo_name="broken-python",
        repo_path="data/target_repo/broken-python",
        metrics=metrics,
        indexer=indexer,
        graph_report_text="# Graph Report\n\nSample excerpt.",
        index_max_chars=config.index_max_chars,
    )


def test_index_builder_includes_summary_and_hot_link(vault_context) -> None:
    """Index includes graph summary and link to hot.md."""
    content = IndexBuilder().build(vault_context)
    assert "Graph Summary" in content
    assert "Nodes: **5**" in content
    assert "[[hot|hot.md]]" in content
    assert "OBS" in content and "SRC" in content


def test_hot_md_includes_hubs_and_careful_wording(vault_context) -> None:
    """Static hot.md lists candidates with non-proof wording."""
    content = HotMdBuilder().build(vault_context)
    assert "Hub Module" in content
    assert "Do not auto-patch" in content
    assert "graph-ranked candidates" in content or "graph suggests" in content


def test_node_page_builder_sanitizes_filenames() -> None:
    """Unsafe node ids become safe markdown filenames."""
    assert sanitize_filename('bad/id:name') == "bad_id_name"
    assert NodePageBuilder().filename_for('bad/id:name') == "bad_id_name.md"


def test_report_builder_includes_relation_and_confidence_counts(vault_context) -> None:
    """Graph summary report lists relation and confidence aggregates."""
    content = ReportBuilder().build(vault_context)
    assert "Relation Counts" in content
    assert "`calls`: 1" in content
    assert "Confidence Counts" in content
    assert "`INFERRED`: 1" in content


def test_vault_builder_writes_expected_files(fixture_paths, tmp_path, monkeypatch) -> None:
    """Vault builder creates index, hot, report, and node pages."""
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
    vault_dir = project_root / "obsidian"
    report_path = project_root / "artifacts" / "graph" / "before" / "GRAPH_REPORT.md"
    report_path.parent.mkdir(parents=True)
    report_path.write_text("# Graph Report", encoding="utf-8")

    result = VaultBuilder(config).build(
        phase="before",
        metrics_path=fixture_paths["metrics"],
        graph_path=fixture_paths["graph"],
        graph_report_path=report_path,
        vault_dir=vault_dir,
    )

    assert result.success is True
    assert (vault_dir / "index.md").is_file()
    assert (vault_dir / "hot.md").is_file()
    assert (vault_dir / "reports" / "graph_summary.md").is_file()
    assert result.node_pages_created >= 3
    assert len(result.files_written) >= 6
