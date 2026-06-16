"""Detect test suite layout in the target repository."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TargetDiscovery:
    has_tests: bool
    test_command: list[str] | None
    reason: str
    python_files: tuple[str, ...]


def discover_target(repo_root: Path) -> TargetDiscovery:
    """Check if target repo has a dedicated test suite."""
    py_files = tuple(
        str(p.relative_to(repo_root)).replace("\\", "/")
        for p in sorted(repo_root.rglob("*.py"))
        if not any(part.startswith(".") for part in p.parts)
        and "graphify-out" not in str(p)
        and "__pycache__" not in str(p)
    )
    # Look for a tests/ directory or test_*.py files
    tests_dir = repo_root / "tests"
    pytest_ini = repo_root / "pytest.ini"
    pyproject = repo_root / "pyproject.toml"
    has_test_dir = tests_dir.is_dir() and any(tests_dir.rglob("test_*.py"))
    has_conftest = (repo_root / "conftest.py").is_file()
    has_config = pytest_ini.is_file() or pyproject.is_file()

    if has_test_dir:
        return TargetDiscovery(
            has_tests=True,
            test_command=["pytest", str(tests_dir), "-v"],
            reason="Found tests/ directory with test_*.py files",
            python_files=py_files,
        )
    if has_conftest and has_config:
        return TargetDiscovery(
            has_tests=True,
            test_command=["pytest", "-v"],
            reason="Found conftest.py with pytest configuration",
            python_files=py_files,
        )
    return TargetDiscovery(
        has_tests=False,
        test_command=None,
        reason="No dedicated test suite found — running fallback validation only",
        python_files=py_files,
    )
