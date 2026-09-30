# Portfolio Example

A simple strategy demonstrating how to use Portfolio in NautilusTrader.

The Portfolio is a central component that tracks the state of your trading account.
It derives account, position, and P&L views from the engine cache and event updates;
these queries do not connect directly to a broker.

## Example Highlights

The strategy shows portfolio information at four key points:

1. **Initial State**: Before any trades are executed.
2. **Position Open**: When a new position is created.
3. **Mid-Trade**: Two minutes after position opening.
4. **Final State**: After all positions are closed (when strategy stops).

To simulate these specific portfolio states, the strategy fires bracket order (a combination of an entry order
with associated take-profit and stop-loss orders), allowing us to demonstrate the complete lifecycle of portfolio states.

## User-defined portfolio statistics

Drift-window addition (upstream commit `7e8c9c9cd`): `Portfolio.register_statistic()` accepts a
user-defined statistic built on the `PortfolioStatistic` base class
(`python/nautilus_trader/analysis/statistic.py` at the pin). This example registers one in the
strategy's `on_start()` so it reaches backtest results and post-run logs for the whole run:

```python
from nautilus_trader.analysis import PortfolioStatistic

class TradeCount(PortfolioStatistic):
    def calculate_from_realized_pnls(self, realized_pnls: list[float]) -> float | None:
        return float(len(realized_pnls))

# In DemoStrategy.on_start():
self.portfolio.register_statistic(TradeCount())
```

The statistic name defaults to the class name split on word boundaries (`TradeCount` registers as
"Trade Count"); override the `name` property to choose it directly. A registration whose name
matches an existing statistic replaces it, and `Portfolio.deregister_statistic()` removes one by
name.

## Additional info

Key differences between `Portfolio` and `Cache`:

`Portfolio`:

- Calculates account, P&L, exposure, and margin views from cached state.
- Receives account, order, and position updates through the engine message bus.
- Does not perform a broker request for each query.

`Cache`:

- Stores all trading data in system memory.
- Useful for quick access to historical data and market state.
- Provides direct access to cached objects; portfolio queries also use this cache.
- Updates automatically as new data arrives.
- Reflects events processed by the engine, not a separate broker-freshness guarantee.

## Additional Resources

For more information about Portfolio in NautilusTrader, see:

- Portfolio API documentation - search the codebase for `Portfolio` class.
- Portfolio concept guide - see the "Portfolio" section in the documentation for more details.
