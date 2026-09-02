---
name: nt-implement
description: "Use when implementing nautilus_trader components. Provides templates for Strategy, Actor, Indicator, Custom Data, Execution Algorithm, Adapters, and custom simulation models (FillModel, MarginModel, PortfolioStatistic). Includes Rust+PyO3 implementation patterns."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Nautilus Trader Implementation

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run python -m pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-implement` reports PASS nt-implement with Cap'n Proto `capnp 1.0.1` available in the standard verification environment; both harness steps (pytest `tests/test_capnp_schema_precision.py` and the owning-crate `cargo check`) returned 0 against `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`. Durable evidence: `references/g2-evidence/nt-implement.json` (`status: pass`, no `pending_reason`). A G2 `cargo check` result is compilation only; this is not spec, testnet, resilience, fuzz, or operations acceptance evidence. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run python -m pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run python -m pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run python -m pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run python -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-implement.json`; repository closure is summarized in `docs/tracking/Findings.md`. |


Implementation gates: no new component starts until the status gate before coding classifies the lane and names test evidence. Production/performance/live changes must target Rust crates and PyO3 seams, then record `cargo nextest`, `cargo clippy`, `cargo deny`, and focused checker/test output before `Pass`.

## Rust production lane

Implement new components in the owning Rust crate: model types in `crates/model/`, backtest models in `crates/backtest/`, adapters in `crates/adapters/`, and strategies through `nt-strategy-builder-rust`. Encode identifiers, precision, lifecycle, and risk state in Rust types; keep hot handlers allocation-aware and deterministic. Use the Nautilus runtime for async work and prove component behavior with focused Rust unit/integration tests before exposing bindings.

For adapters, complete provider, data, execution, reconciliation, factory, and shutdown contracts. Rust owns order commands and state transitions; fail closed on invalid input, overflow, stale state, unknown execution outcomes, and unsupported venue capabilities.

## PyO3 control-plane lane

PyO3 is a narrow boundary for validated configuration, component registration, lifecycle control, and read-only inspection. Convert Python objects into owned Rust domain types immediately, return typed exceptions on validation failures, and keep `StrategyCore`, clients, runtime tasks, signing, risk checks, and order submission in Rust.

Prefer `Py<T>`/`Py<PyAny>` for callback handles, document cleanup and cycle behavior, acquire the GIL only at Python call boundaries, and avoid `Arc<Py<T>>` unless an independent Rust shared-owner design requires it.

## Migration/reference lane

Python migration material is pointer-only here and physically quarantined under `migration_reference/python/` for `nt-implement`. Use those templates only to map an existing Python component to its Rust owner. New work remains Rust-first.

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`.

## Overview

Implement NautilusTrader components with Rust-first patterns and physically
quarantined migration references. This skill covers:

- **Rust components**: Strategy, Actor, Indicator, custom data, execution algorithms, and adapters
- **Rust simulation models**: FillModel, MarginModel, and portfolio statistics
- **Rust+PyO3 bindings**: bounded configuration and inspection around Rust ownership

## Risk Engine

- **Risk Management**: Implement custom risk checks and limits.
- **Position Limits**: Enforce maximum position sizes or exposure.
- **Drawdown Control**: Monitor and react to portfolio drawdowns.

## Exchange-Specific Patterns

- **Order Types**: Implement exchange-specific order types (e.g., Iceberg, Post-Only).
- **Market Data Handling**: Parse and process unique market data streams.
- **API Interaction**: Best practices for interacting with exchange APIs.

## Adapter Architecture (Rust-First)

NautilusTrader adapters follow a **Rust-first** layered architecture:
- **Rust core** (`crates/adapters/your_adapter/`): networking, parsing, state, and execution
- **PyO3 control plane** (`src/python/`): validated configuration and read-only inspection

Canonical reference adapters: **OKX**, **BitMEX**, **Bybit**

**Official ten-phase dependency structure:**
1. Phase 1: Define scope
2. Phase 2: Build the protocol core
3. Phase 3: Implement instruments
4. Phase 4: Implement market data
5. Phase 5: Implement execution
6. Phase 6: Add optional venue capabilities
7. Phase 7: Complete factories and projection
8. Phase 8: Prove conformance
9. Phase 9: Measure performance and robustness
10. Phase 10: Finish documentation and operations

These phases describe dependencies, not release gates. Keep the capability matrix current, allow a
market-data-only adapter to omit execution, and prove one product end to end before expanding.

## Adapter Canonical Contract (2026 Guide Alignment)

When implementing adapters, enforce these constraints across all templates and generated code:

- **Do phases in order** and complete each milestone before progressing.
- **Implement current Rust provider, data, execution, and reconciliation traits completely**.
- **Register Rust data/exec factories through `LiveNodeBuilder`**; prior Python
  interfaces and factory signatures are migration/reference-only under
  `migration_reference/python/`.
- **Follow runtime and FFI safety rules**:
  - use `get_runtime().spawn()` for adapter Rust async tasks
  - store owned Python handles as `Py<T>` / `Py<PyAny>`; avoid redundant `Arc<Py<T>>` unless a separate Rust shared-owner design explicitly requires it
  - model cycles explicitly: plain `Py<T>` does not break cycles; use weakrefs for backrefs and conditional PyO3 `__traverse__`/`__clear__` plus explicit callback cleanup for pyclass-owned traceable cycles
  - keep lock-heavy structures out of hot message paths
- **Enforce modern testing doctrine**:
  - use real captured payload fixtures (docs/live API), not invented schemas
  - avoid arbitrary sleeps in async tests; use condition-based waiting
  - cover Rust unit, integration, provider, data, execution, and factory behavior

## When to Use

- After architecture is defined (via nt-architect)
- When implementing any Nautilus component
- When needing correct method signatures and patterns
- When implementing custom simulation/analysis models
- When implementing performance-critical code in Rust with Python bindings

### Contract-aware implementation checkpoint

Before writing implementation code, check the relevant contract:

- environment/tooling: `references/developer_guide/contracts/environment_tooling.md`
- testing: `references/developer_guide/contracts/testing_policy.md`
- adapters: `references/developer_guide/contracts/adapter_contract.md`
- live runtime: `references/developer_guide/contracts/live_runtime_contract.md`
- design principles: `references/developer_guide/contracts/design_principles.md`

Do not mutate published Nautilus messages in place; preserve message immutability
unless an official source explicitly documents a local mutable builder pattern.

## Implementation Workflow

1. Start from architecture document
2. Implement in dependency order, choosing the **language** for each component
   using the V2 cutover map below (the default for every production component is Rust):
   - Custom Data Types (if needed)
   - Custom Models (FillModel, MarginModel if backtesting)
   - Indicators
   - Actors
   - Strategies
   - Execution Algorithms (if needed)
   - Portfolio Statistics (for analysis)
3. Validate each component before proceeding

### V2 cutover: implement-in-which-language map

NT v2 compatibility note: this whole file references the legacy Python-live
`TradingNode` only as reference-only context for migration; for Rust v2 /
Rust-backed work use `LiveNode`.

| Component | Default language for V2 cutover | Notes |
|---|---|---|
| Custom Data Types | **Rust** (`crates/model/`, PyO3-exposed when required) | Rust owns production data types; bounded PyO3 control-plane bindings are allowed |
| Custom Simulation Models (FillModel, MarginModel) | **Rust** (`crates/backtest/`, PyO3-exposed) | Hot backtest path; Python prototypes are migration/reference-only |
| Indicators | **Rust** (`crates/indicators/`, `Indicator` trait) | Compute-heavy; Rust is the performance default |
| Actors (signal aggregation and stateful processing) | **Rust** | Signal aggregation stays in Rust; Python is migration/reference-only |
| Strategies (order/position logic, entry/exit) | **Rust** (`nt-strategy-builder-rust`) | Explicit Python strategy requests still route to Rust under this repository's cutover policy |
| Execution Algorithms | **Rust** (`crates/trading/src/algorithm/`, integrated by `crates/live/src/node/`) | Execution-critical path stays in Rust; add PyO3 exposure only at the owning crate boundary |
| Portfolio Statistics | **Rust** (`crates/analysis/`) | Performance default; see `crates/analysis/src/statistics/` |
| Adapter networking/parsing (HTTP/WS/normalize) | **Rust** (`crates/adapters/<venue>/`) | Networking and parse paths are always Rust in V2 |
| Live node plumbing | **Rust** (`LiveNode`) | Prefer `LiveNode` for new production; `TradingNode` is legacy Python-live |

Rule of thumb: if the component sits on the networking/parse/perf/state/execution
path it is a Rust cutover target. Ambiguous strategy requests default to Rust. Explicit Python strategy requests still route to Rust,
remain a supported V2 surface but do not change this repository's routing default.


### No cross-contamination: match the strategy language to its builder skill

Upstream strategies can be written in either language, but this repository's
cutover path uses the Rust builder for every new strategy. Do not mix active
Rust guidance with migration/reference Python templates; this is the enforced
no cross-contamination boundary:

- User asked for / scoped a **Python** strategy -> explain the repository policy
  and route to `nt-strategy-builder-rust`. Use `nt-strategy-builder` only to
  inspect an explicitly labelled migration/reference example.
- User asked for / scoped a **Rust** strategy (HFT, perf-critical, ships with a
  Rust adapter) -> `nt-strategy-builder-rust` only.
- Ambiguous ("build a strategy" with no language stated) ->
  `nt-strategy-builder-rust` only;
  never silently mix them into NautilusTrader component patterns.

This keeps each skill's templates, conventions, and node-registration paths
internally consistent and prevents hybrid strategies that fail both toolchains.

## Rust template dependency policy

Read the target workspace version from its root `Cargo.toml` and use workspace
or path dependencies for in-tree Rust examples. Do not copy historical crate
versions into new code.

## Templates

Python production guidance is physically quarantined as migration/reference-only.
See [Templates migration reference](legacy_migration/templates.md).
New production work follows the Rust or bounded PyO3 sections below.

## Custom Simulation Models

Python production guidance is physically quarantined as migration/reference-only.
See [Custom Simulation Models migration reference](legacy_migration/custom-simulation-models.md).
New production work follows the Rust or bounded PyO3 sections below.

## Rust+PyO3 Implementation Patterns

For performance-critical components, NautilusTrader uses Rust with PyO3 bindings. Follow these patterns when implementing core functionality.

### Rust Module Structure

```rust
// -------------------------------------------------------------------------------------------------
//  Copyright (C) 2015-2026 Nautech Systems Pty Ltd. All rights reserved.
//  https://nautechsystems.io
//
//  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
//  You may not use this file except in compliance with the License.
//  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
// -------------------------------------------------------------------------------------------------

//! Custom indicator implementation in Rust.

use nautilus_core::correctness::FAILED;
use nautilus_indicators::indicator::Indicator;
use nautilus_model::data::Bar;

/// Custom momentum indicator.
#[repr(C)]
#[derive(Clone, Debug)]
#[cfg_attr(
    feature = "python",
    pyo3::pyclass(module = "nautilus_trader.indicators")
)]
pub struct CustomMomentum {
    /// The lookback period for momentum calculation.
    pub period: usize,
    /// Whether the indicator has been initialized.
    pub initialized: bool,
    /// Current indicator value.
    value: f64,
    /// Internal price buffer.
    prices: Vec<f64>,
}

impl CustomMomentum {
    /// Creates a new [`CustomMomentum`] instance with correctness checking.
    ///
    /// # Errors
    ///
    /// Returns an error if `period` is zero.
    pub fn new_checked(period: usize) -> anyhow::Result<Self> {
        if period == 0 {
            anyhow::bail!("Period must be positive, was {period}");
        }

        Ok(Self {
            period,
            initialized: false,
            value: 0.0,
            prices: Vec::with_capacity(period + 1),
        })
    }

    /// Creates a new [`CustomMomentum`] instance.
    ///
    /// # Panics
    ///
    /// Panics if `period` is zero.
    pub fn new(period: usize) -> Self {
        Self::new_checked(period).expect(FAILED)
    }

    /// Returns the current indicator value.
    #[must_use]
    pub fn value(&self) -> f64 {
        self.value
    }

    /// Updates the indicator with a new price.
    pub fn update_raw(&mut self, price: f64) {
        self.prices.push(price);

        if self.prices.len() > self.period {
            self.prices.remove(0);
            self.value = price - self.prices[0];
            self.initialized = true;
        }
    }

}

impl Indicator for CustomMomentum {
    fn name(&self) -> String {
        stringify!(CustomMomentum).to_string()
    }

    fn has_inputs(&self) -> bool {
        !self.prices.is_empty()
    }

    fn initialized(&self) -> bool {
        self.initialized
    }

    fn handle_bar(&mut self, bar: &Bar) {
        self.update_raw(bar.close.as_f64());
    }

    fn reset(&mut self) {
        self.prices.clear();
        self.value = 0.0;
        self.initialized = false;
    }
}
```

### PyO3 Bindings

```rust
#[cfg(feature = "python")]
mod python {
    use pyo3::prelude::*;
    use super::CustomMomentum;

    #[pymethods]
    impl CustomMomentum {
        #[new]
        #[pyo3(signature = (period))]
        fn py_new(period: usize) -> PyResult<Self> {
            Self::new_checked(period).map_err(|e| {
                pyo3::exceptions::PyValueError::new_err(e.to_string())
            })
        }

        #[getter]
        fn period(&self) -> usize {
            self.period
        }

        #[getter]
        fn initialized(&self) -> bool {
            self.initialized
        }

        #[getter]
        fn value(&self) -> f64 {
            self.value
        }

        #[pyo3(name = "update_raw")]
        fn py_update_raw(&mut self, price: f64) {
            self.update_raw(price);
        }

        #[pyo3(name = "reset")]
        fn py_reset(&mut self) {
            self.reset();
        }

        fn __repr__(&self) -> String {
            format!(
                "CustomMomentum(period={}, initialized={}, value={})",
                self.period, self.initialized, self.value
            )
        }
    }
}
```

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

### FFI Memory Safety (for Cython interop)

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

When exposing Rust types to Cython via C FFI, follow the memory contract:

```rust
use nautilus_core::ffi::abort_on_panic;

/// Box-backed API wrapper for FFI.
#[repr(C)]
pub struct CustomMomentum_API(Box<CustomMomentum>);

/// Creates a new CustomMomentum instance.
///
/// # Safety
///
/// The returned pointer must be freed with `custom_momentum_drop`.
#[unsafe(no_mangle)]
pub extern "C" fn custom_momentum_new(period: usize) -> CustomMomentum_API {
    abort_on_panic(|| {
        CustomMomentum_API(Box::new(CustomMomentum::new(period)))
    })
}

/// Drops a CustomMomentum instance.
///
/// # Safety
///
/// This function must be called exactly once per instance.
#[unsafe(no_mangle)]
pub extern "C" fn custom_momentum_drop(indicator: CustomMomentum_API) {
    drop(indicator);  // Box drops and frees memory
}

/// Updates the indicator with a new price.
#[unsafe(no_mangle)]
pub extern "C" fn custom_momentum_update(
    indicator: &mut CustomMomentum_API,
    price: f64,
) {
    abort_on_panic(|| {
        indicator.0.update_raw(price);
    })
}
```

### Key Rust Conventions

1. **Error Handling**:
   - Use `anyhow::Result<T>` for fallible functions
   - Use `anyhow::bail!` for early returns with errors
   - Provide `new_checked()` + `new()` pattern for constructors

2. **Type Qualification**:
   - Fully qualify `anyhow::` macros
   - Fully qualify `tokio::` types
   - Import Nautilus domain types directly

3. **Logging**:
   - Use fully qualified `log::debug!`, `log::info!`, `log::warn!`, and
     `log::error!` macros in core and async adapter crates
   - Capitalize messages, omit terminal periods

4. **Python Memory Management**:
   - `Py<T>` / `Py<PyAny>` owns a Python object reference; `Py::clone_ref` and `clone_py_object()` increment that reference count while attached to the interpreter
   - `Arc<Py<T>>` is normally redundant because `Py<T>` already gives owned, shareable Python handles; use an `Arc` wrapper only when an independent Rust shared-owner/lifetime design needs it
   - plain `Py<T>` does not itself break Python reference cycles; removing `Arc` simplifies ownership but does not make back-references safe
   - Use Python weak references for back-references that must not keep their target alive
   - For PyO3 pyclasses that own Python references or other GC-traceable objects which can participate in cycles, implement `__traverse__` and `__clear__`; also provide explicit callback cleanup for external resources or long-lived callback registrations
   - Use `clone_py_object()` from `nautilus_core::python` or `Py::clone_ref` for cloning Python callbacks
   - Implement manual `Clone` for callback-holding structs

   ```rust
   use nautilus_core::python::clone_py_object;

   // CORRECT: owned Python handle, manual Clone
   struct CallbackHolder {
       handler: Option<PyObject>,  // Py<PyAny>; already owns a Python reference
   }

   impl Clone for CallbackHolder {
       fn clone(&self) -> Self {
           Self {
               handler: self.handler.as_ref().map(clone_py_object),
           }
       }
   }
   ```

5. **Testing**:
   - Use `#[rstest]` for all tests
   - No AAA separator comments
   - Use descriptive test names

6. **Unsafe Rust Policy**:
   - Every crate enables `#![deny(unsafe_op_in_unsafe_fn)]`
   - Every `unsafe` block must have a `// SAFETY:` comment explaining validity
   - Document Safety section in doc comments for unsafe functions
   - Cover all unsafe blocks with unit tests

7. **Common Anti-Patterns**:
   - Avoid `.clone()` in hot paths – favour borrowing or `Arc`
   - Avoid `.unwrap()` in production – propagate errors with `?`
   - Avoid `String` when `&str` suffices – minimize allocations
   - Avoid exposing interior mutability – hide mutexes behind safe APIs
   - Avoid large structs in `Result<T, E>` – box large error payloads

8. **Thread-safe Hash Maps** (see `references/developer_guide/rust.md`):
   - `AHashMap` is **not** thread-safe; `Arc<AHashMap>` only for immutable-after-construction
   - Use `DashMap` for concurrent reads and writes: `Arc<DashMap<K, V>>`
   - Use plain `AHashMap` in single-threaded contexts (e.g., WebSocket handler hot path)

9. **Adapter Async Runtime** (see `references/developer_guide/rust.md`):
   - Use `get_runtime().spawn()` instead of `tokio::spawn()` in adapter crates
   - Use `get_runtime().block_on()` only for sync-to-async bridges outside an
     ambient Tokio runtime, such as PyO3 methods, binaries, dedicated threads,
     or tests
   - Never use `get_runtime().block_on()` inside live `DataClient` or
     `ExecutionClient` trait method implementations; spawn work and return
     immediately
   - Import from `nautilus_common::live::get_runtime` (shorter re-export path)
   - Tests are exempt: `#[tokio::test]` creates its own runtime

10. **Cap'n Proto Serialization** (see `references/developer_guide/rust.md`):
    - Schema files in `crates/serialization/schemas/capnp/`
    - Regenerate with `make regen-capnp` or `./scripts/regen_capnp.sh`
    - Verify with `make check-capnp-schemas`; CI enforces consistency
    - Test with `make cargo-test EXTRA_FEATURES="capnp"`

11. **Fixed-point Precision** (see `references/concepts/data.md`):
    - `Price` and `Quantity` use fixed-point arithmetic; raw values must be valid multiples
    - Use `from_raw()` only with values from `.raw` field, Nautilus conversion functions, or Arrow data
    - `FIXED_PRECISION` is `9` (standard) or `16` (high-precision mode)
    - Legacy catalogs pre-Dec 2025 may have floating-point errors; Arrow decode auto-corrects

## Coding Standards

Python production guidance is physically quarantined as migration/reference-only.
See [Coding Standards migration reference](legacy_migration/coding-standards.md).
New production work follows the Rust or bounded PyO3 sections below.

## Implementation Checklist

Before marking a component complete:

- [ ] Config class defined with all parameters
- [ ] Type hints on all methods
- [ ] `on_start` initializes state and subscriptions
- [ ] `on_stop` cleans up (cancel orders, unsubscribe)
- [ ] Historical data requested for warmup
- [ ] No blocking calls in handlers
- [ ] Proper null checks before using cached data
- [ ] Logging at appropriate levels

## References

For API details, load (relative to this skill folder):
- `references/api_reference/trading.md` - Strategy API
- `references/api_reference/common.md` - Actor, OrderFactory
- `references/api_reference/backtest.md` - BacktestEngine, FillModel, venues
- `references/api_reference/analysis.md` - PortfolioAnalyzer, statistics
- `references/api_reference/live.md` - LiveDataClient, LiveExecutionClient
- `references/developer_guide/environment_setup.md` - Development environment setup
- `references/developer_guide/coding_standards.md` - Style guide
- `references/developer_guide/python.md` - Python conventions
- `references/developer_guide/rust.md` - Rust style and conventions
- `references/developer_guide/ffi.md` - FFI memory contract
- `references/developer_guide/adapters.md` - Adapter development guide
- `references/developer_guide/benchmarking.md` - Benchmarking guide
- `references/developer_guide/docs.md` - Documentation style guide

For concept understanding:
- `references/concepts/backtesting.md` - Backtesting concepts and models
- `references/concepts/live.md` - Live trading configuration

## Next Step

After implementation, use **nt-review** skill to validate the code.
