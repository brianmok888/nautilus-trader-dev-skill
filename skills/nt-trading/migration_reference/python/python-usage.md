# Python Usage

> **Migration/reference-only.** This Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-trading` skill.


### Strategy

Subclass `Strategy` from `nautilus_trader.trading.strategy`:

```python
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.config import StrategyConfig

class MyStrategyConfig(StrategyConfig, frozen=True):
    instrument_id: str = None
    bar_type: str = None

class MyStrategy(Strategy):
    def __init__(self, config: MyStrategyConfig):
        super().__init__(config)
        # Store config, initialize state

    def on_start(self):
        # Subscribe to data, register indicators
        self.subscribe_bars(self.bar_type)

    def on_bar(self, bar):
        # Core trading logic
        pass

    def on_quote_tick(self, tick):
        pass

    def on_trade_tick(self, tick):
        pass

    def on_order_filled(self, event):
        # Post-fill logic
        pass

    def on_position_changed(self, event):
        pass

    def on_stop(self):
        # Cleanup
        pass
```

**Key order methods** (inherited from `Actor` → `Strategy`):
- `self.submit_order(order)` — submit to execution
- `self.cancel_order(order)` — cancel open order
- `self.modify_order(order, quantity=None, price=None, trigger_price=None)` — modify open order
- `self.cancel_all_orders(instrument_id)` — cancel all for instrument
- `self.close_position(position)` — close position with market order
- `self.close_all_positions(instrument_id)` — close all for instrument

**Order creation** (via `OrderFactory` on `self.order_factory`):
- `self.order_factory.market(instrument_id, side, quantity)`
- `self.order_factory.limit(instrument_id, side, quantity, price)`
- `self.order_factory.stop_market(instrument_id, side, quantity, trigger_price)`
- `self.order_factory.stop_limit(instrument_id, side, quantity, price, trigger_price)`
- `self.order_factory.trailing_stop_market(instrument_id, side, quantity, trailing_offset, ...)`

### Actor

Subclass `Actor` from `nautilus_trader.trading.actor` for non-trading components (data processing, signal publishing, monitoring):

```python
from nautilus_trader.trading.actor import Actor
from nautilus_trader.config import ActorConfig

class MyActor(Actor):
    def __init__(self, config: ActorConfig):
        super().__init__(config)

    def on_start(self):
        self.subscribe_data(...)

    def on_bar(self, bar):
        # Process data, publish signals via msgbus
        self.publish_signal(name="my_signal", value=signal_value)
```

### Risk & Execution Configuration

```python
from nautilus_trader.config import ExecEngineConfig, RiskEngineConfig

exec_config = ExecEngineConfig(
    load_cache=True,
    allow_cash_positions=True,
)

risk_config = RiskEngineConfig(
    bypass=False,
    max_order_submit_rate="100/00:00:01",  # 100 per second
    max_order_modify_rate="100/00:00:01",
    max_notional_per_order={"GBP/USD.SIM": 1_000_000},
)
```
