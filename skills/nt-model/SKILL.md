---
name: nt-model
description: "Use when working with domain model types, instruments, identifiers, value types, enums, or currencies in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-model

## Develop-only order metadata validation

Current `origin/develop` commit
[`d46f56505`](https://github.com/nautechsystems/nautilus_trader/commit/d46f56505)
adds `OrderInitialized::new_checked`. The fallible constructor rejects a
contingent order without linked order IDs and rejects an execution algorithm
without its execution spawn ID. `OrderInitialized::new` now delegates to that
validation and panics on invalid metadata.

This API is newer than the pinned G2 baseline
`8ecab1ce90d9790b1e18e162842decbae4d9de57`. Use `new_checked` when code must
handle invalid external or persisted order metadata, but gate that code on a
current-develop dependency until the baseline advances.

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `8ecab1ce90d9790b1e18e162842decbae4d9de57`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-model` passed the skill domain's scoped examples and owners against `8ecab1ce90d9790b1e18e162842decbae4d9de57`; schema-v2 provenance is recorded in `references/g2-evidence/nt-model.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-model.json`; repository closure is summarized in `docs/tracking/Findings.md`. |


Model gates: Rust owns identifiers, instruments, enums, fixed-point values, and precision-sensitive invariants; Python receives PyO3 bindings only. Mark `Pass` only after `cargo nextest`, `cargo clippy`, `cargo deny`, high-precision/overflow tests, and binding/stub evidence match the current model API.

## Rust production lane

Rust owns identifiers, instruments, enums, currencies, events, and fixed-point values. Enforce precision, overflow, identifier formatting, and instrument invariants at construction boundaries; use owned snapshots when scoped cache wrappers would cross async or event boundaries. New model types belong in `nautilus_model` and must retain exact raw-value semantics across FFI.

```rust
use nautilus_model::{
    identifiers::InstrumentId,
    types::{Price, Quantity},
};

let instrument_id: InstrumentId = "ETHUSDT-PERP.BINANCE".parse()?;
let price = Price::from_raw(185_050, 2);
let quantity = Quantity::from_raw(15, 1);
```

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

Use `references/developer_guide/rust.md` and the model snapshots under `references/api/model/` as source-pinned upstream material at commit `8ecab1ce90d9790b1e18e162842decbae4d9de57`. Version-scope post-pin APIs such as `OrderInitialized::new_checked` until the baseline advances.

Current-develop betting invariant: increasing a same-side `BetPosition` uses a
stake-weighted average price, not an unweighted mean. Preserve constituent
stake in the numerator and total stake in the denominator, and cover both back
and lay increases. Source: upstream develop commit
`fa507199deb34430a983144e4af028046f2af926`.

## What This Skill Covers

NautilusTrader **domain model** — instruments, identifiers, value types, enums, and currencies.

**Python modules**: `model/identifiers`, `model/instruments/`, `model/types/`, `model/objects`, `model/enums`, `model/tick_scheme/`
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
- Standard mode: `i64` backing with precision 0-9
- High-precision mode: `i128` backing (enable `high-precision` feature flag)
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
