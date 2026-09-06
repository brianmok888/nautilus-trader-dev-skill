---
name: nt-data
description: "Use when working with market data pipelines, data storage, ParquetDataCatalog, serialization, or cache operations in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-data

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run python -m pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-data` passed the skill domain's scoped examples and owners against `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`; schema-v2 provenance is recorded in `references/g2-evidence/nt-data.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run python -m pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run python -m pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run python -m pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run python -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-data.json`; repository closure is summarized in `docs/tracking/Findings.md`. |


Data production evidence includes `cargo nextest`, `cargo clippy`, and `cargo deny`; fixed-point validation and Arrow/serialization checks remain mandatory for affected changes.

Data gates: Rust owns serialization, Arrow schemas, catalog/wrangler hot paths, ordering, and fixed-point validation. Mark `Pass` only after Rust tests cover raw fixed-point overflow, schema round-trips, cache/catalog invariants, and any Python exposure remains research/config or PyO3 boundary code.

## Rust production lane

Implement production ingestion, normalization, aggregation, caching, serialization, and catalog access in Rust with deterministic ordering and fixed-point-safe model types. Keep high-volume data handlers and persistence boundaries Rust-owned, and verify schema compatibility, replay behavior, and relevant cargo gates.

## PyO3 control-plane lane

Use PyO3 for bounded configuration, catalog queries, component registration, and result inspection around Rust data services. Do not move streaming handlers, cache mutation authority, aggregation state, or execution-facing data delivery into Python.

## Migration/reference lane

Python migration material is pointer-only here and physically quarantined under `migration_reference/python/` for `nt-data`.

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at immutable commit `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`.

## What This Skill Covers

NautilusTrader **data infrastructure domain** — data engines, persistence, serialization, and caching.

**Python modules**: `data/` (engine, client, messages), `persistence/`, `serialization/`, `common/` (cache: `Cache`, `CacheConfig`)
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

Python production guidance is physically quarantined as migration/reference-only.
See [Python Usage migration reference](migration_reference/python/python-usage.md).
New production work follows the Rust or bounded PyO3 sections below.

## Python Extension

Python production guidance is physically quarantined as migration/reference-only.
See [Python Extension migration reference](migration_reference/python/python-extension.md).
New production work follows the Rust or bounded PyO3 sections below.

## V2 data-engine and cache invariants

- `DataEngineConfig` and `LiveDataEngineConfig` use `time_bars_origin_offset`.
- Rust cache accessors use scoped borrow wrappers. Use `order_owned` when an
  owned snapshot must cross a boundary, and `try_order` or `try_order_owned`
  when missing order state is an error.
- Cache backing stores live in `nautilus_trader.infrastructure` (Rust:
  `crates/infrastructure/src/{redis,sql}`). `PostgresCacheConfig` and
  `RedisCacheConfig` configure durable cache backing; `RedisMessageBusBacking`/
  `RedisMessageBusConfig` configure Redis-backed message buses. There is no
  `nautilus_trader.cache` Python module at the pinned tree -- `Cache` and
  `CacheConfig` are exported from `nautilus_trader.common`.

## Rust Usage

```rust
use nautilus_data::engine::DataEngine;
use nautilus_persistence::backend::catalog::ParquetDataCatalog;
use nautilus_serialization::arrow::EncodeToRecordBatch;
```

## Cache accessor delta (develop-line)
Source: upstream NautilusTrader commit `aabb824cb377d62ea7ff6a7ce9489a92c705580a`, included in the pinned G2 baseline.

The cache adds `mark_price_count`, `index_price_count`,
`funding_rate_count`, `instrument_status_count`, `has_mark_prices`,
`has_index_prices`, `has_funding_rates`, and `has_instrument_statuses` at the
pinned G2 baseline `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`.

## Rust Extension

### Persistence extension boundary

The pinned V2 persistence crate does not expose a generic custom-backend trait
or PyO3 backend protocol. Do not invent one. Extend a concrete catalog or
persistence implementation only after locating its current trait/configuration
seam under `crates/persistence/`.

### Custom Arrow Schemas in Rust

Register custom schemas, encoders, and decoders with
`nautilus_model::data::register_arrow`, then create `CustomData` values and
persist through `ParquetDataCatalog::write_custom_data_batch(Vec<CustomData>)`
(Rust) or `ParquetDataCatalog.write_custom_data(...)` (PyO3). Built-in Arrow
serializers may remain where upstream owns them, but custom registration belongs
to `nautilus_model::data`. Prove an unregistered write fails explicitly, then
round-trip payloads, metadata, `ts_event`, and `ts_init`.

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

- Rust: use `nautilus_model::data::register_arrow`
- Python: use `nautilus_trader.model.register_custom_data_class`
- Manual callbacks define the Parquet column layout; schemas are not auto-generated

### Data Wrangler Conventions

- Wranglers convert external data to NT data types via the bytes-based
  `process_record_batch_bytes(data: bytes)` API
- Construct with `(instrument_id, price_precision, size_precision)`; precisions
  are required (no inference)
- Use `BarDataWrangler`, `QuoteTickDataWrangler`, `TradeTickDataWrangler`,
  `OrderBookDeltaDataWrangler`, `OrderBookDepth10DataWrangler` (flat exports of
  `nautilus_trader.persistence`)
- The legacy DataFrame-based `process(pd.DataFrame)` framing is documented in the
  serialization patterns guide (`serialization_patterns.md` in this skill's guides tree)

### Streaming Feather Writer

`StreamingFeatherWriter` (flat export of `nautilus_trader.persistence`) streams
cache data to rotating Feather files: construct with
`(path, cache, clock, ...)` and optional `rotation_mode` (int; 3 = no rotation,
2 = scheduled dates, 1 = interval, 0 = size), `max_file_size`,
`rotation_interval_ns`, `rotation_time_ns`, `rotation_timezone`,
`flush_interval_ms`, and `replace`. `subscribe()` starts cache-driven writes,
`close()` finalizes the file. `StreamingConfig` carries the equivalent catalog
path (`catalog_path`, `fs_protocol`, `flush_interval_ms`, `replace_existing`,
`rotation_mode: str`, `max_file_size`, `rotation_interval_ns`, `schedule_ns`)
for engine-level streaming configuration.

### Cache Configuration

The Python `CacheConfig` example is migration/reference-only; see
[Python Usage migration reference](migration_reference/python/python-usage.md).
Keep production cache configuration and capacity-sensitive state Rust-owned.

## References

- `references/concepts/` — data, cache
- `references/api/` — data, persistence, serialization, cache
- `references/developer_guide/` — test datasets, Databento integration, Tardis integration
- `migration_reference/python/examples/data_catalog/` — quarantined Python data-catalog usage
