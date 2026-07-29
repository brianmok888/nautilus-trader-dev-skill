"""
DEX Adapter Tests: BacktestEngine Integration

Smoke test: wire a DEX adapter-style instrument into BacktestEngine and
verify the engine initialises, runs, and disposes without errors.

This mirrors the integration path described in dex_venue_input.py but
tests only the instrument and venue layer — execution logic is tested
separately in test_dex_compliance.py.

No live chain connection required — all data is in-memory.
"""

from decimal import Decimal
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("nautilus_trader")

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.models import FillModel
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.objects import Money, Price, Quantity

_templates = Path(__file__).parent.parent / "migration_reference" / "python" / "templates"


def _load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, _templates / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_config_mod = _load_module("dex_config")
_provider_mod = _load_module("dex_instrument_provider")
_ob_mod = _load_module("dex_order_book_builder")

MyDEXInstrumentProviderConfig = _config_mod.MyDEXInstrumentProviderConfig
MyDEXInstrumentProvider = _provider_mod.MyDEXInstrumentProvider
amm_spot_price = _ob_mod.amm_spot_price


def _build_dex_instrument():
    config = MyDEXInstrumentProviderConfig(sandbox_mode=True)
    provider = MyDEXInstrumentProvider(config=config)
    provider._load_sandbox_instruments()
    instruments = provider.get_all()
    return next(iter(instruments.values()))


def _build_fill_model():
    return FillModel(
        prob_fill_on_limit=0.25,
        prob_slippage=0.70,
        random_seed=42,
    )


def _run_accepts_dex_instrument_case() -> None:
    dex_instrument = _build_dex_instrument()
    base = dex_instrument.base_currency
    quote = dex_instrument.quote_currency
    engine = BacktestEngine()
    try:
        engine.add_venue(
            venue=dex_instrument.id.venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=None,
            starting_balances=[Money(10_000, quote), Money(10, base)],
            fill_model=_build_fill_model(),
        )
        engine.add_instrument(dex_instrument)
        engine.run()
    finally:
        engine.dispose()


def _run_account_report_case() -> None:
    dex_instrument = _build_dex_instrument()
    base = dex_instrument.base_currency
    quote = dex_instrument.quote_currency
    engine = BacktestEngine()
    try:
        venue = dex_instrument.id.venue
        engine.add_venue(
            venue=venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=None,
            starting_balances=[Money(10_000, quote), Money(10, base)],
        )
        engine.add_instrument(dex_instrument)
        engine.run()

        report = engine.trader.generate_account_report(venue)
        assert report is not None
    finally:
        engine.dispose()


def _run_zero_balance_case() -> None:
    dex_instrument = _build_dex_instrument()
    base = dex_instrument.base_currency
    quote = dex_instrument.quote_currency
    engine = BacktestEngine()
    try:
        engine.add_venue(
            venue=dex_instrument.id.venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=None,
            starting_balances=[Money(10_000, quote), Money(0, base)],
        )
        engine.add_instrument(dex_instrument)
        engine.run()
    finally:
        engine.dispose()


_BACKTEST_CASES = {
    "accepts_dex_instrument": _run_accepts_dex_instrument_case,
    "account_report": _run_account_report_case,
    "zero_balance": _run_zero_balance_case,
}


def _run_backtest_case_in_subprocess(case_name: str) -> None:
    result = subprocess.run(
        [sys.executable, __file__, "--backtest-case", case_name],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, (
        f"BacktestEngine case {case_name!r} failed with exit code "
        f"{result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


@pytest.fixture
def dex_instrument():
    """Synthetic DEX instrument from sandbox provider."""
    return _build_dex_instrument()


@pytest.fixture
def dex_fill_model():
    return _build_fill_model()


class TestDEXBacktestEngineIntegration:
    """Integration smoke tests for DEX adapter + BacktestEngine."""

    def test_engine_accepts_dex_instrument(self, dex_instrument, dex_fill_model):
        """BacktestEngine accepts a DEX instrument without error."""
        _run_backtest_case_in_subprocess("accepts_dex_instrument")

    def test_engine_generates_account_report(self, dex_instrument, dex_fill_model):
        _run_backtest_case_in_subprocess("account_report")

    def test_sandbox_provider_instrument_is_valid(self, dex_instrument):
        """Sandbox provider creates instruments with valid precision/fee fields."""
        assert dex_instrument.price_precision > 0
        assert dex_instrument.size_precision > 0
        assert dex_instrument.maker_fee > Decimal("0")
        assert dex_instrument.min_quantity > Quantity.from_str("0")

    def test_amm_price_rounds_to_instrument_precision(self, dex_instrument):
        """Verify AMM price can be expressed at instrument's price precision."""
        reserve0, reserve1 = 1000.0, 3_000_000.0
        spot = amm_spot_price(reserve0, reserve1)

        # Price should be expressible at the configured precision
        price_str = f"{spot:.{dex_instrument.price_precision}f}"
        price = Price.from_str(price_str)
        assert float(price) > 0

    def test_dex_venue_with_zero_balance_initialises(self, dex_instrument):
        """Engine tolerates DEX venue starting with zero additional token balance."""
        _run_backtest_case_in_subprocess("zero_balance")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--backtest-case":
        _BACKTEST_CASES[sys.argv[2]]()
        raise SystemExit(0)
    raise SystemExit("Usage: test_backtest_integration.py --backtest-case CASE")
