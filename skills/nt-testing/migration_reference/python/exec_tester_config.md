# Legacy Python ExecTesterConfig examples

NT v2 compatibility note: legacy Cython/v1 guidance in this file is migration/reference-only; prefer Rust v2/PyO3 for new work.
> Migration/reference-only; not a production default.

```python
from nautilus_trader.testkit import ExecTesterConfig

# Basic execution test
config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.001"),
)

# With specific features
config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.01"),
    enable_limit_buys=True,
)

config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.01"),
    enable_limit_sells=True,
)

config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.01"),
    use_post_only=True,
)

# Current Python V2 execution-test coverage flag exposed by the generated stub
config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.01"),
    limit_aggressive=True,  # marketable limit paths crossing the spread
)

# `test_modify_rejected` and `test_reject_post_only` are Rust builder fields in
# the current source but are not exposed by the generated Python constructor.
```
