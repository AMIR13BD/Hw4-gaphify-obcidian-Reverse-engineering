"""Additional source-based detectors."""

from __future__ import annotations

from pathlib import Path

from ex04_agent.detection.finding import ArchitectureFinding, EvidenceItem
from ex04_agent.detection.source_scanner import SourceScanner

STEP_FILES = (
    "mathsquiz/mathsquiz-step1.py",
    "mathsquiz/mathsquiz-step2.py",
    "mathsquiz/mathsquiz-step3.py",
    "mathsquiz/mathsquiz.py",
)


def detect_execution_blockers(scanner: SourceScanner) -> list[ArchitectureFinding]:
    findings: list[ArchitectureFinding] = []
    for rel in ("mathsquiz/mathsquiz.py", "polygons/polygons.py"):
        scan = scanner.scan_file(rel)
        if scan is None or scan.syntax_valid:
            continue
        findings.append(
            ArchitectureFinding(
                id=f"execution_blocker_{rel.replace('/', '_')}",
                title=f"Syntax blocker in {rel}",
                detector="ExecutionBlockerDetector",
                category="code_health_blocker",
                severity="high",
                confidence="high",
                status="validated_by_source",
                observation="Source validation proves the file does not compile under Python 3.",
                relation="Blocks safe AST analysis, testing, and patching.",
                confidence_reason=str(scan.syntax_error),
                context="Separate from pure architecture; affects analysis workflow.",
                affected_nodes=(),
                affected_files=(rel,),
                evidence=(
                    EvidenceItem("source", rel, None, None, scan.syntax_error or "syntax error"),
                ),
                source_validation="Validated by compile().",
                next_validation_steps=("Fix syntax before automated refactor.",),
            )
        )
    return findings


def detect_duplicate_evolution(scanner: SourceScanner, repo_root: Path) -> list[ArchitectureFinding]:
    existing = [rel for rel in STEP_FILES if (repo_root / rel).is_file()]
    if len(existing) < 3:
        return []
    return [
        ArchitectureFinding(
            id="duplicate_evolution_mathsquiz",
            title="Multiple mathsquiz evolution versions coexist",
            detector="DuplicateEvolutionDetector",
            category="organization",
            severity="low",
            confidence="high",
            status="needs_manual_validation",
            observation=(
                "Tutorial step files and a combined mathsquiz.py live together. "
                "This may be intentional for teaching."
            ),
            relation="Parallel versions of the same feature increase maintenance surface.",
            confidence_reason=f"Found files: {', '.join(existing)}",
            context="Do not treat as automatically bad; teaching repos often keep all steps.",
            affected_nodes=(),
            affected_files=tuple(existing),
            evidence=tuple(
                EvidenceItem("source", path, None, None, "step/evolution file present")
                for path in existing
            ),
            source_validation="File inventory validated; intent needs manual confirmation.",
            next_validation_steps=("Confirm which file is canonical for execution.",),
        )
    ]
