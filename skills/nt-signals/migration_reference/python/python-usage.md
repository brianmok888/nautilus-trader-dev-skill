# Python Usage

> **Migration/reference-only.** This non-AI Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-signals` skill. The only active Python lane is AI/advisory work
> routed through `nt-evomap-integration`.


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
