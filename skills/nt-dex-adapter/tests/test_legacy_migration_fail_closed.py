import asyncio
import importlib.util
import inspect
import math
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from nautilus_trader.execution.messages import (
    GenerateFillReports,
    GenerateOrderStatusReport,
    GenerateOrderStatusReports,
    GeneratePositionStatusReports,
)
from nautilus_trader.execution.reports import (
    ExecutionMassStatus,
    FillReport,
    OrderStatusReport,
    PositionStatusReport,
)
from nautilus_trader.model.identifiers import AccountId, ClientId, Venue
from nautilus_trader.test_kit.stubs.component import TestComponentStubs
from pydantic import SecretStr

_TEMPLATES = Path(__file__).parent.parent / "migration_reference" / "python" / "templates"
_LEGACY_TEMPLATES = _TEMPLATES / "legacy_migration"


def _install_template_package() -> None:
    templates_package = ModuleType("dex_templates")
    templates_package.__path__ = [str(_TEMPLATES)]
    legacy_package = ModuleType("dex_templates.legacy_migration")
    legacy_package.__path__ = [str(_LEGACY_TEMPLATES)]
    sys.modules["dex_templates"] = templates_package
    sys.modules["dex_templates.legacy_migration"] = legacy_package


def _load_module(name: str):
    _install_template_package()
    root = _LEGACY_TEMPLATES if name in {"dex_data_client", "dex_exec_client", "dex_factory"} else _TEMPLATES
    package = "dex_templates.legacy_migration" if root == _LEGACY_TEMPLATES else "dex_templates"
    spec = importlib.util.spec_from_file_location(f"{package}.{name}", root / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_exec_module = _load_module("dex_exec_client")
_data_module = _load_module("dex_data_client")
_config_module = _load_module("dex_config")
_ExecutionClient = _exec_module.MyDEXExecutionClient
_DataClient = _data_module.MyDEXDataClient


class _LifecycleProbe:
    def __init__(self) -> None:
        self.lifecycle_events: list[str] = []
        self.state_events: list[str] = []
        self._pending_txs: dict[str, str] = {}
        self._generate_mass_status_reconciliation = False

    def generate_order_submitted(self, **kwargs) -> None:
        self.lifecycle_events.append("submitted")

    def generate_order_rejected(self, **kwargs) -> None:
        self.lifecycle_events.append("rejected")

    def generate_order_canceled(self, **kwargs) -> None:
        self.lifecycle_events.append("canceled")

    def generate_order_expired(self, **kwargs) -> None:
        self.lifecycle_events.append("expired")

    def generate_order_filled(self, **kwargs) -> None:
        self.lifecycle_events.append("filled")

    def generate_account_state(self, **kwargs) -> None:
        self.state_events.append("account")


@pytest.mark.parametrize(
    "method_name,command",
    (
        ("_submit_order", SimpleNamespace(order=SimpleNamespace())),
        ("_cancel_order", SimpleNamespace(order=SimpleNamespace())),
        ("_cancel_all_orders", SimpleNamespace()),
        ("_modify_order", SimpleNamespace(client_order_id="O-1")),
        ("_query_order", SimpleNamespace(client_order_id="O-1")),
    ),
)
def test_unsupported_external_order_commands_fail_without_events(method_name: str, command) -> None:
    probe = _LifecycleProbe()

    with pytest.raises(NotImplementedError):
        asyncio.run(getattr(_ExecutionClient, method_name)(probe, command))

    assert probe.lifecycle_events == []
    assert probe.state_events == []


def test_unimplemented_account_state_fails_without_state_event() -> None:
    probe = _LifecycleProbe()

    with pytest.raises(NotImplementedError):
        asyncio.run(_ExecutionClient._update_account_state(probe))

    assert probe.state_events == []


@pytest.mark.parametrize(
    "method_name,arguments",
    (
        ("generate_order_status_report", (SimpleNamespace(),)),
        ("generate_order_status_reports", (SimpleNamespace(),)),
        ("generate_fill_reports", (SimpleNamespace(),)),
        ("generate_position_status_reports", (SimpleNamespace(),)),
    ),
)
def test_unimplemented_reconciliation_fails_without_events(
    method_name: str,
    arguments: tuple[SimpleNamespace],
) -> None:
    probe = _LifecycleProbe()

    with pytest.raises(NotImplementedError):
        asyncio.run(getattr(_ExecutionClient, method_name)(probe, *arguments))

    assert probe.lifecycle_events == []
    assert probe.state_events == []


def test_receipt_monitor_fails_without_terminal_event() -> None:
    probe = _LifecycleProbe()

    with pytest.raises(NotImplementedError):
        asyncio.run(_ExecutionClient._wait_for_receipt(probe, SimpleNamespace(), "0xabc"))

    assert probe.lifecycle_events == []
    assert probe.state_events == []


@pytest.mark.parametrize(
    "method_name,parameter_name,parameter_type,return_type",
    (
        (
            "generate_order_status_report",
            "command",
            GenerateOrderStatusReport,
            OrderStatusReport | None,
        ),
        (
            "generate_order_status_reports",
            "command",
            GenerateOrderStatusReports,
            list[OrderStatusReport],
        ),
        ("generate_fill_reports", "command", GenerateFillReports, list[FillReport]),
        (
            "generate_position_status_reports",
            "command",
            GeneratePositionStatusReports,
            list[PositionStatusReport],
        ),
    ),
)
def test_reconciliation_signatures_match_pinned_contract(
    method_name: str,
    parameter_name: str,
    parameter_type,
    return_type,
) -> None:
    signature = inspect.signature(getattr(_ExecutionClient, method_name), eval_str=True)

    assert tuple(signature.parameters) == ("self", parameter_name)
    assert signature.parameters[parameter_name].annotation == parameter_type
    assert signature.return_annotation == return_type


def test_mass_status_fails_without_toggling_reconciliation_state() -> None:
    client, loop = _construct_execution_client()

    try:
        assert client.reconciliation_active is False
        with pytest.raises(NotImplementedError):
            loop.run_until_complete(client.generate_mass_status(lookback_mins=15))
        assert client.reconciliation_active is False
    finally:
        loop.close()

    signature = inspect.signature(_ExecutionClient.generate_mass_status, eval_str=True)
    assert tuple(signature.parameters) == ("self", "lookback_mins")
    assert signature.parameters["lookback_mins"].annotation == int | None
    assert signature.parameters["lookback_mins"].default is None
    assert signature.return_annotation == ExecutionMassStatus | None


@pytest.mark.parametrize("amount_in", (0.0, -1.0, math.inf, -math.inf, math.nan))
def test_invalid_swap_input_fails_before_trade_tick(amount_in: float, monkeypatch: pytest.MonkeyPatch) -> None:
    trade_ticks: list[tuple[tuple[object, ...], dict[str, object]]] = []
    monkeypatch.setattr(_data_module, "TradeTick", lambda *args, **kwargs: trade_ticks.append((args, kwargs)))

    with pytest.raises(ValueError):
        _DataClient._swap_event_to_trade_tick(
            SimpleNamespace(),
            SimpleNamespace(),
            amount_in,
            1.0,
            "0xabc",
            1,
            True,
        )

    assert trade_ticks == []


@pytest.mark.parametrize("amount_out", (0.0, -1.0, math.inf, -math.inf, math.nan))
def test_invalid_swap_output_fails_before_trade_tick(amount_out: float, monkeypatch: pytest.MonkeyPatch) -> None:
    trade_ticks: list[tuple[tuple[object, ...], dict[str, object]]] = []
    monkeypatch.setattr(_data_module, "TradeTick", lambda *args, **kwargs: trade_ticks.append((args, kwargs)))

    with pytest.raises(ValueError):
        _DataClient._swap_event_to_trade_tick(
            SimpleNamespace(),
            SimpleNamespace(),
            1.0,
            amount_out,
            "0xabc",
            1,
            True,
        )

    assert trade_ticks == []


@pytest.mark.parametrize(
    "amount_in,amount_out",
    (
        (1.0, 1e-12),
        (1e-308, 1e308),
        (1e-12, 1.0),
    ),
)
def test_invalid_derived_swap_values_fail_before_trade_tick(
    amount_in: float,
    amount_out: float,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trade_ticks: list[tuple[tuple[object, ...], dict[str, object]]] = []
    monkeypatch.setattr(_data_module, "TradeTick", lambda *args, **kwargs: trade_ticks.append((args, kwargs)))

    with pytest.raises(ValueError):
        _DataClient._swap_event_to_trade_tick(
            SimpleNamespace(),
            SimpleNamespace(),
            amount_in,
            amount_out,
            "0xabc",
            1,
            True,
        )

    assert trade_ticks == []


def test_ordinary_positive_swap_constructs_trade_tick(monkeypatch: pytest.MonkeyPatch) -> None:
    trade_ticks: list[dict[str, object]] = []
    monkeypatch.setattr(_data_module, "TradeTick", lambda **kwargs: trade_ticks.append(kwargs) or kwargs)
    client = SimpleNamespace(clock=SimpleNamespace(timestamp_ns=lambda: 2))

    result = _DataClient._swap_event_to_trade_tick(
        client,
        SimpleNamespace(),
        2.0,
        6.0,
        "0xabc",
        1,
        True,
    )

    assert result == trade_ticks[0]
    assert str(result["price"]) == "3.000000"
    assert str(result["size"]) == "2.00000000"


@pytest.mark.parametrize(
    "amount_in,amount_out",
    (
        (1.0, 1e100),
        (1e100, 1e100),
        (1e12, 1.0),
    ),
    ids=("price", "quantity", "finite-quantity"),
)
def test_out_of_range_fixed_point_values_raise_domain_error_before_trade_tick(
    amount_in: float,
    amount_out: float,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trade_ticks: list[dict[str, object]] = []
    monkeypatch.setattr(_data_module, "TradeTick", lambda **kwargs: trade_ticks.append(kwargs))

    with pytest.raises(_data_module.InvalidSwapEventError):
        _DataClient._swap_event_to_trade_tick(
            SimpleNamespace(),
            SimpleNamespace(),
            amount_in,
            amount_out,
            "0xabc",
            1,
            True,
        )

    assert trade_ticks == []


def _construct_execution_client(private_key: str = ""):
    loop = asyncio.new_event_loop()
    provider = _exec_module.MyDEXInstrumentProvider(_config_module.MyDEXInstrumentProviderConfig())
    client = _ExecutionClient(
        loop=loop,
        client_id=ClientId("MYDEX"),
        venue=Venue("MYDEX"),
        account_id=AccountId("MYDEX-001"),
        msgbus=TestComponentStubs.msgbus(),
        cache=TestComponentStubs.cache(),
        clock=TestComponentStubs.clock(),
        instrument_provider=provider,
        config=_exec_module.MyDEXExecClientConfig(private_key=SecretStr(private_key)),
    )
    return client, loop


def test_legacy_clients_construct_with_current_base_contract() -> None:
    loop = asyncio.new_event_loop()
    clock = TestComponentStubs.clock()
    msgbus = TestComponentStubs.msgbus()
    cache = TestComponentStubs.cache()
    provider_config = _config_module.MyDEXInstrumentProviderConfig()
    provider = _exec_module.MyDEXInstrumentProvider(provider_config)

    try:
        data_client = _DataClient(
            loop=loop,
            client_id=ClientId("MYDEX"),
            venue=Venue("MYDEX"),
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=provider,
            config=_data_module.MyDEXDataClientConfig(),
        )
        exec_client = _ExecutionClient(
            loop=loop,
            client_id=ClientId("MYDEX"),
            venue=Venue("MYDEX"),
            account_id=AccountId("MYDEX-001"),
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=provider,
            config=_exec_module.MyDEXExecClientConfig(),
        )
    finally:
        loop.close()

    assert data_client._instrument_provider is provider
    assert exec_client._instrument_provider is provider
    assert exec_client.account_id == AccountId("MYDEX-001")


def test_execution_base_config_serializes_without_operational_secret() -> None:
    secret = "round-three-secret"
    client, loop = _construct_execution_client(private_key=secret)

    try:
        serialized = client._component_config.json().decode()
        assert secret not in serialized
        assert secret not in repr(client._operational_config)
    finally:
        loop.close()


def test_exec_factory_uses_canonical_contract_and_derives_account_id() -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    loop = asyncio.new_event_loop()

    try:
        client = factory_module.MyDEXLiveExecClientFactory.create(
            loop,
            "MYDEX",
            factory_module.MyDEXExecClientConfig(),
            TestComponentStubs.msgbus(),
            TestComponentStubs.cache(),
            TestComponentStubs.clock(),
        )
    finally:
        loop.close()

    assert client.account_id == AccountId("MYDEX-001")
    signature = inspect.signature(factory_module.MyDEXLiveExecClientFactory.create)
    assert tuple(signature.parameters) == ("loop", "name", "config", "msgbus", "cache", "clock")


def test_provider_cache_key_includes_rpc_pools_and_sandbox_inputs() -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    base = factory_module.MyDEXDataClientConfig(
        rpc_url="https://rpc.example",
        pool_addresses=["0x1"],
        sandbox_mode=True,
    )
    different_pool = factory_module.MyDEXDataClientConfig(
        rpc_url="https://rpc.example",
        pool_addresses=["0x2"],
        sandbox_mode=True,
    )
    different_sandbox = factory_module.MyDEXDataClientConfig(
        rpc_url="https://rpc.example",
        pool_addresses=["0x1"],
        sandbox_mode=False,
    )

    first = factory_module._get_or_create_instrument_provider(base)
    assert factory_module._get_or_create_instrument_provider(base) is first
    assert factory_module._get_or_create_instrument_provider(different_pool) is not first
    assert factory_module._get_or_create_instrument_provider(different_sandbox) is not first


def test_provider_cache_separates_chains_and_preserves_chain_id() -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    ethereum = factory_module.MyDEXDataClientConfig(
        rpc_url="https://rpc.example",
        chain_id=1,
        pool_addresses=["0x1"],
    )
    arbitrum = factory_module.MyDEXDataClientConfig(
        rpc_url="https://rpc.example",
        chain_id=42161,
        pool_addresses=["0x1"],
    )

    ethereum_provider = factory_module._get_or_create_instrument_provider(ethereum)
    arbitrum_provider = factory_module._get_or_create_instrument_provider(arbitrum)

    assert arbitrum_provider is not ethereum_provider
    assert ethereum_provider._config.chain_id == 1
    assert arbitrum_provider._config.chain_id == 42161


def test_nested_provider_config_is_authoritative_and_fully_preserved() -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    nested = factory_module.MyDEXInstrumentProviderConfig(
        rpc_url="https://nested.example",
        chain_id=42161,
        pools=["0xnested"],
        sandbox_mode=False,
        load_all=True,
        load_ids=frozenset({"WETH-USDC.MYDEX"}),
        filters={"quote_currency": "USDC"},
        log_warnings=False,
        use_gamma_markets=True,
    )
    client_config = factory_module.MyDEXDataClientConfig(
        instrument_provider=nested,
        rpc_url="https://direct.example",
        chain_id=1,
        pool_addresses=["0xdirect"],
        sandbox_mode=True,
    )

    provider = factory_module._get_or_create_instrument_provider(client_config)

    assert provider._config == nested


@pytest.mark.parametrize(
    "provider_config",
    (
        _config_module.MyDEXInstrumentProviderConfig(load_all=True),
        _config_module.MyDEXInstrumentProviderConfig(load_ids=frozenset({"WETH-USDC.MYDEX"})),
        _config_module.MyDEXInstrumentProviderConfig(filters={"quote_currency": "USDC"}),
        _config_module.MyDEXInstrumentProviderConfig(pools=["0x2"]),
    ),
)
def test_provider_cache_identity_includes_all_effective_fields(provider_config) -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    provider_config = factory_module.MyDEXInstrumentProviderConfig(**provider_config.dict())
    default_config = factory_module.MyDEXDataClientConfig(
        instrument_provider=factory_module.MyDEXInstrumentProviderConfig(),
    )
    changed_config = factory_module.MyDEXDataClientConfig(instrument_provider=provider_config)

    default_provider = factory_module._get_or_create_instrument_provider(default_config)
    changed_provider = factory_module._get_or_create_instrument_provider(changed_config)

    assert changed_provider is not default_provider
    assert changed_provider._config == provider_config


def test_effective_provider_config_owns_deeply_immutable_source_values() -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    pools = ["0x1"]
    filters = {"quote_currency": "USDC"}
    source = factory_module.MyDEXInstrumentProviderConfig(
        pools=pools,
        filters=filters,
    )
    client_config = factory_module.MyDEXDataClientConfig(instrument_provider=source)

    provider = factory_module._get_or_create_instrument_provider(client_config)
    pools.append("0x2")
    filters["base_currency"] = "WETH"

    assert provider._config is not source
    assert provider._config.pools == ("0x1",)
    assert provider._config.filters == {"quote_currency": "USDC"}
    with pytest.raises(TypeError):
        provider._config.filters["base_currency"] = "WETH"


def test_semantically_identical_provider_config_reuses_canonical_identity() -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    first = factory_module.MyDEXDataClientConfig(
        instrument_provider=factory_module.MyDEXInstrumentProviderConfig(
            load_ids=frozenset({"ETH-USDC.MYDEX", "BTC-USDC.MYDEX"}),
            filters={"quote_currency": "USDC", "base_currency": "WETH"},
        ),
    )
    second = factory_module.MyDEXExecClientConfig(
        instrument_provider=factory_module.MyDEXInstrumentProviderConfig(
            load_ids=frozenset({"BTC-USDC.MYDEX", "ETH-USDC.MYDEX"}),
            filters={"base_currency": "WETH", "quote_currency": "USDC"},
        ),
    )

    first_provider = factory_module._get_or_create_instrument_provider(first)
    second_provider = factory_module._get_or_create_instrument_provider(second)

    assert second_provider is first_provider


def test_identical_full_effective_provider_config_reuses_cached_provider() -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    first_config = factory_module.MyDEXDataClientConfig(
        instrument_provider=factory_module.MyDEXInstrumentProviderConfig(
            chain_id=42161,
            load_all=True,
            filters={"quote_currency": "USDC"},
        ),
    )
    second_config = factory_module.MyDEXExecClientConfig(
        instrument_provider=factory_module.MyDEXInstrumentProviderConfig(
            chain_id=42161,
            load_all=True,
            filters={"quote_currency": "USDC"},
        ),
    )

    first = factory_module._get_or_create_instrument_provider(first_config)
    second = factory_module._get_or_create_instrument_provider(second_config)

    assert second is first


def test_data_and_execution_factories_honor_nested_provider_config() -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    nested = factory_module.MyDEXInstrumentProviderConfig(chain_id=42161, load_all=True)
    loop = asyncio.new_event_loop()

    try:
        data_client = factory_module.MyDEXLiveDataClientFactory.create(
            loop,
            "MYDEX",
            factory_module.MyDEXDataClientConfig(instrument_provider=nested),
            TestComponentStubs.msgbus(),
            TestComponentStubs.cache(),
            TestComponentStubs.clock(),
        )
        exec_client = factory_module.MyDEXLiveExecClientFactory.create(
            loop,
            "MYDEX",
            factory_module.MyDEXExecClientConfig(instrument_provider=nested),
            TestComponentStubs.msgbus(),
            TestComponentStubs.cache(),
            TestComponentStubs.clock(),
        )
    finally:
        loop.close()

    assert data_client._instrument_provider is exec_client._instrument_provider
    assert data_client._instrument_provider._config == nested


def test_direct_legacy_provider_fields_apply_when_nested_config_is_standard_default() -> None:
    factory_module = _load_module("dex_factory")
    factory_module._instrument_providers.clear()
    client_config = factory_module.MyDEXDataClientConfig(
        rpc_url="https://direct.example",
        chain_id=1,
        pool_addresses=["0xdirect"],
        sandbox_mode=False,
    )

    provider = factory_module._get_or_create_instrument_provider(client_config)

    assert provider._config.rpc_url == "https://direct.example"
    assert provider._config.chain_id == 1
    assert provider._config.pools == ("0xdirect",)
    assert provider._config.sandbox_mode is False


def test_templates_remain_classified_as_legacy_migration_only() -> None:
    for name in ("dex_exec_client.py", "dex_data_client.py"):
        path = _LEGACY_TEMPLATES / name
        assert "TEMPLATE_CLASSIFICATION: legacy executable" in path.read_text(encoding="utf-8")
        assert path.parent.name == "legacy_migration"
