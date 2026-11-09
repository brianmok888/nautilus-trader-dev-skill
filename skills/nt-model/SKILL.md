---
name: nt-model
description: "Use when working with domain model types, instruments, identifiers, value types, enums, or currencies in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-model

## Order metadata validation (develop-line)

Upstream commit
[`d46f56505`](https://github.com/nautechsystems/nautilus_trader/commit/d46f56505),
included in the pinned G2 baseline, adds `OrderInitialized::new_checked`. The fallible constructor rejects a
contingent order without linked order IDs and rejects an execution algorithm
without its execution spawn ID. `OrderInitialized::new` now delegates to that
validation and panics on invalid metadata.

This API is included in the pinned G2 baseline
`77d785c69205c4326e6aadb46d03fb45357a78f2`. Use `new_checked` when code must
handle invalid external or persisted order metadata.

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `77d785c69205c4326e6aadb46d03fb45357a78f2`; `references/upstream-delta-review.json` records the complete 586-commit reviewed transition to this pin. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `python3 tools/check_legacy_labelling.py` and `python3 tools/check_dev_guide_sync.py` passed on the synchronized source tree. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `python3 tools/check_skill_g2_harnesses.py --execute --skill nt-model` is the current-pin harness; evidence is `references/g2-evidence/nt-model.json`. Pass requires its actual successful execution against `77d785c69205c4326e6aadb46d03fb45357a78f2`. A G2 `cargo check` result is compilation only; it does not prove spec, testnet, resilience, fuzz, or operations acceptance. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `python3 -m pytest -q tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed as part of 158 repository checks; source audits checked current Rust/PyO3 ownership and callback signatures. Runtime execution is covered separately by G2. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `python3 -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed 158 repository policy checks; this does not certify downstream application behavior. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` and `python3 tools/check_rust_trading_reference_sync.py` passed; exact source comparisons covered 22 shared guides, 33 trading source files, 81 analysis files, and 23 matching adapter examples. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `python3 tools/check_legacy_labelling.py` and the 158-test source-policy run passed for migration labels, language lanes, precision, callbacks, and fail-closed guidance; live venue acceptance remains change-specific. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | `references/g2-evidence/nt-model.json` records current-pin G2 execution (status pass, owned-content hash match); mission closure receipts under `docs/tracking/receipts/nt-v2-rc-20261109/`; `python3 tools/check_governance_receipts.py` validated 497 receipts. |


Model gates: Rust owns identifiers, instruments, enums, fixed-point values, and precision-sensitive invariants; Python receives PyO3 bindings only. Mark `Pass` only after `cargo nextest`, `cargo clippy`, `cargo deny`, high-precision/overflow tests, and binding/stub evidence match the current model API.

## Rust production lane

Rust owns identifiers, instruments, enums, currencies, events, and fixed-point values. Enforce precision, overflow, identifier formatting, and instrument invariants at construction boundaries; use owned snapshots when scoped cache wrappers would cross async or event boundaries. New model types belong in `nautilus_model` and must retain exact raw-value semantics across FFI.

```rust
use nautilus_model::{
    identifiers::InstrumentId,
    types::{Price, Quantity},
};

let instrument_id: InstrumentId = "ETHUSDT-PERP.BINANCE".parse()?;
let price = Price::new(1850.50, 2);
let quantity = Quantity::new(1.5, 1);
```

These constructors accept human values. `from_raw` accepts native fixed-point
values scaled by the active `FIXED_PRECISION`, not integers scaled only by the
display precision. Current develop validates that raw values are representable
at the declared precision; incorrectly scaled raw values can panic.

## PyO3 control-plane lane

PyO3 provides construction, inspection, serialization, and conversion of Rust-owned model values. Register bindings in `nautilus_model/src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates the owning crate submodule. Preserve raw fixed-point values across the boundary, translate fallible validation into Python errors, and keep domain invariants in Rust rather than duplicating them in Python.

```rust
use pyo3::prelude::*;

#[pymethods]
impl MyIdentifier {
    #[new]
    fn py_new(value: &str) -> PyResult<Self> {
        value.parse().map_err(|err| pyo3::exceptions::PyValueError::new_err(err.to_string()))
    }
}
```

## Migration/reference lane

Prior Python model examples and extension guidance are quarantined under `migration_reference/python/`. They document migration and API comparison only; they are not an active production lane.

## Source-pinned upstream lane


Current source pin: `77d785c69205c4326e6aadb46d03fb45357a78f2`. The latest
published RC is `v2.0.0rc8`; develop is an unreleased rc9 source boundary.
See `references/README.md`. Older commit-specific notes below are historical
review context; they do not establish current G2 execution or release availability.

Use `references/developer_guide/rust.md` and the model snapshots under `references/api/model/` as upstream-derived guidance reviewed against the current pin `77d785c69205c4326e6aadb46d03fb45357a78f2` during the 586-commit transition review (they are curated extracts, not byte-copies; per-section headers carry their own pins). `OrderInitialized::new_checked` is verified at this pin; check release availability separately.

Current-develop betting invariant: increasing a same-side `BetPosition` uses a
stake-weighted average price, not an unweighted mean. Preserve constituent
stake in the numerator and total stake in the denominator, and cover both back
and lay increases. Source: upstream develop commit
`fa507199deb34430a983144e4af028046f2af926`.

Order accounting at the pinned baseline: order event history is read-only through
`events()` (construct order cores with `OrderCore::new`; the `events` field is private),
and `avg_px`/`slippage` use a chronological fixed-point fold that rebuilds — rather than
subtracts — on corrections and deserialization, so incremental averages agree with
full-history recomputation. Source: pinned upstream commit
`77d785c69205c4326e6aadb46d03fb45357a78f2` (`21ecc5f854`).

## What This Skill Covers

NautilusTrader **domain model** — instruments, identifiers, value types, enums, and currencies.

**Python modules**: `nautilus_trader.model` (flat PyO3 re-export) and `nautilus_trader.testkit`
**Rust crates**: `nautilus_model` (identifiers, instruments, types, enums)

## When To Use

- Working with domain model types (instruments, identifiers, value types)
- Creating or configuring instruments
- Understanding identifier string formats
- Using `Price`, `Quantity`, `Money`, `Currency` types
- Defining `SyntheticInstrument` or custom tick schemes
- Understanding enum types used across the system

## When NOT To Use

- **Custom data for signals** → use `nt-signals` (`@customdataclass`)
- **Order lifecycle** → use `nt-trading`
- **Data persistence** → use `nt-data`
- **Adapter-specific instrument loading** → use `nt-adapters`

## Rust Usage

```rust
use nautilus_model::identifiers::{InstrumentId, Venue, Symbol};
use nautilus_model::instruments::CryptoPerpetual;
use nautilus_model::types::{Price, Quantity, Money};
use nautilus_model::enums::{OrderSide, OrderType};
```

## Rust Extension

### New Instrument Types

**18 `InstrumentAny` variants:**
- `Betting` - payload type `BettingInstrument` for betting markets
- `BinaryOption` — binary options
- `Cfd` — contracts for difference
- `Commodity` — commodities
- `CryptoFuture` — crypto dated futures
- `CryptoFuturesSpread` — crypto futures spreads
- `CryptoOption` — crypto options
- `CryptoOptionSpread` — crypto option spreads
- `CryptoPerpetual` — crypto perpetual swaps
- `CurrencyPair` — FX pairs
- `Equity` — stocks
- `FuturesContract` — dated futures
- `FuturesSpread` — futures spreads
- `IndexInstrument` — indices
- `OptionContract` — dated options
- `OptionSpread` — option spreads
- `PerpetualContract` — generic perpetual contracts
- `TokenizedAsset` — tokenized assets

SyntheticInstrument is separate from `InstrumentAny` and is not one of these variants.

All 18 `InstrumentAny` variants are defined in Rust (`crates/model/src/instruments/`) and exposed to Python via PyO3. `SyntheticInstrument` remains a separate type. New instruments follow the same pattern:

```rust
use pyo3::prelude::*;
use nautilus_model::identifiers::InstrumentId;
use nautilus_model::types::{Price, Quantity, Currency};

#[pyclass]
pub struct MyInstrument {
    id: InstrumentId,
    price_precision: u8,
    size_precision: u8,
    // Custom fields
}

#[pymethods]
impl MyInstrument {
    #[new]
    fn new(id: InstrumentId, price_precision: u8, size_precision: u8) -> Self { ... }

    #[getter]
    fn id(&self) -> InstrumentId { self.id }

    fn make_price(&self, value: f64) -> Price {
        Price::new(value, self.price_precision)
    }

    fn make_qty(&self, value: f64) -> Quantity {
        Quantity::new(value, self.size_precision)
    }
}
```

### New Identifier Types

Identifiers are lightweight string wrappers with `Copy` semantics:

```rust
use pyo3::prelude::*;
use ustr::Ustr;  // Interned string type; add `ustr` to Cargo.toml

#[pyclass]
#[derive(Clone, Copy, Debug, Hash, PartialEq, Eq)]
pub struct MyIdentifier {
    value: Ustr,  // Interned for O(1) equality checks
}

#[pymethods]
impl MyIdentifier {
    #[new]
    fn new(value: &str) -> Self {
        Self { value: Ustr::from(value) }
    }

    fn __repr__(&self) -> String { format!("MyIdentifier('{}')", self.value) }
    fn __hash__(&self) -> u64 { ... }
}
```

### Value Types in Rust

Value types (`Price`, `Quantity`, `Money`) use fixed-point representation internally:
- Standard mode: signed `Price`/`Money` use `i64`; non-negative `Quantity` uses `u64`, with precision 0-9
- High-precision mode: signed `Price`/`Money` use `i128`; `Quantity` uses `u128` (enable `high-precision`)
- Construction: `Price::new(value, precision)` or `Price::from_raw(raw_value, precision)`
- Cross-FFI: use `from_raw` to preserve exact precision when passing between Rust and Python

### PyO3 Binding Conventions

- Use `#[pyclass]` and `#[pymethods]` for Python-visible types
- Register in the owning crate’s `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates that crate submodule
- Identifier types: implement `Hash`, `PartialEq`, `Eq`, `Copy`
- Value types: use `Copy` semantics, implement `Display` for `__repr__`
- Wrap FFI functions in `abort_on_panic(|| { ... })`
- Use `Ustr` (interned strings) for identifiers — O(1) equality and hashing

## Key Conventions

### Identifier String Formats

- `InstrumentId`: `"{symbol}.{venue}"` (e.g., `"ETHUSDT-PERP.BINANCE"`)
- `Venue`: uppercase alphanumeric (e.g., `"BINANCE"`, `"SIM"`)
- `Symbol`: venue-specific format (e.g., `"ETHUSDT-PERP"`, `"EUR/USD"`)
- `TraderId`: `"{name}-{tag}"` (e.g., `"TRADER-001"`)
- `StrategyId`: `"{name}-{tag}"` (e.g., `"EMACross-001"`)

### Instrument Creation Patterns

- Live: Instruments loaded automatically by adapter's `InstrumentProvider`
- Backtest: Created via `TestInstrumentProvider` or loaded from catalog
- Always use `instrument.make_qty()` and `instrument.make_price()` for correct precision

### Value Type Precision

- `Price` and `Quantity` carry precision metadata
- Always construct with correct precision for the instrument
- Use `instrument.make_qty(value)` / `instrument.make_price(value)` helpers
- High-precision mode available for sub-tick precision needs

### Rust ↔ Python Conversion

Value types convert automatically between Rust and Python via PyO3:
- Rust `Price` ↔ Python `Price` (transparent)
- Rust `Quantity` ↔ Python `Quantity` (transparent)
- String identifiers convert via `from_str()` / `to_string()`

## References

- `references/concepts/` — instruments, value types, overview
- `references/api/model/` — identifiers, instruments, orders, position, events, objects, data, book, tick_scheme, index
