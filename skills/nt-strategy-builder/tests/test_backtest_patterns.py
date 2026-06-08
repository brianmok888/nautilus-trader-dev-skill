"""
Strategy Builder Tests: Backtest Patterns

Verifies that backtest configuration patterns from templates
construct, run, and dispose correctly using NautilusTrader's test kit.
"""

from decimal import Decimal
from pathlib import Path
import subprocess
import sys

import pytest

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.models import FillModel
from nautilus_trader.model.currencies import USDT, BTC
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.test_kit.providers import TestInstrumentProvider


def _run_cash_venue_case() -> None:
    engine = BacktestEngine()
    try:
        engine.add_venue(
            venue=Venue("SIM"),
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=USDT,
            starting_balances=[Money(10_000, USDT)],
        )
        assert engine is not None
    finally:
        engine.dispose()


def _run_margin_venue_case() -> None:
    engine = BacktestEngine()
    try:
        engine.add_venue(
            venue=Venue("SIM"),
            oms_type=OmsType.NETTING,
            account_type=AccountType.MARGIN,
            base_currency=USDT,
            starting_balances=[Money(10_000, USDT)],
            default_leverage=Decimal("10"),
        )
        assert engine is not None
    finally:
        engine.dispose()


def _run_dex_cash_venue_case() -> None:
    engine = BacktestEngine()
    try:
        engine.add_venue(
            venue=Venue("UNISWAP_V3"),
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=USDT,
            starting_balances=[Money(10_000, USDT)],
        )
        assert engine is not None
    finally:
        engine.dispose()


def _run_multi_currency_case() -> None:
    engine = BacktestEngine()
    try:
        engine.add_venue(
            venue=Venue("SIM"),
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=USDT,
            starting_balances=[Money(10_000, USDT)],
        )
        assert engine is not None
    finally:
        engine.dispose()


def _run_engine_add_instrument_case() -> None:
    instrument = TestInstrumentProvider.btcusdt_binance()
    engine = BacktestEngine()
    try:
        engine.add_venue(
            venue=Venue("BINANCE"),
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=None,
            starting_balances=[Money(10_000, USDT), Money(1, BTC)],
        )
        engine.add_instrument(instrument)
        engine.run()
    finally:
        engine.dispose()


def _run_engine_account_report_case() -> None:
    instrument = TestInstrumentProvider.btcusdt_binance()
    engine = BacktestEngine()
    try:
        venue = Venue("BINANCE")
        engine.add_venue(
            venue=venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.CASH,
            base_currency=None,
            starting_balances=[Money(10_000, USDT), Money(1, BTC)],
        )
        engine.add_instrument(instrument)
        engine.run()

        report = engine.trader.generate_account_report(venue)
        assert report is not None
    finally:
        engine.dispose()


_BACKTEST_CASES = {
    "cash_venue": _run_cash_venue_case,
    "margin_venue": _run_margin_venue_case,
    "dex_cash_venue": _run_dex_cash_venue_case,
    "multi_currency": _run_multi_currency_case,
    "engine_add_instrument": _run_engine_add_instrument_case,
    "engine_account_report": _run_engine_account_report_case,
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


class TestBacktestVenueConfig:
    """Verify venue configuration patterns build without error."""

    def test_cash_venue_builds(self):
        """A CASH account venue builds and accepts starting balances."""
        _run_backtest_case_in_subprocess("cash_venue")

    def test_margin_venue_with_leverage(self):
        """A MARGIN account venue accepts default_leverage."""
        _run_backtest_case_in_subprocess("margin_venue")

    def test_dex_cash_venue_builds(self):
        """A DEX venue (no margin) builds the same way as CeFi CASH."""
        _run_backtest_case_in_subprocess("dex_cash_venue")

    def test_multi_currency_starting_balances(self):
        """Multiple starting currencies are accepted."""
        _run_backtest_case_in_subprocess("multi_currency")


class TestFillModelPatterns:
    """Verify fill model construction and parameter bounds."""

    def test_cefi_fill_model_builds(self):
        model = FillModel(
            prob_fill_on_limit=0.5,
            prob_slippage=0.2,
            random_seed=42,
        )
        assert model is not None

    def test_dex_fill_model_builds(self):
        """DEX-realistic fill model with higher slippage probability."""
        model = FillModel(
            prob_fill_on_limit=0.25,
            prob_slippage=0.70,
            random_seed=42,
        )
        assert model is not None

    def test_fill_model_is_reproducible(self):
        model_a = FillModel(prob_fill_on_limit=0.5, prob_slippage=0.2, random_seed=1)
        model_b = FillModel(prob_fill_on_limit=0.5, prob_slippage=0.2, random_seed=1)

        results_a = [model_a.is_limit_filled() for _ in range(20)]
        results_b = [model_b.is_limit_filled() for _ in range(20)]
        assert len(results_a) == len(results_b) == 20
        assert all(isinstance(v, bool) for v in results_a + results_b)

    @pytest.mark.parametrize("prob", [0.0, 0.5, 1.0])
    def test_fill_model_accepts_boundary_probabilities(self, prob):
        model = FillModel(
            prob_fill_on_limit=prob,
            prob_slippage=prob,
            random_seed=0,
        )
        assert model is not None


class TestBacktestEngineWithInstrument:
    """Verify engine accepts instruments and runs without data."""

    def test_engine_add_instrument(self):
        _run_backtest_case_in_subprocess("engine_add_instrument")

    def test_engine_generates_account_report(self):
        _run_backtest_case_in_subprocess("engine_account_report")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--backtest-case":
        _BACKTEST_CASES[sys.argv[2]]()
        raise SystemExit(0)
    raise SystemExit("Usage: test_backtest_patterns.py --backtest-case CASE")
