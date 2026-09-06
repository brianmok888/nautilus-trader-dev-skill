# ARCHIVAL / MIGRATION NOTE

NT v2 compatibility note: only the historical Cython/v1 naming noted in the overview below is retained for migration/reference-only context; the tables, examples, and how-tos in this file document the pinned V2 surface (Rust `crates/indicators`, flat PyO3 `nautilus_trader.indicators` package). Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# NautilusTrader Indicators Reference Guide

## Overview

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

All indicators are implemented in Rust under `crates/indicators/src/` and re-exported to Python
via PyO3 as `@typing.final` classes in the flat `nautilus_trader.indicators` module. The v1
guide's Cython-compiled classes and the Python `nautilus_trader.indicators.base.Indicator`
base class are historical; the authoring surface is the Rust `Indicator` trait
(`crates/indicators/src/indicator.rs`). Every Python-visible indicator exposes:

- `has_inputs: bool` -- whether any data has been received
- `initialized: bool` -- whether the warmup period is satisfied
- `reset()` -- reset all state

The typed update surface varies per indicator, so check the specific class in
`nautilus_trader.indicators` for what it actually exposes. Bar-only indicators
expose only `handle_bar` (15 classes at the pin, e.g. `CommodityChannelIndex`,
`DonchianChannel`, `IchimokuCloud`, `Stochastics`, `OnBalanceVolume`,
`LinearRegression`); `BookImbalanceRatio` exposes none of the bar/tick handlers
and updates via `handle_book(book)` / `update(best_bid, best_ask)`;
`SpreadAnalyzer` exposes `handle_quote_tick` but no `handle_bar` or
`update_raw`. Most price-based indicators also expose `update_raw(...)` --
direct numeric update, no data object required; calling a handler an indicator
does not implement panics with `is not implemented for`.

---

## Averages

All moving averages implement the Rust `MovingAverage` trait, whose shared members are `value`, `count`, and `update_raw`; most classes also expose `period` and `price_type` properties. `AdaptiveMovingAverage` has no single `period` -- it is parameterized by `period_efficiency_ratio`, `period_fast`, and `period_slow`.

| Class | Params | Description | Rust crate path |
|---|---|---|---|
| `SimpleMovingAverage` | `period` | Arithmetic mean over rolling window | `average::sma` |
| `ExponentialMovingAverage` | `period` | EMA with alpha = 2/(period+1) | `average::ema` |
| `DoubleExponentialMovingAverage` | `period` | DEMA: 2*EMA1 - EMA2 for reduced lag | `average::dema` |
| `WeightedMovingAverage` | `period, weights` | Weighted average with explicit weights (`len(weights) == period`, positive sum) | `average::wma` |
| `HullMovingAverage` | `period` | Alan Hull's fast smooth MA using nested WMAs | `average::hma` |
| `AdaptiveMovingAverage` | `period_efficiency_ratio (>=2), period_fast, period_slow` | Kaufman AMA adapting to noise via EfficiencyRatio | `average::ama` |
| `WilderMovingAverage` | `period` | EMA variant with alpha = 1/period (Wilder smoothing) | `average::rma` |
| `VariableIndexDynamicAverage` | `period, price_type=None, cmo_ma_type=WILDER` | VIDYA: EMA with dynamic alpha from Chande Momentum Oscillator | `average::vidya` |
| `ZScore` | `period, price_type=None` | Rolling z-score `(last - mean) / sample std`; window expands to `period` then slides; outputs `value`/`mean`/`std` | `average::zscore` |

**Factory** (Rust-only): `MovingAverageFactory::create(moving_average_type, period)` in `nautilus_indicators::average` returns the matching `Box<dyn MovingAverage>` given a `MovingAverageType` enum value -- the type comes first and there are no keyword arguments; the pinned Python indicators package does not export this factory. `MovingAverageType` has exactly five CamelCase variants at the pin: `Simple`, `Exponential`, `DoubleExponential`, `Wilder`, `Hull` (`crates/indicators/src/average/mod.rs`). `WeightedMovingAverage` and `VariableIndexDynamicAverage` exist as classes but cannot be produced via the factory.

`LinearRegression` and `VolumeWeightedAveragePrice` are Python-visible at the pinned tip (`python/nautilus_trader/indicators/__init__.pyi:35,52`) alongside their Rust implementations in `nautilus_indicators::average`.

---

## Momentum

| Class | Params | Output | Description | Rust path |
|---|---|---|---|---|
| `RelativeStrengthIndex` | `period, ma_type=EXP` | `value` (0-1) | RSI via average gain/loss ratio | `momentum::rsi` |
| `RateOfChange` | `period, use_log=False` | `value` | Price ROC: simple or log returns | `momentum::roc` |
| `ChandeMomentumOscillator` | `period, ma_type=WILDER` | `value` (-100..100) | CMO: momentum with overbought/oversold at +/-50 | `momentum::cmo` |
| `Stochastics` | `period_k, period_d, slowing=1, ma_type=EXP, d_method="ratio"` | `value_k, value_d` | %K/%D oscillator; supports "ratio" and "moving_average" D methods | `momentum::stochastics` |
| `CommodityChannelIndex` | `period, scalar=0.015, ma_type=SIMPLE` | `value` | CCI: deviation of typical price from its MA | `momentum::cci` |
| `EfficiencyRatio` | `period (>=2)` | `value` (0-1) | Kaufman ER: \|P(t)−P(t−n)\| / sum of \|ΔP\| over the n price changes in the window (initialized after n inputs) | `ratio::efficiency_ratio` |
| `RelativeVolatilityIndex` | `period, scalar=100, ma_type=SIMPLE` | `value` (0-100) | RVI: standard deviation direction tracker | `volatility::rvi` |
| `PsychologicalLine` | `period, ma_type=SIMPLE` | `value` (0-100) | Percentage of bars closing above prior close | `momentum::psl` |

---

## Trend

| Class | Params | Output | Description | Rust path |
|---|---|---|---|---|
| `ArcherMovingAveragesTrends` | `fast_period, slow_period, signal_period, ma_type=EXP` | `long_run, short_run` | Detects trend runs from fast/slow MA divergence | `momentum::amat` |
| `AroonOscillator` | `period` | `aroon_up, aroon_down, value` | Periods since highest high / lowest low over the full `period+1` window, scanned newest-to-oldest; ties resolve to the most recent occurrence | `momentum::aroon` |
| `DirectionalMovement` | `period, ma_type=EXP` | `pos, neg` | +DI / -DI directional movement lines | `momentum::dm` |
| `MovingAverageConvergenceDivergence` | `fast_period, slow_period, ma_type=SIMPLE` | `value` | MACD: difference of fast and slow MAs | `momentum::macd` |
| `IchimokuCloud` | `tenkan=9, kijun=26, senkou=52, displacement=26` | `tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span` | Full Ichimoku Kinko Hyo with 5 components | `momentum::ichimoku` |
| `LinearRegression` | `period` | `value, slope, intercept, degree, cfo, r2` | OLS regression over rolling window | `average::lr` |
| `Bias` | `period, ma_type=SIMPLE` | `value` | Rate of change between price and its MA: (price/MA) - 1 | `momentum::bias` |
| `Swings` | `period` | `direction, changed, high_price, low_price, length, duration` | Swing high/low detection with timing metrics | `momentum::swings` |

---

## Volatility

| Class | Params | Output | Description | Rust path |
|---|---|---|---|---|
| `AverageTrueRange` | `period, ma_type=SIMPLE, use_previous=True, value_floor=0` | `value` | ATR: smoothed true range | `volatility::atr` |
| `BollingerBands` | `period, k, ma_type=SIMPLE` | `upper, middle, lower` | Bands at k standard deviations from MA | `momentum::bb` |
| `DonchianChannel` | `period` | `upper, middle, lower` | Highest high / lowest low channel | `volatility::dc` |
| `KeltnerChannel` | `period, k_multiplier, ma_type=SIMPLE, ma_type_atr=SIMPLE, use_previous=True, atr_floor=0` | `upper, middle, lower` | ATR-based envelope around MA of typical price | `volatility::kc` |
| `KeltnerPosition` | `period, k_multiplier, ...` | `value` | Relative position within Keltner channel (-1..+1 range, unbounded) | `volatility::kp` |
| `VerticalHorizontalFilter` | `period, ma_type=SIMPLE` | `value` | VHF: highest-lowest range / sum of changes (trending vs ranging) | `momentum::vhf` |
| `VolatilityRatio` | `fast_period, slow_period, ma_type=SIMPLE, use_previous=False, value_floor=0` | `value` | Ratio of slow ATR to fast ATR | `volatility::vr` |

---

## Volume

| Class | Params | Output | Description | Rust path |
|---|---|---|---|---|
| `OnBalanceVolume` | `period` (required) | `value` | Cumulative positive/negative volume momentum | `momentum::obv` |
| `VolumeWeightedAveragePrice` | (none) | `value` | Intraday VWAP, auto-resets on new day | `average::vwap` |
| `KlingerVolumeOscillator` | `fast_period, slow_period, signal_period, ma_type=EXP` | `value` | Compares volume to price movement for reversal prediction | `momentum::kvo` |
| `Pressure` | `period, ma_type=EXP, atr_floor=0` | `value, value_cumulative` | Relative volume needed to move price across ATR | `momentum::pressure` |

---

## Book and Candle Descriptors

| Class | Params | Output | Description | Rust path |
|---|---|---|---|---|
| `BookImbalanceRatio` | (none) | `value` | Best-bid/best-ask size ratio from the order book top; updates via `handle_book(book)` or `update(best_bid, best_ask)` | `book::imbalance` |
| `FuzzyCandle` | `direction, size, body_size, upper_wick_size, lower_wick_size` | descriptor fields | Candle descriptor value emitted by `FuzzyCandlesticks` | `volatility::fuzzy` |
| `CandleDirection` | (enum: `Bull`/`None`/`Bear`) | - | Direction category used by `FuzzyCandle` | `volatility::fuzzy` |
| `CandleSize` | (enum: `None`..`ExtremelyLarge`) | - | Size category used by `FuzzyCandle` | `volatility::fuzzy` |
| `CandleBodySize` | (enum: `None`..`Trend`) | - | Body-size category used by `FuzzyCandle` | `volatility::fuzzy` |
| `CandleWickSize` | (enum: `None`/`Small`/`Medium`/`Large`) | - | Upper/lower wick-size category used by `FuzzyCandle` | `volatility::fuzzy` |

---

## Other

| Class | Module | Description | Rust path |
|---|---|---|---|
| `FuzzyCandlesticks` | `fuzzy_candlesticks` | Fuzzifies OHLC bars into categorical direction/size/body/wick descriptors | `volatility::fuzzy` |
| `SpreadAnalyzer` | `spread_analyzer` | Tracks current and average bid-ask spread for an instrument | `ratio::spread_analyzer` |

---

## Building a Custom Indicator

Custom indicators are authored in Rust by implementing the `Indicator` trait
(`crates/indicators/src/indicator.rs`); there is no Python base class at the pin --
`nautilus_trader.indicators` re-exports PyO3-wrapped classes only. Implement
`name`, `has_inputs`, `initialized`, `reset`, the typed handlers your indicator
supports (`handle_bar`, `handle_quote`, `handle_trade`, `handle_book`, ...),
and keep the calculation in an `update_raw` method:

### Step-by-step: Exponential Weighted Momentum (Rust)

```rust
use nautilus_indicators::indicator::Indicator;
use nautilus_model::data::Bar;

pub struct ExponentialWeightedMomentum {
    period: usize,
    value: f64,
    prev_price: f64,
    count: usize,
    has_inputs: bool,
    initialized: bool,
}

impl ExponentialWeightedMomentum {
    pub fn new(period: usize) -> Self {
        assert!(period > 0, "period must be positive");
        Self {
            period,
            value: 0.0,
            prev_price: 0.0,
            count: 0,
            has_inputs: false,
            initialized: false,
        }
    }
}

impl Indicator for ExponentialWeightedMomentum {
    fn name(&self) -> String {
        stringify!(ExponentialWeightedMomentum).to_string()
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
        self.prev_price = 0.0;
        self.count = 0;
        self.has_inputs = false;
        self.initialized = false;
    }
}

impl ExponentialWeightedMomentum {
    // Core calculation -- typed handlers just extract prices and delegate here
    pub fn update_raw(&mut self, close: f64) {
        if self.count == 0 {
            self.prev_price = close;
            self.count = 1;
            self.has_inputs = true;
            return;
        }
        let alpha = 2.0 / (self.period as f64 + 1.0);
        let momentum = close - self.prev_price;
        self.value = alpha * momentum + (1.0 - alpha) * self.value;
        self.prev_price = close;
        self.count += 1;
        self.initialized = self.count >= self.period;
    }
}
```

**Key patterns:**

- Implement only the handlers your indicator consumes; the trait defaults panic
  with `is not implemented for` when an unimplemented handler is called, which
  the PyO3 wrapper surfaces to Python.
- `has_inputs` flips on the first data point; `initialized` flips once enough
  data exists for valid output (here `count >= period`).
- `update_raw()` -- keep the calculation here; typed handlers just extract
  prices and delegate.
- `reset()` -- must reset ALL stateful values while preserving configuration.
- To make the indicator Python-visible, add a PyO3 wrapper under
  `crates/indicators/src/python/` following the built-in bindings (separate
  `#[pyclass]`/`#[pymethods]` wrapper; do not substitute `#[pymethods]` for the
  Rust `Indicator` implementation). Without a wrapper the indicator is
  Rust-only.

**Registering your custom indicator** -- once Python-visible, registration is
the same as built-in indicators:

```python
def on_start(self):
    self.ewm = ExponentialWeightedMomentum(period=20)
    self.register_indicator_for_bars(bar_type, self.ewm)
    self.subscribe_bars(bar_type)
```

See `../../SKILL.md` "Custom Indicator in Rust" for the condensed version of
this authoring path.

---

## Usage Patterns

### Creating and registering indicators in a strategy

```python
from nautilus_trader.indicators import (
    ExponentialMovingAverage,
    RelativeStrengthIndex,
    BollingerBands,
)


class MyStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.ema_fast = ExponentialMovingAverage(10)
        self.ema_slow = ExponentialMovingAverage(20)
        self.rsi = RelativeStrengthIndex(14)
        self.bbands = BollingerBands(20, k=2.0)

    def on_start(self):
        bar_type = BarType.from_str("EURUSD.SIM-1-MINUTE-MID-INTERNAL")
        # Auto-feeds bar data to the indicator
        self.register_indicator_for_bars(bar_type, self.ema_fast)
        self.register_indicator_for_bars(bar_type, self.ema_slow)
        self.register_indicator_for_bars(bar_type, self.rsi)
        self.register_indicator_for_bars(bar_type, self.bbands)
        self.subscribe_bars(bar_type)

    def on_bar(self, bar: Bar):
        if not self.ema_slow.initialized:
            return  # Wait for warmup
        # Access computed values
        if self.ema_fast.value > self.ema_slow.value and self.rsi.value < 0.7:
            # Trading logic...
            pass
```

### Registering for quotes or trades

```python
def on_start(self):
    instrument_id = InstrumentId.from_str("EURUSD.SIM")
    self.register_indicator_for_quote_ticks(instrument_id, self.ema)
    self.subscribe_quote_ticks(instrument_id)
    # OR
    self.register_indicator_for_trade_ticks(instrument_id, self.ema)
    self.subscribe_trade_ticks(instrument_id)
```

### Manual updates with raw values

```python
# When you have numeric values directly (e.g., from a custom source)
ema = ExponentialMovingAverage(20)
ema.update_raw(1.2345)
ema.update_raw(1.2350)
print(ema.value)  # Current EMA value
print(ema.initialized)  # True after 20 updates
```

### Using MovingAverageFactory

```rust
use nautilus_indicators::average::{MovingAverageFactory, MovingAverageType};

// Create any factory-supported MA type with a uniform interface (type first)
let ma = MovingAverageFactory::create(MovingAverageType::Hull, 20);
```

### Multi-output indicators

Some indicators produce multiple values rather than a single `value`:

```python
stoch = Stochastics(14, 3)
# After warmup:
stoch.value_k  # %K line
stoch.value_d  # %D line

bbands = BollingerBands(20, k=2.0)
bbands.upper  # Upper band
bbands.middle  # Middle band (MA)
bbands.lower  # Lower band

ichimoku = IchimokuCloud()
ichimoku.tenkan_sen
ichimoku.kijun_sen
ichimoku.senkou_span_a
ichimoku.senkou_span_b
ichimoku.chikou_span
```

---

## Cascaded Indicators Pattern

Indicators can feed into other indicators. The framework supports this naturally since
`update_raw()` accepts plain numeric values.

**Built-in cascading examples** from the codebase:

- `DoubleExponentialMovingAverage` internally chains two `ExponentialMovingAverage` instances:
  EMA1 feeds into EMA2, then `value = 2*EMA1 - EMA2`.
- `HullMovingAverage` chains three `WeightedMovingAverage` instances with different periods.
- `AdaptiveMovingAverage` uses an `EfficiencyRatio` to dynamically adjust its smoothing.
- `KeltnerChannel` embeds an `AverageTrueRange` and a `MovingAverage`.
- `KeltnerPosition` wraps a full `KeltnerChannel`.
- `VariableIndexDynamicAverage` embeds a `ChandeMomentumOscillator`.

**Manual cascading in a strategy:**

```python
class CascadedStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.rsi = RelativeStrengthIndex(14)
        self.rsi_ema = ExponentialMovingAverage(9)  # Smooth the RSI

    def on_start(self):
        bar_type = BarType.from_str("EURUSD.SIM-1-MINUTE-MID-INTERNAL")
        self.register_indicator_for_bars(bar_type, self.rsi)
        self.subscribe_bars(bar_type)

    def on_bar(self, bar: Bar):
        if self.rsi.has_inputs:
            # Feed RSI output into EMA
            self.rsi_ema.update_raw(self.rsi.value)
        if not self.rsi_ema.initialized:
            return
        # Use smoothed RSI
        smoothed_rsi = self.rsi_ema.value
```

Note: the second indicator (`rsi_ema`) is NOT registered with `register_indicator_for_bars` --
it is updated manually in `on_bar` using the first indicator's output.

---

## Rust Crate Structure

The Rust implementations live in `crates/indicators/src/` and mirror the Python API:

```
crates/indicators/src/
  indicator.rs          # Indicator trait
  lib.rs                # Crate root
  average/              # sma, ema, dema, hma, wma, ama, rma, vidya, vwap, lr, zscore
  momentum/             # rsi, roc, cmo, stochastics, cci, macd, aroon, amat,
                        # bb, bias, dm, ichimoku, kvo, obv, pressure, psl, swings, vhf
  ratio/                # efficiency_ratio, spread_analyzer
  volatility/           # atr, dc, kc, kp, rvi, vr, fuzzy
  book/                 # imbalance
  python/               # PyO3 bindings
```

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

The Rust crate is `nautilus-indicators` and the Python bindings are generated via PyO3
in the `python/` subdirectory. There is no Cython build at the pinned upstream: Rust with
PyO3 bindings is the only indicator implementation.
