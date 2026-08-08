# Live runtime contract

> **Migration/reference-only.** This Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-live` skill. The only active Python lane is AI/advisory work
> outside this repository.


Read `references/developer_guide/contracts/live_runtime_contract.md` before
choosing a live runtime.

NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.

- Use `nautilus_trader.live.LiveNode` for Rust v2 / Rust-backed live-node work.
- Python live connectivity examples may still use
  `nautilus_trader.live.node.TradingNode`; label those examples as Python live
  or integration-specific rather than universal defaults.
- Keep reconciliation enabled for production execution clients unless a venue
  limitation is documented and reviewed.

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

### TradingNode Configuration

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

```python
from nautilus_trader.live.node import TradingNode
from nautilus_trader.config import TradingNodeConfig, LiveExecEngineConfig, LiveRiskEngineConfig

# NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

config = TradingNodeConfig(
    trader_id="TRADER-001",
    log_level="INFO",
    exec_engine=LiveExecEngineConfig(
        reconciliation=True,
        reconciliation_lookback_mins=1440,
    ),
    risk_engine=LiveRiskEngineConfig(
        bypass=False,
        max_order_submit_rate="100/00:00:01",
    ),
    data_clients={
        "BINANCE": BinanceDataClientConfig(...),
    },
    exec_clients={
        "BINANCE": BinanceExecClientConfig(...),
    },
)


node = TradingNode(config=config)
```

### Node Lifecycle

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

```python
# Build node
node = TradingNode(config=config)

# Add strategies
node.trader.add_strategy(my_strategy)

# Build (connects adapters, initializes components)
node.build()

# Run (starts event loop)
node.run()

# Stop (graceful shutdown)
node.stop()

# Dispose (cleanup resources)
node.dispose()
```

### Logging Configuration

```python
from nautilus_trader.config import LoggingConfig

logging_config = LoggingConfig(
    log_level="INFO",
    log_level_file="DEBUG",
    log_directory="/var/log/nautilus/",
    log_file_format="{trader_id}_{instance_id}",
    log_colors=True,
)
```

### Clock & Timers

```python
# In Strategy/Actor:
self.clock.set_timer(
    name="my_timer",
    interval=timedelta(seconds=60),
    callback=self.on_timer,
)

# Cancel timer
self.clock.cancel_timer("my_timer")

# Check active timers
active = self.clock.timer_names
```

### Component Lifecycle

All components follow: `INITIALIZED → RUNNING → STOPPED → DISPOSED`

```python
from nautilus_trader.common.component import Component

# Component states
component.state  # ComponentState enum
component.is_initialized
component.is_running
component.is_stopped
component.is_disposed
```
