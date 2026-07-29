"""Non-production smoke checks for quarantined Python migration templates."""

import importlib.util
import asyncio
import sys
from pathlib import Path

import pytest
from nautilus_trader.model.identifiers import AccountId, ClientId, Venue
from nautilus_trader.test_kit.stubs.component import TestComponentStubs

pytest.importorskip("pydantic")

_templates = Path(__file__).parent.parent / "templates"
_legacy_templates = _templates / "legacy_migration"
sys.path.insert(0, str(_templates))


def _load_migration_module(name: str):
    root = _legacy_templates if name in {"dex_data_client", "dex_exec_client", "dex_factory"} else _templates
    spec = importlib.util.spec_from_file_location(name, root / f"{name}.py")
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
