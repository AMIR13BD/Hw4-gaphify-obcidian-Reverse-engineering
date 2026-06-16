"""Deterministic graph story from metrics and Graphify report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.agents.base import BaseAgent
from ex04_agent.workflow.state import PipelineState, merge_completed


class GraphInterpreterAgent(BaseAgent):
    """Write a careful graph narrative from existing artifacts."""

    name = "graph_interpreter"

    def run(self, phase: str = "before", metrics_path: Path | str | None = None) -> Path:
        path = Path(metrics_path or self._story_metrics_path(phase))
        if not path.is_file():
            msg = f"Metrics file not found: {path}"
            raise FileNotFoundError(msg)
        metrics = json.loads(path.read_text(encoding="utf-8"))
        story_path = self._story_output_path(phase)
        story_path.parent.mkdir(parents=True, exist_ok=True)
        story_path.write_text(self._render_story(phase, metrics), encoding="utf-8")
        return story_path

    def run_pipeline(
        self,
        state: PipelineState,
        recorder: AgentTraceRecorder,
    ) -> dict[str, Any]:
        phase = str(state.get("phase", "before"))
        metrics_path = state.get("metrics_path") or str(self._story_metrics_path(phase))
        try:
            story_path = self.run(phase=phase, metrics_path=metrics_path)
            recorder.record(
                self.name,
                "completed",
                inputs={"metrics_path": metrics_path},
                outputs={"story_path": str(story_path)},
            )
            return merge_completed(state, self.name, story_path=str(story_path))
        except Exception as exc:
            recorder.record(self.name, "failed", errors=[str(exc)])
            errors = list(state.get("errors", []))
            errors.append(str(exc))
            return {"errors": errors}

    def _story_metrics_path(self, phase: str) -> Path:
        return self.config.project_root / "reports" / "architecture" / f"metrics_{phase}.json"

    def _story_output_path(self, phase: str) -> Path:
        return self.config.project_root / "reports" / "architecture" / f"story_{phase}.md"

    def _render_story(self, phase: str, metrics: dict[str, Any]) -> str:
        summary = metrics.get("summary", {})
        top_hubs = metrics.get("top_hubs", [])
        communities = metrics.get("communities", {})
        lines = [
            f"# Graph Story — {phase}",
            "",
            "The graph suggests the following reverse-engineering narrative. "
            "All statements are graph-derived and **require validation in source**.",
            "",
            f"- Nodes: {summary.get('node_count', 0)}",
            f"- Links: {summary.get('link_count', 0)}",
            f"- Communities: {len(communities)}",
            f"- Connected components: {summary.get('connected_component_count', 0)}",
            "",
            "## Possible Hubs",
            "",
        ]
        for hub in top_hubs[:6]:
            lines.append(
                f"- **{hub.get('label', hub.get('id'))}** — possible hub "
                f"(degree {hub.get('total_degree', 0)}); graph suggests reviewing "
                f"`{hub.get('source_file') or 'n/a'}`."
            )
        lines.extend(["", "## Community Overview", ""])
        for community, count in sorted(communities.items()):
            lines.append(f"- Community {community}: {count} nodes")
        lines.extend(
            [
                "",
                "## Investigation Notes",
                "",
                "- Use OBS → REL → CONF → CTX → SRC before drawing architecture conclusions.",
                "- God-node candidates are connectivity signals, not confirmed design flaws.",
                "- Compare with `obsidian/hot.md` and node pages for deeper context.",
            ]
        )
        return "\n".join(lines) + "\n"
