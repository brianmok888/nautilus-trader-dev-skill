from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Final

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.cutover_inventory import ACTIVE_PYTHON_SKILL, CUTOVER_SKILL_NAMES

CLASSIFICATION_PREFIX: Final = "# TEMPLATE_CLASSIFICATION: "
AI_CLASSIFICATION: Final = (
    "AI/advisory Python; non-production; off execution-critical paths"
)
MIGRATION_CLASSIFICATION: Final = "migration/reference-only; not a production default"
LEGACY_CLASSIFICATION: Final = (
    "legacy executable; migration/reference-only; not a production default"
)
SOURCE_SNAPSHOT_CLASSIFICATION: Final = (
    "source snapshot; migration/reference-only; not a production default"
)
ALLOWED_CLASSIFICATIONS: Final = {
    AI_CLASSIFICATION,
    MIGRATION_CLASSIFICATION,
    LEGACY_CLASSIFICATION,
    SOURCE_SNAPSHOT_CLASSIFICATION,
}
AI_SKILL: Final = Path("skills") / ACTIVE_PYTHON_SKILL
LEGACY_EXACT_NAMES: Final = {
    "TradingNode",
    "TradingNodeConfig",
    "LiveDataClientFactory",
    "LiveExecClientFactory",
    "LiveExecutionClientFactory",
    "LiveDataClient",
    "LiveMarketDataClient",
    "LiveExecutionClient",
}
CONCRETE_FACTORY_RE: Final = re.compile(
    r"(?:^|\.)[A-Za-z_][A-Za-z0-9_]*Live(?:Data|Exec|Execution)ClientFactory$"
)
TEXTUAL_LEGACY_RE: Final = re.compile(
    r"\b(?:TradingNode|TradingNodeConfig|LiveDataClientFactory|"
    + r"LiveExecClientFactory|LiveExecutionClientFactory|LiveDataClient|LiveMarketDataClient|"
    + r"LiveExecutionClient|[A-Za-z_][A-Za-z0-9_]*Live(?:Data|Exec|Execution)ClientFactory)\b"
)
PYTHON_SUFFIXES: Final = {".py", ".pyi", ".pyx", ".pxd", ".pxi"}


def classification_error(path: Path, root: Path) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    classifications = [
        line.removeprefix(CLASSIFICATION_PREFIX)
        for line in lines
        if line.startswith(CLASSIFICATION_PREFIX)
    ]
    if not classifications:
        return "missing classification"
    if len(classifications) != 1:
        return f"expected exactly one classification, found {len(classifications)}"

    classification = classifications[0]
    if classification not in ALLOWED_CLASSIFICATIONS:
        return f"unknown classification: {classification}"

    header_index = 1 if lines and lines[0].startswith("#!") else 0
    if lines[header_index] != f"{CLASSIFICATION_PREFIX}{classification}":
        return "classification is not in header"

    relative = path.relative_to(root)
    if classification == AI_CLASSIFICATION and not relative.is_relative_to(AI_SKILL):
        return "AI classification is only allowed under skills/nt-evomap-integration"
    if (
        classification == SOURCE_SNAPSHOT_CLASSIFICATION
        and relative.parts[0] != "references"
    ):
        return "source snapshot classification is only allowed under references"
    if (
        classification == AI_CLASSIFICATION
        and "python_sidecar" not in relative.parts
        and "templates" not in relative.parts
    ):
        return "AI classification requires the python_sidecar path component"
    if classification == LEGACY_CLASSIFICATION and "legacy_migration" not in relative.parts:
        return "legacy classification requires a legacy_migration path component"
    if has_legacy_executable_signal(path) and classification != LEGACY_CLASSIFICATION:
        return "legacy executable requires the exact legacy classification"
    if (
        classification == MIGRATION_CLASSIFICATION
        and len(relative.parts) > 2
        and relative.parts[0] == "skills"
        and relative.parts[1] in CUTOVER_SKILL_NAMES
        and relative.parts[1] != ACTIVE_PYTHON_SKILL
        and "migration_reference" not in relative.parts
    ):
        return "non-AI migration Python requires a migration_reference path component"
    return None


def shipped_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in PYTHON_SUFFIXES:
            continue
        relative = path.relative_to(root)
        if (
            "tests" in relative.parts
            or "__pycache__" in relative.parts
            or relative.parts[0] in {".git", ".omx", ".worktrees", "tools"}
            or relative.name == "conftest.py"
        ):
            continue
        files.append(path)
    return files


def has_legacy_executable_signal(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return bool(
            path.suffix in {".pyx", ".pxd", ".pxi"}
            or any(term in text for term in ("cdef ", "cpdef ", "cimport "))
            or TEXTUAL_LEGACY_RE.search(text)
        )

    return any(_is_legacy_node(node) for node in ast.walk(tree))


def _is_legacy_node(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        names = (node.id,)
    elif isinstance(node, ast.Attribute):
        names = (node.attr,)
    elif isinstance(node, ast.alias):
        names = (node.name.rsplit(".", 1)[-1], node.asname or "")
    else:
        return False
    return any(
        name in LEGACY_EXACT_NAMES or bool(CONCRETE_FACTORY_RE.fullmatch(name))
        for name in names
    )
