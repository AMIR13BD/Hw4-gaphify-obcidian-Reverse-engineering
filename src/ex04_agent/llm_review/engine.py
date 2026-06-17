"""Orchestrate optional graph-guided LLM review."""

from __future__ import annotations

import math
from datetime import UTC, datetime

from ex04_agent.llm_review.context_loader import load_graph_guided_context
from ex04_agent.llm_review.model import LlmReviewMetadata
from ex04_agent.llm_review.openai_client import ChatClient, OpenAiChatClient
from ex04_agent.llm_review.prompt import SYSTEM_PROMPT, build_user_prompt
from ex04_agent.llm_review.report_writer import write_review
from ex04_agent.shared.config import AppConfig


class LlmReviewEngine:
    """Run one optional LLM call on graph-guided context only."""

    def __init__(self, config: AppConfig, client: ChatClient | None = None) -> None:
        self._config = config
        self._client = client or OpenAiChatClient()

    def run(self, *, phase: str = "before"):
        """Load graph-guided context, call LLM once, write reports."""
        if phase not in {"before", "after"}:
            msg = f"Invalid phase {phase!r}; expected 'before' or 'after'"
            raise ValueError(msg)

        context = load_graph_guided_context(self._config.project_root, phase)
        user_prompt = build_user_prompt(context.combined_text)
        completion = self._client.complete(system=SYSTEM_PROMPT, user=user_prompt)

        metadata = LlmReviewMetadata(
            model_name=getattr(self._client, "model_name", "unknown"),
            input_files_used=[rel for rel, _ in context.files],
            character_count=context.character_count,
            estimated_input_tokens=math.ceil(context.character_count / 4),
            provider_prompt_tokens=completion.prompt_tokens,
            provider_completion_tokens=completion.completion_tokens,
            provider_total_tokens=completion.total_tokens,
            timestamp=datetime.now(UTC).isoformat(),
            llm_calls=1,
            phase=phase,
        )
        return write_review(
            root=self._config.project_root,
            phase=phase,
            response_text=completion.text,
            metadata=metadata,
        )
