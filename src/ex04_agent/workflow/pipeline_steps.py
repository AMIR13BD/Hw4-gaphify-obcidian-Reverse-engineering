"""Executable pipeline step handlers for LangGraph nodes."""

from __future__ import annotations

from typing import Any

from ex04_agent.agent_trace.recorder import AgentTraceRecorder
from ex04_agent.workflow.state import PipelineState, merge_completed


def run_graphify(agents, state: PipelineState, recorder: AgentTraceRecorder) -> dict[str, Any]:
    phase = str(state.get("phase", "before"))
    try:
        result = agents.graphify_runner.run(phase=phase)
        dest = agents.config.project_root / "artifacts" / "graph" / phase
        artifacts = {
            "graph_json": str(dest / "graph.json"),
            "graph_html": str(dest / "graph.html"),
            "graph_report": str(dest / "GRAPH_REPORT.md"),
        }
        recorder.record(
            "graphify_runner",
            "completed" if result.success else "failed",
            inputs={"phase": phase, "dry_run": state.get("dry_run")},
            outputs={"success": result.success, "artifacts": artifacts},
            errors=[result.error] if result.error else [],
        )
        if result.success:
            return merge_completed(state, "graphify_runner", graph_artifacts=artifacts)
        errors = list(state.get("errors", []))
        if result.error:
            errors.append(result.error)
        return {"graph_artifacts": artifacts, "errors": errors}
    except Exception as exc:
        recorder.record("graphify_runner", "failed", errors=[str(exc)])
        errors = list(state.get("errors", []))
        errors.append(str(exc))
        return {"errors": errors}


def run_graph_parser(agents, state: PipelineState, recorder: AgentTraceRecorder) -> dict[str, Any]:
    phase = str(state.get("phase", "before"))
    metrics_path = agents.config.project_root / "reports" / "architecture" / f"metrics_{phase}.json"
    try:
        agents.graph_parser.run(phase=phase)
        recorder.record(
            "graph_parser",
            "completed",
            inputs={"phase": phase},
            outputs={"metrics_path": str(metrics_path)},
        )
        return merge_completed(state, "graph_parser", metrics_path=str(metrics_path))
    except Exception as exc:
        recorder.record("graph_parser", "failed", errors=[str(exc)])
        errors = list(state.get("errors", []))
        errors.append(str(exc))
        return {"errors": errors}


def run_obsidian_vault(agents, state: PipelineState, recorder: AgentTraceRecorder) -> dict[str, Any]:
    phase = str(state.get("phase", "before"))
    vault = agents.config.project_root / "obsidian"
    try:
        result = agents.obsidian_vault.run(phase=phase, vault_dir=vault, dynamic_hot=False)
        paths = {
            "index": result.index_path,
            "hot": result.hot_path,
            "report": result.report_path,
            "vault_dir": result.vault_dir,
        }
        recorder.record(
            "obsidian_vault",
            "completed",
            inputs={"phase": phase},
            outputs={"paths": paths, "node_pages": result.node_pages_created},
        )
        return merge_completed(state, "obsidian_vault", obsidian_paths=paths)
    except Exception as exc:
        recorder.record("obsidian_vault", "failed", errors=[str(exc)])
        errors = list(state.get("errors", []))
        errors.append(str(exc))
        return {"errors": errors}


def run_dynamic_hotmd(agents, state: PipelineState, recorder: AgentTraceRecorder) -> dict[str, Any]:
    phase = str(state.get("phase", "before"))
    try:
        result = agents.obsidian_vault.run_dynamic_hotmd(phase=phase)
        recorder.record(
            "dynamic_hotmd",
            "completed",
            inputs={"phase": phase},
            outputs={
                "hot_path": result.hot_path,
                "snapshot_path": result.snapshot_path,
                "top_labels": list(result.top_labels),
            },
        )
        return merge_completed(state, "dynamic_hotmd", hotmd_path=result.hot_path)
    except Exception as exc:
        recorder.record("dynamic_hotmd", "failed", errors=[str(exc)])
        errors = list(state.get("errors", []))
        errors.append(str(exc))
        return {"errors": errors}
