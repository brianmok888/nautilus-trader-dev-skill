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
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; current-develop drift is version-scoped in `README.md`. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 25 tests. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-data` passed the skill domain's scoped examples and owners against `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; schema-v2 provenance is recorded in `references/g2-evidence/nt-data.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 tests. |
| G4 Lane and API shape | Classify migration-only Python, active AI/advisory Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'` passed 24 tests. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md` records the post-fix audit; `uv run python tools/check_skill_g2_harnesses.py --check-cards` validates all 18 cards and evidence artifacts. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Data production evidence includes `cargo nextest`, `cargo clippy`, and `cargo deny`; fixed-point validation and Arrow/serialization checks remain mandatory for affected changes.

Data gates: Rust owns serialization, Arrow schemas, catalog/wrangler hot paths, ordering, and fixed-point validation. Mark `Pass` only after Rust tests cover raw fixed-point overflow, schema round-trips, cache/catalog invariants, and any Python exposure remains research/config or PyO3 boundary code.

## Rust production lane

## PyO3 control-plane lane

## Migration/reference lane

Python migration material is pointer-only here and physically quarantined under `migration_reference/python/` for `nt-data`.

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at `6e59fd74eaacacbb7410936f1766bd89fcce6f59`.

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

Non-AI Python guidance is physically quarantined as migration/reference-only.
See [Python Usage migration reference](migration_reference/python/python-usage.md).
New production work follows the Rust or bounded PyO3 sections below; the sole
active Python lane is AI/advisory work in `nt-evomap-integration`.

## Python Extension

Non-AI Python guidance is physically quarantined as migration/reference-only.
See [Python Extension migration reference](migration_reference/python/python-extension.md).
New production work follows the Rust or bounded PyO3 sections below; the sole
active Python lane is AI/advisory work in `nt-evomap-integration`.

## V2 data-engine and cache invariants

- `DataEngineConfig` and `LiveDataEngineConfig` use `time_bars_origin_offset`.
- Rust cache accessors use scoped borrow wrappers. Use `order_owned` when an
  owned snapshot must cross a boundary, and `try_order` or `try_order_owned`
  when missing order state is an error.

## Rust Usage

```rust
use nautilus_data::engine::DataEngine;
use nautilus_persistence::catalog::ParquetDataCatalog;
use nautilus_serialization::arrow::ArrowSerializer;
```

## Develop-only cache accessor delta
Source: upstream NautilusTrader commit `aabb824cb377d62ea7ff6a7ce9489a92c705580a`.

This post-pin develop snapshot adds `mark_price_count`, `index_price_count`,
`funding_rate_count`, `instrument_status_count`, `has_mark_prices`,
`has_index_prices`, `has_funding_rates`, and `has_instrument_statuses`.
Treat these accessors as develop-only until the reproducible upstream baseline
advances.

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

The Python `CacheConfig` example is migration/reference-only; see
[Python Usage migration reference](migration_reference/python/python-usage.md).
Keep production cache configuration and capacity-sensitive state Rust-owned.

## References

- `references/concepts/` — data, cache
- `references/api/` — data, persistence, serialization, cache
- `references/developer_guide/` — test datasets, Databento integration, Tardis integration
- `migration_reference/python/examples/data_catalog/` — quarantined Python data-catalog usage
