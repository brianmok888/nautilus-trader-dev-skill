---
name: nt-trading
description: "Use when working with strategy logic, order execution, risk management, position/portfolio tracking, or exec algorithms in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-trading

## V2 order-event and migration hardening

- Handle `OrderFillVoided` as a first-class execution event. `OrderStatus.VOIDED`/`VOIDED` is terminal: do not emit or accept later order state updates for that order.
- Implement strategy and execution-algorithm `on_order_fill_voided` behavior when the venue can void fills, and test replay with the referenced fill available locally before reopen.
- `PortfolioConfig.use_mark_prices` defaults to `true`; trading logic or tests requiring last-price valuation must opt out with `use_mark_prices=False` and document the reason.
- `ExecutionEngineConfig.carry_replay_events_on_reopen` affects NETTING close/reopen replay; position/order lifecycle tests should cover it when restart reconciliation is in scope.
- Use `RedisMessageBusBacking` in Python V2 message-bus configuration.
- SQL/catalog migration must be completed before relying on historical orders, fills, or positions after an in-place V2 upgrade.
- deferred V2 limits for unsupported order types, TIFs, callbacks, or adapter features must be visible in the capability matrix.
- shared adapter task tracking, if upstream supports it for the adapter, must prevent leaked submit/modify/cancel tasks and clear task state on terminal events.
- Rust crates with unsafe execution-critical code must use `#![deny(unsafe_op_in_unsafe_fn)]`.


## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `81eedc7cea29a52c0568f0bfbafd190c2bebe74f`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run python -m pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-trading` passed the skill domain's scoped examples and owners against `81eedc7cea29a52c0568f0bfbafd190c2bebe74f`; schema-v2 provenance is recorded in `references/g2-evidence/nt-trading.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run python -m pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run python -m pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run python -m pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run python -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-trading.json`; repository closure is summarized in `docs/tracking/Findings.md`. |


Trading gates: Rust owns execution-critical order, risk, position, portfolio, and execution-algorithm paths; Python production material is migration/reference-only; Mark `Pass` only with `cargo nextest`, `cargo clippy`, `cargo deny`, risk/order lifecycle tests, and fail-closed behavior evidence.

## Rust production lane

Keep strategy execution, order lifecycle, risk checks, positions, portfolio state, accounting, and execution algorithms in Rust. Enforce fail-closed decisions and terminal-event invariants, then verify order, fill, void, cancel, reconciliation, and precision behavior with targeted Rust tests and the required cargo gates.

### Develop/nightly-only Rust component state lifecycle

Source: upstream develop commit `9a9e5fe7b762410229b380d5af92d32c13169c3a`.
This support is **develop/nightly only** and is not available in the pinned baseline or stable releases; gate configuration and deployments by the actual upstream revision.

Across backtest and live, state-enabled kernels use
`Cache::load_actor_state` and `Cache::load_strategy_state` to load before component startup, then call Rust `DataActor::on_load` and
`Strategy::on_load`. On shutdown they call Rust `DataActor::on_save` and
`Strategy::on_save`, persist those byte maps, and use
`NautilusKernel::save_trader_state` to save once during shutdown.
`NautilusKernel::finalize_stop` integrates that save with the live shutdown
sequence; the backtest engine also saves after its residual processing and
before engine/cache disposal.

Treat `on_load` and `on_save` as Rust component lifecycle hooks, not an escape
hatch for Python execution callbacks. Strategy, actor, order, risk, and
reconciliation execution ownership remains in Rust, and callback or database
failures must be surfaced without bypassing cleanup.

## PyO3 control-plane lane

Use PyO3 only for typed configuration, Rust component registration, lifecycle control, and read-only inspection of trading results. Python must not submit, modify, or cancel orders, own risk decisions, mutate authoritative portfolio state, or process execution-critical callbacks.

## Migration/reference lane

Python migration material is pointer-only here and physically quarantined under `migration_reference/python/` for `nt-trading`.

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at immutable commit `81eedc7cea29a52c0568f0bfbafd190c2bebe74f`.

## What This Skill Covers

NautilusTrader **trading domain** — strategy logic, order execution, risk management, and portfolio/position tracking.

**Python modules**: `trading/`, `execution/`, `risk/`, `accounting/`, `portfolio/`
**Rust crates**: `nautilus_trading`, `nautilus_execution`, `nautilus_risk`, `nautilus_portfolio`

## When To Use

- Writing or modifying a `Strategy` or `Actor`
- Configuring order execution (order types, time-in-force, exec algorithms)
- Setting up risk management (risk engine config, margin models)
- Working with positions, portfolio queries, or accounting
- Building custom execution algorithms (`ExecAlgorithm`)
- Order lifecycle handling (`submit_order`, `cancel_order`, `modify_order`)

## When NOT To Use

- **Custom indicators or signal generation** → use `nt-signals`
- **Fill models or simulated exchange** → use `nt-backtest`
- **Adapter configuration** → use `nt-adapters`
- **Domain model types (instruments, identifiers)** → use `nt-model`
- **Data persistence or catalog** → use `nt-data`
- **Live node system setup** → use `nt-live`

## Python Usage

Python production guidance is physically quarantined as migration/reference-only.
See [Python Usage migration reference](migration_reference/python/python-usage.md).
New production work follows the Rust or bounded PyO3 sections below.

## Python Extension

Python production guidance is physically quarantined as migration/reference-only.
See [Python Extension migration reference](migration_reference/python/python-extension.md).
New production work follows the Rust or bounded PyO3 sections below.

## v1.227.0 Rust trading deltas
Source: upstream NautilusTrader pin `81eedc7cea29a52c0568f0bfbafd190c2bebe74f`.

- `PortfolioSnapshot` events provide per-account mark-to-market snapshots when `snapshot_interval_ms` is configured; subscribe through the portfolio message-bus APIs when snapshot streams are part of the strategy contract.
- Rust `Strategy` order APIs take optional `Params`; pass `None` when no custom params are needed to avoid needless `IndexMap` allocation.
- Rust `Strategy::cancel_order` / `modify_order` take `ClientOrderId`; `cancel_orders` takes `Vec<ClientOrderId>`.
- `OrderFactory::bracket` is now a builder-style method (`factory.bracket()...call()`), not the older flat constructor form.
- Invalid Python order `create()` calls now raise `ValueError`; Rust order conversions should use `TryFrom<OrderInitialized>` / `try_from` / `try_into` rather than removed `From<OrderInitialized>`.

## Rust Usage

NautilusTrader has a complete Rust implementation (v2 Rust) that runs without Python. Strategies and actors are written in pure Rust, compiled to standalone binaries.

### Rust Strategy

A strategy owns a `StrategyCore` and implements `DataActor` for data handling. The `nautilus_strategy!` macro implements `DataActorNative`, `StrategyNative`, and `Strategy`; use the strategy facade methods rather than relying on deref coercions.

```rust
use nautilus_common::actor::DataActor;
use nautilus_model::{
    data::QuoteTick,
    enums::OrderSide,
    identifiers::{InstrumentId, StrategyId},
    types::Quantity,
};
use nautilus_trading::{nautilus_strategy, strategy::{Strategy, StrategyConfig, StrategyCore}};

pub struct MyStrategy {
    core: StrategyCore,
    instrument_id: InstrumentId,
    trade_size: Quantity,
}

impl MyStrategy {
    pub fn new(instrument_id: InstrumentId) -> Self {
        let config = StrategyConfig {
            strategy_id: Some(StrategyId::from("MY_STRAT-001")),
            order_id_tag: Some("001".to_string()),
            ..Default::default()
        };
        Self {
            core: StrategyCore::new(config),
            instrument_id,
            trade_size: Quantity::from("1.0"),
        }
    }
}

// Generates DataActorNative, StrategyNative, and Strategy implementations.
nautilus_strategy!(MyStrategy);

impl std::fmt::Debug for MyStrategy {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("MyStrategy").finish()
    }
}

impl DataActor for MyStrategy {
    fn on_start(&mut self) -> anyhow::Result<()> {
        self.subscribe_quotes(self.instrument_id, None, None);
        Ok(())
    }

    fn on_quote(&mut self, quote: &QuoteTick) -> anyhow::Result<()> {
        let order = self.order().market(
            self.instrument_id,
            OrderSide::Buy,
            self.trade_size,
            None, None, None, None, None, None, None,
        );
        self.submit_order(order, None, None, None)?;
        Ok(())
    }
}
```

**Override Strategy hooks** (order/position event handlers) by passing a block to the macro:

```rust
use nautilus_model::events::OrderRejected;

nautilus_strategy!(MyStrategy, {
    fn on_order_rejected(&mut self, event: OrderRejected) {
        log::warn!("Order rejected: {}", event.reason);
    }
});
```

**Order creation** (via `self.core.order_factory()`):
- `market(instrument_id, side, quantity, ...)`
- `limit(instrument_id, side, quantity, price, ...)`
- `stop_market(instrument_id, side, quantity, trigger_price, ...)`
- `stop_limit(instrument_id, side, quantity, price, trigger_price, ...)`
- `market_if_touched(...)`, `limit_if_touched(...)`, `trailing_stop_market(...)`

**Order management** (via `Strategy` trait, available on `self`):

| Method | Action |
|---|---|
| `submit_order` | Submit a new order to the venue |
| `submit_order_list` | Submit a list of contingent orders |
| `modify_order` | Modify price, quantity, or trigger price |
| `cancel_order` | Cancel a specific order |
| `cancel_orders` | Cancel a filtered set of orders |
| `cancel_all_orders` | Cancel all orders for an instrument |
| `close_position` | Close a position with a market order |
| `close_all_positions` | Close all open positions |

### Rust Actor

An actor owns a `DataActorCore` and receives data/events without order management. The `nautilus_actor!` macro implements `DataActorNative`; use `DataActor` facade methods rather than deref coercions.

```rust
use nautilus_common::{nautilus_actor, actor::{DataActor, DataActorConfig, DataActorCore}};
use nautilus_model::{data::QuoteTick, identifiers::{ActorId, InstrumentId}};

pub struct SpreadMonitor {
    core: DataActorCore,
    instrument_id: InstrumentId,
}

impl SpreadMonitor {
    pub fn new(instrument_id: InstrumentId) -> Self {
        let config = DataActorConfig {
            actor_id: Some(ActorId::from("SPREAD_MON-001")),
            ..Default::default()
        };
        Self {
            core: DataActorCore::new(config),
            instrument_id,
        }
    }
}

nautilus_actor!(SpreadMonitor);

impl std::fmt::Debug for SpreadMonitor {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("SpreadMonitor").finish()
    }
}

impl DataActor for SpreadMonitor {
    fn on_start(&mut self) -> anyhow::Result<()> {
        self.subscribe_quotes(self.instrument_id, None, None);
        Ok(())
    }

    fn on_quote(&mut self, quote: &QuoteTick) -> anyhow::Result<()> {
        let spread = quote.ask_price.as_f64() - quote.bid_price.as_f64();
        log::info!("Spread: {spread:.5}");
        Ok(())
    }
}
```

### Common DataActor Handlers

Handlers have default no-op implementations. Override only what the component needs; consult the current `DataActor` trait for the complete lifecycle, data, signal, depth, state, and fault hooks:

| Handler | Receives |
|---|---|
| `on_start` | Actor started |
| `on_stop` | Actor stopped |
| `on_quote` | `QuoteTick` |
| `on_trade` | `TradeTick` |
| `on_bar` | `Bar` |
| `on_book_deltas` | `OrderBookDeltas` |
| `on_book` | `OrderBook` (at interval) |
| `on_instrument` | `InstrumentAny` |
| `on_mark_price` | `MarkPriceUpdate` |
| `on_index_price` | `IndexPriceUpdate` |
| `on_funding_rate` | `FundingRateUpdate` |
| `on_option_greeks` | `OptionGreeks` |
| `on_option_chain` | `OptionChainSlice` |
| `on_instrument_status` | `InstrumentStatus` |
| `on_data` | `CustomData` |
| `on_signal` | `Signal` |
| `on_book_depth` | `OrderBookDepth10` |
| `on_time_event` | `TimeEvent` |
| `on_save` / `on_load` / `on_reset` | component state lifecycle |

Order events such as `on_order_filled` and `on_order_canceled` belong to the
`Strategy` trait, not `DataActor`.

### Running Rust Components

Two supported registration paths run Rust strategies/actors:

1. **Pure Rust** — standalone binary, no Python runtime:
   ```rust
   let strategy = MyStrategy::new(instrument_id);
   node.add_strategy(strategy)?;
   node.add_actor(actor)?;
   node.run().await?;
   ```

2. **Bundled examples from PyO3** — register bundled Rust examples by calling
   `node.add_builtin_strategy(type_name, config)` or
   `node.add_builtin_actor(type_name, config)` from the Python control plane.

   These methods require the examples feature and are not a first-class extension API.

### Guard Safety

When accessing other actors in callbacks:
- Look up actors by ID each time; do not cache an `ActorRef`
- Drop the guard before scope ends; never store in a field
- Never hold a guard across an `.await` point

## Rust Extension (PyO3 Path)

### Bundled Rust Examples from Python

`add_builtin_strategy(type_name, config)` and `add_builtin_actor(type_name, config)` expose only the Rust examples compiled with the examples feature. They are not a first-class extension API for custom components.

| Config | Strategy |
|---|---|
| `EmaCrossConfig` | `EmaCross` |
| `GridMarketMakerConfig` | `GridMarketMaker` |
| `DeltaNeutralVolConfig` | `DeltaNeutralVol` |

| Config | Actor |
|---|---|
| `BookImbalanceActorConfig` | `BookImbalanceActor` |

Implement custom strategies and actors in Rust and register them directly with `node.add_strategy(strategy)?` or `node.add_actor(actor)?`.

### PyO3 Binding Conventions

- Use `#[pyclass]` and `#[pymethods]` for Python-visible types
- Register bindings in the owning crate’s `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates that crate submodule
- Python v2 live callbacks must use typed live runner channels; never call
  `Python::attach` from Tokio worker tasks.
- Wrap FFI functions in `abort_on_panic(|| { ... })` — Rust panics must never unwind across FFI

## Coding Conventions

### Python

- **Type hints**: All strategy/actor method signatures MUST include type annotations
- **Union syntax**: Use PEP 604 (`Instrument | None`) not `Optional[Instrument]`
- **Truthiness**: Use `if x is None` for None checks, `if not my_list:` for empty collections
- **Docstrings**: NumPy style, imperative mood. No docstrings on `_private` methods
- **Strategy methods**: `on_start`, `on_bar`, `on_quote_tick`, `on_trade_tick`, `on_timer`, `on_save`, `on_load`, `on_reset`, `on_stop`

### Rust

- Use `nautilus_strategy!` macro for Rust strategies
- Error handling: `Result<T, E>`, never panic
- Guard safety: Check `is_flat()` before operations requiring flat position
- Handle `None` returns from cache queries explicitly

## Key Conventions

### Order Lifecycle

Orders follow a strict state machine: `INITIALIZED → SUBMITTED → ACCEPTED → [PARTIALLY_FILLED] → FILLED | CANCELED | EXPIRED | REJECTED`. Never assume order state — always check via events.

### Position State

Positions transition: `OPENING → OPEN → CLOSING → CLOSED`. A position's `side` is determined by its net quantity. Hedge mode vs netting mode affects how fills create/modify positions.

### Live-Readiness Checklist

- Handle all order events (not just fills — also rejects, cancels, expirations)
- Implement `on_stop()` cleanup (cancel open orders, optionally close positions)
- Use `self.clock.timer_names` for timer management
- Check `self.portfolio.is_net_long()` / `is_net_short()` for position awareness
- Log state transitions at appropriate levels

### Testing

- Use `BacktestEngine` for strategy unit tests
- Verify order submission counts, fill events, position states
- Test edge cases: partial fills, rejects, disconnections
- See `references/developer_guide/testing.md` for patterns

## References

- `references/concepts/` — strategies, actors, execution, orders, positions, portfolio, rust
- `references/api/` — trading, execution, risk, portfolio, accounting, orders, position, events
- `references/developer_guide/` — testing patterns, write_rust_strategy, write_rust_actor
- `references/examples/` — Rust strategies (ema_cross, grid_mm) and Rust actors (imbalance)
- `migration_reference/python/examples/` — quarantined Python EMA, actor, and msgbus examples
- `migration_reference/python/templates/` — quarantined Python strategy and execution-algorithm references
