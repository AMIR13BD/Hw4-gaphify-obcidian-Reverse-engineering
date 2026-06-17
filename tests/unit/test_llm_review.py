"""Tests for optional graph-guided LLM review."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import pytest

from ex04_agent.llm_review.context_loader import context_paths, load_graph_guided_context
from ex04_agent.llm_review.engine import LlmReviewEngine
from ex04_agent.llm_review.openai_client import ChatCompletionResult, OpenAiChatClient
from ex04_agent.shared.config import AppConfig, HotMdWeights


@dataclass
class FakeChatClient:
    """Mock LLM client for tests."""

    model_name: str = "test-model"
    response: str = "Inspect hot.md candidates first."

    def complete(self, *, system: str, user: str) -> ChatCompletionResult:
        return ChatCompletionResult(
            text=self.response,
            prompt_tokens=120,
            completion_tokens=45,
            total_tokens=165,
        )


def _config(root: Path) -> AppConfig:
    return AppConfig(
        version="1.00",
        target_repo="data/target_repo/broken-python",
        graphify_cli="graphify",
        max_iterations=3,
        allow_patches=False,
        index_max_chars=1000,
        hotmd_weights=HotMdWeights(1, 1, 1, 1, 1, 1),
        project_root=root,
        config_path=root / "config" / "setup.json",
    )


def _write_context(root: Path, phase: str = "before") -> None:
    (root / "obsidian").mkdir(parents=True)
    (root / "reports" / "architecture").mkdir(parents=True)
    (root / "obsidian" / "hot.md").write_text("# hot\n", encoding="utf-8")
    (root / "obsidian" / "index.md").write_text("# index\n", encoding="utf-8")
    (root / "reports" / "architecture" / f"findings_{phase}.md").write_text("# findings\n", encoding="utf-8")
    (root / "reports" / "architecture" / f"recommendations_{phase}.md").write_text(
        "# recommendations\n", encoding="utf-8"
    )


def test_context_paths_only_graph_guided_files(tmp_path: Path) -> None:
    paths = context_paths(tmp_path, "before")
    rels = {p.relative_to(tmp_path).as_posix() for p in paths}
    assert rels == {
        "obsidian/hot.md",
        "obsidian/index.md",
        "reports/architecture/findings_before.md",
        "reports/architecture/recommendations_before.md",
    }


def test_engine_reads_only_graph_guided_files(tmp_path: Path) -> None:
    _write_context(tmp_path)
    (tmp_path / "secret.py").write_text("should not be read", encoding="utf-8")

    read_paths: list[str] = []
    original_read_text = Path.read_text

    def tracked_read_text(self: Path, *args, **kwargs):
        read_paths.append(str(self))
        return original_read_text(self, *args, **kwargs)

    with patch.object(Path, "read_text", tracked_read_text):
        context = load_graph_guided_context(tmp_path, "before")

    assert len(context.files) == 4
    assert all("secret.py" not in path for path in read_paths)
    expected_suffixes = {
        "obsidian/hot.md",
        "obsidian/index.md",
        "reports/architecture/findings_before.md",
        "reports/architecture/recommendations_before.md",
    }
    normalized = {Path(path).relative_to(tmp_path).as_posix() for path in read_paths}
    assert normalized == expected_suffixes


def test_engine_writes_output_files(tmp_path: Path) -> None:
    _write_context(tmp_path)
    result = LlmReviewEngine(_config(tmp_path), client=FakeChatClient()).run(phase="before")

    md_path = Path(result.markdown_path)
    json_path = Path(result.json_path)
    assert md_path.is_file()
    assert json_path.is_file()
    assert "Inspect hot.md candidates first." in md_path.read_text(encoding="utf-8")

    metadata = json.loads(json_path.read_text(encoding="utf-8"))
    assert metadata["llm_calls"] == 1
    assert metadata["model_name"] == "test-model"
    assert metadata["provider_total_tokens"] == 165
    assert "OPENAI_API_KEY" not in json.dumps(metadata)
    assert metadata["input_files_used"] == [
        "obsidian/hot.md",
        "obsidian/index.md",
        "reports/architecture/findings_before.md",
        "reports/architecture/recommendations_before.md",
    ]


def test_openai_client_missing_api_key_exits_safely(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = OpenAiChatClient(api_key=None)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        client.complete(system="s", user="u")
