from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION_PREFIX = "# TEMPLATE_CLASSIFICATION: "
AI_CLASSIFICATION = "AI/advisory Python; non-production; off execution-critical paths"
MIGRATION_CLASSIFICATION = "migration/reference-only; not a production default"
LEGACY_CLASSIFICATION = (
    "legacy executable; migration/reference-only; not a production default"
)
ALLOWED_CLASSIFICATIONS = {
    AI_CLASSIFICATION,
    MIGRATION_CLASSIFICATION,
    LEGACY_CLASSIFICATION,
}
PYTHON_SUFFIXES = {".py", ".pyi", ".pyx", ".pxd", ".pxi"}
AI_SKILL = Path("skills/nt-evomap-integration")


def test_every_shipped_python_guidance_file_has_one_exact_classification() -> None:
    errors = {
        path.relative_to(REPO_ROOT).as_posix(): error
        for path in _shipped_python_files(REPO_ROOT)
        if (error := _classification_error(path, REPO_ROOT)) is not None
    }

    assert errors == {}


def test_directory_membership_does_not_classify_python(tmp_path: Path) -> None:
    for directory in ("references", "templates", "legacy_migration"):
        path = tmp_path / "skills/nt-example" / directory / "example.py"
        _write(path, "print('not classified')\n")

        assert _classification_error(path, tmp_path) == "missing classification"


def test_malformed_duplicate_and_unknown_classifications_fail(tmp_path: Path) -> None:
    cases = {
        "malformed.py": f"{CLASSIFICATION_PREFIX[:-1]}{MIGRATION_CLASSIFICATION}\n",
        "duplicate.py": (
            f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
            f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
        ),
        "unknown.py": f"{CLASSIFICATION_PREFIX}reference only\n",
    }

    errors: dict[str, str | None] = {}
    for name, text in cases.items():
        path = tmp_path / "skills/nt-example" / name
        _write(path, text)
        errors[name] = _classification_error(path, tmp_path)

    assert errors == {
        "malformed.py": "missing classification",
        "duplicate.py": "expected exactly one classification, found 2",
        "unknown.py": "unknown classification: reference only",
    }


def test_classification_must_be_first_line_or_follow_shebang(tmp_path: Path) -> None:
    late = tmp_path / "skills/nt-example/late.py"
    shebang = tmp_path / "skills/nt-example/shebang.py"
    _write(late, f"# comment\n{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n")
    _write(
        shebang,
        f"#!/usr/bin/env python3\n{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n",
    )

    assert _classification_error(late, tmp_path) == "classification is not in header"
    assert _classification_error(shebang, tmp_path) is None


def test_ai_classification_is_rejected_outside_evomap_skill(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-example/example.py"
    _write(path, f"{CLASSIFICATION_PREFIX}{AI_CLASSIFICATION}\n")

    assert _classification_error(path, tmp_path) == (
        "AI classification is only allowed under skills/nt-evomap-integration"
    )


def test_migration_classification_does_not_bless_trading_node(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-example/legacy_migration/node.py"
    _write(
        path,
        f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
        "from nautilus_trader.live.node import TradingNode\n",
    )

    assert _classification_error(path, tmp_path) == (
        "legacy executable requires the exact legacy classification"
    )


def test_legacy_classification_requires_legacy_migration_namespace(
    tmp_path: Path,
) -> None:
    path = tmp_path / "skills/nt-example/templates/node.py"
    _write(
        path,
        f"{CLASSIFICATION_PREFIX}{LEGACY_CLASSIFICATION}\n"
        "from nautilus_trader.config import TradingNodeConfig\n",
    )

    assert _classification_error(path, tmp_path) == (
        "legacy classification requires a legacy_migration path component"
    )


def test_legacy_classification_inside_legacy_migration_passes(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-example/legacy_migration/node.py"
    _write(
        path,
        f"{CLASSIFICATION_PREFIX}{LEGACY_CLASSIFICATION}\n"
        "from nautilus_trader.live.node import TradingNode\n",
    )

    assert _classification_error(path, tmp_path) is None


def test_cython_and_v1_executable_signals_require_legacy_quarantine(
    tmp_path: Path,
) -> None:
    cython = tmp_path / "skills/nt-example/templates/clock.pyx"
    v1_api = tmp_path / "skills/nt-example/templates/config.py"
    _write(
        cython,
        f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
        "cdef class LegacyClock:\n    pass\n",
    )
    _write(
        v1_api,
        f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
        "from nautilus_trader.live.factories import LiveDataClientFactory\n",
    )

    assert _classification_error(cython, tmp_path) == (
        "legacy executable requires the exact legacy classification"
    )
    assert _classification_error(v1_api, tmp_path) == (
        "legacy executable requires the exact legacy classification"
    )


def _shipped_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted((root / "skills").glob("nt*/**/*")):
        if not path.is_file() or path.suffix not in PYTHON_SUFFIXES:
            continue
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        files.append(path)
    return files


def _classification_error(path: Path, root: Path) -> str | None:
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
    if classification == LEGACY_CLASSIFICATION and "legacy_migration" not in relative.parts:
        return "legacy classification requires a legacy_migration path component"
    if _has_legacy_executable_signal(path) and classification != LEGACY_CLASSIFICATION:
        return "legacy executable requires the exact legacy classification"
    return None


def _has_legacy_executable_signal(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return bool(
            path.suffix in {".pyx", ".pxd", ".pxi"}
            or any(term in text for term in ("cdef ", "cpdef ", "cimport "))
        )

    legacy_names = {"TradingNode", "TradingNodeConfig", "LiveDataClientFactory"}
    return any(
        isinstance(node, ast.Name) and node.id in legacy_names
        or isinstance(node, ast.alias) and node.name.rsplit(".", 1)[-1] in legacy_names
        for node in ast.walk(tree)
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
