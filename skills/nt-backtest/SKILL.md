---
name: nt-backtest
description: "Use when working with backtesting engine, fill models, matching engine, simulated exchange, or backtest configuration in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-backtest

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run python -m pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-backtest` passed the skill domain's scoped examples and owners against `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`; schema-v2 provenance is recorded in `references/g2-evidence/nt-backtest.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run python -m pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run python -m pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run python -m pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run python -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-backtest.json`; repository closure is summarized in `docs/tracking/Findings.md`. |


Backtest gates: use Rust `BacktestEngine`/`BacktestNode` for research, configuration, production, and performance simulation; all Python backtest material is migration/reference-only. Require deterministic ordering, fill-model, account/position reconciliation, `cargo nextest`, `cargo clippy`, and `cargo deny` evidence before `Pass`.

Compatibility note: the historical phrase `Python research/config` names only
the quarantined migration material; the active path is Rust BacktestEngine.

## Rust production lane

Build production and performance simulations with Rust `BacktestEngine` or `BacktestNode`, Rust strategies, deterministic event ordering, and explicit venue, fill, fee, latency, account, and reconciliation models. Keep matching and execution-critical simulation behavior in Rust and validate it with targeted tests plus the required cargo gates.

## PyO3 control-plane lane

Use PyO3 only to assemble backtest configuration, register Rust components, initiate bounded runs, and inspect immutable results. Python must not own matching, fill decisions, order submission, risk checks, or event sequencing; those remain inside the Rust engine.

### Develop/nightly-only PyO3 `CustomData` injection

Source: upstream develop commit `998005124e298e9b0c2f6c60be21e581f3426da1`.
This API is **develop/nightly only** and is not available in the pinned baseline or stable releases; version-gate it and re-check upstream before use.

The PyO3 `BacktestEngine.add_data(...)` conversion now accepts model
`CustomData` and forwards it as Rust `Data::Custom`. Use this as bounded control/data injection for timestamped inputs that Rust actors or strategies
consume. Validation does not require an instrument for custom data, while the
normal ordering and run boundaries still apply.

This capability does not widen Python authority: Python may prepare and inject
the custom payloads, but matching and execution remain Rust-owned. It is not a
path for Python fill decisions, matching logic, risk checks, order execution,
or authoritative event sequencing.

## Migration/reference lane

Python migration material is pointer-only here and physically quarantined under `migration_reference/python/` for `nt-backtest`.

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at immutable commit `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`.

## What This Skill Covers

NautilusTrader **backtesting domain** — backtest engine, simulated exchange, fill models, and matching logic.

**Python modules**: `backtest/`, `execution/` (both flat at the pinned tree)
**Rust crates**: `nautilus_backtest`, `nautilus_execution` (matching engine incl. the Rust-only `matching_core` module)

## When To Use

- Setting up and running backtests (`BacktestNode`, `BacktestEngine`)
- Configuring simulated exchanges and venues
- Customizing fill models, latency models, fee models
- Backtest configuration (`BacktestRunConfig`, `BacktestVenueConfig`)
- Understanding matching engine behavior
- Benchmarking backtest performance

## When NOT To Use

- **Strategy/order logic** → use `nt-trading`
- **Data loading/catalog** → use `nt-data`
- **Live deployment** → use `nt-live`
- **Indicator logic** → use `nt-signals`

## `BacktestResult` analysis (develop-line)
Source: upstream NautilusTrader pin `73d4dd5b3be4cb198bb20c89da6963c85eb24f3a` (state verified at that pin; kept as historical citation).

Upstream commit
[`501ebe4a8`](https://github.com/nautechsystems/nautilus_trader/commit/501ebe4a8),
included in the pinned G2 baseline, adds `BacktestResult.returns_series`. Rust stores it as an ordered
`BTreeMap<UnixNanos, f64>`; the PyO3 property is `dict[int, float]`, keyed by
nanosecond timestamps. It supports a result-only tearsheet after the node or
engine is no longer retained. A cache-backed chart still needs live node state,
and multi-currency analysis should pass an explicit currency where the
tearsheet API requires one.

The property is present at the pinned G2 baseline `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`.
The pinned result statistics (`stats_pnls`, `stats_returns`, and
`stats_general`) remain available.

## v1.227.0 backtest/matching deltas
Source: upstream NautilusTrader pin `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`.

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

- Continuous futures can be used with adjusted aggregated bars.
- `time_bars_origins` is now `time_bars_origin_offset` in data-engine configs.
- `OrderMatchingEngineConfig` defaults were aligned with the Cython per-engine constructor.
- `OrderMatchingCore` exposes tick-size updates and zero-allocation `iter_*` read-only APIs used by trailing-stop and GTD timing logic.

## Python Usage

Python production guidance is physically quarantined as migration/reference-only.
See [Python Usage migration reference](migration_reference/python/python-usage.md).
New production work follows the Rust or bounded PyO3 sections below.

## Python Extension

Python production guidance is physically quarantined as migration/reference-only.
See [Python Extension migration reference](migration_reference/python/python-extension.md).
New production work follows the Rust or bounded PyO3 sections below.

## Rust Usage

NautilusTrader provides two Rust APIs for backtesting: `BacktestEngine` (low-level) and `BacktestNode` (high-level with catalog streaming). Both run without Python.

### Dependencies

Add to your `Cargo.toml`:

```toml
[dependencies]
nautilus-backtest = { version = "0.63", features = ["streaming"] }
nautilus-execution = "0.63"
nautilus-model = { version = "0.63", features = ["test-support"] }
nautilus-persistence = "0.63"
nautilus-trading = { version = "0.63", features = ["examples"] }

ahash = "0.8"
anyhow = "1"
tempfile = "3"
ustr = "1"
```

Drop `streaming`, `nautilus-persistence`, `tempfile`, `ustr` if only using the low-level `BacktestEngine`.

**Feature flags:**

| Flag | Crate | Effect |
|---|---|---|
| `high-precision` | `nautilus-model` | 16-digit fixed precision (default 9). Required for crypto. |
| `test-support` | `nautilus-model` | Test support (pulls in `rstest`). The `stubs` module (`audusd_sim`, etc.) is compiled unconditionally -- no feature flag. |
| `examples` | `nautilus-trading` | Example strategies (`EmaCross`, `GridMarketMaker`) |
| `streaming` | `nautilus-backtest` | Catalog-based data streaming via `BacktestNode` |
| `defi` | `nautilus-backtest` | DeFi data support (`nautilus-model/defi`, 18-decimal wei precision, implies `high-precision`). With the feature enabled, `add_data` transparently registers a DeFi data client when a batch contains `Data::Defi` items. |

### BacktestEngine (Low-Level API)

Direct control: build engine, add venues/instruments, load data in memory, register strategies, run.

```rust
use nautilus_backtest::{
    config::{BacktestEngineConfig, SimulatedVenueConfig},
    engine::BacktestEngine,
};
use nautilus_model::{
    enums::{AccountType, BookType, OmsType},
    identifiers::Venue,
    instruments::{Instrument, InstrumentAny, stubs::audusd_sim},
    types::{Money, Quantity},
};
use nautilus_trading::examples::strategies::EmaCross;

// 1. Create engine
let mut engine = BacktestEngine::new(BacktestEngineConfig::default())?;

// 2. Add venue through the current typed configuration builder.
engine.add_venue(
    SimulatedVenueConfig::builder()
        .venue(Venue::from("SIM"))
        .oms_type(OmsType::Hedging)
        .account_type(AccountType::Margin)
        .book_type(BookType::L1_MBP)
        .starting_balances(vec![Money::from("1_000_000 USD")])
        .build()?,
)?;

// 3. Add instrument and data
let instrument = InstrumentAny::CurrencyPair(audusd_sim());
let instrument_id = instrument.id();
engine.add_instrument(&instrument)?;
let quotes = generate_quotes(instrument_id);
engine.add_data(quotes, None, true, true);

// 4. Register strategy and run
let strategy = EmaCross::new(instrument_id, Quantity::from("100000"), 10, 20);
engine.add_strategy(strategy)?;
engine.run(None, None, None, false)?;
```

Run the example: `cargo run -p nautilus-backtest --features examples --example engine-ema-cross`

### Typed batch input/replay (drift window)

`BacktestEngine::add_data_batch(data, client_id, validate, sort)`
(`crates/backtest/src/engine.rs:436` at the pin) accepts a single typed
`DataBatch` (`crates/model/src/data/batch.rs`) instead of per-item `Data`
values. The batch keeps concrete storage per data family and replays its items
as `DataRef`s, avoiding heterogeneous `Vec<Data>` assembly for uniform streams:

```rust
use nautilus_model::data::{DataBatch, QuoteTick};

// Vec<QuoteTick> converts into a typed DataBatch via From<Vec<T>>.
let batch = DataBatch::from(quotes_vec);
engine.add_data_batch(batch, None, true, true)?;
```

On the high-level side, `BacktestNode` now streams data lazily across multiple
`BacktestDataConfig` entries (upstream commit `ec1894d6f`): every data config is
queried separately and k-way merged by `ts_init`, so the `chunk_size` memory
bound also holds for multi-config runs instead of falling back to a merged
`Vec<Data>` load.

### BacktestNode (High-Level API)

Loads data from `ParquetDataCatalog` and streams in configurable chunks. Requires `streaming` feature.

Current-develop window contract (upstream commit
`4175a5f09a4e3563a00423f43625f9a187823f4a`): a bounded run peeks before
consuming. The first item past `requested_end` remains available to a later
run instead of being discarded. When no data has arrived, inferred clock
advancement is capped at 10 seconds; an explicit end still controls the run
boundary. Regression tests must prove both post-window retention and bounded
no-data advancement.

```rust
use nautilus_backtest::{
    config::{BacktestDataConfig, BacktestEngineConfig, BacktestRunConfig, BacktestVenueConfig, NautilusDataType},
    node::BacktestNode,
};
use nautilus_model::enums::{AccountType, BookType, OmsType};
use nautilus_persistence::backend::catalog::ParquetDataCatalog;
use ustr::Ustr;

// 1. Write data to catalog
let catalog = ParquetDataCatalog::new(catalog_path, None, None, None, None);
catalog.write_instruments(vec![instrument])?;
catalog.write_to_parquet(&quotes, None, None, None)?;

// 2. Configure the run (configs use builder pattern)
let venue_config = BacktestVenueConfig::builder()
    .name(Ustr::from("SIM"))
    .oms_type(OmsType::Hedging)
    .account_type(AccountType::Margin)
    .book_type(BookType::L1_MBP)
    .starting_balances(vec!["1_000_000 USD".to_string()])
    .build()?;

let data_config = BacktestDataConfig::builder()
    .data_type(NautilusDataType::QuoteTick)
    .catalog_path(catalog_path.to_string())
    .instrument_id(instrument_id)
    .build()?;

let run_config = BacktestRunConfig::builder()
    .id("ema-cross-run".to_string())
    .venues(vec![venue_config])
    .data(vec![data_config])
    .maybe_chunk_size(Some(100))
    .build()?;

// `BacktestRunConfig.id` defaults to a random UUID4; `get_engine_mut` is a
// plain map lookup by that id, so set an explicit `.id(...)` when you need to
// fetch the engine afterwards.

// 3. Build, add strategies, run
let mut node = BacktestNode::new(vec![run_config])?;
node.build()?;

let engine = node.get_engine_mut("ema-cross-run").context("engine not found")?;
engine.add_strategy(EmaCross::new(instrument_id, Quantity::from("100000"), 10, 20))?;

node.run()?;
```

Run the example: `cargo run -p nautilus-backtest --features examples,streaming --example node-ema-cross`

### Registering Actors

Actors register with `add_actor` (same pattern as strategies):

```rust
let actor = SpreadMonitor::new(instrument_id);
engine.add_actor(actor)?;
```

### Simulation Modules

Venue-level simulation logic beyond the core matching loop plugs in through the
`modules` field of `SimulatedVenueConfig` (`Vec<SimulationModuleHandle>`, empty
by default). A module implements the `SimulationModule` trait
(`crates/backtest/src/modules/mod.rs`): `pre_process` filters/adapts market
data before the matching engine sees it, `process` returns a batch of account
balance adjustments at the current timestamp, and `acknowledge` confirms the
ordered application outcomes of each completed batch.

Shipped modules:

- `FXRolloverInterestModule` -- FX rollover interest from OECD-style records
  (`InterestRateRecord { location, time, value }`; e.g. `"AUS"`, `"2024-01"`, `5.25`).
- `CfdSwapModule` -- CFD swap adjustments from `CfdSwapRate` records plus a
  rollover time and triple-roll weekday.

```rust
use nautilus_backtest::modules::{
    fx_rollover::InterestRateRecord, FXRolloverInterestModule, SimulationModuleHandle,
};

let rollover = FXRolloverInterestModule::new(vec![InterestRateRecord {
    location: "AUS".to_string(),
    time: "2024-01".to_string(),
    value: 5.25,
}])?;

let venue = SimulatedVenueConfig::builder()
    .venue(Venue::from("SIM"))
    // ... other venue settings ...
    .modules(vec![SimulationModuleHandle::new(rollover)])
    .build()?;
```

Python-authored modules are supported through the PyO3 `SimulationModule`/
`PythonSimulationModule` bridge (`crates/backtest/src/python/modules.rs`).

## Rust Extension (PyO3 Path)

### Performance-Optimized Fill Models

Rust fill models for complex matching logic (order book simulation, market impact):

```rust
use nautilus_execution::models::fill::{FillModel, FillModelHandle, ProbabilisticFillState};
use nautilus_model::{
    data::order::BookOrder,
    enums::{BookType, OrderSide},
    instruments::InstrumentAny,
    orderbook::OrderBook,
    orders::OrderAny,
    types::{Price, Quantity},
};

#[derive(Debug)]
pub struct MyFillModel {
    state: ProbabilisticFillState,
}

impl MyFillModel {
    pub fn new(prob_fill_on_limit: f64, prob_slippage: f64) -> anyhow::Result<Self> {
        Ok(Self {
            state: ProbabilisticFillState::new(prob_fill_on_limit, prob_slippage, Some(42))?,
        })
    }
}

impl FillModel for MyFillModel {
    fn is_limit_filled(&mut self) -> anyhow::Result<bool> {
        Ok(self.state.is_limit_filled())
    }

    fn is_slipped(&mut self) -> anyhow::Result<bool> {
        Ok(self.state.is_slipped())
    }

    fn get_orderbook_for_fill_simulation(
        &mut self,
        instrument: &InstrumentAny,
        _order: &OrderAny,
        best_bid: Price,
        best_ask: Price,
    ) -> anyhow::Result<Option<OrderBook>> {
        // Build the liquidity view yourself; the trait has no helper for this.
        let mut book = OrderBook::new(instrument.id(), BookType::L2_MBP);
        let size_prec = instrument.size_precision();
        let size = Quantity::from_mantissa_exponent(10_000_000_000, 0, size_prec);
        book.add(
            BookOrder::new(OrderSide::Buy, best_bid, size, 1),
            0,
            0,
            Default::default(),
        );
        book.add(
            BookOrder::new(OrderSide::Sell, best_ask, size, 2),
            0,
            0,
            Default::default(),
        );
        Ok(Some(book))
    }
}

let fill_model = MyFillModel::new(0.7, 0.1)?;
// Pass it through the venue configuration builder:
// SimulatedVenueConfig::builder()... .fill_model(FillModelHandle::new(fill_model)) .build()?
```

### Custom Matching Logic

The matching engine core lives in `crates/execution/src/matching_core.rs`. Change it only when the behavior belongs to the shared matching contract, and preserve the existing matching-engine integration and deterministic tests.

### PyO3 Binding Conventions

- Use `#[pyclass]` and `#[pymethods]` for Python-visible types
- Register in the owning crate’s `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates that crate submodule
- Wrap FFI functions in `abort_on_panic(|| { ... })`
- Use workspace dependency inheritance (`serde = { workspace = true }`)

## Key Conventions

### BacktestNode vs BacktestEngine

- **BacktestNode**: Configuration-driven, supports multiple runs, recommended for most use cases
- **BacktestEngine**: Direct API, better for strategy unit tests and programmatic control

### Benchmarking Practices

- Use `BacktestEngine` timing for consistent benchmarks
- Profile with `py-spy` or `cProfile` for hotspot identification
- Compare against baseline runs with same data
- See `references/developer_guide/benchmarking.md` for detailed practices

### Backtest Reproducibility

- Same data + same config = same results (deterministic)
- Set `random_seed` in fill model for stochastic fills
- Log all configuration for reproducibility

### Time Advancement

- Backtest engine advances time event-by-event
- Clock timers fire at their scheduled times during replay
- `ts_event` on data determines processing order

## References

- `references/concepts/` — backtesting, order book
- `references/api/` — backtest API
- `references/developer_guide/` — benchmarking practices, benchmarking review checklist, run_rust_backtest
- `references/examples/rust_backtest/` — Rust backtests (engine_ema_cross, node_ema_cross)
- `migration_reference/python/examples/` — quarantined Python clock, portfolio, cache, and model-config examples
- `templates/` — fill_model.py
