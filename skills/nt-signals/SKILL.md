---
name: nt-signals
description: "Use when working with indicators, signal generation, bar aggregation, custom data types, analysis statistics, or tearsheets in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-signals

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as f20f8af36e0f488779d3f543a217b2d19ea2db81. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed block-scoped legacy/Cython/v1 and TradingNode enforcement; `tests/test_dev_guide_sync.py` covers leakage and exemption boundaries. |
| G2 V2 example validation | Validate repository Rust examples against the pinned NT V2 develop/master baseline. | Pass | `python3 tools/check_rust_trading_reference_sync.py --compile` matched pinned upstream f20f8af and `cargo check -p nautilus-trading --features examples,high-precision --lib` passed. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py tests/test_dev_guide_sync.py` passed PyO3 registration, live-runner callback, Rust ownership, and V2 boundary regressions. |
| G4 Lane and API shape | Classify supported Python V2, AI/advisory, config/control-plane, and Rust hot-path lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template inventory and V2 API regressions; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 254 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 108 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pending | Final schema and enforcement remediation must be independently reviewed, committed, and pushed before closure. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Signal gates: Python may prototype indicators, research/config notebooks, and AI/advisory aggregation, but Rust production owns performance-heavy indicators, tick/bar pipelines, ordering, and fixed-point signal transforms. Require `cargo nextest`, `cargo clippy`, `cargo deny`, and deterministic signal tests before `Pass`.

## What This Skill Covers

NautilusTrader **signals and analysis domain** — indicators, custom data types, bar aggregation, portfolio statistics, and reporting.

**Python modules**: `indicators/`, `data/aggregation`, `model/data`, `model/book`, `model/custom`, `analysis/`
**Rust crates**: `nautilus_indicators`, `nautilus_analysis`, `nautilus_model` (data subset)

## When To Use

- Using or building custom indicators (EMA, RSI, Bollinger Bands, etc.)
- Signal generation and publishing
- Bar aggregation (custom bar types, time/tick/volume bars)
- Defining custom data types (`@customdataclass`)
- Portfolio statistics, tearsheets, and analysis reporting
- Order book data processing

## When NOT To Use

- **Strategy order logic** → use `nt-trading`
- **Data persistence or catalog** → use `nt-data`
- **Domain model types (instruments, identifiers)** → use `nt-model`
- **Backtest engine configuration** → use `nt-backtest`

## Python Usage

### Built-in Indicators

```python
from nautilus_trader.indicators.average.ema import ExponentialMovingAverage
from nautilus_trader.indicators.rsi import RelativeStrengthIndex
from nautilus_trader.indicators.bollinger_bands import BollingerBands

# Create indicators
ema_fast = ExponentialMovingAverage(period=10)
ema_slow = ExponentialMovingAverage(period=20)
rsi = RelativeStrengthIndex(period=14)

# Register in strategy's on_start():
self.register_indicator_for_bars(bar_type, ema_fast)
self.register_indicator_for_bars(bar_type, ema_slow)
```

**Indicator categories:**
- **Averages**: `ExponentialMovingAverage`, `SimpleMovingAverage`, `WeightedMovingAverage`, `AdaptiveMovingAverage`, `HullMovingAverage`, `DoubleExponentialMovingAverage`, `WilderMovingAverage`, `VariableIndexDynamic`
- **Momentum**: `RelativeStrengthIndex`, `Stochastics`, `CommodityChannelIndex`, `RateOfChange`
- **Volatility**: `BollingerBands`, `AverageTrueRange`, `KeltnerChannel`, `DonchianChannel`, `VolatilityRatio`
- **Trend**: `AroonOscillator`, `DirectionalMovement`, `LinearRegression`, `ArcherMovingAveragesTrends`
- **Volume**: `OnBalanceVolume`, `VolumeWeightedAveragePrice`

### v1.227.0 signal/data deltas

- `DataActor.subscribe_signal` accepts an optional `priority` for ordered subscriber dispatch; pass `None` / omit it when ordering is not required.
- Continuous futures support adjusted aggregated bars via `ContinuousFutureAdjustmentType` and the `BarBuilder` price-adjustment pipeline.
- `BarType` exposes native `is_externally_aggregated` and `is_internally_aggregated` helpers.

### Bar Aggregation

```python
from nautilus_trader.model.data import BarType, BarSpecification
from nautilus_trader.model.enums import BarAggregation, PriceType

# Time bars
bar_type = BarType.from_str("ETHUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL")

# Tick bars
tick_bars = BarSpecification(step=100, aggregation=BarAggregation.TICK, price_type=PriceType.LAST)

# Volume bars
vol_bars = BarSpecification(step=1000, aggregation=BarAggregation.VOLUME, price_type=PriceType.LAST)
```

### Custom Data Types

```python
from nautilus_trader.model.custom import customdataclass

@customdataclass
class MySignalData:
    signal_value: float
    signal_strength: int
    # ts_event and ts_init auto-provided by decorator
```

### Analysis & Tearsheets

```python
from nautilus_trader.analysis.analyzer import PortfolioAnalyzer
from nautilus_trader.analysis.reporter import ReportProvider

analyzer = PortfolioAnalyzer()
# analyzer automatically registered in backtest/live node
# Access via node.analyzer after run
```

## Python Extension

### Custom Indicator

Subclass `Indicator` and implement `handle_bar()`, `update_raw()`, `_reset()`:

```python
from nautilus_trader.indicators import Indicator

class MyIndicator(Indicator):
    def __init__(self, period: int):
        super().__init__(params=[period])
        self.period = period
        self.value = 0.0
        self.count = 0

    def handle_bar(self, bar):
        self.update_raw(bar.close.as_double())

    def update_raw(self, value: float):
        if not self.has_inputs:
            self._set_has_inputs(True)
        # TODO: Core calculation
        self.count += 1
        if not self.initialized and self.count >= self.period:
            self._set_initialized(True)

    def _reset(self):
        self.value = 0.0
        self.count = 0
```

See `templates/indicator.py` for full template.

### Custom PortfolioStatistic

```python
from nautilus_trader.analysis.statistic import PortfolioStatistic

class MyStatistic(PortfolioStatistic):
    def calculate_from_returns(self, returns):
        if not self._check_valid_returns(returns):
            return None
        return float(returns.mean())
```

Return values must be JSON-serializable (float, int, str, bool, None).

See `templates/portfolio_statistic.py` for full template.

### Custom Data Types

Use `@customdataclass` decorator — it auto-generates serialization methods (dict, bytes, Arrow). See `templates/custom_data.py`.

## Rust Usage

```rust
use nautilus_indicators::average::ema::ExponentialMovingAverage;
use nautilus_indicators::rsi::RelativeStrengthIndex;
use nautilus_analysis::analyzer::PortfolioAnalyzer;
```

## Rust Extension

### Custom Indicator in Rust

Rust indicators are significantly faster for compute-heavy calculations (e.g., order book features, multi-timeframe analysis). Implement the `Indicator` trait:

```rust
use pyo3::prelude::*;
use nautilus_indicators::indicator::Indicator;

#[pyclass]
pub struct MyRustIndicator {
    period: usize,
    value: f64,
    count: usize,
    has_inputs: bool,
    initialized: bool,
}

#[pymethods]
impl MyRustIndicator {
    #[new]
    fn new(period: usize) -> Self {
        Self { period, value: 0.0, count: 0, has_inputs: false, initialized: false }
    }

    fn handle_bar(&mut self, bar: &Bar) {
        self.update_raw(bar.close.as_f64());
    }

    fn update_raw(&mut self, value: f64) {
        self.has_inputs = true;
        // Core calculation
        self.count += 1;
        if self.count >= self.period {
            self.initialized = true;
        }
    }

    fn reset(&mut self) {
        self.value = 0.0;
        self.count = 0;
        self.has_inputs = false;
        self.initialized = false;
    }

    #[getter]
    fn value(&self) -> f64 { self.value }
    #[getter]
    fn initialized(&self) -> bool { self.initialized }
    #[getter]
    fn has_inputs(&self) -> bool { self.has_inputs }
}
```

See `crates/indicators/src/` for the full Rust indicator library. All built-in indicators have Rust implementations that are exposed to Python via PyO3.

### Custom Statistics in Rust

Portfolio statistics can also be implemented in Rust for performance. See `crates/analysis/src/statistics/` for examples (Sharpe ratio, Sortino, max drawdown, etc.).

### PyO3 Binding Conventions

- Use `#[pyclass]` and `#[pymethods]` for Python-visible types
- Register bindings in the owning crate’s `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates that crate submodule
- Use `#[getter]` for read-only properties
- Wrap FFI functions in `abort_on_panic(|| { ... })` — panics must never unwind across FFI

## Coding Conventions

### Python Indicator Conventions

- **Type hints**: Required on all indicator methods
- **Name attribute**: Every indicator must have a unique `_name` using `params_init` or `_name_not_ratio`
- **Value access**: Use `handle_bar` / `handle_quote_tick` / `handle_trade_tick` as appropriate
- **Reset**: Implement `reset()` to clear internal state
- **Partial**: Implement `handle_partial()` if indicator supports partial candles

### Rust Indicator Conventions

- Use `#[pyclass]` with `#[pymethods]` for PyO3 exposure
- Implement the indicator trait for `handle_bar`, `handle_quote_tick`, etc.
- Keep state serializable for `on_save`/`on_load`

## Key Conventions

### Indicator Naming

- Match NT convention: `ExponentialMovingAverage` not `EMA` (class name)
- Short names used in `name` property (auto-derived)
- Parameters passed to `super().__init__(params=[...])` for serialization

### Registration Pattern

Always register indicators via `self.register_indicator_for_bars()` or `self.register_indicator_for_quote_ticks()` in `on_start()` — never call `handle_bar()` manually.

### Custom Data Serialization

- `@customdataclass` auto-generates Arrow schemas
- `InstrumentId` fields are auto-converted to/from strings
- All fields need type annotations
- `ts_event` and `ts_init` are auto-prepended (don't define them)

## References

- `references/concepts/` — reports, visualization, portfolio, data
- `references/api/` — indicators, analysis, data, book, portfolio
- `references/python/` — analysis source reference (config, tearsheet, statistic, themes)
- `references/rust/` — analysis Rust source reference
- `references/examples/` — indicator usage, cascaded indicators, bar aggregation
- `templates/` — indicator.py, custom_data.py, portfolio_statistic.py
