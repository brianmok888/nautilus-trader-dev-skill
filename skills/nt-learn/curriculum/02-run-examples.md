# Stage 02: Running Rust Examples

## Goal

Run source-pinned NautilusTrader Rust examples and identify the crate, feature flags, configuration,
and runtime boundary each example exercises.

## Prerequisites

- Stage 01 completed
- Pinned upstream checkout available through `tools/upstream_baseline.py`
- Rust toolchain and Cargo installed

## Concepts

Use examples as executable API evidence, not as extension templates. Confirm the example's owning
crate and enabled features before adapting it. New strategies use the public Rust extension seam in
`nt-strategy-builder-rust`; built-in examples may use crate-private or framework-owned APIs.

## Steps

1. Compile the canonical backtest example:

```bash
cargo check -p nautilus-backtest --example engine-ema-cross --features examples
```

2. Inspect the mirrored source at
   `references/nt-backtest/references/examples/rust_backtest/engine_ema_cross.rs`.
3. Compare the engine example with the node example in the same reference directory.
4. Trace strategy lifecycle and event ownership through
   `references/nt-trading/references/examples/rust_trading/examples/strategies/ema_cross/`.
5. Record the crate, feature flag, input data, lifecycle entry point, and observable output.

## Checkpoint

You can compile a pinned Rust example, explain its ownership boundary, and distinguish a built-in
example from a supported custom-strategy extension seam.
