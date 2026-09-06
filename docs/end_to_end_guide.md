# End-to-End Strategy Guide: Rust Strategy to Live Trading

This guide gives the default NautilusTrader Development Skills workflow for a new production-oriented system. The primary path is Rust-first: create a Cargo project, build a native Rust strategy, attach it to a Rust `LiveNode`, and run it on Tokio. It follows the upstream `docs/how_to/run_rust_live_trading.md` pattern: `LiveNode::builder(...)`, adapter client factories, `node.add_strategy(...)`, then `node.run().await`.

All new strategy, integration, and live work follows the Rust-first path in this guide. Python NT material is migration/reference-only unless an upstream contract explicitly requires Python bindings.

**Prerequisites**:
- Rust 1.98.0 toolchain and Cargo installed for the pinned `ac22d5cf4` develop baseline.
- NautilusTrader skills installed, especially `nt-architect`, `nt-implement`, `nt-strategy-builder-rust`, `nt-live`, `nt-testing`, and `nt-review`.
- Venue credentials available through environment variables or a local `.env` file for live/sandbox runs.

---

## Primary Path: Rust Strategy to LiveNode

### Step 1: Create a Rust Cargo project

Start with a standard Rust binary crate so the default deliverable is a compiled trading node.

```bash
cargo new my-strategy --bin
cd my-strategy
```

Add NautilusTrader live/trading crates, your venue adapter, and runtime support to `Cargo.toml`. The published crates.io lane is `0.63`; the pinned source workspace declares `0.64.0`, which is not published on crates.io. These are intentionally different lanes: use the release snippet below for a standalone project, or use the source-pinned path lane in repository validation when exact API parity with commit `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d` is required. `cargo info nautilus-live@0.63.0` succeeds while `cargo info nautilus-live@0.64.0` reports no published version.

```toml
[dependencies]
anyhow = "1"
dotenvy = "0.15"
log = "0.4"
tokio = { version = "1", features = ["full"] }

nautilus-common = "0.63"
nautilus-backtest = { version = "0.63", features = ["streaming"] }
nautilus-live = "0.63"
nautilus-model = "0.63"
nautilus-okx = "0.63"
nautilus-trading = { version = "0.63", features = ["examples"] }
```

Use the relevant adapter crate for your venue; OKX is shown because the official upstream `docs/how_to/run_rust_live_trading.md` guide uses OKX.

### Step 2: Design the native strategy and risk boundary

Use `nt-architect` before coding to document the production contract:

- **Venue/instrument**: exact `InstrumentId`, account, environment, and adapter crate.
- **Strategy type**: native Rust strategy or a vetted built-in Rust strategy config.
- **Signals**: market data subscriptions and deterministic signal transitions.
- **Risk**: order sizing, exposure limits, kill-switch behavior, and reconciliation expectations.
- **Testing evidence**: unit tests for strategy state transitions plus DataTester/ExecTester or adapter examples for venue behavior.

For a first live wiring pass, use a native Rust strategy builder from `nautilus-trading` examples, then replace it with your custom Rust strategy after the node, adapter, and risk boundaries are proven.

### Step 3: Build the LiveNode

Create `src/main.rs` with the same shape as the upstream Rust live-trading how-to: configure adapter clients, build a `LiveNode`, add the strategy, and await the node run.

```rust
use anyhow::Result;
use log::LevelFilter;
use nautilus_common::{enums::Environment, logging::logger::LoggerConfig};
use nautilus_live::node::LiveNode;
use nautilus_model::{
    identifiers::{AccountId, InstrumentId, TraderId},
    types::Quantity,
};
use nautilus_okx::{
    common::enums::OKXInstrumentType,
    config::{OKXDataClientConfig, OKXExecutionClientConfig},
    factories::{OKXDataClientFactory, OKXExecutionClientFactory},
};
use nautilus_trading::examples::strategies::{
    GridMarketMaker, GridMarketMakerConfig,
};

#[tokio::main]
async fn main() -> Result<()> {
    dotenvy::dotenv().ok();

    let trader_id = TraderId::from("TRADER-001");
    let account_id = AccountId::from("OKX-001");

    let data_config = OKXDataClientConfig::builder()
        .instrument_types(vec![OKXInstrumentType::Swap])
        .build();

    let exec_config = OKXExecutionClientConfig::builder()
        .account_id(account_id)
        .instrument_types(vec![OKXInstrumentType::Swap])
        .build();

    let log_config = LoggerConfig {
        stdout_level: LevelFilter::Info,
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
        .with_delay_post_stop_secs(5)
        .build()?;

    let mut strategy_config = GridMarketMakerConfig::builder()
        .instrument_id(InstrumentId::from("ETH-USDT-SWAP.OKX"))
        .max_position(Quantity::from("0.10"))
        .num_levels(3)
        .grid_step_bps(100)
        .skew_factor(0.5)
        .requote_threshold_bps(10)
        .expire_time_secs(8)
        .on_cancel_resubmit(true)
        .build();

    // OKX rejects hyphens in client order IDs.
    strategy_config.base.use_hyphens_in_client_order_ids = false;

    let strategy = GridMarketMaker::new(strategy_config);
    node.add_strategy(strategy)?;
    node.run().await?;

    Ok(())
}
```

Production nodes should leave reconciliation enabled unless a venue-specific runbook documents why it is disabled. Treat any simplified demo setting as sandbox-only.

### Step 4: Backtest the Rust strategy

Before venue connectivity, exercise the native strategy with the official Rust backtesting surfaces. Follow upstream `docs/how_to/run_rust_backtest.md`: use `BacktestEngine` for direct in-memory control or `BacktestNode` for catalog streaming. The upstream EMA-cross examples are the executable reference shapes:

```bash
cargo run -p nautilus-backtest --features examples --example engine-ema-cross
cargo run -p nautilus-backtest --features examples,streaming --example node-ema-cross
```

For your own crate, add deterministic tests around signal transitions, simulated fills, position/risk limits, and shutdown state. Do not promote a strategy to the live node merely because the live wiring compiles.

### Step 5: Configure credentials and environment

Store secrets outside source control. For OKX-style adapters, use environment variables or `.env` loaded by `dotenvy`:

```bash
export OKX_API_KEY="your_api_key"
export OKX_API_SECRET="your_api_secret"
export OKX_API_PASSPHRASE="your_passphrase"
```

For demo/sandbox trading, use venue-provided demo credentials and set the adapter config fields required by that venue. Each adapter integration guide owns its exact credential and environment variable contract.

### Step 6: Test before live execution

Use `nt-testing` and `nt-review` to collect evidence before connecting to a venue:

- `cargo fmt --check`
- `cargo clippy --all-targets --all-features -- -D warnings`
- `cargo nextest run --all-targets --all-features`
- Adapter DataTester evidence for subscriptions and request/response data paths.
- Adapter ExecTester evidence for submit/cancel/fill/reject/reconnect behavior.
- A live safety dry run with sandbox credentials and logs captured.

Do not mark the system production-ready until startup, shutdown, reconnect, reconciliation, risk checks, and audit logging have fresh evidence.

### Step 7: Run the live node

Run with release optimizations after tests pass and credentials are configured:

```bash
cargo run --release
```

The node runs until interrupted or shut down programmatically. Monitor structured logs for adapter connection, instrument discovery, subscriptions, reconciliation, and order lifecycle events.

---

## Progressive Cutover Gates

Before promoting a strategy or integration, copy the gate card from
`docs/tracking/CutoverGateTemplate.md` and evaluate every applicable gate:

1. Architecture Consistency
2. Dependency and Build Health
3. API and Binding Contract
4. Correctness Test Pyramid
5. Performance Regression Control
6. Resilience and Failure Recovery
7. Observability and Operability
8. Security Safety and Governance
9. Release and Rollback Readiness
10. Integration and Acceptance
11. Continuous Improvement

A release is not ready while an applicable gate is `Pending` or `Blocked`.
Evidence must name the owner, verification date, baseline, next action, and any
blocker; `N/A` belongs only in Applicability with a source-backed reason.

## Advanced: Adapter and DEX Work

If your venue requires a custom adapter, keep the same Rust-first live shape and implement the venue boundary behind NautilusTrader adapter traits:

1. Use `nt-adapters` or `nt-dex-adapter` to design the data client, execution client, instrument provider, and credentials model.
2. Prove adapter behavior with DataTester and ExecTester before attaching strategy logic.
3. Wire the adapter factories into `LiveNode::builder(...)` and keep secrets in environment/config, not code.
4. Re-run `nt-review` for risk, reconciliation, async runtime, FFI, and deployment readiness.

---

## Appendix: Python Migration Reference

NT v2 compatibility note: legacy `TradingNode` and Python integration material are migration/reference-only. Use Rust `LiveNode` for all new integration and live work.

Existing Python strategy, notebook, exploratory analysis, and prototyping material is migration/reference-only under this repository's stricter cutover policy. New strategy research and rapid prototyping route to `nt-strategy-builder-rust`; use existing Python material only to understand or migrate prior systems.

The Python boundaries are:

- Existing Python strategy research, data analysis, visualization, and tearsheet workflows are migration/reference-only.

Migration/reference Python must not place orders, own risk checks, block adapter liveness, or become authoritative for production order state. Implement new reviewed and tested strategy logic directly in the Rust path.

For new Rust-backed live work, use `LiveNode` and the primary Rust path above.
