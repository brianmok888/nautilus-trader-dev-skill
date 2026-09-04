# Stage 04: First Rust Strategy

## Goal

Implement a minimal Rust strategy through NautilusTrader's supported extension seam.

## Prerequisites

- Stage 03 completed
- Load `nt-strategy-builder-rust`, `nt-trading`, and `nt-testing`

## Workflow

1. Define a typed, validated configuration.
2. Construct the strategy through `StrategyCore` and the supported registration pattern documented
   by `nt-strategy-builder-rust`.
3. Request historical data before subscribing to live updates.
4. Define warmup and initialization conditions explicitly.
5. Handle typed data events without blocking the runtime.
6. Create orders through current model factories and perform fail-closed pre-submit checks.
7. Make stop/reset/dispose behavior deterministic.
8. Add unit tests for state transitions and a pinned compile test for the extension seam.

## Source-Pinned References

- `skills/nt-trading/references/examples/rust_trading/examples/strategies/ema_cross/`
- `skills/nt-strategy-builder-rust/SKILL.md`
- Pinned upstream how-to: `docs/how_to/write_rust_strategy.md`

Built-in strategies are architecture evidence, not automatically public extension APIs. Follow the
builder skill when its supported seam differs from an upstream internal example.

## Exercises

1. Implement a no-order warmup phase.
2. Emit at most one order for one deterministic signal transition.
3. Test insufficient data, invalid precision, and stop/reset behavior.
4. Compile the extracted skill example:

```bash
uv run pytest -q tests/test_rust_first_end_to_end.py::test_rust_strategy_skill_example_compiles_against_pinned_upstream
```

## Checkpoint

You can build and test a Rust strategy without Python execution authority and explain lifecycle,
warmup, data subscription, risk, order, and cleanup ownership.
