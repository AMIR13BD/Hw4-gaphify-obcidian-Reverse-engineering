"""Record per-agent pipeline traces."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AgentTraceEntry:
    """Single agent handoff record."""

    timestamp: str
    agent: str
    status: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AgentTraceRecorder:
    """Write JSON traces under reports/agent_runs/."""

    def __init__(self, base_dir: Path, run_id: str) -> None:
        self._run_dir = base_dir / run_id
        self._run_dir.mkdir(parents=True, exist_ok=True)
        self._entries: list[AgentTraceEntry] = []

    @property
    def run_dir(self) -> Path:
        return self._run_dir

    def record(
        self,
        agent: str,
        status: str,
        *,
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
        errors: list[str] | None = None,
    ) -> AgentTraceEntry:
        entry = AgentTraceEntry(
            timestamp=datetime.now(UTC).isoformat(),
            agent=agent,
            status=status,
            inputs=inputs or {},
            outputs=outputs or {},
            errors=errors or [],
        )
        self._entries.append(entry)
        path = self._run_dir / f"{entry.timestamp.replace(':', '-')}_{agent}.json"
        path.write_text(json.dumps(entry.to_dict(), indent=2), encoding="utf-8")
        return entry

    def write_combined(self) -> Path:
        """Write combined trace for the full run."""
        path = self._run_dir / "run_trace.json"
        payload = {
            "run_id": self._run_dir.name,
            "entries": [entry.to_dict() for entry in self._entries],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
