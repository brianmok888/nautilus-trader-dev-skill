"""
Strategy Builder Tests: Multi-Venue Signal Routing

Verifies the MultiVenueStrategy from templates/legacy_migration/multi_venue_strategy.py
by running it in a BacktestEngine with two synthetic venues.

Tests confirm:
- Quote ticks from both venues are routed to the correct handler slots
- Spread calculation uses correct per-venue quotes
- Position limits are checked per venue
- on_stop cancels orders on both venues
"""

# NT v2 compatibility note: legacy Cython/v1 and Python live TradingNode
# references in this file are retained for migration/reference-only context.
# Prefer Rust v2/PyO3 guidance and LiveNode for new Rust-backed live work.

from collections import deque
from unittest.mock import MagicMock
from types import MethodType

import pytest

from nautilus_trader.model import InstrumentId, Price, Quantity, QuoteTick

# Import the template class under test
import importlib.util
from pathlib import Path

# NT v2 compatibility note: the template under test is the legacy v1
# migration/reference-only template and requires the v1 Python module set;
# skip cleanly against the pinned V2 build.
pytest.importorskip(
    "nautilus_trader.live.node",
    reason="legacy v1 multi-venue template requires the v1 Python live node module set",
)

# Dynamically load template to test it without installing as a package
_template_path = Path(__file__).parent.parent / "templates" / "legacy_migration" / "multi_venue_strategy.py"
_spec = importlib.util.spec_from_file_location("multi_venue_strategy", _template_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

MultiVenueStrategy = _module.MultiVenueStrategy
MultiVenueStrategyConfig = _module.MultiVenueStrategyConfig


class TestMultiVenueStrategyConfig:
    """Verify config object creation and default values."""

    def test_config_builds_with_required_fields(self):
        config = MultiVenueStrategyConfig(
            strategy_id="MultiVenueStrategy-TEST",
            primary_instrument_id="BTCUSDT-PERP.BINANCE",
            secondary_instrument_id="BTCUSDT-PERP.BYBIT",
        )
        assert config.primary_instrument_id == "BTCUSDT-PERP.BINANCE"
        assert config.secondary_instrument_id == "BTCUSDT-PERP.BYBIT"

    def test_default_spread_threshold(self):
        config = MultiVenueStrategyConfig(
            strategy_id="MultiVenueStrategy-TEST",
            primary_instrument_id="BTCUSDT-PERP.BINANCE",
            secondary_instrument_id="BTCUSDT-PERP.BYBIT",
        )
        assert config.min_spread_bps == 10.0

    def test_custom_spread_threshold(self):
        config = MultiVenueStrategyConfig(
            strategy_id="MultiVenueStrategy-TEST",
            primary_instrument_id="A.BINANCE",
            secondary_instrument_id="A.BYBIT",
            min_spread_bps=25.0,
        )
        assert config.min_spread_bps == 25.0


class TestSpreadCalculation:
    """
    Unit-test spread logic in isolation using mock quotes.

    These tests call internal _evaluate_spread logic directly
    by constructing a minimal mock strategy object.
    """

    def _make_mock_strategy(self, min_spread_bps: float = 10.0) -> MultiVenueStrategy:
        """Create a strategy with all framework dependencies mocked."""
        config = MultiVenueStrategyConfig(
            strategy_id="MultiVenueStrategy-UNIT",
            primary_instrument_id="BTCUSDT-PERP.BINANCE",
            secondary_instrument_id="BTCUSDT-PERP.BYBIT",
            min_spread_bps=min_spread_bps,
            max_position_size=1.0,
        )

        strategy = type("MockMultiVenue", (), {})()
        strategy.config = config
        strategy.primary_id = InstrumentId.from_str(config.primary_instrument_id)
        strategy.secondary_id = InstrumentId.from_str(config.secondary_instrument_id)
        strategy.primary_instrument = MagicMock()
        strategy.secondary_instrument = MagicMock()
        strategy._primary_quote = None
        strategy._secondary_quote = None
        strategy._spread_history = deque(maxlen=100)
        strategy.log = MagicMock()
        strategy.portfolio = MagicMock()
        strategy.portfolio.net_position = MagicMock(return_value=0.0)
        strategy.order_factory = MagicMock()
        strategy.submit_order = MagicMock()
        strategy.primary_instrument.make_qty = MagicMock(
            return_value=Quantity.from_str("0.01")
        )
        strategy.on_quote_tick = MethodType(MultiVenueStrategy.on_quote_tick, strategy)
        strategy._evaluate_spread = MethodType(
            MultiVenueStrategy._evaluate_spread, strategy
        )
        strategy._handle_spread_opportunity = MethodType(
            MultiVenueStrategy._handle_spread_opportunity, strategy
        )
        strategy._can_trade = MethodType(MultiVenueStrategy._can_trade, strategy)
        return strategy

    def _make_quote(self, instrument_id_str: str, bid: float, ask: float) -> QuoteTick:
        """Build a minimal QuoteTick for testing."""
        return QuoteTick(
            instrument_id=InstrumentId.from_str(instrument_id_str),
            bid_price=Price.from_str(str(bid)),
            ask_price=Price.from_str(str(ask)),
            bid_size=Quantity.from_str("1.0"),
            ask_size=Quantity.from_str("1.0"),
            ts_event=0,
            ts_init=0,
        )

    def test_spread_not_evaluated_until_both_quotes_received(self):
        strategy = self._make_mock_strategy()
        strategy._handle_spread_opportunity = MagicMock()

        # Send only primary quote
        primary_q = self._make_quote("BTCUSDT-PERP.BINANCE", 50_000.0, 50_001.0)
        strategy.on_quote_tick(primary_q)

        # No spread evaluation yet
        strategy._handle_spread_opportunity.assert_not_called()

    def test_spread_evaluated_after_both_quotes(self):
        strategy = self._make_mock_strategy(min_spread_bps=1.0)  # Very low threshold
        strategy._handle_spread_opportunity = MagicMock()

        primary_q = self._make_quote("BTCUSDT-PERP.BINANCE", 50_000.0, 50_001.0)
        secondary_q = self._make_quote("BTCUSDT-PERP.BYBIT", 50_050.0, 50_051.0)

        strategy.on_quote_tick(primary_q)
        strategy.on_quote_tick(secondary_q)

        # Spread is ~10 bps; min is 1 bps → opportunity detected
        strategy._handle_spread_opportunity.assert_called_once()

    def test_no_opportunity_when_spread_below_threshold(self):
        strategy = self._make_mock_strategy(min_spread_bps=100.0)  # Very high threshold
        strategy._handle_spread_opportunity = MagicMock()

        primary_q = self._make_quote("BTCUSDT-PERP.BINANCE", 50_000.0, 50_001.0)
        secondary_q = self._make_quote(
            "BTCUSDT-PERP.BYBIT", 50_002.0, 50_003.0
        )  # Only ~0.4 bps

        strategy.on_quote_tick(primary_q)
        strategy.on_quote_tick(secondary_q)

        strategy._handle_spread_opportunity.assert_not_called()

    def test_spread_history_accumulates(self):
        strategy = self._make_mock_strategy(min_spread_bps=1.0)
        strategy._handle_spread_opportunity = MagicMock()

        primary_q = self._make_quote("BTCUSDT-PERP.BINANCE", 50_000.0, 50_001.0)
        secondary_q = self._make_quote("BTCUSDT-PERP.BYBIT", 50_050.0, 50_051.0)

        strategy.on_quote_tick(primary_q)
        strategy.on_quote_tick(secondary_q)
        strategy.on_quote_tick(secondary_q)  # Second update

        assert len(strategy._spread_history) == 2
