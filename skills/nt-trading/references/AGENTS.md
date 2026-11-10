# Trading Reference Snapshots

## OVERVIEW
Trading API pages, concepts and Rust examples; score 9, with a distinct
reference domain whose example modules retain their own tests and provenance.

## WHERE TO LOOK
| Need | Location |
|------|----------|
| Order and execution reference | `api/orders.md`, `api/execution.md` |
| Portfolio and position reference | `concepts/portfolio.md`, `concepts/positions.md` |
| Native Rust lifecycle and wiring | `concepts/rust.md` |
| Actor construction | `guides/write_rust_actor.md` |
| Strategy construction and order management | `guides/write_rust_strategy.md` |
| Example module inventory | `examples/rust_trading/examples/mod.rs` |
| Strategy module inventory | `examples/rust_trading/examples/strategies/mod.rs` |
| Configuration validation example | `examples/rust_trading/examples/strategies/hurst_vpin_directional/` |
| State separated from callbacks | `examples/rust_trading/examples/strategies/orderbook_imbalance/` |

## CONVENTIONS
- Example strategy directories keep README, configuration, implementation,
  module exports and tests together; inspect the whole local contract.
- `HurstVpinDirectional` exposes `new_checked` and `new`; the order-book
  imbalance example exposes `OrderBookImbalance::from_config`.
- Composite market maker, delta-neutral volatility, EMA crossover and grid
  market maker examples provide additional local comparison points.
- Hurst/VPIN examples combine trade aggressor volumes, dollar-bar estimation
  and quote-gated entries; their exit rules belong to that example design.
- Native trait requirements and signatures may change between source versions.

## ANTI-PATTERNS
- Promoting an example-specific parameter or topology into a framework rule.
- Copying strategy callbacks without their configuration and state checks.
- Treating reference `tests.rs` files as recorded test execution results.
- Reading a position page's historical reviewed tip as a newer release claim.
