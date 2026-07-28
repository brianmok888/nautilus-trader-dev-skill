---
name: nt-live
description: "Use when working with live trading nodes, system boot, NautilusKernel, engine configuration, component lifecycle, or deployment in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-live

## V2 callback and nightly migration hardening

NT v2 compatibility note: Python live/integration-specific TradingNode examples in this section are migration/reference-only; use LiveNode for Rust v2/Rust-backed work.

- Python callback rule: no `Python::attach` from Tokio worker tasks. Worker tasks must not acquire the GIL directly to call Python strategy, actor, execution-algorithm, or adapter callbacks; route work onto live runner channels and let the live runner drain/dispatch those channels.
- For Python-facing live V2 work, prefer `LiveNode`/PyO3 paths. Treat Python `TradingNode` examples as legacy/reference-only unless a guide explicitly labels them current Python-only integration guidance.
- `ExecutionEngineConfig.carry_replay_events_on_reopen` carries replay state across NETTING close/reopen cycles; keep reconciliation/restart tests for close/reopen sequences.
- `PortfolioConfig.use_mark_prices` defaults to `true`; set `false` only when a test or deployment intentionally excludes mark-price valuation.
- `RedisMessageBusBacking` is the current Python V2 Redis message-bus backing name.
- SQL/catalog migration: regenerate or migrate persisted SQL/catalog state before in-place V2 upgrades and smoke replay after migration.
- deferred V2 limits must be documented as explicit live-readiness gaps, not silently accepted.
- shared adapter task tracking, when upstream support exists for the adapter, must track spawned tasks through terminal events and abort outstanding tasks during stop/drop.
- Rust live crates that contain unsafe code must enable `#![deny(unsafe_op_in_unsafe_fn)]` at crate root and wrap each unsafe operation in an explicit `unsafe {}` block with a local safety reason.


## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as f20f8af36e0f488779d3f543a217b2d19ea2db81. |
| G1 Lane classification | Classify the work as Rust execution-critical/performance, supported Python V2 strategy/config, Python AI/advisory, or legacy. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template lane inventory and Python/Rust V2 strategy boundary tests. |
| G2 Legacy label | Label legacy Cython/v1 and Python live TradingNode guidance as migration/reference-only. | Pass | Compatibility note in this file names legacy Cython/v1 and Python live `TradingNode` as migration/reference-only. |
| G3 Rust ownership | Rust owns runtime, adapter networking/parsing, normalization, risk/execution state, and performance-sensitive paths; Python and Rust strategies remain supported V2 surfaces. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the ownership-boundary regression tests; `references/developer_guide/python.md:12-14` records upstream Python strategy support. |
| G4 NT V2 API shape | Use current NT V2/PyO3 API shapes and crate/module boundaries instead of retired APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` byte-compared all 18 guide bodies to pinned upstream f20f8af; `uv run pytest -q tests/test_v2_guidance_hardening.py` passed current API-shape regressions. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 253 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 106 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pending | Final Phase 4 reconciliation, logical commit SHAs, and push evidence are recorded only after the working tree is committed and pushed. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

NT v2 compatibility note: Python live TradingNode material in the live gates is migration/reference-only; use LiveNode for Rust v2/Rust-backed work.

Live gates: `LiveNode` is the default for Rust-backed production live work; Python `TradingNode` material is migration/reference-only. Before `Pass`, prove startup/shutdown/reconnect/reconciliation behavior with `cargo nextest`, `cargo clippy`, `cargo deny`, config validation, and live safety dry-run evidence.

## What This Skill Covers

NautilusTrader **live infrastructure domain** — live trading nodes, system kernel, configuration, component lifecycle, and deployment.

**Python modules**: `live/`, `system/`, `config/`, `common/`, `core/`
**Rust crates**: `nautilus_system`, `nautilus_live`, `nautilus_common`, `nautilus_core`

## When To Use

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

- Configuring and launching live trading nodes
- `NautilusKernel` boot sequence and system setup
- Engine configuration (`TradingNodeConfig`)
- Component lifecycle management (INITIALIZED → RUNNING → STOPPED → DISPOSED)
- Logging setup and monitoring
- Clock configuration and timer management
- Deployment and production readiness
- Reconciliation and state recovery

## When NOT To Use

- **Adapter-specific configuration** → use `nt-adapters`
- **Strategy logic** → use `nt-trading`
- **Backtest setup** → use `nt-backtest`
- **Data persistence** → use `nt-data`

## Python Usage

## Live runtime contract

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

## Python Extension

### Custom Component

```python
from nautilus_trader.common.component import Component

class MyComponent(Component):
    def __init__(self, ...):
        super().__init__(...)

    def _start(self):
        # Called during component start
        pass

    def _stop(self):
        # Called during component stop
        pass

    def _reset(self):
        # Called during component reset
        pass

    def _dispose(self):
        # Called during component disposal
        pass
```

## Rust Usage

The `LiveNode` connects to real venues through adapter clients. It uses a builder pattern and runs as a standalone Rust binary — no Python runtime needed.

### Dependencies

```toml
[dependencies]
nautilus-common = "0.57"
nautilus-live = "0.57"
nautilus-model = "0.57"
nautilus-okx = "0.57"          # or any venue adapter
nautilus-trading = { version = "0.57", features = ["examples"] }

anyhow = "1"
dotenvy = "0.15"
log = "0.4"
tokio = { version = "1", features = ["full"] }
```

### LiveNode Builder

```rust
use log::LevelFilter;
use nautilus_common::{
    enums::Environment,
    logging::{logger::LoggerConfig, writer::FileWriterConfig},
};
use nautilus_live::node::LiveNode;
use nautilus_model::identifiers::{AccountId, TraderId};
use nautilus_okx::{
    common::enums::OKXInstrumentType,
    config::{OKXDataClientConfig, OKXExecClientConfig},
    factories::{OKXDataClientFactory, OKXExecutionClientFactory},
};

let trader_id = TraderId::from("TESTER-001");
let account_id = AccountId::from("OKX-001");

let data_config = OKXDataClientConfig {
    instrument_types: vec![OKXInstrumentType::Swap],
    ..Default::default()
};

let exec_config = OKXExecClientConfig {
    trader_id,
    account_id,
    instrument_types: vec![OKXInstrumentType::Swap],
    ..Default::default()
};

let log_config = LoggerConfig {
    stdout_level: LevelFilter::Info,
    fileout_level: LevelFilter::Info,
    file_config: Some(FileWriterConfig {
        directory: Some("logs".into()),
        file_name: Some("live-node.log".into()),
        ..Default::default()
    }),
    clear_log_file: false,
    ..Default::default()
};

let mut node = LiveNode::builder(trader_id, Environment::Live)?
    .with_name("MY-NODE-001".to_string())
    .with_logging(log_config)
    .add_data_client(
        None,
        Box::new(OKXDataClientFactory::new()),
        Box::new(data_config),
    )?
    .add_exec_client(
        None,
        Box::new(OKXExecutionClientFactory::new()),
        Box::new(exec_config),
    )?
    .with_reconciliation(true)
    .with_delay_post_stop_secs(5)
    .build()?;
```

### Add Strategies and Run

```rust
use nautilus_model::{identifiers::InstrumentId, types::Quantity};
use nautilus_trading::examples::strategies::{GridMarketMaker, GridMarketMakerConfig};

let mut config = GridMarketMakerConfig::new(
    InstrumentId::from("ETH-USDT-SWAP.OKX"),
    Quantity::from("10.0"),  // max_position (hard cap on net exposure)
)
    .with_trade_size(Quantity::from("0.10"))  // per-order quantity
    .with_num_levels(3)
    .with_grid_step_bps(100)
    .with_skew_factor(0.5)
    .with_requote_threshold_bps(10)
    .with_expire_time_secs(8)
    .with_on_cancel_resubmit(true);

config.base.use_hyphens_in_client_order_ids = false; // OKX requirement

let strategy = GridMarketMaker::new(config);
node.add_strategy(strategy)?;
node.run().await?;
```

### Async Runtime

`LiveNode::run()` is async and requires a Tokio runtime:

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();
    // ... node setup ...
    node.run().await?;
    Ok(())
}
```

The node runs until interrupted (Ctrl+C) or shut down programmatically.

### Current v2 LiveNode deltas

- v2 `LiveNode` shutdown handles Unix SIGTERM in the Rust path.
- Rust live and sandbox node builders support `with_clock_factory` for
  deterministic clock injection.
- `LiveNode metrics` are available for Rust live runner observability.
- Python and PyO3 configs support WebSocket transport backend selection.
- The `event_store` format changed in v1.230.0; beta v1.227-v1.229 stores
  must be regenerated rather than migrated in-place.
- Live reconciliation uses monotonic-time gates and `RecencyMap` tracking;
  review recency-sensitive checks for monotonic-clock use before deployment.

### v1.227.0 LiveNode config notes

- `LoggerConfig` can be constructed directly from Python and Rust; Rust `LiveNode` supports `file_config` and `clear_log_file`.
- `LiveNodeConfig` and adapter client configs implement serde `Deserialize`, so TOML-backed config loading is viable for Rust live nodes.
- Portfolio mark-to-market snapshots are emitted as `PortfolioSnapshot` events when `snapshot_interval_ms` is configured.

### Environment Variables

Adapters read API credentials from environment variables. Use `.env` + `dotenvy`:

```bash
export OKX_API_KEY="your_api_key"
export OKX_API_SECRET="your_api_secret"
export OKX_API_PASSPHRASE="your_passphrase"
```

Each adapter documents required variables in its integration guide.

### Adapter Examples

Most adapters include runnable `node_data_tester.rs` and `node_exec_tester.rs` examples:

| Adapter | Example directory |
|---|---|
| Architect AX | `crates/adapters/architect_ax/examples/` |
| Betfair | `crates/adapters/betfair/examples/` |
| Binance | `crates/adapters/binance/examples/` |
| BitMEX | `crates/adapters/bitmex/examples/` |
| Bybit | `crates/adapters/bybit/examples/` |
| Databento | `crates/adapters/databento/examples/` |
| Deribit | `crates/adapters/deribit/examples/` |
| dYdX | `crates/adapters/dydx/examples/` |
| Hyperliquid | `crates/adapters/hyperliquid/examples/` |
| Kraken | `crates/adapters/kraken/examples/` |
| OKX | `crates/adapters/okx/examples/` |
| Polymarket | `crates/adapters/polymarket/examples/` |
| Sandbox | `crates/adapters/sandbox/examples/` |
| Tardis | `crates/adapters/tardis/examples/` |

### Reconciliation

In production, enable reconciliation so the engine aligns cached state with the venue on startup:
- Keep `.with_reconciliation(true)` or the production default enabled unless an adapter limitation is documented and reviewed
- See `references/concepts/live.md` for reconciliation details

## Rust Extension (PyO3 Path)

### Infrastructure Components in Rust

```rust
use pyo3::prelude::*;

#[pyclass]
pub struct MyInfraComponent {
    // Component state
}

#[pymethods]
impl MyInfraComponent {
    #[new]
    fn new() -> Self { /* ... */ }
}
```

**PyO3 conventions:**
- Use `#[pyclass]` and `#[pymethods]` for Python-visible types
- Register in the owning crate’s `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates that crate submodule
- Python v2 live callback routing: never call `Python::attach()` from Tokio worker
  tasks. Send typed events through live runner channels; the runner dispatches
  callbacks on the host live event-loop thread.
- Tokio integration: use the Nautilus shared runtime and tracked tasks; do not
  construct an independent runtime inside live components.
- See `references/developer_guide/ffi.md` for FFI patterns
- See `references/developer_guide/rust.md` for Rust coding standards

## Key Conventions

### Component Lifecycle

Components follow strict state machine: `INITIALIZED → RUNNING → STOPPED → DISPOSED`. State transitions are enforced — calling `start()` on a `RUNNING` component raises an error. Always check state before operations.

### Logging Patterns

- Use `self.log.info()`, `self.log.warning()`, `self.log.error()`, `self.log.debug()`
- Log state transitions and significant events
- Use structured messages: `f"Order submitted: {order.client_order_id}"`
- Set appropriate log levels per component

### Config Validation

- All config classes use `frozen=True` (immutable after creation)
- Validate config before node creation
- Use type hints for config fields
- Secrets should be passed via environment variables, not config files

### Production Readiness

- Enable reconciliation for live trading
- Configure appropriate rate limits
- Set up file logging for production
- Use health checks and monitoring
- Handle graceful shutdown properly

### Coding Standards

See `references/developer_guide/coding_standards.md` for project-wide conventions including:

### Production Readiness Checklist

- [ ] Config validated in `__init__`
- [ ] State saved via `on_save` and restored via `on_load`
- [ ] Timers cleaned up in `on_stop`
- [ ] Error handling covers all event handlers
- [ ] Logging configured for debugging and monitoring
- [ ] Adapter credentials via environment variables, not hardcoded
- [ ] Environment variables: `PYO3_PYTHON`, `PYTHONHOME`, and Linux
      `LD_LIBRARY_PATH` derived with `sysconfig.get_config_var("LIBDIR")`

- Python style (PEP 8, type hints, docstrings)
- Rust style (edition 2024, clippy lints)
- FFI patterns (GIL management, callback forwarding)

## References

NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.

- `references/concepts/` — architecture, cache, logging, live, overview, rust
- `references/api/` — system, core, common, config, live
- `references/developer_guide/` — coding standards, FFI, Python conventions, Rust conventions, environment setup
- `references/developer_guide/contracts/live_runtime_contract.md` — LiveNode versus TradingNode guidance
- `references/examples/live/` — per-adapter live examples (Binance, Bybit, Databento, etc.)
