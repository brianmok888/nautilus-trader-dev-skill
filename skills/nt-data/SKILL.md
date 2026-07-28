---
name: nt-data
description: "Use when working with market data pipelines, data storage, ParquetDataCatalog, serialization, or cache operations in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-data

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

Data production evidence includes `cargo nextest`, `cargo clippy`, and `cargo deny`; fixed-point validation and Arrow/serialization checks remain mandatory for affected changes.

Data gates: Rust owns serialization, Arrow schemas, catalog/wrangler hot paths, ordering, and fixed-point validation. Mark `Pass` only after Rust tests cover raw fixed-point overflow, schema round-trips, cache/catalog invariants, and any Python exposure remains research/config or PyO3 boundary code.

## What This Skill Covers

NautilusTrader **data infrastructure domain** — data engines, persistence, serialization, and caching.

**Python modules**: `data/` (engine, client, messages), `persistence/`, `serialization/`, `cache/`
**Rust crates**: `nautilus_data`, `nautilus_persistence`, `nautilus_serialization`

## When To Use

- Loading market data from `ParquetDataCatalog`
- Configuring data subscriptions and data engine
- Persisting data to Parquet files
- Arrow serialization and custom schema registration
- Cache queries (instruments, orders, positions, accounts)
- Data wranglers for external data sources
- Integrating Databento or Tardis data

## When NOT To Use

- **Bar aggregation or indicators** → use `nt-signals`
- **Backtest data loading** → use `nt-backtest` (which uses nt-data references)
- **Data model types (instruments, identifiers)** → use `nt-model`
- **Adapter-specific data clients** → use `nt-adapters`

## Python Usage

### ParquetDataCatalog

```python
from nautilus_trader.persistence.catalog import ParquetDataCatalog

# Initialize catalog
catalog = ParquetDataCatalog("/path/to/data")

# Query instruments
instruments = catalog.instruments()

# Query bars
bars = catalog.bars(
    instrument_ids=["ETHUSDT-PERP.BINANCE"],
    bar_type="ETHUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL",
)

# Query trade ticks
trades = catalog.trade_ticks(instrument_ids=["ETHUSDT-PERP.BINANCE"])

# Query quote ticks
quotes = catalog.quote_ticks(instrument_ids=["ETHUSDT-PERP.BINANCE"])

# Write data
catalog.write_data(bars)
catalog.write_data(trade_ticks)
```

### Data Engine Subscriptions

```python
# In Strategy/Actor on_start():
self.subscribe_bars(bar_type)
self.subscribe_quote_ticks(instrument_id)
self.subscribe_trade_ticks(instrument_id)
self.subscribe_order_book_deltas(instrument_id)
self.subscribe_order_book_depth(instrument_id, depth=10)
```

### v1.227.0 data/cache notes

- `DataEngineConfig` / `LiveDataEngineConfig` renamed `time_bars_origins` to `time_bars_origin_offset`.
- `Cache.purge_instrument(...)` trims unused instrument records.
- Rust cache accessors now use scoped borrow wrappers (`OrderRef`, `AccountRef`, `PositionRef`); use `order_owned`, `account_owned`, or `position_owned` when an owned snapshot must cross a boundary. Use `try_order` or `try_order_owned` when a missing order is an error, so callers receive `OrderLookupError` instead of inventing ad hoc not-found errors.
- Custom Arrow storage supports `#[custom_data_field(json)]` for JSON-backed Serde fields with PyO3 dict conversion for `IndexMap` / `HashMap` values.

### Cache Queries

```python
# Access via self.cache in Strategy/Actor:
instrument = self.cache.instrument(instrument_id)
instruments = self.cache.instruments(venue=venue)
order = self.cache.order(client_order_id)
orders = self.cache.orders(instrument_id=instrument_id)
position = self.cache.position(position_id)
positions = self.cache.positions(instrument_id=instrument_id)
account = self.cache.account(account_id)
bar = self.cache.bar(bar_type)
quote = self.cache.quote_tick(instrument_id)
trade = self.cache.trade_tick(instrument_id)
```

### Data Wranglers

```python
from nautilus_trader.persistence.wranglers import BarDataWrangler

wrangler = BarDataWrangler(bar_type=bar_type, instrument=instrument)
bars = wrangler.process(df)  # pandas DataFrame → NautilusTrader Bar objects
```

## Python Extension

### Custom DataClient

```python
from nautilus_trader.data.client import MarketDataClient

class MyDataClient(MarketDataClient):
    def __init__(self, ...):
        super().__init__(...)

    async def _connect(self):
        # Establish connection to data source
        pass

    async def _disconnect(self):
        # Clean up connection
        pass

    async def _subscribe_trade_ticks(self, instrument_id):
        # Subscribe to trade feed
        pass

    def _handle_trade_tick(self, tick):
        # Forward tick to data engine
        self._handle_data(tick)
```

### Custom Arrow Serializers

Register custom Arrow schemas for custom data types:

```python
import pyarrow as pa
from nautilus_trader.serialization.arrow.serializer import register_arrow

# If using @customdataclass, serialization is auto-generated
# For manual registration:
register_arrow(
    data_cls=MyCustomData,
    schema=pa.schema([...]),
    serializer=my_serializer_func,
    deserializer=my_deserializer_func,
)
```

## Rust Usage

```rust
use nautilus_data::engine::DataEngine;
use nautilus_persistence::catalog::ParquetDataCatalog;
use nautilus_serialization::arrow::ArrowSerializer;
```

## Rust Extension

### Custom Persistence Backend

The persistence layer uses Arrow as its intermediate format. Custom backends implement reading/writing Arrow RecordBatches:

```rust
use pyo3::prelude::*;
use arrow::record_batch::RecordBatch;

#[pyclass]
pub struct MyStorageBackend {
    // Backend state (connection pool, file handles, etc.)
}

#[pymethods]
impl MyStorageBackend {
    #[new]
    fn new(connection_str: &str) -> PyResult<Self> { ... }

    fn write_batch(&self, batch: &RecordBatch) -> PyResult<()> { ... }
    fn read_batches(&self, query: &str) -> PyResult<Vec<RecordBatch>> { ... }
}
```

### Custom Arrow Schemas in Rust

For performance-critical serialization, implement Arrow schema conversion in Rust rather than Python. See `crates/serialization/src/arrow/` for the built-in schema implementations.

### PyO3 Binding Conventions

- Use `#[pyclass]` and `#[pymethods]` for Python-visible types
- Register in the owning crate’s `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates that crate submodule
- Arrow types cross the FFI boundary via PyArrow's C Data Interface
- Wrap FFI functions in `abort_on_panic(|| { ... })`

## Key Conventions

### Catalog Query Patterns

- Always filter by `instrument_ids` for efficient queries
- Use `start` and `end` timestamps to bound time range
- Catalog returns data sorted by `ts_event`

### Arrow Schema Registration

- Custom data types using `@customdataclass` auto-register schemas
- Manual registration needed for custom serialization logic
- Schemas define the Parquet column layout

### Data Wrangler Conventions

- Wranglers convert external DataFrames to NT data types
- Input DataFrames should have timestamp index or column
- Use `BarDataWrangler`, `QuoteTickDataWrangler`, `TradeTickDataWrangler`

### Cache Configuration

```python
from nautilus_trader.config import CacheConfig

cache_config = CacheConfig(
    tick_capacity=10_000,
    bar_capacity=10_000,
)
```

## References

- `references/concepts/` — data, cache
- `references/api/` — data, persistence, serialization, cache
- `references/developer_guide/` — test datasets, Databento integration, Tardis integration
- `references/examples/` — data catalog usage
