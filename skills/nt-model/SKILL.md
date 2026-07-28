---
name: nt-model
description: "Use when working with domain model types, instruments, identifiers, value types, enums, or currencies in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-model

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as f20f8af36e0f488779d3f543a217b2d19ea2db81. |
| G1 Lane classification | Classify the work as Rust execution-critical/performance, supported Python V2 strategy/config, Python AI/advisory, or legacy. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template lane inventory and Python/Rust V2 strategy boundary tests. |
| G2 Legacy label | Label legacy Cython/v1 and Python live TradingNode guidance as migration/reference-only. | Pass | Compatibility note in this file names legacy Cython/v1 and Python live `TradingNode` as migration/reference-only. |
| G3 Rust ownership | Rust owns runtime, adapter networking/parsing, normalization, risk/execution state, and performance-sensitive paths; Python and Rust strategies remain supported V2 surfaces. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the ownership-boundary regression tests; `references/developer_guide/python.md:12-14` records upstream Python strategy support. |
| G4 NT V2 API shape | Use current NT V2/PyO3 API shapes and crate/module boundaries instead of retired APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` byte-compared all 18 guide bodies to pinned upstream f20f8af; `uv run pytest -q tests/test_v2_guidance_hardening.py` passed current API-shape regressions. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 253 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 106 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pending | Final Phase 4 reconciliation, logical commit SHAs, and push evidence are recorded only after the working tree is committed and pushed. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Model gates: Rust owns identifiers, instruments, enums, fixed-point values, and precision-sensitive invariants; Python receives PyO3 bindings only. Mark `Pass` only after `cargo nextest`, `cargo clippy`, `cargo deny`, high-precision/overflow tests, and binding/stub evidence match the current model API.

## What This Skill Covers

NautilusTrader **domain model** — instruments, identifiers, value types, enums, and currencies.

**Python modules**: `model/identifiers`, `model/instruments/` (14 types), `model/types/`, `model/objects`, `model/enums`, `model/tick_scheme/`
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

## Python Usage

### v1.227.0 model deltas

- `InstrumentId::parse_parent_components` and `InstrumentClass` parent suffix conversion helpers are exposed via PyO3.
- Rust cache model accessors may return scoped wrapper newtypes (`OrderRef`, `AccountRef`, `PositionRef`) rather than raw references; request owned snapshots when values cross async/event boundaries.

### Identifiers

```python
from nautilus_trader.model.identifiers import InstrumentId, Venue, Symbol, TraderId, StrategyId

instrument_id = InstrumentId.from_str("ETHUSDT-PERP.BINANCE")
venue = Venue("BINANCE")
symbol = Symbol("ETHUSDT-PERP")

# Identifier components
instrument_id.venue  # Venue("BINANCE")
instrument_id.symbol  # Symbol("ETHUSDT-PERP")
```

### Value Types

```python
from nautilus_trader.model.objects import Price, Quantity, Money, Currency

# Price with precision
price = Price.from_str("1850.50")
price = Price(1850.50, precision=2)

# Quantity with precision
qty = Quantity.from_str("1.5")
qty = Quantity(1.5, precision=1)

# Money
balance = Money(10_000, Currency.from_str("USD"))
balance = Money.from_str("10000 USD")

# Arithmetic
total = price * qty  # Returns float
```

### Instruments

```python
from nautilus_trader.model.instruments import CurrencyPair, Equity, CryptoPerpetual, FuturesContract

# Instruments are typically loaded from adapters or created for backtests
# Access via cache:
instrument = self.cache.instrument(instrument_id)

# Key properties:
instrument.id           # InstrumentId
instrument.venue        # Venue
instrument.base_currency    # Currency (for pairs)
instrument.quote_currency   # Currency
instrument.price_precision  # int
instrument.size_precision   # int
instrument.lot_size         # Quantity
instrument.min_quantity     # Quantity
instrument.max_quantity     # Quantity
instrument.min_price        # Price
instrument.max_price        # Price

# Create quantity/price with correct precision:
qty = instrument.make_qty(1.5)
price = instrument.make_price(1850.50)
```

**14 instrument types:**
- `CurrencyPair` — FX pairs (EUR/USD)
- `Equity` — stocks
- `FuturesContract` — dated futures
- `OptionContract` — dated options
- `CryptoPerpetual` — perpetual swaps
- `CryptoFuture` — crypto dated futures
- `CryptoOption` — crypto options
- `Commodity` — commodities
- `Index` — indices
- `CFD` — contracts for difference
- `BettingInstrument` — betting markets
- `BinaryOption` — binary options
- `SyntheticInstrument` — user-defined synthetic
- `Instrument` — base class

### Enums

```python
from nautilus_trader.model.enums import (
    OrderSide,       # BUY, SELL
    OrderType,       # MARKET, LIMIT, STOP_MARKET, STOP_LIMIT, etc.
    TimeInForce,     # GTC, IOC, FOK, GTD, DAY
    PositionSide,    # LONG, SHORT, FLAT
    OmsType,         # HEDGING, NETTING
    AccountType,     # CASH, MARGIN
    OrderStatus,     # INITIALIZED, SUBMITTED, ACCEPTED, FILLED, CANCELED, etc.
    BarAggregation,  # TICK, SECOND, MINUTE, HOUR, DAY, etc.
    PriceType,       # BID, ASK, MID, LAST
    BookType,        # L1_MBP, L2_MBP, L3_MBO
)
```

### Currencies

```python
from nautilus_trader.model.currencies import BTC, ETH, USD, USDT

# Or dynamically:
currency = Currency.from_str("USD")
```

## Python Extension

### SyntheticInstrument

```python
from nautilus_trader.model.instruments import SyntheticInstrument

# Define a synthetic instrument from a formula combining other instruments
synthetic = SyntheticInstrument(
    symbol=Symbol("SPREAD-1"),
    price_precision=2,
    components=[instrument_id_1, instrument_id_2],
    formula="(component_0 - component_1)",
)
```

### Custom Tick Schemes

```python
from nautilus_trader.model.tick_scheme import TickScheme

# Define custom tick schemes for instruments with non-uniform tick sizes
```

## Rust Usage

```rust
use nautilus_model::identifiers::{InstrumentId, Venue, Symbol};
use nautilus_model::instruments::CryptoPerpetual;
use nautilus_model::types::{Price, Quantity, Money};
use nautilus_model::enums::{OrderSide, OrderType};
```

## Rust Extension

### New Instrument Types

All 14 instrument types are defined in Rust (`crates/model/src/instruments/`) and exposed to Python via PyO3. New instruments follow the same pattern:

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
use nautilus_model::identifier::Ustr;  // Interned string type

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
