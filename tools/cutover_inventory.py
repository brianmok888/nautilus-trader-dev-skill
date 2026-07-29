from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Final

ACTIVE_PYTHON_SKILL: Final = "nt-evomap-integration"
CUTOVER_SKILL_NAMES: Final = (
    "nt",
    "nt-adapters",
    "nt-architect",
    "nt-backtest",
    "nt-data",
    "nt-dev",
    "nt-dex-adapter",
    "nt-implement",
    "nt-learn",
    "nt-live",
    "nt-model",
    "nt-review",
    "nt-signals",
    "nt-strategy-builder",
    "nt-strategy-builder-rust",
    "nt-testing",
    "nt-trading",
)


def cutover_skill_paths(root: Path) -> tuple[Path, ...]:
    return tuple(root / "skills" / name / "SKILL.md" for name in CUTOVER_SKILL_NAMES)


def discovered_cutover_skill_names(root: Path) -> tuple[str, ...]:
    return tuple(
        sorted(
            path.parent.name
            for path in (root / "skills").glob("nt*/SKILL.md")
            if path.parent.name != ACTIVE_PYTHON_SKILL
        )
    )


def validate_cutover_inventory(root: Path) -> list[str]:
    configured = set(CUTOVER_SKILL_NAMES)
    discovered = set(discovered_cutover_skill_names(root))
    return [
        *(f"cutover inventory missing skill: {name}" for name in sorted(discovered - configured)),
        *(f"cutover inventory contains unknown skill: {name}" for name in sorted(configured - discovered)),
    ]


def validate_root_skill_python_fences(paths: Iterable[Path], root: Path) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line == "```python":
                errors.append(
                    f"{path.relative_to(root).as_posix()}:{line_number}: "
                    "non-AI root skill contains a Python fence"
                )
    return errors
