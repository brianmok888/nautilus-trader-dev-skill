# Custom Simulation Models

> **Migration/reference-only.** This Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-implement` skill. The only active Python lane is AI/advisory work
> outside this repository.


### Custom FillModel

Implement custom fill simulation for backtesting. Controls order queue position and execution probability.

```python
from decimal import Decimal
from nautilus_trader.backtest.models import FillModel
from nautilus_trader.model.orders import Order
from nautilus_trader.model.instruments import Instrument

class VolatilityAdjustedFillModel(FillModel):
    """
    Fill model that adjusts probabilities based on market volatility.

    Parameters
    ----------
    base_prob_fill_on_limit : float
        Base probability for limit order fills.
    base_prob_slippage : float
        Base probability for slippage on market orders.
    volatility_multiplier : float
        Multiplier applied based on volatility regime.
    random_seed : int, optional
        Seed for reproducible results.
    """

    def __init__(
        self,
        base_prob_fill_on_limit: float = 0.5,
        base_prob_slippage: float = 0.3,
        volatility_multiplier: float = 1.5,
        random_seed: int | None = None,
    ) -> None:
        super().__init__(
            prob_fill_on_limit=base_prob_fill_on_limit,
            # prob_fill_on_stop is deprecated in v1.223.0; use prob_slippage
            prob_slippage=base_prob_slippage,
            random_seed=random_seed,
        )
        self._volatility_multiplier = volatility_multiplier
        self._current_volatility = 1.0  # Updated externally

    def set_volatility(self, volatility: float) -> None:
        """Update current volatility regime."""
        self._current_volatility = volatility

    def is_limit_filled(self) -> bool:
        """Check if limit order fills based on volatility-adjusted probability."""
        # Higher volatility = more likely to get filled (more price movement)
        adjusted_prob = min(1.0, self.prob_fill_on_limit * self._current_volatility)
        return self._random.random() < adjusted_prob

    def is_slipped(self) -> bool:
        """Check if slippage occurs based on volatility-adjusted probability."""
        # Higher volatility = more likely slippage
        adjusted_prob = min(1.0, self.prob_slippage * self._current_volatility * self._volatility_multiplier)
        return self._random.random() < adjusted_prob
```

**Usage in backtest:**

```python
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.config import BacktestEngineConfig

fill_model = VolatilityAdjustedFillModel(
    base_prob_fill_on_limit=0.3,
    base_prob_slippage=0.2,
    volatility_multiplier=1.5,
    random_seed=42,
)

engine = BacktestEngine(
    config=BacktestEngineConfig(
        trader_id="TESTER-001",
        fill_model=fill_model,
    )
)
```

### Custom MarginModel

Implement custom margin calculation for different venue types.

```python
from decimal import Decimal
from nautilus_trader.backtest.models import MarginModel
from nautilus_trader.backtest.config import MarginModelConfig
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Money, Quantity, Price
from nautilus_trader.model.enums import PositionSide

class RiskAdjustedMarginModel(MarginModel):
    """
    Margin model that applies risk multipliers based on instrument characteristics.

    Receives configuration through MarginModelConfig.config dict:
    - risk_multiplier: float - Base risk multiplier (default 1.0)
    - use_leverage: bool - Whether to divide by leverage (default False)
    - volatility_buffer: float - Additional buffer for volatile instruments (default 0.0)
    """

    def __init__(self, config: MarginModelConfig) -> None:
        """Initialize with configuration parameters."""
        self.risk_multiplier = Decimal(str(config.config.get("risk_multiplier", 1.0)))
        self.use_leverage = config.config.get("use_leverage", False)
        self.volatility_buffer = Decimal(str(config.config.get("volatility_buffer", 0.0)))

    def calculate_margin_init(
        self,
        instrument: Instrument,
        quantity: Quantity,
        price: Price,
        leverage: Decimal,
        use_quote_for_inverse: bool = False,
    ) -> Money:
        """
        Calculate initial margin for order submission.

        Parameters
        ----------
        instrument : Instrument
            The instrument for the calculation.
        quantity : Quantity
            The order quantity.
        price : Price
            The order price.
        leverage : Decimal
            The account leverage.
        use_quote_for_inverse : bool
            Use quote currency for inverse instruments.

        Returns
        -------
        Money
            The initial margin requirement.
        """
        notional = instrument.notional_value(quantity, price, use_quote_for_inverse)

        if self.use_leverage and leverage > 0:
            adjusted_notional = notional.as_decimal() / leverage
        else:
            adjusted_notional = notional.as_decimal()

        # Apply instrument margin requirement with risk adjustments
        margin = adjusted_notional * instrument.margin_init * self.risk_multiplier
        margin += adjusted_notional * self.volatility_buffer  # Add volatility buffer

        return Money(margin, instrument.quote_currency)

    def calculate_margin_maint(
        self,
        instrument: Instrument,
        side: PositionSide,
        quantity: Quantity,
        price: Price,
        leverage: Decimal,
        use_quote_for_inverse: bool = False,
    ) -> Money:
        """Calculate maintenance margin for open positions."""
        notional = instrument.notional_value(quantity, price, use_quote_for_inverse)

        if self.use_leverage and leverage > 0:
            adjusted_notional = notional.as_decimal() / leverage
        else:
            adjusted_notional = notional.as_decimal()

        margin = adjusted_notional * instrument.margin_maint * self.risk_multiplier

        return Money(margin, instrument.quote_currency)
```

**Usage in backtest config:**

```python
from nautilus_trader.backtest.config import BacktestVenueConfig, MarginModelConfig

venue_config = BacktestVenueConfig(
    name="SIM",
    oms_type="NETTING",
    account_type="MARGIN",
    starting_balances=["1_000_000 USD"],
    margin_model=MarginModelConfig(
        model_type="my_package.my_module:RiskAdjustedMarginModel",
        config={
            "risk_multiplier": 1.5,
            "use_leverage": False,
            "volatility_buffer": 0.02,
        },
    ),
)
```

### Custom PortfolioStatistic

Implement custom portfolio statistics for analysis.

```python
from decimal import Decimal
from nautilus_trader.analysis.statistic import PortfolioStatistic
from nautilus_trader.model.position import Position
from nautilus_trader.model.orders import Order

class WinStreakStatistic(PortfolioStatistic):
    """Calculate maximum winning and losing streaks."""

    def __init__(self) -> None:
        super().__init__()
        self._name = "Win Streak"

    @property
    def name(self) -> str:
        return self._name

    def calculate_from_orders(self, orders: list[Order]) -> dict[str, int]:
        """
        Calculate win/loss streaks from filled orders.

        Returns
        -------
        dict[str, int]
            Dictionary with max_win_streak and max_loss_streak.
        """
        # Implementation for order-based calculation
        return {"max_win_streak": 0, "max_loss_streak": 0}

    def calculate_from_positions(self, positions: list[Position]) -> dict[str, int]:
        """
        Calculate win/loss streaks from closed positions.

        Returns
        -------
        dict[str, int]
            Dictionary with max_win_streak and max_loss_streak.
        """
        if not positions:
            return {"max_win_streak": 0, "max_loss_streak": 0}

        max_win_streak = 0
        max_loss_streak = 0
        current_win_streak = 0
        current_loss_streak = 0

        for position in positions:
            if not position.is_closed:
                continue

            realized_pnl = position.realized_pnl
            if realized_pnl is None:
                continue

            if float(realized_pnl) > 0:
                current_win_streak += 1
                current_loss_streak = 0
                max_win_streak = max(max_win_streak, current_win_streak)
            else:
                current_loss_streak += 1
                current_win_streak = 0
                max_loss_streak = max(max_loss_streak, current_loss_streak)

        return {
            "max_win_streak": max_win_streak,
            "max_loss_streak": max_loss_streak,
        }


class RiskAdjustedReturnStatistic(PortfolioStatistic):
    """Calculate risk-adjusted return metrics."""

    def __init__(self, risk_free_rate: float = 0.0) -> None:
        super().__init__()
        self._name = "Risk Adjusted Return"
        self._risk_free_rate = risk_free_rate

    @property
    def name(self) -> str:
        return self._name

    def calculate_from_positions(self, positions: list[Position]) -> dict[str, float]:
        """
        Calculate Sharpe-like ratio from positions.

        Returns
        -------
        dict[str, float]
            Dictionary with avg_return, volatility, and sharpe_ratio.
        """
        import numpy as np

        returns = []
        for position in positions:
            if position.is_closed and position.realized_pnl is not None:
                # Simplified: use PnL as return proxy
                returns.append(float(position.realized_pnl))

        if len(returns) < 2:
            return {"avg_return": 0.0, "volatility": 0.0, "sharpe_ratio": 0.0}

        avg_return = np.mean(returns)
        volatility = np.std(returns)

        if volatility == 0:
            sharpe_ratio = 0.0
        else:
            sharpe_ratio = (avg_return - self._risk_free_rate) / volatility

        return {
            "avg_return": float(avg_return),
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe_ratio),
        }
```

**Usage with PortfolioAnalyzer:**

```python
from nautilus_trader.analysis.analyzer import PortfolioAnalyzer

analyzer = PortfolioAnalyzer()

# Register custom statistics
analyzer.register_statistic(WinStreakStatistic())
analyzer.register_statistic(RiskAdjustedReturnStatistic(risk_free_rate=0.02))

# Calculate after backtest
results = engine.run()
analyzer.calculate_statistics(positions=results.positions)
```
