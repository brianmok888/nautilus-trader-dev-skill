NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-implement Knowledge Base

**Purpose:** Implement NautilusTrader components using correct patterns and templates. Covers Python components, simulation models, Rust+PyO3 bindings, and adapter development.

**Entry Point:** `SKILL.md` (555 lines)

## TEMPLATE QUICK REFERENCE (5 files)

| Need | Template | Key Feature |
|------|----------|-------------|
| Cap'n Proto schema | `capnp_schema.capnp` | Zero-copy serialization schema |
| Exchange connectivity migration reference | `legacy_migration/adapters/exchange.py` | Legacy Python LiveDataClient, LiveExecutionClient |
| Data-only adapter | `legacy_migration/adapters/data_provider.py` | Data streaming only |
| Exchange-specific config example | `legacy_migration/adapters/kraken_config.py` | Venue configuration patterns |
| Backtest visualization | `legacy_migration/backtest_viz.py` | Plotly tearsheet config |

## IMPLEMENTATION WORKFLOW

Dependency order:
1. Custom Data Types (if needed)
2. Custom Models (FillModel, MarginModel if backtesting)
3. Indicators
4. Actors
5. Strategies
6. Execution Algorithms (if needed)
7. Portfolio Statistics (for analysis)

Validate each component before proceeding to the next.

## v1.223.0 API ADDITIONS (2026-02-21)

Legacy/migration note: the v1.223/v1.224 tables below are historical Python-changelog records, not current API guidance; verify every symbol against the pinned v2 tree before use.

| Feature | Usage |
|---------|-------|
| `strategy.market_exit()` | Fully close position with market order (config-driven TIF/reduce-only) |
| `StrategyConfig.manage_stop = True` | Auto-calls `market_exit()` on strategy stop |
| `PerpetualContract` | Prefer over `CryptoPerpetual` for new implementations |
| `request_funding_rates()` / `FundingRateUpdate` | Funding rate data streams |
| `BacktestDataConfig.optimize_file_loading` | Faster Parquet loading for large backtests |
| `trade_execution` default `True` | Set `False` explicitly for bar-only matching |

## v1.224.0 CHANGES (2026-03-03)

| Change | Impact |
|--------|--------|
| `InstrumentProvider` defaults | Only `load_all_async` required; `load_ids_async`/`load_async` have defaults |
| `fill_limit_at_touch` → `fill_limit_inside_spread` | Renamed; `BestPriceFillModel` fills inside spread by default |
| Coinbase International adapter removed | `COINBASE_INTX` deleted; use different venue |
| Binance Ed25519 Spot/Margin | Now raises `ValueError`; Futures soft-deprecated |
| Hyperliquid `builder_fee_refresh_mins` | Config removed |

## KEY IMPLEMENTATION PATTERNS

### Model Loading
- **Preferred:** `msgspec.msgpack.decode()` — fast, typed deserialization
- **ONNX:** `ort.InferenceSession` in `on_start`, inference in `on_bar`
- **Never** load models in hot handlers — always `on_start`

### Data Catalog
- `ParquetDataCatalog` for persistence
- Write instruments before other data
- Use `BacktestDataConfig` for custom data with `metadata` dict

### Multi-Timeframe
- Define `BarType` for each timeframe
- Use internal aggregation: `5-MINUTE-LAST-INTERNAL@1-MINUTE-EXTERNAL`
- Request historical for all, then subscribe live

### Position Sizing
- Use `instrument.make_qty()` for precision (never raw `float`)
- Check `min_quantity` / `max_quantity`
- Risk-based: `(equity * risk_per_trade) / (ATR * multiplier)`

### Risk Checks
- Pre-trade validation: position limits, exposure limits, daily loss
- Use `self.portfolio.net_position()` and `self.portfolio.net_exposure()`

## ADAPTER CANONICAL CONTRACT

**Ten-Phase Implementation Sequence (Phase 0-9):**
1. Phase 0: Define scope - capability matrix, venue constraints, protocol boundaries, initial slice
2. Phase 1: Build the protocol core - HTTP/WS clients, models, parsing, protocol tests
3. Phase 2: Implement instruments - parsing, loading, symbol mapping, updates
4. Phase 3: Implement market data - public streams, historical requests, order books
5. Phase 4: Implement execution - account bootstrap, reconciliation, order flow
6. Phase 5: Add optional venue capabilities - advanced order types, batch operations, venue data
7. Phase 6: Complete factories and projection - configs, Rust factories, PyO3 registration
8. Phase 7: Prove conformance - unit, integration, mock-transport tests
9. Phase 8: Measure performance and robustness
10. Phase 9: Finish documentation and operations

**Required Rust traits:**
- `InstrumentProvider`: `load_all(filters)`, `load_ids(instrument_ids, filters)`, `load(instrument_id, filters)`
- `DataClient` / `ExecutionClient`: full trait implementations for market data and order execution plus reconciliation report generation
- Factories: `DataClientFactory::create(name, config, cache: CacheView, clock)` and `ExecutionClientFactory::create(trader_id, name, config, cache: CacheView)`, registered via `LiveNodeBuilder::add_data_client` / `add_exec_client`

(The v1 Python `LiveDataClient`/`LiveExecutionClient` class families and the `create(loop, name, config, msgbus, cache, clock)` factory signature are migration/reference-only.)

**Testing doctrine:**
- Real captured payload fixtures (not invented schemas)
- No arbitrary sleeps in async tests; use condition-based waiting
- Cover: providers, data, execution, factories

## RUST+PyO3 PATTERNS

### Constructor Pattern
```rust
pub fn new_checked(params) -> anyhow::Result<Self> { ... }
pub fn new(params) -> Self { Self::new_checked(params).expect(FAILED) }
```

### FFI Memory Safety
- `#[repr(C)]` struct wrapping `Box<Inner>`
- `abort_on_panic(|| { ... })` on all FFI functions
- Matching drop for every constructor
- Type-specific CVec drops (never generic)

### PyO3 Conventions
- `py_*` prefix on Rust function names
- `#[pyo3(name = "...")]` for clean Python API
- Plain `PyObject` / `Py<T>` for ordinary callbacks; `Arc<Py<T>>` only with documented shared-ownership need, cycle audit, and cleanup plan
- Manual `Clone` using `clone_py_object()`

### Runtime
- `get_runtime().spawn()` in adapter code (never `tokio::spawn()` from Python threads)
- `#[rstest]` for all Rust tests
- `#![deny(unsafe_op_in_unsafe_fn)]` in every crate

## CODING STANDARDS

### Python
- Type hints on all signatures: `def on_bar(self, bar: Bar) -> None:`
- NumPy docstrings, imperative mood
- Config classes: `{Component}Config`
- Strategy IDs: `{Class}-{tag}`
- Instrument IDs: `{symbol}.{venue}`
- 100 char line limit, trailing commas

### Rust
- `anyhow::Result<T>` + `anyhow::bail!` for fallible functions
- Fully qualify `anyhow::` and `tokio::` macros
- `log::*` macros everywhere (fully qualified, e.g. `log::debug!`) per the pinned Rust guide (`docs/developer_guide/rust.md:296`); `tracing` appears only in the Interactive Brokers adapter, not as a general convention
- Capitalize messages, omit terminal periods
- Rust doc comments: **indicative mood** ("Returns the client", not "Return")

## IMPLEMENTATION CHECKLIST

- Config class defined with all parameters
- Type hints on all methods
- `on_start` initializes state and subscriptions
- `on_stop` cleans up (cancel orders, unsubscribe)
- Historical data requested for warmup
- No blocking calls in handlers
- Proper null checks before using cached data
- Logging at appropriate levels

## REFERENCES (symlinked)

- `references/api_reference/` — trading.md, common.md, backtest.md, analysis.md, live.md
- `references/developer_guide/` — python.md, rust.md, ffi.md, adapters.md, benchmarking.md
- `references/concepts/` — backtesting.md, live.md

## NEXT STEP

After implementation → **nt-review** skill for validation.
