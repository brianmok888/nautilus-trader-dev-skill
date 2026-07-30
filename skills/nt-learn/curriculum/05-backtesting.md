# Stage 05: Rust Backtesting Deep Dive

## Goal

Run Rust backtests using the pinned V2 engine and node examples while preserving production
component ownership.

## Prerequisites

- Stage 04 completed
- Load `nt-backtest`, `nt-data`, and `nt-testing`

## Backtest Surfaces

- Engine example: `references/nt-backtest/references/examples/rust_backtest/engine_ema_cross.rs`
- Node example: `references/nt-backtest/references/examples/rust_backtest/node_ema_cross.rs`

Choose the engine surface for direct programmatic orchestration and the node surface for
configuration-driven wiring. Keep strategy logic and model ownership identical to live deployment.

## Workflow

1. Define venue, account, OMS, matching, latency, and fill assumptions.
2. Load typed instruments and timestamp-ordered data.
3. Register the Rust strategy and required actors.
4. Configure reproducible seeds and deterministic engine settings.
5. Run the backtest and inspect orders, positions, portfolio, and analyzer outputs.
6. Validate fill-model assumptions separately from strategy correctness.
7. Record dataset identity, config, source commit, and output artifacts.

## Verification

```bash
cargo check -p nautilus-backtest --examples --features examples
```

Add focused tests for clock boundaries, precision, warmup, fill behavior, venue rules, and
reproducibility. A profitable result is not correctness evidence.

## Checkpoint

You can select the Rust engine or node surface, run a reproducible backtest, and explain which
assumptions belong to strategy, venue, matching engine, fill model, data, and portfolio analysis.
