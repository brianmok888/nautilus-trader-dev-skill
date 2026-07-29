import asyncio
import importlib.util
import inspect
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from nautilus_trader.execution.messages import GenerateFillReports
from nautilus_trader.execution.messages import GenerateOrderStatusReport
from nautilus_trader.execution.messages import GenerateOrderStatusReports
from nautilus_trader.execution.messages import GeneratePositionStatusReports
from nautilus_trader.execution.reports import FillReport
from nautilus_trader.execution.reports import ExecutionMassStatus
from nautilus_trader.execution.reports import OrderStatusReport
from nautilus_trader.execution.reports import PositionStatusReport
from nautilus_trader.model.identifiers import AccountId
from nautilus_trader.model.identifiers import ClientId
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.test_kit.stubs.component import TestComponentStubs


_TEMPLATES = Path(__file__).parent.parent / "templates"
_LEGACY_TEMPLATES = _TEMPLATES / "legacy_migration"
sys.path.insert(0, str(_TEMPLATES))


def _load_module(name: str):
    root = _LEGACY_TEMPLATES if name in {"dex_data_client", "dex_exec_client"} else _TEMPLATES
    spec = importlib.util.spec_from_file_location(name, root / f"{name}.py")
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
    probe = _LifecycleProbe()

    with pytest.raises(NotImplementedError):
        asyncio.run(_ExecutionClient.generate_mass_status(probe, lookback_mins=15))

    assert probe._generate_mass_status_reconciliation is False
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


def test_templates_remain_classified_as_legacy_migration_only() -> None:
    for name in ("dex_exec_client.py", "dex_data_client.py"):
        path = _LEGACY_TEMPLATES / name
        assert "TEMPLATE_CLASSIFICATION: legacy executable" in path.read_text(encoding="utf-8")
        assert path.parent.name == "legacy_migration"
