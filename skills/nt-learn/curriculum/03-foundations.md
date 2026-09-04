# Stage 03: Rust Architecture Foundations

## Goal

Understand NautilusTrader's Rust ownership boundaries, fixed-point model types, messages, cache,
and runtime lifecycle.

## Prerequisites

- Stage 02 completed
- Read `nt-model` and `nt-architect`

## Core Architecture

- `nautilus_model` owns identifiers, instruments, orders, events, prices, and quantities.
- `nautilus_common` owns shared runtime infrastructure and state services, including the
  actor framework (`DataActor` and friends under `crates/common/src/actor`).
- `nautilus_data` owns data-engine processing and requests.
- `nautilus_trading` owns strategies and execution algorithms, and re-exports the
  `nautilus_common` actor framework (it does not own it).
- `nautilus_backtest` and `nautilus_live` provide runtime wiring while preserving component
  ownership.

## Value Types

Use `Price`, `Quantity`, identifiers, currencies, and instrument constructors rather than primitive
floating-point values or free-form strings. Preserve raw fixed-point values and precision through
serialization and FFI boundaries.

## Messages and State

Components exchange typed commands, events, and data. Keep messages immutable after publication,
define deterministic event ordering, and assign each mutable state machine one Rust owner. Use the
cache as a shared read model, not as an implicit execution authority.

## Exercises

1. Trace `InstrumentId`, `Price`, and `Quantity` from `nautilus_model` into one Rust strategy.
2. Draw an ownership matrix for strategy, cache, data engine, risk engine, and execution engine.
3. Identify every boundary where precision, ordering, or lifecycle errors must fail closed.
4. Run:

```bash
cargo check -p nautilus-model --all-targets
```

## Checkpoint

You can identify the Rust crate that owns each domain concept and explain why fixed-point values,
typed identifiers, immutable messages, and explicit lifecycle boundaries are required.
