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

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as 6e59fd74eaacacbb7410936f1766bd89fcce6f59. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed block-scoped legacy/Cython/v1 and TradingNode enforcement; `tests/test_dev_guide_sync.py` covers leakage and exemption boundaries. |
| G2 V2 example validation | Validate mirrored Rust trading examples against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-trading` checks source sync and compile contracts; durable provenance is recorded in `references/g2-evidence/nt-trading.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py tests/test_dev_guide_sync.py` passed PyO3 registration, live-runner callback, Rust ownership, and V2 boundary regressions. |
| G4 Lane and API shape | Classify supported Python V2, AI/advisory, config/control-plane, and Rust hot-path lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template inventory and V2 API regressions; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 308 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 113 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | All 18 targeted G2 harnesses passed and `uv run python tools/check_skill_g2_harnesses.py --check-cards` validated their durable evidence; no readiness row is Pending or Blocked. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Trading gates: Rust owns execution-critical order, risk, position, portfolio, and execution-algorithm paths; Python is limited to research/config and AI/advisory sidecars off execution-critical paths. Mark `Pass` only with `cargo nextest`, `cargo clippy`, `cargo deny`, risk/order lifecycle tests, and fail-closed behavior evidence.

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

## Python Extension

### Custom ExecAlgorithm

Subclass `ExecAlgorithm` from `nautilus_trader.execution.algorithm`:

```python
from nautilus_trader.execution.algorithm import ExecAlgorithm

class MyExecAlgorithm(ExecAlgorithm):
    def on_start(self):
        pass

    def on_order(self, order):
        # Custom execution logic — split, time-slice, etc.
        self.submit_order(order)

    def on_stop(self):
        pass
```

Register in config:
```python
exec_algorithms=[MyExecAlgorithm.fully_qualified_name()]
```

### Custom Margin/Position Sizing

Extend risk calculations by subclassing margin models or implementing custom position sizing logic in your Strategy.

## v1.227.0 Rust trading deltas

- `PortfolioSnapshot` events provide per-account mark-to-market snapshots when `snapshot_interval_ms` is configured; subscribe through the portfolio message-bus APIs when snapshot streams are part of the strategy contract.
- Rust `Strategy` order APIs take optional `Params`; pass `None` when no custom params are needed to avoid needless `IndexMap` allocation.
- Rust `Strategy::cancel_order` / `modify_order` take `ClientOrderId`; `cancel_orders` takes `Vec<ClientOrderId>`.
- `OrderFactory::bracket` is now a builder-style method (`factory.bracket()...call()`), not the older flat constructor form.
- Invalid Python order `create()` calls now raise `ValueError`; Rust order conversions should use `TryFrom<OrderInitialized>` / `try_from` / `try_into` rather than removed `From<OrderInitialized>`.

## Rust Usage

NautilusTrader has a complete Rust implementation (v2 Rust) that runs without Python. Strategies and actors are written in pure Rust, compiled to standalone binaries.

### Rust Strategy

A strategy owns a `StrategyCore` and implements `DataActor` for data handling. The `nautilus_strategy!` macro wires up `Deref`/`DerefMut` and the `Strategy` trait.

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

// Generates Deref<Target = DataActorCore>, DerefMut, and Strategy trait impl
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
        let order = self.core.order_factory().market(
            self.instrument_id,
            OrderSide::Buy,
            self.trade_size,
            None, None, None, None, None, None, None,
        );
        self.submit_order(order, None, None)?;
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

An actor owns a `DataActorCore` and receives data/events without order management. The `nautilus_actor!` macro wires up `Deref`/`DerefMut`.

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

### DataActor Handler Table

All handlers have default no-op implementations. Override only what you need:

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
| `on_order_filled` | `OrderFilled` |
| `on_order_canceled` | `OrderCanceled` |
| `on_time_event` | `TimeEvent` |

### Running Rust Components

Three paths to run Rust strategies/actors:

1. **Pure Rust** — standalone binary, no Python runtime:
   ```rust
   let strategy = MyStrategy::new(instrument_id);
   node.add_strategy(strategy)?;
   node.run().await?;
   ```

2. **Native config from Python** — register built-in Rust strategies from Python:
   ```python
   from nautilus_trader.core.nautilus_pyo3.trading import GridMarketMakerConfig
   config = GridMarketMakerConfig(instrument_id=..., trade_size=...)
   node.add_native_strategy(config)
   ```

3. **Plugin loading** (planned) — load compiled `cdylib` crates at runtime.

### Guard Safety

When accessing other actors in callbacks:
- Look up actors by ID each time; do not cache an `ActorRef`
- Drop the guard before scope ends; never store in a field
- Never hold a guard across an `.await` point

## Rust Extension (PyO3 Path)

### Exposing Rust Strategies to Python

Use `#[pyclass]` configs with `add_native_strategy`/`add_native_actor` dispatch:

| Config | Strategy |
|---|---|
| `EmaCrossConfig` | `EmaCross` |
| `GridMarketMakerConfig` | `GridMarketMaker` |
| `DeltaNeutralVolConfig` | `DeltaNeutralVol` |

| Config | Actor |
|---|---|
| `BookImbalanceActorConfig` | `BookImbalanceActor` |

To add custom components to this path: add a `#[pyclass]` config and dispatch arm in `add_native_strategy` or `add_native_actor`.

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
- `references/examples/` — backtest examples (EMA cross, actor data/signals, msgbus), Rust strategies (ema_cross, grid_mm), Rust actors (imbalance)
- `templates/` — strategy.py, actor.py, exec_algorithm.py
