"""Non-production smoke checks for quarantined Python migration templates."""

import pytest

# NT v2 compatibility note: legacy: migration/reference-only — this module exercises the quarantined v1
# Python templates and v1-only helper surface (TestComponentStubs,
# execution.messages/reports commands, nautilus_trader.model.data) that do not
# exist in the pinned V2 Python package (6df23738). It is retained for
# migration review and skips against the pinned interpreter.
pytest.skip(
    "legacy v1 template/module surface absent from the pinned V2 package "
    "(migration/reference-only; see NT-2026-09-05-145)",
    allow_module_level=True,
)

import importlib.util
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
from nautilus_trader.model.identifiers import AccountId, ClientId, Venue
from nautilus_trader.test_kit.stubs.component import TestComponentStubs

pytest.importorskip("pydantic")


_templates = Path(__file__).parent.parent / "migration_reference" / "python" / "templates"
_legacy_templates = _templates / "legacy_migration"


def _install_template_package() -> None:
    templates_package = ModuleType("dex_templates")
    templates_package.__path__ = [str(_templates)]
    legacy_package = ModuleType("dex_templates.legacy_migration")
    legacy_package.__path__ = [str(_legacy_templates)]
    sys.modules["dex_templates"] = templates_package
    sys.modules["dex_templates.legacy_migration"] = legacy_package


def _load_migration_module(name: str):
    _install_template_package()
    root = _legacy_templates if name in {"dex_data_client", "dex_exec_client", "dex_factory"} else _templates
    package = "dex_templates.legacy_migration" if root == _legacy_templates else "dex_templates"
    spec = importlib.util.spec_from_file_location(f"{package}.{name}", root / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize(
    "module_name",
    (
        "dex_config",
        "dex_instrument_provider",
        "dex_data_client",
        "dex_exec_client",
        "dex_factory",
    ),
)
def test_quarantined_migration_template_imports(module_name: str) -> None:
    assert _load_migration_module(module_name) is not None


def test_quarantined_migration_clients_construct() -> None:
    data_module = _load_migration_module("dex_data_client")
    exec_module = _load_migration_module("dex_exec_client")
    config_module = _load_migration_module("dex_config")
    provider_module = _load_migration_module("dex_instrument_provider")
    provider = provider_module.MyDEXInstrumentProvider(config_module.MyDEXInstrumentProviderConfig())
    loop = asyncio.new_event_loop()

    try:
        data_module.MyDEXDataClient(
            loop=loop,
            client_id=ClientId("MYDEX"),
            venue=Venue("MYDEX"),
            msgbus=TestComponentStubs.msgbus(),
            cache=TestComponentStubs.cache(),
            clock=TestComponentStubs.clock(),
            instrument_provider=provider,
            config=config_module.MyDEXDataClientConfig(),
        )
        exec_module.MyDEXExecutionClient(
            loop=loop,
            client_id=ClientId("MYDEX"),
            venue=Venue("MYDEX"),
            account_id=AccountId("MYDEX-001"),
            msgbus=TestComponentStubs.msgbus(),
            cache=TestComponentStubs.cache(),
            clock=TestComponentStubs.clock(),
            instrument_provider=provider,
            config=config_module.MyDEXExecClientConfig(),
        )
    finally:
        loop.close()


@pytest.mark.parametrize("module_name", ("dex_data_client", "dex_exec_client", "dex_factory"))
def test_legacy_executable_imports_in_clean_subprocess(module_name: str) -> None:
    # Templates are package modules: direct-file execution is intentionally unsupported.
    script = f"import templates.legacy_migration.{module_name}"
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(_templates.parent)},
    )

    assert result.returncode == 0, result.stderr
