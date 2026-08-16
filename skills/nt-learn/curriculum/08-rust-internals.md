# Stage 08: Rust internals and PyO3 boundaries

NT v2 compatibility note: legacy Cython/FFI material is migration/reference-only;
current binding guidance is Rust/PyO3-oriented.

## Goal

NT v2 compatibility note: historical Cython material is migration/reference-only;
the active goal is current Rust/PyO3 ownership.

Navigate the current Rust workspace, trace a domain type through its owning
crate, and verify the optional PyO3 projection without reviving Cython or a
Python execution lane.

## Prerequisites

- Stage 07 complete
- Rust ownership, traits, enums, and modules
- A source checkout prepared by Stage 01

## Current workspace map

The active Rust source lives under `crates/`. Treat crate ownership as the
starting point for every change:

| Area | Representative crate responsibility |
| --- | --- |
| `core` | timestamps, UUIDs, runtime primitives |
| `model` | identifiers, fixed-point values, instruments, data, orders, events |
| `common` | cache, message bus, clocks, component infrastructure |
| `data` | data engines, clients, aggregation |
| `execution` | execution engine, clients, OMS behavior |
| `trading` | actors, strategies, execution algorithms |
| `backtest` | simulated exchange, matching, fill models |
| `live` / `system` | live-node ownership and orchestration |
| `persistence` / `serialization` | durable and wire representations |
| `adapters` | venue-specific integration |
| `pyo3` and crate-local `python` modules | explicit Python projections |

Prefer the narrowest owning crate. Add a PyO3 projection only when a documented
consumer needs it; the Rust domain type remains authoritative.

## Fixed-point domain model

Price and quantity values carry integer raw values plus precision. Never replace
that representation with floating-point values in a schema or external boundary.

```rust
pub struct Price {
    raw: i64,
    precision: u8,
}

pub enum OrderAny {
    Market(MarketOrder),
    Limit(LimitOrder),
    StopMarket(StopMarketOrder),
}
```

Inspect the current source before copying names or paths; nightly/develop can
move modules while preserving the ownership rule.

## Component and message lifecycle

Actors and strategies own registration, callback handling, and cleanup. A
component must unregister or cancel anything it registered during shutdown.
Message handling remains deterministic on the component's event loop; do not
create a second runtime in a hot callback.

Use source search to trace the current implementation:

```bash
rg "trait Actor|trait Strategy|enum ComponentState" crates
rg "register|subscribe|unsubscribe" crates/common crates/trading
```

## PyO3 projection

NT v2 compatibility note: historical Cython declarations are
migration/reference-only; use the current Rust/PyO3 projection below.

The current binding path is Rust plus PyO3. A projection belongs next to its
Rust owner or in the dedicated projection crate and must preserve the Rust
type's invariants.

```rust
#[pymethods]
#[pyo3_stub_gen::derive::gen_stub_pymethods]
impl Price {
    #[new]
    fn py_new(value: f64, precision: u8) -> PyResult<Self> {
        Self::new_checked(value, precision).map_err(to_pyvalue_err)
    }
}
```

NT v2 compatibility note: historical Cython declarations are
migration/reference-only; confirm bindings in the current Rust/PyO3 sources.

This shape matches the current `crates/model/src/python/types/price.rs`
projection: PyO3 methods are implemented on the owning Rust `Price`, and stub
generation is explicit. Confirm the current owning type and generated stub path
before implementation; do not infer the public projection from a historical
migration/reference-only Cython declaration.

## Build and test

Compile the owning crate first, then compile its projection boundary:

```bash
cargo check -p nautilus-model --all-targets --features high-precision
cargo check -p nautilus-pyo3 --features python,ffi,high-precision --lib
cargo test -p nautilus-model --features high-precision
```

Run `cargo fmt --all -- --check` and targeted Clippy for any crate you change.
When a Python projection changes, include its generated-stub and boundary tests,
but keep strategy, adapter, backtest, and live ownership in Rust.

## Exercises

1. Locate `Price` in `crates/model`, trace its raw/precision invariants, and run
   the crate's targeted tests.
2. Trace one `OrderAny` variant from construction through execution events.
3. Find the current PyO3 projection for a model type and identify where the
   generated public stub is checked.
4. Locate registration and shutdown cleanup for one Rust actor or strategy.

## Checkpoint

Continue to Stage 09 when:

- [ ] you can identify the owning Rust crate before editing a projection
- [ ] you can explain fixed-point raw/precision invariants
- [ ] you can compile a Rust crate and its PyO3 boundary separately
- [ ] you can trace registration to cleanup
NT v2 compatibility note: historical Cython material is migration/reference-only;
new bindings use Rust/PyO3.

- [ ] you know that historical Cython material is migration-only

NT v2 compatibility note: historical Cython/FFI material is
migration/reference-only; use the labelled snapshot only when migrating.

For historical Cython/FFI and Python-first internals material, use the explicitly
labelled migration snapshot under
`skills/nt-learn/migration_reference/python/curriculum/08-rust-internals.md`.
