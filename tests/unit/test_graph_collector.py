"""Tests for GraphCollector."""

from pathlib import Path

from ex04_agent.graph.collector import GraphCollector
from ex04_agent.shared.config import load_config


def _write_graphify_out(root: Path) -> Path:
    out = root / "graphify-out"
    out.mkdir(parents=True, exist_ok=True)
    (out / "graph.json").write_text("{}", encoding="utf-8")
    (out / "graph.html").write_text("<html></html>", encoding="utf-8")
    (out / "GRAPH_REPORT.md").write_text("# report", encoding="utf-8")
    (out / "manifest.json").write_text("{}", encoding="utf-8")
    return out


def test_collector_copies_expected_artifacts(tmp_path, monkeypatch) -> None:
    """Required and present optional artifacts are copied to phase directory."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (project_root / "config" / "setup.json").write_text(
        (Path(__file__).resolve().parents[2] / "config" / "setup.json").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )
    target = project_root / "data" / "target_repo" / "broken-python"
    target.mkdir(parents=True)
    _write_graphify_out(target)

    monkeypatch.setattr(
        "ex04_agent.shared.config.find_project_root",
        lambda start=None: project_root,
    )
    config = load_config(project_root / "config" / "setup.json")

    result = GraphCollector(config).collect("before", source_dir=target / "graphify-out")

    assert result.success is True
    assert "graph.json" in result.copied
    assert "graph.html" in result.copied
    assert "GRAPH_REPORT.md" in result.copied
    assert (result.dest_dir / "graph.json").is_file()


def test_missing_optional_artifacts_do_not_crash(tmp_path, monkeypatch) -> None:
    """Missing optional files are reported but do not fail collection."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "config").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    setup_src = Path(__file__).resolve().parents[2] / "config" / "setup.json"
    (project_root / "config" / "setup.json").write_text(
        setup_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    source = project_root / "graphify-out"
    source.mkdir()
    (source / "graph.json").write_text("{}", encoding="utf-8")
    (source / "graph.html").write_text("<html></html>", encoding="utf-8")
    (source / "GRAPH_REPORT.md").write_text("# report", encoding="utf-8")

    monkeypatch.setattr(
        "ex04_agent.shared.config.find_project_root",
        lambda start=None: project_root,
    )
    config = load_config(project_root / "config" / "setup.json")
    result = GraphCollector(config).collect("after", source_dir=source)

    assert result.success is True
    assert ".graphify_root" in result.missing_optional
    assert result.missing_required == ()
