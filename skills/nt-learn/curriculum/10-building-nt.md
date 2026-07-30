# Stage 10: Building NautilusTrader in Rust

## Goal

Extend NautilusTrader through the current Rust crate, adapter, PyO3, test, and documentation
boundaries.

## Prerequisites

- Stage 09 completed
- Load `nt-dev`, `nt-implement`, `nt-adapters`, and `nt-testing`

## Contribution Surfaces

| Change | Primary owner | Required evidence |
| --- | --- | --- |
| Domain type or instrument | `crates/model/` | Rust unit/property tests, serialization and precision checks |
| Indicator or analysis statistic | owning Rust crate | unit tests, benchmarks where hot-path relevant |
| Actor, strategy, execution algorithm | `crates/trading/` or supported external seam | lifecycle and integration tests |
| Backtest/runtime behavior | `crates/backtest/` or `crates/live/` | deterministic engine/node tests |
| Adapter | `crates/adapters/<venue>/` | official ten phases and change-specific acceptance |
| Python exposure | owning crate plus `crates/pyo3/` | registration, generated stubs, boundary tests |

## Workflow

1. Read the owning crate and its `AGENTS.md` or developer-guide contract.
2. Add the smallest failing Rust test.
3. Implement in the owning Rust module.
4. Add PyO3 projection only when a Python control-plane boundary is required.
5. Run targeted Cargo tests/checks, formatting, clippy, and relevant repo gates.
6. Update source-pinned guidance only when the public contract changed.

## Verification

```bash
cargo fmt --all -- --check
cargo check -p nautilus-core -p nautilus-model -p nautilus-pyo3 --features python,ffi,high-precision --lib
```

## Checkpoint

You can locate the Rust owner for a change, preserve FFI/PyO3 boundaries, and produce focused test,
build, documentation, and migration evidence.
