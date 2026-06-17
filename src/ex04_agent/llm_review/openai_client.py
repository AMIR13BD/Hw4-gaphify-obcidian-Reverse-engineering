"""Minimal OpenAI chat client (stdlib HTTP, mock-friendly)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChatCompletionResult:
    """Normalized chat completion response."""

    text: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None


class ChatClient(Protocol):
    """Protocol for mockable LLM chat clients."""

    def complete(self, *, system: str, user: str) -> ChatCompletionResult:
        """Send one chat completion request."""


class OpenAiChatClient:
    """Call OpenAI chat completions using OPENAI_API_KEY from the environment."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self._api_key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY")
        self._model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self._timeout = timeout_seconds

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, *, system: str, user: str) -> ChatCompletionResult:
        if not self._api_key:
            msg = (
                "OPENAI_API_KEY is not set. Export OPENAI_API_KEY in your environment "
                "to run optional graph-guided LLM review."
            )
            raise ValueError(msg)

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            msg = f"OpenAI API error ({exc.code}): {detail}"
            raise ValueError(msg) from exc

        choices = body.get("choices") or []
        if not choices:
            msg = "OpenAI API returned no choices"
            raise ValueError(msg)

        text = choices[0].get("message", {}).get("content", "").strip()
        usage = body.get("usage") or {}
        return ChatCompletionResult(
            text=text,
            prompt_tokens=_optional_int(usage.get("prompt_tokens")),
            completion_tokens=_optional_int(usage.get("completion_tokens")),
            total_tokens=_optional_int(usage.get("total_tokens")),
        )


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(value)
