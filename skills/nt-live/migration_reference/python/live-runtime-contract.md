# Live runtime contract

> **Migration/reference-only.** This Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-live` skill.

Read `references/developer_guide/contracts/live_runtime_contract.md` before
choosing a live runtime.

NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.

- Use `nautilus_trader.live.LiveNode` for Rust v2 / Rust-backed live-node work.
- NT v2 compatibility note: legacy v1 Python live examples imported
  `nautilus_trader.live.node.TradingNode`; current: that module does not exist at the pinned
  baseline (`live/` ships only `__init__.py`/`__init__.pyi`). Migrate v1 examples to
  `nautilus_trader.live.LiveNode` (builder + `run`/`stop`/`dispose`), labelling any surviving v1
  snippets as Python live or integration-specific history rather than usable defaults.
- Keep reconciliation enabled for production execution clients unless a venue
  limitation is documented and reviewed.

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

### TradingNode Configuration

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

```python
from nautilus_trader.config import (
    LiveExecutionEngineConfig,
    LiveRiskEngineConfig,
)

# NT v2 compatibility note: legacy v1 used TradingNodeConfig with a LoggingConfig-style
# `log_level` and the v1 name `LiveExecEngineConfig`; current: LiveNodeConfig with
# `logging=LoggerConfig(stdout_level=...)` and `LiveExecutionEngineConfig`.

config = LiveNodeConfig(
    trader_id="TRADER-001",
    logging=LoggerConfig(stdout_level="INFO"),
    exec_engine=LiveExecutionEngineConfig(
        reconciliation=True,
        reconciliation_lookback_mins=1440,
    ),
    risk_engine=LiveRiskEngineConfig(
        bypass=False,
        max_order_submit_rate="100/00:00:01",
    ),
)
```

NT v2 compatibility note: legacy v1 also declared `data_clients`/`exec_clients` config dicts on
the node config with per-name factory registration; current: attach adapter clients through
`LiveNodeBuilder.add_data_client` / `add_exec_client` (or the Rust builder equivalents).

### Node Lifecycle

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

```python
# Build node (current: LiveNode.builder(...) ... .build())
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

NT v2 compatibility note: legacy v1 lifecycle shown above; current: `LiveNode` has no separate
`build()` registration step - the builder wires clients, `run()`/`run_async()` runs the event loop,
`handle().stop()` requests graceful shutdown from any thread, and `dispose()` releases resources
after the run task finishes.

### Logging Configuration

NT v2 compatibility note: legacy v1 `LoggingConfig` shown below; current:
`nautilus_trader.common.LoggerConfig` with `stdout_level`/`fileout_level`/
`component_levels`/`is_colored` and file settings via `FileWriterConfig`.

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

NT v2 compatibility note: legacy v1 claimed `INITIALIZED → RUNNING → STOPPED → DISPOSED`;
current: `PRE_INITIALIZED → READY → RUNNING → STOPPED → DISPOSED` with additional `DEGRADED` and
`FAULTED` states (`crates/common/src/enums.rs`).

```python
from nautilus_trader.common.component import Component

# Component states
component.state  # ComponentState enum
component.is_initialized
component.is_running
component.is_stopped
component.is_disposed
```
