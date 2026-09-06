# TEMPLATE_CLASSIFICATION: migration/reference-only; not a production default
# -------------------------------------------------------------------------------------------------
#  NautilusTrader FillModel Template
#
#  Subclass FillModel to customize how simulated orders are filled in backtests.
#  Controls fill probability, slippage, and order book simulation.
#
#  Built-in models: BestPriceFillModel, OneTickSlippageFillModel, TwoTierFillModel,
#  ThreeTierFillModel, ProbabilisticFillModel, SizeAwareFillModel, etc.
#
#  v2 note: the Python FillModel.__init__() takes no arguments. Probabilistic
#  parameters live on the built-in models (DefaultFillModel, ProbabilisticFillModel,
#  ...); a custom subclass stores its own parameters and implements the
#  custom-object protocol: is_limit_filled(), is_slipped(), and optionally
#  fill_limit_inside_spread() and get_orderbook_for_fill_simulation().
# -------------------------------------------------------------------------------------------------

import random

from nautilus_trader.execution import FillModel
from nautilus_trader.model import OrderBook, Price

class MyFillModel(FillModel):
    """
    TODO: Describe custom fill model behavior.

    Parameters
    ----------
    prob_fill_on_limit : float, default 1.0
        Probability of limit orders filling at limit price (0.0-1.0).
    prob_slippage : float, default 0.0
        Probability of aggressive order execution slipping (0.0-1.0).
    random_seed : int, optional
        Random seed for reproducibility.
    """

    def __init__(
        self,
        prob_fill_on_limit: float = 1.0,
        prob_slippage: float = 0.0,
        random_seed: int | None = None,
    ):
        super().__init__()  # base FillModel takes no arguments
        self.prob_fill_on_limit = prob_fill_on_limit
        self.prob_slippage = prob_slippage
        self._rng = random.Random(random_seed)
        # TODO: Initialize custom model parameters

    def is_limit_filled(self) -> bool:
        """Whether a limit order fills when its price level is touched."""
        return self._rng.random() < self.prob_fill_on_limit

    def is_slipped(self) -> bool:
        """Whether an order fill slips by one tick."""
        return self._rng.random() < self.prob_slippage

    def fill_limit_inside_spread(self) -> bool:
        """
        Whether limit orders at/inside the spread can fill.

        Return True if your model provides liquidity inside bid-ask spread.
        Default False: limit orders only fill when price crosses them.
        """
        return False

    def get_orderbook_for_fill_simulation(
        self,
        instrument,
        order,
        best_bid: Price,
        best_ask: Price,
    ) -> OrderBook | None:
        """
        Return a simulated OrderBook for fill simulation.

        This is the primary extension point. Return:
        - OrderBook: custom liquidity levels to define fill prices/sizes
        - None: use default fill logic (prob_fill_on_limit, prob_slippage)

        Parameters
        ----------
        instrument :
            The instrument being traded.
        order :
            The order to simulate fills for.
        best_bid : Price
            Current best bid price.
        best_ask : Price
            Current best ask price.

        Returns
        -------
        OrderBook or None
            Custom simulated order book, or None for default behavior.
        """
        # TODO: Implement custom fill simulation logic
        #
        # Example: create a synthetic order book with custom liquidity:
        #   from nautilus_trader.model import BookOrder, BookType, OrderSide
        #   book = OrderBook(instrument.id, BookType.L2_MBP)
        #   book.add(BookOrder(OrderSide.BUY, best_bid, size_1, 1), 0, 0, 0)
        #   book.add(BookOrder(OrderSide.SELL, best_ask, size_2, 2), 0, 0, 0)
        #   return book
        return None  # Use default fill behavior

# Usage in backtest config:
#
# BacktestVenueConfig(
#     name="SIM",
#     oms_type="NETTING",
#     account_type="MARGIN",
#     base_currency="USD",
#     starting_balances=["1_000_000 USD"],
#     fill_model=MyFillModel(prob_fill_on_limit=0.95, prob_slippage=0.1, random_seed=42),
# )
#
# LatencyModel (built-in, no subclass needed):
#
# from nautilus_trader.execution import StaticLatencyModel
#
# latency = StaticLatencyModel(
#     base_latency_nanos=1_000_000,     # 1ms base
#     insert_latency_nanos=5_000_000,   # 5ms for new orders
#     update_latency_nanos=2_000_000,   # 2ms for modifications
#     cancel_latency_nanos=1_000_000,   # 1ms for cancellations
# )
