"""
Strategy Builder Tests: Conftest

Shared fixtures for unit and integration tests.
"""

# NT v2 compatibility note: this Python test lane is migration/reference-only
# context; prefer Rust v2/PyO3 guidance and LiveNode for new Rust-backed work.
# Imports target the pinned V2 package-root module set.

import pytest

nautilus_trader = pytest.importorskip("nautilus_trader")
pytest.importorskip(
    "nautilus_trader._libnautilus.common",
    reason="skill tests require the pinned NautilusTrader V2 module set",
)

from decimal import Decimal

from nautilus_trader.backtest import BacktestEngine
from nautilus_trader.backtest import BacktestEngineConfig
from nautilus_trader.execution import DefaultFillModel, FillModel
from nautilus_trader.model import (
    AccountType,
    Currency,
    CurrencyPair,
    InstrumentId,
    Money,
    OmsType,
    Price,
    Quantity,
    Symbol,
    Venue,
)
from nautilus_trader.testkit.providers import TestInstrumentProvider

USDT = Currency.from_str("USDT")
ETH = Currency.from_str("ETH")


# ─── INSTRUMENT FIXTURES ───────────────────────────────────────────────────────


@pytest.fixture
def btcusdt_binance():
    """Standard BTC/USDT instrument on Binance."""
    return TestInstrumentProvider.btcusdt_binance()


@pytest.fixture
def eth_usdc_uniswap():
    """
    Synthetic DEX instrument (WETH/USDC on Uniswap V3).
    Uses CurrencyPair as the closest standard Nautilus instrument type for AMM pools.
    """
    return CurrencyPair(
        instrument_id=InstrumentId(Symbol("WETH-USDC"), Venue("UNISWAP_V3")),
        raw_symbol=Symbol("WETH-USDC"),
        base_currency=ETH,
        quote_currency=USDT,
        price_precision=6,
        size_precision=8,
        price_increment=Price.from_str("0.000001"),
        size_increment=Quantity.from_str("0.00000001"),
        lot_size=None,
        max_quantity=None,
        min_quantity=Quantity.from_str("0.001"),
        max_notional=None,
        min_notional=None,
        max_price=None,
        min_price=None,
        margin_init=Decimal("0"),
        margin_maint=Decimal("0"),
        maker_fee=Decimal("0.003"),  # Uniswap 0.3% pool
        taker_fee=Decimal("0.003"),
        ts_event=0,
        ts_init=0,
    )


# ─── FILL MODEL FIXTURES ───────────────────────────────────────────────────────


@pytest.fixture
def cefi_fill_model():
    """Realistic CeFi fill model."""
    return DefaultFillModel(
        prob_fill_on_limit=0.5,
        prob_slippage=0.2,
        random_seed=42,
    )


@pytest.fixture
def dex_fill_model():
    """Realistic DEX fill model with higher slippage."""
    return DefaultFillModel(
        prob_fill_on_limit=0.25,
        prob_slippage=0.70,
        random_seed=42,
    )


# ─── BACKTEST ENGINE FIXTURES ──────────────────────────────────────────────────


@pytest.fixture
def cefi_engine(btcusdt_binance, cefi_fill_model):
    """BacktestEngine pre-configured with a standard CeFi venue."""
    engine = BacktestEngine(BacktestEngineConfig())
    engine.add_venue(
        venue=Venue("BINANCE"),
        oms_type=OmsType.NETTING,
        account_type=AccountType.CASH,
        base_currency=USDT,
        starting_balances=[Money(10_000, USDT)],
        fill_model=cefi_fill_model,
    )
    engine.add_instrument(btcusdt_binance)
    yield engine
    engine.dispose()


@pytest.fixture
def dex_engine(eth_usdc_uniswap, dex_fill_model):
    """BacktestEngine pre-configured with a DEX venue."""
    engine = BacktestEngine(BacktestEngineConfig())
    engine.add_venue(
        venue=Venue("UNISWAP_V3"),
        oms_type=OmsType.NETTING,
        account_type=AccountType.CASH,
        base_currency=USDT,
        starting_balances=[Money(10_000, USDT)],
        fill_model=dex_fill_model,
    )
    engine.add_instrument(eth_usdc_uniswap)
    yield engine
    engine.dispose()
