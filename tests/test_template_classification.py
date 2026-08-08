from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.template_classification import classification_error, shipped_python_files

REPO_ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION_PREFIX = "# TEMPLATE_CLASSIFICATION: "
MIGRATION_CLASSIFICATION = "migration/reference-only; not a production default"
LEGACY_CLASSIFICATION = (
    "legacy executable; migration/reference-only; not a production default"
)
SOURCE_SNAPSHOT_CLASSIFICATION = (
    "source snapshot; migration/reference-only; not a production default"
)
ALLOWED_CLASSIFICATIONS = {
    MIGRATION_CLASSIFICATION,
    LEGACY_CLASSIFICATION,
    SOURCE_SNAPSHOT_CLASSIFICATION,
}
PYTHON_SUFFIXES = {".py", ".pyi", ".pyx", ".pxd", ".pxi"}


def test_every_shipped_python_guidance_file_has_one_exact_classification() -> None:
    errors = {
        path.relative_to(REPO_ROOT).as_posix(): error
        for path in shipped_python_files(REPO_ROOT)
        if (error := classification_error(path, REPO_ROOT)) is not None
    }

    assert errors == {}


def test_directory_membership_does_not_classify_python(tmp_path: Path) -> None:
    for directory in ("references", "templates", "legacy_migration"):
        path = tmp_path / "skills/nt-example" / directory / "example.py"
        _write(path, "print('not classified')\n")

        assert classification_error(path, tmp_path) == "missing classification"


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
        errors[name] = classification_error(path, tmp_path)

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

    assert classification_error(late, tmp_path) == "classification is not in header"
    assert classification_error(shebang, tmp_path) is None


def test_shipped_python_discovery_includes_reference_python(tmp_path: Path) -> None:
    path = tmp_path / "references/api_reference/conf.py"
    _write(path, f"{CLASSIFICATION_PREFIX}{SOURCE_SNAPSHOT_CLASSIFICATION}\n")

    assert path in shipped_python_files(tmp_path)


def test_source_snapshot_classification_is_allowed_only_under_references(
    tmp_path: Path,
) -> None:
    reference = tmp_path / "references/api_reference/conf.py"
    template = tmp_path / "skills/nt-example/templates/conf.py"
    text = f"{CLASSIFICATION_PREFIX}{SOURCE_SNAPSHOT_CLASSIFICATION}\n"
    _write(reference, text)
    _write(template, text)

    assert classification_error(reference, tmp_path) is None
    assert classification_error(template, tmp_path) == (
        "source snapshot classification is only allowed under references"
    )


def test_migration_classification_does_not_bless_trading_node(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-example/legacy_migration/node.py"
    _write(
        path,
        f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
        "from nautilus_trader.live.node import TradingNode\n",
    )

    assert classification_error(path, tmp_path) == (
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

    assert classification_error(path, tmp_path) == (
        "legacy classification requires a legacy_migration path component"
    )


def test_legacy_classification_inside_legacy_migration_passes(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-example/legacy_migration/node.py"
    _write(
        path,
        f"{CLASSIFICATION_PREFIX}{LEGACY_CLASSIFICATION}\n"
        "from nautilus_trader.live.node import TradingNode\n",
    )

    assert classification_error(path, tmp_path) is None


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

    assert classification_error(cython, tmp_path) == (
        "legacy executable requires the exact legacy classification"
    )
    assert classification_error(v1_api, tmp_path) == (
        "legacy executable requires the exact legacy classification"
    )


def test_qualified_trading_node_call_requires_legacy_quarantine(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-example/templates/node.py"
    _write(
        path,
        f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
        "import nautilus_trader.live.node\n"
        "node = nautilus_trader.live.node.TradingNode(config=config)\n",
    )

    assert classification_error(path, tmp_path) == (
        "legacy executable requires the exact legacy classification"
    )


def test_syntax_error_with_known_legacy_api_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-example/templates/malformed.py"
    _write(
        path,
        f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
        "from nautilus_trader.live.node import TradingNode\n"
        "def broken(:\n",
    )

    assert classification_error(path, tmp_path) == (
        "legacy executable requires the exact legacy classification"
    )


def test_live_factory_variants_require_legacy_quarantine(tmp_path: Path) -> None:
    variants = (
        "LiveExecClientFactory",
        "LiveExecutionClientFactory",
        "MyVenueLiveDataClientFactory",
        "MyVenueLiveExecClientFactory",
    )
    for variant in variants:
        path = tmp_path / "skills/nt-example/templates" / f"{variant}.py"
        _write(
            path,
            f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
            f"class Factory({variant}):\n    pass\n",
        )

        assert classification_error(path, tmp_path) == (
            "legacy executable requires the exact legacy classification"
        )


def test_live_client_subclasses_require_legacy_quarantine(tmp_path: Path) -> None:
    for surface in ("LiveDataClient", "LiveMarketDataClient", "LiveExecutionClient"):
        path = tmp_path / "skills/nt-example/templates" / f"{surface}.py"
        _write(
            path,
            f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n"
            f"class Client({surface}):\n    pass\n",
        )

        assert classification_error(path, tmp_path) == (
            "legacy executable requires the exact legacy classification"
        )


def test_aliased_legacy_imports_require_legacy_quarantine(tmp_path: Path) -> None:
    imports = (
        "from nautilus_trader.live.node import TradingNode as Node",
        "from nautilus_trader.live.data_client import LiveDataClient as DataClient",
        "from nautilus_trader.live.execution_client import LiveExecutionClient as ExecClient",
        "from nautilus_trader.live.factories import LiveExecClientFactory as Factory",
        "from venue.factories import MyVenueLiveDataClientFactory as Factory",
    )
    for index, statement in enumerate(imports):
        path = tmp_path / "skills/nt-example/templates" / f"alias_{index}.py"
        _write(
            path,
            f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n{statement}\n",
        )

        assert classification_error(path, tmp_path) == (
            "legacy executable requires the exact legacy classification"
        )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_migration_python_is_physically_quarantined(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-trading/templates/strategy.py"
    _write(path, f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n")

    assert classification_error(path, tmp_path) == (
        "migration Python requires a migration_reference path component"
    )


def test_dex_migration_python_is_physically_quarantined(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-dex-adapter/templates/dex_config.py"
    _write(path, f"{CLASSIFICATION_PREFIX}{MIGRATION_CLASSIFICATION}\n")

    assert classification_error(path, tmp_path) == (
        "migration Python requires a migration_reference path component"
    )
