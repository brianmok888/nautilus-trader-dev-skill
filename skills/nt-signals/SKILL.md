---
name: nt-signals
description: "Use when working with indicators, signal generation, bar aggregation, custom data types, analysis statistics, or tearsheets in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-signals

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `6df237382eb1d8411906f9b1790fa06f8ba7aad4`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run python -m pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-signals` passed the skill domain's scoped examples and owners against `6df237382eb1d8411906f9b1790fa06f8ba7aad4`; schema-v2 provenance is recorded in `references/g2-evidence/nt-signals.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run python -m pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run python -m pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run python -m pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run python -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-signals.json`; repository closure is summarized in `docs/tracking/Findings.md`. |


Signal gates: Rust owns indicator prototyping, research implementations, production indicators, tick/bar pipelines, ordering, and fixed-point signal transforms. Non-NautilusTrader development lanes are outside this repository. Require `cargo nextest`, `cargo clippy`, `cargo deny`, and deterministic signal tests before `Pass`.

## Rust production lane

Implement production indicators, aggregators, custom data, and signal state machines in Rust using deterministic updates and fixed-point-safe domain values where applicable. Keep per-event computation and state mutation off Python paths, and validate warm-up, reset, ordering, and numerical edge cases with Rust tests.

## PyO3 control-plane lane

Use PyO3 to construct and configure Rust indicators, register signal components, and inspect derived outputs. Python may orchestrate bounded analysis but must not own production market-data subscriptions, event handlers, mutable signal state, or trading decisions.

## Migration/reference lane

Python migration material is pointer-only here and physically quarantined under `migration_reference/python/` for `nt-signals`.

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at immutable commit `6df237382eb1d8411906f9b1790fa06f8ba7aad4`.

## What This Skill Covers

NautilusTrader **signals and analysis domain** — indicators, custom data types, bar aggregation, portfolio statistics, and reporting.

**Python modules**: flat `nautilus_trader.indicators`, `nautilus_trader.model`, `nautilus_trader.data`, `nautilus_trader.analysis`
**Rust crates**: `nautilus_indicators`, `nautilus_analysis`, `nautilus_model` (data subset)

## When To Use

- Using or building custom indicators (EMA, RSI, Bollinger Bands, etc.)
- Signal generation and publishing
- Bar aggregation (custom bar types, time/tick/volume bars)
- Registering custom data types with `register_custom_data_class`
- Portfolio statistics, tearsheets, and analysis reporting
- Order book data processing

## When NOT To Use

- **Strategy order logic** → use `nt-trading`
- **Data persistence or catalog** → use `nt-data`
- **Domain model types (instruments, identifiers)** → use `nt-model`
- **Backtest engine configuration** → use `nt-backtest`

## Python Usage

Python production guidance is physically quarantined as migration/reference-only.
See [Python Usage migration reference](migration_reference/python/python-usage.md).
New production work follows the Rust or bounded PyO3 sections below.

## Python Extension

Python production guidance is physically quarantined as migration/reference-only.
See [Python Extension migration reference](migration_reference/python/python-extension.md).
New production work follows the Rust or bounded PyO3 sections below.

## V2 signal and continuous-futures invariants

- Signal subscription dispatch supports explicit `priority` ordering.
- Continuous futures use `ContinuousFutureAdjustmentType` in the adjusted bar
  aggregation path.

## Rust Usage

Current-develop reset invariant: `reset` must preserve configuration while
clearing runtime observations. Do not overwrite constructor parameters such as
adaptive-average bounds or fuzzy-candlestick thresholds with defaults. Re-run
post-reset input sequences and assert configured behavior, not only an empty
buffer. Source: upstream develop commit
`8003bed6ef75d3cea8271dc368aba2630d7f9db6`.

```rust
use nautilus_indicators::average::ema::ExponentialMovingAverage;
use nautilus_indicators::momentum::rsi::RelativeStrengthIndex;
use nautilus_analysis::analyzer::PortfolioAnalyzer;
```

Use `MovingAverageFactory::create` (pinned source
`crates/indicators/src/average/mod.rs`) to obtain any built-in moving average
as a `Box<dyn MovingAverage + Send + Sync>` from a `MovingAverageType` and
period; the factory is Rust-only and is not exposed to Python.

```rust
use nautilus_indicators::average::{MovingAverageFactory, MovingAverageType};

let ma = MovingAverageFactory::create(MovingAverageType::Exponential, 20);
// ma: Box<dyn MovingAverage + Send + Sync>
```

The pinned crate also ships a rolling `ZScore` (Rust `crates/indicators/src/average/zscore.rs`, Python `ZScore(period, price_type=None)` exposing `value`/`mean`/`std`; the window expands to `period` then slides, with the sample standard deviation recomputed each update).

## Rust Extension

### Custom Indicator in Rust

Rust indicators are significantly faster for compute-heavy calculations (e.g., order book features, multi-timeframe analysis). Implement the `Indicator` trait:

```rust
use nautilus_indicators::indicator::Indicator;
use nautilus_model::data::Bar;

pub struct MyRustIndicator {
    period: usize,
    value: f64,
    count: usize,
    has_inputs: bool,
    initialized: bool,
}

impl MyRustIndicator {
    fn new(period: usize) -> Self {
        assert!(period > 0, "period must be positive");
        Self { period, value: 0.0, count: 0, has_inputs: false, initialized: false }
    }

    fn update_raw(&mut self, value: f64) {
        self.value = value;
        self.has_inputs = true;
        self.count += 1;
        self.initialized = self.count >= self.period;
    }
}

impl Indicator for MyRustIndicator {
    fn name(&self) -> String {
        stringify!(MyRustIndicator).to_string()
    }

    fn has_inputs(&self) -> bool {
        self.has_inputs
    }

    fn initialized(&self) -> bool {
        self.initialized
    }

    fn handle_bar(&mut self, bar: &Bar) {
        self.update_raw(bar.close.as_f64());
    }

    fn reset(&mut self) {
        self.value = 0.0;
        self.count = 0;
        self.has_inputs = false;
        self.initialized = false;
    }
}
```

Add separate PyO3 wrappers following `crates/indicators/src/python/` when the
indicator must be Python-visible; do not substitute `#[pymethods]` for the Rust
`Indicator` implementation.

See `crates/indicators/src/` for the full Rust indicator library. All built-in indicators have Rust implementations that are exposed to Python via PyO3.

### Custom Statistics in Rust

Portfolio statistics can also be implemented in Rust for performance. See `crates/analysis/src/statistics/` for examples (Sharpe ratio, Sortino, max drawdown, etc.).

### PyO3 Binding Conventions

- Use `#[pyclass]` and `#[pymethods]` for Python-visible types
- Register bindings in the owning crate’s `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates that crate submodule
- Use `#[getter]` for read-only properties
- Wrap FFI functions in `abort_on_panic(|| { ... })` — panics must never unwind across FFI

## Tearsheets and Themes

The current V2 Python reporting surface lives in `nautilus_trader.analysis`
User-defined portfolio statistics are supported at the pinned baseline (upstream `7e8c9c9cd`): subclass the Python `PortfolioStatistic` base class from `nautilus_trader.analysis.statistic` (`python/nautilus_trader/analysis/statistic.py:16`) and register instances with `Portfolio.register_statistic` / the analyzer route (`crates/analysis/src/python/analyzer.rs:145`); the Rust trait (`crates/analysis/src/statistic.rs`) drives calculation and no longer exposes `calculate_from_orders`. Registering Rust-native statistics via `PortfolioApi` remains available from strategies.

(pinned source `analysis/tearsheet.py`, `analysis/themes.py`,
`analysis/config.py`):

- `create_tearsheet(engine_or_result, ...)` renders a tearsheet from a
  `BacktestEngine` or `BacktestResult`; the `output_path` extension selects
  interactive HTML or static image formats.
- `create_tearsheet_from_stats(stats_pnls, stats_returns, stats_general, returns, ...)`
  renders from precomputed statistics for offline analysis.
- `register_chart(name, func=None)` registers a custom chart (usable as a
  decorator); `get_chart(name)` and `list_charts()` read the chart registry.
- `register_theme(name, template, colors)` registers a custom Plotly theme;
  `get_theme(name)` and `list_themes()` read the theme registry.
- `TearsheetConfig` (in `analysis/config.py`) customizes output; install the
  `visualization` extra for tearsheet dependencies.

## Coding Conventions

### Indicator Conventions

Author new indicators in Rust: implement the `Indicator` trait (pinned source
`crates/indicators/src/indicator.rs`) with `name`, `has_inputs`, `initialized`,
`reset`, and the typed handlers `handle_bar` / `handle_quote` / `handle_trade`
(`handle_delta` / `handle_deltas` / `handle_depth` / `handle_book` for
order-book inputs). Add PyO3 wrappers under `crates/indicators/src/python/`
when the indicator must be Python-visible; see `Rust Extension` above.

Legacy v1 Python-authoring bullets, retained for migration reference only
(`handle_quote_tick` / `handle_trade_tick` remain the Python-visible method
names on built-in PyO3 indicators):

- **Type hints**: Required on all indicator methods
- **Value access**: Use `handle_bar` / `handle_quote_tick` / `handle_trade_tick` as appropriate on the PyO3 surface
- **Reset**: Implement `reset()` to clear internal state

### Rust Indicator Conventions

- Use `#[pyclass]` with `#[pymethods]` for PyO3 exposure
- Implement the `Indicator` trait handlers `handle_bar` / `handle_quote` / `handle_trade` (and `handle_delta` / `handle_deltas` / `handle_depth` / `handle_book` for order-book inputs)
- Keep state serializable for `on_save`/`on_load`

## Key Conventions

### Indicator Naming

- Match NT convention: `ExponentialMovingAverage` not `EMA` (class name)
- Short names used in `name` property (auto-derived)
- Rust `Indicator::name()` returns the indicator name string; Python exposes it as the `name` property

### Registration Pattern

Always register indicators via `self.register_indicator_for_bars()` or `self.register_indicator_for_quote_ticks()` in `on_start()` — never call `handle_bar()` manually.

### Custom Data Serialization

- Register current Python types with `nautilus_trader.model.register_custom_data_class(MySignal)` (single class argument)
- Provide a `to_json` instance method and a `from_json(data)` classmethod for JSON/message use
- Provide explicit `encode_record_batch_py` and `decode_record_batch_py` callbacks for catalog persistence; Arrow schemas are not auto-generated
- Define stable Unix-nanosecond `ts_event` and `ts_init` fields in the type contract

## References

- `references/concepts/` — reports, visualization, portfolio, data
- `references/api/` — indicators, analysis, data, book, portfolio
- `migration_reference/python/python/analysis/` — quarantined Python analysis source reference (config, tearsheet, statistic, themes)
- `references/rust/` — analysis Rust source reference
- `migration_reference/python/examples/` — quarantined Python indicator, cascaded-indicator, and bar-aggregation examples
- `migration_reference/python/templates/` — quarantined indicator.py, custom_data.py, portfolio_statistic.py templates
