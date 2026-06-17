"""Prompt builder for graph-guided LLM review."""

from __future__ import annotations

SYSTEM_PROMPT = (
    "You are assisting with graph-guided reverse engineering of a small Python teaching "
    "repository. Answer using only the supplied context bundles. Be concise and careful: "
    "treat graph signals as investigation candidates, not proven facts."
)

USER_QUESTIONS = (
    "Based only on the graph-guided context below, answer:\n"
    "1. What does the graph-guided evidence suggest inspecting first?\n"
    "2. What are the likely bug/root-cause candidates?\n"
    "3. Why is this context smaller than naive full-repo reading?\n"
    "4. Which files/snippets should be checked before patching?"
)


def build_user_prompt(context_text: str) -> str:
    """Combine review questions with bundled graph-guided context."""
    return f"{USER_QUESTIONS}\n\n---\n\n{context_text}"
