NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Rust

Nautilus has an active, readiness-scoped Rust implementation under the `crates/` directory.
You can write actors, strategies, run backtests, and trade live without Python
where the required v2 engine, adapter, and test coverage are ready.
The domain model is shared across all paths, and the v2 PyO3 path runs
Python strategies on the Rust engine directly.

:::warning
The Rust API is under active development. Method signatures and trait
requirements may change between releases.
:::

## System implementations

Nautilus has three implementations. Understanding where each stands helps
you choose the right one for your use case.

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

- **v1 legacy**: Cython/Python classes under `nautilus_trader/`. Fully
  featured with the broadest component coverage.
- **v2 Rust**: Pure Rust under `crates/`. Runs without Python where the
  required engine, adapter, and test coverage exist.
- **v2 PyO3**: Python user-components (actors, strategies) running on
  the Rust core via PyO3 bindings. Combines Python convenience with
  Rust engine performance.

### Capability matrix

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

| Component             | v1 legacy (Cython) | v2 Rust        | v2 PyO3 (Python on Rust) |
|-----------------------|--------------------|----------------|--------------------------|
| Strategy              | ✓                  | ✓              | ✓                        |
| Actor                 | ✓                  | ✓              | ✓                        |
| DataEngine            | ✓                  | ✓              | ✓                        |
| ExecutionEngine       | ✓                  | ✓              | ✓                        |
| RiskEngine            | ✓                  | ✓              | ✓                        |
| BacktestEngine        | ✓                  | ✓              | ✓                        |
| BacktestNode          | ✓                  | ✓              | ✓                        |
| LiveNode              | ✓                  | ✓              | ✓                        |
| OrderEmulator         | ✓                  | ✓              | ✓                        |
| Matching engine       | ✓                  | ✓              | ✓                        |
| Portfolio             | ✓                  | ✓              | ✓                        |
| Accounts              | ✓                  | ✓              | ✓                        |
| Cache                 | ✓                  | ✓              | ✓                        |
| MessageBus            | ✓                  | ✓              | ✓                        |
| Data catalog          | ✓                  | ✓              | ✓                        |
| Indicators            | ✓                  | ✓              | ✓                        |
| Exec algorithms       | TWAP               | TWAP           | TWAP                     |
| Controller            | ✓                  | -              | -                        |
| Tearsheets            | ✓                  | -              | -                        |
| Config serialization  | ✓                  | -              | -                        |

### Adapters

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

| Adapter             | v1 legacy (Cython) | v2 Rust | v2 PyO3 |
|---------------------|--------------------|---------|---------|
| Architect AX        | ✓                  | ✓       | ✓       |
| Betfair             | ✓                  | ✓       | ✓       |
| Binance             | ✓                  | ✓       | ✓       |
| BitMEX              | ✓                  | ✓       | ✓       |
| Bybit               | ✓                  | ✓       | ✓       |
| Databento           | ✓                  | ✓       | ✓       |
| Deribit             | ✓                  | ✓       | ✓       |
| dYdX                | ✓                  | ✓       | ✓       |
| Hyperliquid         | ✓                  | ✓       | ✓       |
| Interactive Brokers | ✓                  | -       | -       |
| Kraken              | ✓                  | ✓       | ✓       |
| OKX                 | ✓                  | ✓       | ✓       |
| Polymarket          | ✓                  | ✓       | ✓       |
| Sandbox             | ✓                  | ✓       | ✓       |
| Tardis              | ✓                  | ✓       | ✓       |

### Choosing a path

- **v1 legacy** is the most complete today. Use it if you need the
  Controller, tearsheets, Interactive Brokers, or config serialization.
- **v2 Rust** gives native performance without a Python runtime. Use it for
  latency-sensitive deployments or teams that prefer a compiled language when
  the required engine, adapter, and test coverage exist; do not assume complete
  v1-equivalent coverage.
- **v2 PyO3**: Python user-components (actors, strategies) run on the
  Rust core engine with Rust performance for data processing and
  execution, while keeping the Python authoring experience.

## Project setup

The Nautilus crates are published to
[crates.io](https://crates.io/crates/nautilus-backtest). Add them to your
`Cargo.toml`:

```toml
[dependencies]
nautilus-backtest = "0.61"
nautilus-common = "0.61"
nautilus-execution = "0.61"
nautilus-model = { version = "0.61", features = ["stubs"] }
nautilus-trading = { version = "0.61", features = ["examples"] }

anyhow = "1"
log = "0.4"
```

For live trading, add the live crate and the adapter for your venue:

```toml
[dependencies]
nautilus-live = "0.61"
nautilus-okx = "0.61"
```

To track the latest development branch, point all Nautilus dependencies at the
same git source to avoid type mismatches between crates.io and git versions:

```toml
[dependencies]
nautilus-backtest = { git = "https://github.com/nautechsystems/nautilus_trader.git", branch = "develop" }
nautilus-common = { git = "https://github.com/nautechsystems/nautilus_trader.git", branch = "develop" }
nautilus-execution = { git = "https://github.com/nautechsystems/nautilus_trader.git", branch = "develop" }
nautilus-model = { git = "https://github.com/nautechsystems/nautilus_trader.git", branch = "develop", features = ["stubs"] }
nautilus-trading = { git = "https://github.com/nautechsystems/nautilus_trader.git", branch = "develop", features = ["examples"] }
```

Follow the checked-out `rust-toolchain.toml` for the active Rust version.
Source-aligned work as of 2026-07-28 uses Rust 1.97.1; older 1.96.x
release/docs references are lag notes unless the checked-out repository pins them.

### Feature flags

| Flag             | Crate               | Effect                                                        |
|------------------|---------------------|---------------------------------------------------------------|
| `high-precision` | `nautilus-model`    | 16-digit fixed precision (default is 9). Required for crypto. |
| `stubs`          | `nautilus-model`    | Test instrument stubs (`audusd_sim`, etc.).                   |
| `examples`       | `nautilus-trading`  | Example strategies (`EmaCross`, `GridMarketMaker`).           |
| `streaming`      | `nautilus-backtest` | Catalog‑based data streaming via `BacktestNode`.              |
| `defi`           | `nautilus-model`    | DeFi data types. Implies `high-precision`.                    |

:::tip
Standard 9-digit precision handles most traditional finance instruments.
Enable `high-precision` for crypto venues where prices can have many decimal
places (e.g. `0.00000001`).
:::

## Actors

An actor receives market data, custom data/signals, and system events but does not manage orders.
Implement the `DataActor` trait and bind your struct to `DataActorCore` via
`Deref`/`DerefMut`. Your struct must also implement `Debug` (required by the
blanket `Component` impl). The core provides subscription methods, cache
access, and clock access directly on your struct.

### Handler methods

Override any handler on the `DataActor` trait to receive the corresponding
data or event. All handlers have default no-op implementations, so you only
override what you need.

| Handler                | Receives                  |
|------------------------|---------------------------|
| `on_start`             | Actor started.            |
| `on_stop`              | Actor stopped.            |
| `on_quote`             | `QuoteTick`               |
| `on_trade`             | `TradeTick`               |
| `on_bar`               | `Bar`                     |
| `on_book_deltas`       | `OrderBookDeltas`         |
| `on_book`              | `OrderBook` (at interval) |
| `on_instrument`        | `InstrumentAny`           |
| `on_mark_price`        | `MarkPriceUpdate`         |
| `on_index_price`       | `IndexPriceUpdate`        |
| `on_funding_rate`      | `FundingRateUpdate`       |
| `on_option_greeks`     | `OptionGreeks`            |
| `on_option_chain`      | `OptionChainSlice`        |
| `on_instrument_status` | `InstrumentStatus`        |
| `on_order_filled`      | `OrderFilled`             |
| `on_order_canceled`    | `OrderCanceled`           |
| `on_time_event`        | `TimeEvent`               |

For a step-by-step walkthrough, see the
[Write an Actor (Rust)](https://nautilustrader.io/docs/latest/how_to/write_rust_actor/) how-to guide.
For a complete example, see
[`BookImbalanceActor`](https://github.com/nautechsystems/nautilus_trader/tree/develop/crates/trading/src/examples/actors/imbalance).

## Strategies

A strategy extends an actor with order management. Implement both
`DataActor` (for data handling) and `Strategy` (for access to
`StrategyCore`). The `StrategyCore` wraps `DataActorCore` and adds an
`OrderFactory`, `OrderManager`, and portfolio integration.

### Order management

The `Strategy` trait provides order methods through `StrategyCore`:

| Method                | Action                                    |
|-----------------------|-------------------------------------------|
| `submit_order`        | Submit a new order to the venue.          |
| `submit_order_list`   | Submit a list of contingent orders.       |
| `modify_order`        | Modify price, quantity, or trigger price. |
| `cancel_order`        | Cancel a specific order.                  |
| `cancel_orders`       | Cancel a filtered set of orders.          |
| `cancel_all_orders`   | Cancel all orders for an instrument.      |
| `close_position`      | Close a position with a market order.     |
| `close_all_positions` | Close all open positions.                 |

The `OrderFactory` (accessed via `self.core.order_factory()`) builds order
objects: `market`, `limit`, `stop_market`, `stop_limit`,
`market_if_touched`, `limit_if_touched`, and `trailing_stop_market`.

For a step-by-step walkthrough, see the
[Write a Strategy (Rust)](https://nautilustrader.io/docs/latest/how_to/write_rust_strategy/) how-to guide.
For complete examples, see
[`EmaCross`](https://github.com/nautechsystems/nautilus_trader/tree/develop/crates/trading/src/examples/strategies/ema_cross)
and
[`GridMarketMaker`](https://github.com/nautechsystems/nautilus_trader/tree/develop/crates/trading/src/examples/strategies/grid_mm).

### Running Rust components

Rust strategies and actors use direct native registration. Python can register
only bundled examples compiled behind the examples feature.

#### Pure Rust

Write your strategy and `main` function in Rust, then build a standalone
binary with `cargo build`. This path requires no Python runtime.

```rust
let strategy = GridMarketMaker::new(config);
node.add_strategy(strategy)?;
node.add_actor(actor)?;
node.run().await?;
```

See [Run Live Trading (Rust)](https://nautilustrader.io/docs/latest/how_to/run_rust_live_trading/) for a
full walkthrough.

#### Bundled examples from Python

Use `add_builtin_strategy(type_name, config)` or
`add_builtin_actor(type_name, config)` only for bundled Rust examples. These
methods require the examples feature and are not a first-class extension API.

```python
node.add_builtin_strategy(type_name, config)
node.add_builtin_actor(type_name, config)
```

Built-in strategy configs:

| Config                  | Strategy              |
|-------------------------|-----------------------|
| `EmaCrossConfig`        | `EmaCross`            |
| `GridMarketMakerConfig` | `GridMarketMaker`     |
| `DeltaNeutralVolConfig` | `DeltaNeutralVol`     |

Built-in actor configs (via `add_builtin_actor(type_name, config)`):

| Config                     | Actor                 |
|----------------------------|-----------------------|
| `BookImbalanceActorConfig` | `BookImbalanceActor`  |

Custom components are implemented in Rust and registered directly with
`node.add_strategy(strategy)?` or `node.add_actor(actor)?`. The bundled Python
methods are not a general extension path.

#### Plugin loading (planned)

A future plugin system will load compiled shared libraries at runtime.
Users compile strategies and actors as `cdylib` crates and the node
loads them without recompilation. This path is not yet available.

## Backtesting

For annotated walkthroughs of both APIs, see the
[Run a Backtest (Rust)](https://nautilustrader.io/docs/latest/how_to/run_rust_backtest/) how-to guide.

### `BacktestEngine` (low-level API)

Construct the engine, add venues and instruments, load data, register
strategies, and run. See the full working example:

```bash
cargo run -p nautilus-backtest --features examples --example engine-ema-cross
```

Source:
[`crates/backtest/examples/engine_ema_cross.rs`](https://github.com/nautechsystems/nautilus_trader/tree/develop/crates/backtest/examples/engine_ema_cross.rs)

### `BacktestNode` (high-level API)

Loads data from a `ParquetDataCatalog` and supports streaming in
configurable chunk sizes. Requires the `streaming` feature on
`nautilus-backtest`. See the full working example:

```bash
cargo run -p nautilus-backtest --features examples,streaming --example node-ema-cross
```

Source:
[`crates/backtest/examples/node_ema_cross.rs`](https://github.com/nautechsystems/nautilus_trader/tree/develop/crates/backtest/examples/node_ema_cross.rs)

## Live trading

For an annotated walkthrough, see the
[Run Live Trading (Rust)](https://nautilustrader.io/docs/latest/how_to/run_rust_live_trading/) how-to guide.

The `LiveNode` connects to real venues through adapter clients. The builder
pattern configures data and execution clients, then `run()` starts the async
event loop. Each adapter provides its own factory and config types.

| Adapter        | Example                                                  |
|----------------|----------------------------------------------------------|
| Architect AX   | `crates/adapters/architect_ax/examples/`                 |
| Betfair        | `crates/adapters/betfair/examples/`                      |
| Binance        | `crates/adapters/binance/examples/`                      |
| BitMEX         | `crates/adapters/bitmex/examples/`                       |
| Blockchain     | `crates/adapters/blockchain/examples/`                   |
| Bybit          | `crates/adapters/bybit/examples/`                        |
| Databento      | `crates/adapters/databento/examples/`                    |
| Deribit        | `crates/adapters/deribit/examples/`                      |
| dYdX           | `crates/adapters/dydx/examples/`                         |
| Hyperliquid    | `crates/adapters/hyperliquid/examples/`                  |
| Kraken         | `crates/adapters/kraken/examples/`                       |
| OKX            | `crates/adapters/okx/examples/`                          |
| Polymarket     | `crates/adapters/polymarket/examples/`                   |
| Sandbox        | `crates/adapters/sandbox/examples/`                      |
| Tardis         | `crates/adapters/tardis/examples/`                       |

Most adapters include `node_data_tester.rs` and `node_exec_tester.rs`
examples. These test data requests, streaming, and order execution
against live venues.

## Related guides

- [Write an Actor (Rust)](https://nautilustrader.io/docs/latest/how_to/write_rust_actor/) - Step-by-step actor walkthrough.
- [Write a Strategy (Rust)](https://nautilustrader.io/docs/latest/how_to/write_rust_strategy/) - Step-by-step strategy walkthrough.
- [Run a Backtest (Rust)](https://nautilustrader.io/docs/latest/how_to/run_rust_backtest/) - BacktestEngine and BacktestNode usage.
- [Run Live Trading (Rust)](https://nautilustrader.io/docs/latest/how_to/run_rust_live_trading/) - LiveNode setup and venue connection.
- [Architecture](https://nautilustrader.io/docs/latest/developer_guide/architecture/) - System design and data/execution flow.
- [Actors](https://nautilustrader.io/docs/latest/developer_guide/actors/) - Actor concepts (applies to both Python and Rust).
- [Strategies](https://nautilustrader.io/docs/latest/developer_guide/strategies/) - Strategy concepts and handler reference.
- [Events](https://nautilustrader.io/docs/latest/developer_guide/events/) - Event types and handler dispatch.
- [Backtesting](https://nautilustrader.io/docs/latest/developer_guide/backtesting/) - Backtest concepts and matching engine behavior.
