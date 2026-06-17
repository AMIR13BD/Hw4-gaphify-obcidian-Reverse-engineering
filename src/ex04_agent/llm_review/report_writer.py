"""Write graph-guided LLM review reports."""

from __future__ import annotations

import json
from pathlib import Path

from ex04_agent.llm_review.model import LlmReviewMetadata, LlmReviewResult


def output_paths(root: Path, phase: str) -> tuple[Path, Path]:
    """Return markdown and JSON output paths for a phase."""
    report_dir = root / "reports" / "llm"
    report_dir.mkdir(parents=True, exist_ok=True)
    return (
        report_dir / f"graph_guided_llm_review_{phase}.md",
        report_dir / f"llm_review_{phase}.json",
    )


def write_review(
    *,
    root: Path,
    phase: str,
    response_text: str,
    metadata: LlmReviewMetadata,
) -> LlmReviewResult:
    """Persist markdown response and metadata JSON."""
    md_path, json_path = output_paths(root, phase)

    md_body = (
        f"# Graph-Guided LLM Review — {phase}\n\n"
        f"- Model: `{metadata.model_name}`\n"
        f"- Timestamp: {metadata.timestamp}\n"
        f"- LLM calls: {metadata.llm_calls}\n\n"
        "## Context files used\n\n"
        + "\n".join(f"- `{path}`" for path in metadata.input_files_used)
        + "\n\n## LLM response\n\n"
        + response_text
        + "\n"
    )
    md_path.write_text(md_body, encoding="utf-8")

    json_path.write_text(json.dumps(metadata.to_dict(), indent=2), encoding="utf-8")
    return LlmReviewResult(
        response_text=response_text,
        metadata=metadata,
        markdown_path=str(md_path),
        json_path=str(json_path),
    )
