"""
Rust-first NautilusTrader v2 exchange adapter template.

Default architecture:
- Rust core owns protocol/domain normalization, WebSocket/HTTP clients, signing,
  order-book state, and request/response models.
- PyO3 exposes a small Python extension package for NautilusTrader integration.
- Python remains the control plane: configuration, factories, and LiveNode wiring.

NT v2 compatibility note: TradingNode/Python-live factories are legacy/reference-only;
do not use them as the default for new adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class RustExchangeCore(Protocol):
    """PyO3 binding boundary implemented by the Rust adapter crate."""

    def load_instruments(self) -> list[Any]: ...

    def start_data(self) -> None: ...

    def stop_data(self) -> None: ...

    def submit_order(self, command: Any) -> Any: ...

    def cancel_order(self, command: Any) -> Any: ...


@dataclass(frozen=True)
class ExchangeAdapterConfig:
    """Python control-plane config passed into the Rust core via PyO3."""

    venue: str
    api_key: str | None = None
    api_secret: str | None = None
    base_url_http: str | None = None
    base_url_ws: str | None = None
    account_type: str = "spot"


class ExchangeInstrumentProvider:
    """Instrument provider delegates discovery/normalization to Rust core."""

    def __init__(self, core: RustExchangeCore) -> None:
        self._core = core

    def load_all(self) -> list[Any]:
        return self._core.load_instruments()


class ExchangeDataClient:
    """Python Nautilus client wrapper around Rust market-data core."""

    def __init__(self, core: RustExchangeCore) -> None:
        self._core = core

    def connect(self) -> None:
        self._core.start_data()

    def disconnect(self) -> None:
        self._core.stop_data()


class ExchangeExecClient:
    """Python Nautilus execution wrapper around Rust order-entry core."""

    def __init__(self, core: RustExchangeCore) -> None:
        self._core = core

    def submit_order(self, command: Any) -> Any:
        return self._core.submit_order(command)

    def cancel_order(self, command: Any) -> Any:
        return self._core.cancel_order(command)


def build_rust_core(config: ExchangeAdapterConfig) -> RustExchangeCore:
    """
    Import the PyO3 module and construct the Rust core.

    Replace `exchange_pyo3.ExchangeCore` with the crate module exported from
    `crates/adapters/<venue>/src/python.rs`.
    """

    from exchange_pyo3 import ExchangeCore  # type: ignore[import-not-found]

    return ExchangeCore(config)


def build_exchange_adapter(config: ExchangeAdapterConfig) -> dict[str, Any]:
    """Build the Python integration layer for a Rust-backed LiveNode."""

    core = build_rust_core(config)
    return {
        "core": core,
        "instrument_provider": ExchangeInstrumentProvider(core),
        "data_client": ExchangeDataClient(core),
        "exec_client": ExchangeExecClient(core),
    }


def wire_livenode(node: Any, config: ExchangeAdapterConfig) -> None:
    """
    Register Rust-backed clients with a LiveNode or equivalent v2 node surface.

    Keep this function thin; adapter behavior belongs in the Rust core and its
    capability-gated DataTester/ExecTester coverage.
    """

    adapter = build_exchange_adapter(config)
    node.add_instrument_provider(config.venue, adapter["instrument_provider"])
    node.add_data_client(config.venue, adapter["data_client"])
    node.add_exec_client(config.venue, adapter["exec_client"])
