# Stage 11: Rust Testing and Quality

## Goal

Choose and execute the Rust test, compile, acceptance, property, fuzz, benchmark, and operations
gates that match a NautilusTrader change.

## Prerequisites

- Stage 10 completed
- Load `nt-testing`, `nt-dev`, and the owning domain skill

## Test Layers

1. Rust unit tests for state transitions, parsers, precision, and error paths.
2. Integration tests across real crate/component boundaries.
3. Spec execution tests for adapter data/execution behavior.
4. Controlled-venue or testnet acceptance when external behavior is claimed.
5. Property and fuzz tests for untrusted or combinatorial boundaries.
6. Benchmarks for confirmed hot paths.
7. Reconciliation, restart, and operations drills for live readiness.

## Adapter Testers

Use the source-pinned Rust node tester examples instead of copying Python tester configuration:

- `references/nt-adapters/references/examples/rust_adapters/bitmex/node_data_tester.rs`
- `references/nt-adapters/references/examples/rust_adapters/bitmex/node_exec_tester.rs`
- corresponding venue directories under `references/nt-adapters/references/examples/rust_adapters/`

The owning testkit crate remains the executable authority:

```bash
cargo test -p nautilus-testkit --lib
cargo check -p nautilus-derive --examples --features examples
```

## Checkpoint

You can map a change to measurable Rust evidence and distinguish compilation, unit/integration,
spec, controlled-venue, resilience, fuzz, benchmark, and operations proof.
