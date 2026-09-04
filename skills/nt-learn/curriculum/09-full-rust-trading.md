# Stage 09: Full Rust Trading

## Goal

Write trading systems entirely in Rust — strategies, actors, backtests, and live trading — without Python.

## Prerequisites

- Stage 08 complete (understand Rust crate structure, traits, PyO3)
- Comfortable with Rust ownership, traits, and error handling

## Why Full Rust?

NautilusTrader's v2 Rust path provides:
- **Native performance** — no Python GIL, no FFI overhead
- **No Python runtime** — deploy as standalone binaries
- **Same domain model** — shared types across all paths
- **Readiness-scoped coverage** — legacy: this migration/reference-only comparison
  is not a production default; use the Rust path where the required engine, adapter,
  and tests exist; do not assume complete v1-equivalent coverage

## Project Setup

### Cargo.toml

```toml
[dependencies]
nautilus-backtest = { version = "0.62", features = ["streaming"] }
nautilus-common = "0.62"
nautilus-execution = "0.62"
nautilus-live = "0.62"
nautilus-model = "0.62"
nautilus-persistence = "0.62"
nautilus-trading = { version = "0.62", features = ["examples"] }

# Add venue adapter for live trading
nautilus-okx = "0.62"

ahash = "0.8"
anyhow = "1"
dotenvy = "0.15"
log = "0.4"
tempfile = "3"
tokio = { version = "1", features = ["full"] }
ustr = "1"
```

### Feature Flags

| Flag | Crate | Effect |
|------|-------|--------|
| `high-precision` | `nautilus-model` | 16-digit precision (required for crypto) |
| `examples` | `nautilus-trading` | Example strategies (`EmaCross`, `GridMarketMaker`) |
| `streaming` | `nautilus-backtest` | Catalog-based data streaming via `BacktestNode` |
| `defi` | `nautilus-model` | DeFi data types (implies `high-precision`) |

There is no `stubs` cargo feature. Test instrument stubs (`audusd_sim()` and
friends) live in `nautilus_model::stubs`, compiled under `test-support` (or in
tests) per `crates/model/src/lib.rs`.

Rust toolchain: follow the checked-out `rust-toolchain.toml`; source-aligned
work as of 2026-08-22 uses Rust 1.98.0. Older 1.97.x release/docs
references are lag notes unless the checked-out repository pins them.

## Writing a Rust Actor

An actor receives data but does not manage orders. Three steps:

### 1. Define struct with `DataActorCore`

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
        Self { core: DataActorCore::new(config), instrument_id }
    }
}
```

### 2. Wire up with macro + Debug

```rust
nautilus_actor!(SpreadMonitor);

impl std::fmt::Debug for SpreadMonitor {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("SpreadMonitor").finish()
    }
}
```

### 3. Implement DataActor trait

```rust
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

Key points:
- `nautilus_actor!` generates `Deref<Target = DataActorCore>` — subscription methods available directly on `self`
- `Debug` is required (trait bound on `DataActor`)
- All handlers return `anyhow::Result<()>` and have default no-op implementations

## Writing a Rust Strategy

A strategy extends an actor with order management. Uses `StrategyCore` instead of `DataActorCore`.

### 1. Define struct with `StrategyCore`

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
```

### 2. Wire up with macro + Debug

```rust
nautilus_strategy!(MyStrategy);

impl std::fmt::Debug for MyStrategy {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("MyStrategy").finish()
    }
}
```

### 3. Implement DataActor trait

```rust
impl DataActor for MyStrategy {
    fn on_start(&mut self) -> anyhow::Result<()> {
        self.subscribe_quotes(self.instrument_id, None, None);
        Ok(())
    }

    fn on_quote(&mut self, quote: &QuoteTick) -> anyhow::Result<()> {
        let order = self.core.order_factory().market(
            self.instrument_id, OrderSide::Buy, self.trade_size,
            None, None, None, None, None, None, None,
        );
        self.submit_order(order, None, None)?;
        Ok(())
    }
}
```

### 4. Override Strategy hooks (optional)

```rust
nautilus_strategy!(MyStrategy, {
    fn on_order_rejected(&mut self, event: OrderRejected) {
        log::warn!("Order rejected: {}", event.reason);
    }
});
```

Key differences from actor:
- `nautilus_strategy!` also generates the `Strategy` trait impl (`core()`/`core_mut()`)
- Order factory: `self.core.order_factory().market(...)`, `.limit(...)`, `.stop_market(...)`, etc.
- Order management: `self.submit_order()`, `self.cancel_order()`, `self.close_position()`, etc.

## Running a Backtest

### BacktestEngine (low-level)

```rust
use nautilus_backtest::{
    config::{BacktestEngineConfig, SimulatedVenueConfig},
    engine::BacktestEngine,
};

let mut engine = BacktestEngine::new(BacktestEngineConfig::default())?;

// Add venue (single SimulatedVenueConfig argument), instrument, data
engine.add_venue(
    SimulatedVenueConfig::builder()
        .venue(Venue::from("SIM"))
        .oms_type(OmsType::Hedging)
        .account_type(AccountType::Margin)
        .book_type(BookType::L1_MBP)
        .starting_balances(vec![Money::from("1_000_000 USD")])
        .build()?,
)?;
engine.add_instrument(&instrument)?;
engine.add_data(quotes, None, true, true);

// Add strategy and run
let strategy = MyStrategy::new(instrument_id);
engine.add_strategy(strategy)?;
engine.run(None, None, None, false)?;
```

Run built-in example:
```bash
cargo run -p nautilus-backtest --features examples --example engine-ema-cross
```

### BacktestNode (high-level, with catalog streaming)

```rust
use nautilus_backtest::node::BacktestNode;

let mut node = BacktestNode::new(vec![run_config])?;
node.build()?;

let engine = node.get_engine_mut("my-run").context("engine not found")?;
engine.add_strategy(strategy)?;

node.run()?;
```

Run built-in example:
```bash
cargo run -p nautilus-backtest --features examples,streaming --example node-ema-cross
```

## Running Live Trading

### LiveNode with adapter

```rust
use nautilus_live::node::LiveNode;
use nautilus_okx::factories::{OKXDataClientFactory, OKXExecutionClientFactory};

let mut node = LiveNode::builder(trader_id, Environment::Live)?
    .with_name("MY-NODE".to_string())
    .with_logging(log_config)
    .add_data_client(None, Box::new(OKXDataClientFactory::new()), Box::new(data_config))?
    .add_exec_client(None, Box::new(OKXExecutionClientFactory::new()), Box::new(exec_config))?
    .build()?;

node.add_strategy(strategy)?;
node.run().await?;
```

Key requirements:
- `#[tokio::main]` on main function (LiveNode is async)
- Environment variables for API credentials (`dotenvy::dotenv().ok()`)
- Enable reconciliation in production (remove `.with_reconciliation(false)`)

## Handler Reference

| Handler | Receives |
|---------|----------|
| `on_start` | Actor/strategy started |
| `on_stop` | Actor/strategy stopped |
| `on_data` | `CustomData` |
| `on_signal` | `Signal` |
| `on_quote` | `QuoteTick` |
| `on_trade` | `TradeTick` |
| `on_bar` | `Bar` |
| `on_book_deltas` | `OrderBookDeltas` |
| `on_book_depth` | `OrderBookDepth10` |
| `on_book` | `OrderBook` (at interval) |
| `on_instrument` | `InstrumentAny` |
| `on_mark_price` | `MarkPriceUpdate` |
| `on_index_price` | `IndexPriceUpdate` |
| `on_funding_rate` | `FundingRateUpdate` |
| `on_option_greeks` | `OptionGreeks` |
| `on_option_chain` | `OptionChainSlice` |
| `on_instrument_status` | `InstrumentStatus` |
| `on_instrument_close` | `InstrumentClose` |
| `on_block` | `Block` (DeFi) |
| `on_pool` | `Pool` (DeFi) |
| `on_pool_swap` | `PoolSwap` (DeFi) |
| `on_pool_liquidity_update` | `PoolLiquidityUpdate` (DeFi) |
| `on_pool_fee_collect` | `PoolFeeCollect` (DeFi) |
| `on_pool_flash` | `PoolFlash` (DeFi) |
| `on_historical_data` | `CustomData` (scalar or batch list) |
| `on_historical_book_deltas` | `[OrderBookDelta]` batch |
| `on_historical_book_depth` | `[OrderBookDepth10]` batch |
| `on_historical_quotes` | `[QuoteTick]` batch |
| `on_historical_trades` | `[TradeTick]` batch |
| `on_historical_bars` | `[Bar]` batch |
| `on_historical_mark_prices` | `[MarkPriceUpdate]` batch |
| `on_historical_index_prices` | `[IndexPriceUpdate]` batch |
| `on_historical_funding_rates` | `[FundingRateUpdate]` batch |
| `on_order_filled` | `OrderFilled` |
| `on_order_canceled` | `OrderCanceled` |
| `on_time_event` | `TimeEvent` |

These are the `DataActor` trait handlers owned by `nautilus_common`
(`crates/common/src/actor/data_actor.rs` in the pinned checkout); the DeFi rows
require the `defi` cargo feature. For a guided walkthrough of the engine and node
backtest flows, see the pinned upstream how-to `docs/how_to/run_rust_backtest.md`.

## Exercises

1. **Write an actor**: Create a `VolumeTracker` actor that subscribes to trades and logs cumulative volume per instrument. Register it with a `BacktestEngine`.

2. **Write a strategy**: Create a simple mean-reversion strategy that buys when price drops below the 20-period SMA and sells when it rises above. Use `self.core.order_factory().market(...)`.

3. **Run a backtest**: Set up a `BacktestEngine` with the `audusd_sim()` stub instrument, generate quote data, register your strategy, and run. Examine the output.

4. **Explore live setup**: Read an adapter example (e.g., `crates/adapters/okx/examples/node_data_tester.rs`). Understand the `LiveNode::builder()` pattern and how data/exec factories wire up.

## Checkpoint

You're ready for Stage 10 when:
- [ ] You can write a Rust actor with `DataActorCore` + `nautilus_actor!` + `DataActor` trait
- [ ] You can write a Rust strategy with `StrategyCore` + `nautilus_strategy!` + order management
- [ ] You can set up and run a `BacktestEngine` in Rust
- [ ] You understand `LiveNode::builder()` and adapter factory patterns
- [ ] You know the handler table and can subscribe to the data types you need
