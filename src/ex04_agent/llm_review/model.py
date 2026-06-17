"""Models for optional graph-guided LLM review."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class LlmReviewMetadata:
    """Metadata for a single graph-guided LLM review call."""

    model_name: str
    input_files_used: list[str]
    character_count: int
    estimated_input_tokens: int
    provider_prompt_tokens: int | None
    provider_completion_tokens: int | None
    provider_total_tokens: int | None
    timestamp: str
    llm_calls: int
    phase: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LlmReviewResult:
    """Markdown response plus metadata and output paths."""

    response_text: str
    metadata: LlmReviewMetadata
    markdown_path: str
    json_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "markdown_path": self.markdown_path,
            "json_path": self.json_path,
        }
