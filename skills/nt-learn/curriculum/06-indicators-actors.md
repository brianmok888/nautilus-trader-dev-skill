# Stage 06: Rust Indicators and Actors

## Goal

Build Rust indicators and actors with explicit state, deterministic update order, and typed message
boundaries.

## Prerequisites

- Stage 05 completed
- Load `nt-signals`, `nt-trading`, and `nt-architect`

## Indicators

Use an indicator for a focused calculation with explicit warmup, update, initialization, reset, and
value semantics. Keep hot-path updates allocation-aware and test numerical boundaries against
fixed-point inputs.

## Actors

Use a `DataActor` or domain actor when the component owns stateful aggregation, inference,
publishing, timers, or request/subscription coordination but does not own order decisions.

## Messaging Patterns

- Typed data flow for market and custom data.
- Message-bus publication for immutable domain events.
- Request/response for bounded queries with explicit correlation.

Never block hot handlers, create an isolated async runtime, or allow Python to publish
execution-authoritative messages.

## Source-Pinned Reference

Study `skills/nt-trading/references/examples/rust_trading/examples/actors/imbalance/` for actor
structure and tests. Treat its owning crate and version as part of the example contract.

## Exercises

1. Implement and test indicator warmup/reset invariants.
2. Implement an actor that publishes one typed state transition per input transition.
3. Test deterministic ordering, duplicate input, late input, stop, and reset.
4. Compile the owners:

```bash
cargo check -p nautilus-indicators -p nautilus-trading --all-targets
```

## Checkpoint

You can choose between indicator, actor, and strategy ownership and prove lifecycle, state,
message, and ordering behavior with Rust tests.
