"""Source-based architecture detectors."""

from __future__ import annotations

from ex04_agent.detection.finding import ArchitectureFinding, EvidenceItem
from ex04_agent.detection.source_scanner import SourceScanner


def detect_mixed_responsibility(scanner: SourceScanner) -> list[ArchitectureFinding]:
    findings: list[ArchitectureFinding] = []
    for rel in ("polygons/polygons.py",):
        scan = scanner.scan_file(rel)
        if scan is None or len(scan.responsibilities) < 4:
            continue
        line_hits = scanner.find_lines(rel, r"input\(|print\(|class |turtle|def ")
        findings.append(
            ArchitectureFinding(
                id="mixed_responsibility_polygons",
                title="Candidate mixed responsibilities in polygons.py",
                detector="MixedResponsibilityDetector",
                category="mixed_responsibility",
                severity="high",
                confidence="high",
                status="validated_by_source",
                observation=(
                    "Source scan suggests multiple responsibilities in one file: "
                    f"{', '.join(scan.responsibilities)}."
                ),
                relation="Class/model, calculation, drawing, I/O, and top-level execution coexist.",
                confidence_reason="Responsibility tags detected in source file.",
                context="SRC: polygons.py combines tutorial script and reusable module patterns.",
                affected_nodes=("polygons_polygons",),
                affected_files=(rel,),
                evidence=tuple(
                    EvidenceItem(
                        "source",
                        rel,
                        min(line_hits) if line_hits else None,
                        max(line_hits) if line_hits else None,
                        f"responsibility={tag}",
                    )
                    for tag in scan.responsibilities
                ),
                source_validation="Validated by source responsibility scan.",
                next_validation_steps=(
                    "Split drawing, domain logic, and CLI entry point.",
                    "Phase 9 may consider safe extraction recommendations.",
                ),
            )
        )
    return findings


def detect_top_level_side_effects(scanner: SourceScanner) -> list[ArchitectureFinding]:
    findings: list[ArchitectureFinding] = []
    for rel in ("polygons/polygons.py", "mathsquiz/mathsquiz-step2.py"):
        scan = scanner.scan_file(rel)
        if scan is None or "top_level_execution" not in scan.responsibilities:
            continue
        lines = scanner.find_lines(rel, r"^[^#\s].*(input\(|print\(|\w+\()")
        findings.append(
            ArchitectureFinding(
                id=f"top_level_{rel.replace('/', '_').replace('.', '_')}",
                title=f"Top-level side effects in {rel}",
                detector="TopLevelSideEffectDetector",
                category="import_script_mixing",
                severity="medium",
                confidence="high",
                status="validated_by_source",
                observation=(
                    "Graph suggests importable code and runnable script behavior may be mixed."
                ),
                relation="Module-level input/print/calls run on import.",
                confidence_reason="Top-level execution tags and line matches.",
                context="Not a confirmed bug unless import fails; needs manual confirmation.",
                affected_nodes=(),
                affected_files=(rel,),
                evidence=tuple(
                    EvidenceItem("source", rel, line, line, "top-level execution")
                    for line in lines[:5]
                ),
                source_validation="Validated by source line scan.",
                next_validation_steps=("Try importing module without running side effects.",),
            )
        )
    return findings


def detect_hidden_globals(scanner: SourceScanner) -> list[ArchitectureFinding]:
    findings: list[ArchitectureFinding] = []
    for rel in ("mathsquiz/mathsquiz-step2.py", "mathsquiz/mathsquiz-step3.py"):
        for fn, line_no, global_name in scanner.hidden_global_uses(rel):
            findings.append(
                ArchitectureFinding(
                    id=f"hidden_global_{rel.replace('/', '_')}_{fn}",
                    title=f"Possible hidden global `{global_name}` in {fn}()",
                    detector="HiddenGlobalStateDetector",
                    category="hidden_global_state",
                    severity="medium",
                    confidence="high",
                    status="validated_by_source",
                    observation=(
                        f"Function `{fn}` appears to use global `{global_name}` "
                        "instead of its parameters."
                    ),
                    relation="Parameter/global mismatch increases coupling.",
                    confidence_reason="AST or text scan of function body.",
                    context="Example: print_final_scores(final_score) prints global score.",
                    affected_nodes=(),
                    affected_files=(rel,),
                    evidence=(
                        EvidenceItem("source", rel, line_no, line_no, f"uses global `{global_name}`"),
                    ),
                    source_validation="Validated by source scan.",
                    next_validation_steps=("Confirm intended parameter usage in source.",),
                )
            )
    return findings

