# Python Usage

> **Migration/reference-only.** This Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-backtest` skill.


### BacktestNode (Recommended)

`BacktestNode` is the high-level API for running backtests with configuration:

```python
from nautilus_trader.backtest import BacktestNode
from nautilus_trader.config import (
    BacktestRunConfig,
    BacktestDataConfig,
    BacktestVenueConfig,
    BacktestEngineConfig,
    ImportableStrategyConfig,
)
from nautilus_trader.model import BarAggregation, BarSpecification, PriceType

config = BacktestRunConfig(
    engine=BacktestEngineConfig(),
    data=[
        BacktestDataConfig(
            catalog_path="/path/to/data",
            data_type="Bar",
            instrument_id="ETHUSDT-PERP.BINANCE",
            bar_spec=BarSpecification(1, BarAggregation.MINUTE, PriceType.LAST),
        ),
    ],
    venues=[
        BacktestVenueConfig(
            name="BINANCE",
            oms_type="NETTING",
            account_type="MARGIN",
            base_currency=None,
            starting_balances=["10_000 USDT"],
        ),
    ],
)

# v1 migration note: data used `data_cls="nautilus_trader.model.data:Bar"` with a
# `bar_type=` string; the pinned config takes `data_type` plus `bar_spec`/`bar_types`.

node = BacktestNode(configs=[config])
node.build()
node.add_strategy_from_config(
    config.id,
    ImportableStrategyConfig(
        strategy_path="my_module:MyStrategy",
        config={"instrument_id": "ETHUSDT-PERP.BINANCE", ...},
    ),
)
results = node.run()
```

### BacktestEngine (Direct API)

`BacktestEngine` provides lower-level control, useful for strategy testing:

```python
from nautilus_trader.backtest import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig

engine = BacktestEngine(config=BacktestEngineConfig())

# Add venue
engine.add_venue(
    venue=Venue("SIM"),
    oms_type=OmsType.HEDGING,
    account_type=AccountType.MARGIN,
    base_currency=USD,
    starting_balances=[Money(1_000_000, USD)],
)

# Add data
engine.add_data(bars)
engine.add_instrument(instrument)

# Add strategy
engine.add_strategy(strategy)

# Run
engine.run()

# Get results
engine.trader.generate_order_fills_report()
engine.trader.generate_positions_report()
```

### Venue Configuration

```python
BacktestVenueConfig(
    name="SIM",
    oms_type="HEDGING",  # HEDGING or NETTING
    account_type="MARGIN",  # CASH or MARGIN
    base_currency="USD",
    starting_balances=["1_000_000 USD"],
    fill_model=FillModel(),  # Optional custom fill model
    # latency_model=LatencyModel(), # Optional latency simulation
)
```
