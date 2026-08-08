# Templates

> **Migration/reference-only.** This Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-implement` skill. The only active Python lane is AI/advisory work
> outside this repository.


> **New in v1.227.0 (2026-05-18)** — Current baseline changes for new code:
> - Read the target workspace version from its root `Cargo.toml` and use workspace/path dependencies for in-tree examples; do not copy a historical crate version into new code.
> - Use adapter `environment` enums; Binance/Kraken live enum names are `Live` / `LIVE`.
> - Use `time_bars_origin_offset`, not `time_bars_origins`.
> - Use `DataActor.subscribe_signal(..., priority=None)` when ordered signal dispatch matters.
> - Use `TryFrom<OrderInitialized>` / `try_into` for order initialization validation.
> - Use the builder-style `OrderFactory::bracket()...call()` Rust API.

> **New in v1.224.0 (2026-03-03)** — Breaking changes and new features:
> - **InstrumentProvider simplification**: `load_ids_async()` and `load_async()` now have default implementations that Only `load_all_async()` is required in adapter subclasses.
> - **`fill_limit_inside_spread`**: Renamed from `fill_limit_at_touch`. `BestPriceFillModel` now fills inside bid-ask spread by default.
> - **Coinbase International adapter removed**: `COINBASE_INTX` package deleted (RFC #3555). Use a different venue.
> - **`OrderBook.get_target_px_for_quantity()`**: New method for book impact analysis.
> - **BitMEX dead man's switch**: New `deadmans_switch_timeout_secs` config field.
> - **OKX trailing stop + algo amend support**.
> - **Hyperliquid order modify support** (`builder_fee_refresh_mins` config removed).
> - **Betfair batch operations**: `SubmitOrderList` and `BatchCancelOrders` now supported.
> - **Binance Ed25519**: Spot/Margin raises `ValueError` for Ed25519 env vars. Futures soft-deprecated.
> - **WS `connect()` now needs `loop_=self._loop` parameter in adapter code.

> - **Rust `InstrumentProvider` trait**: New crate-level trait formalizes adapter patterns at `crates/common/src/providers.rs`.

> **New in v1.223.0 (2026-02-21)** — Key API additions to use in new implementations:
> - **`strategy.market_exit(instrument_id)`** — Convenience method to fully close a position with a market order. Hooks: `on_market_exit()`, `post_market_exit()`. Check: `is_exiting()`. Config: `market_exit_interval_ms` (100), `market_exit_max_attempts` (100), `market_exit_time_in_force`, `market_exit_reduce_only` (True).
> - **`StrategyConfig.manage_stop = True`** — Automatically calls `market_exit()` when the strategy is stopped.
> - **`PerpetualContract`** — New instrument type for asset-class-agnostic perpetual swaps. Prefer over `CryptoPerpetual` for new implementations.
> - **`request_funding_rates()` / `FundingRateUpdate`** — New data request method and data type for funding rate streams.
> - **`BacktestDataConfig.optimize_file_loading`** — Set `True` for faster Parquet loading in large backtests.
> - **`trade_execution` default changed to `True`** — If you want bar-only matching, explicitly set `trade_execution=False` in `BacktestVenueConfig`.

**Strategy Handler Reference (v1.223.0+):**

| Handler | Trigger |
|---------|----------|
| `on_start` | Strategy start |
| `on_stop` | Strategy stop |
| `on_resume` | Resume from degraded state |
| `on_reset` | Reset for reuse |
| `on_dispose` | Cleanup before removal |
| `on_degrade` | Enter degraded mode |
| `on_fault` | Unrecoverable error |
| `on_save` | Serialize state |
| `on_load` | Deserialize state |
| `on_bar` | Bar data received |
| `on_quote_tick` | Quote tick received |
| `on_trade_tick` | Trade tick received |
| `on_order_book_deltas` | Order book delta received |
| `on_order_book` | Order book snapshot received |
| `on_instrument` | Instrument update received |
| `on_instrument_status` | Instrument status change |
| `on_instrument_close` | Instrument close received |
| `on_historical_data` | Historical data response |
| `on_data` | Custom data received |
| `on_signal` | Signal received |
| `on_event` | Catch-all event handler |
| `on_order_initialized` | Order created |
| `on_order_denied` | Order denied by risk engine |
| `on_order_emulated` | Order entered emulator |
| `on_order_released` | Order released from emulator |
| `on_order_submitted` | Order submitted to venue |
| `on_order_rejected` | Order rejected by venue |
| `on_order_accepted` | Order accepted by venue |
| `on_order_canceled` | Order canceled |
| `on_order_expired` | Order expired |
| `on_order_triggered` | Order triggered |
| `on_order_updated` | Order modified |
| `on_order_filled` | Order (partially) filled |
| `on_position_opened` | Position opened |
| `on_position_changed` | Position changed (partial fill) |
| `on_position_closed` | Position closed |
| `on_market_exit` | Market exit in progress hook |
| `post_market_exit` | After market exit completes |

During market exit, non-reduce-only orders are auto-denied; order lists with any non-reduce-only order denied entirely.

> **New in v1.224.0 (2026-03-03)** — Breaking changes and new features:
> - **InstrumentProvider simplification**: `load_ids_async()` and `load_async()` now have default implementations that delegate to `load_all_async()`. Only `load_all_async()` is required in adapter subclasses.
> - **`fill_limit_inside_spread`**: Renamed from `fill_limit_at_touch`. `BestPriceFillModel` now fills inside bid-ask spread by default.
> - **Coinbase International adapter removed**: `COINBASE_INTX` package deleted (RFC #3555). Use a different venue.
> - **WS `connect()` requires `loop_=` param**: All custom adapter WebSocket connect calls now need `loop_=self._loop`.
> - **`OrderBook.get_target_px_for_quantity()`**: New method for book impact analysis.
> - **BitMEX dead man's switch**: New `deadmans_switch_timeout_secs` config field.
> - **OKX**: Trailing stop market + algo amend support.
> - **Hyperliquid**: Order modify support; `builder_fee_refresh_mins` config removed.
> - **Betfair**: `SubmitOrderList` and `BatchCancelOrders` batch operations.
> - **Binance Ed25519**: Spot/Margin `BINANCE_ED25519_*` env vars now raise `ValueError`.

### Quick Reference: Which Template?

Every Python template must carry a local `# TEMPLATE_CLASSIFICATION: ...` header.
Treat unclassified Python templates as invalid. Upstream NT V2 supports Python and
Rust strategies, but this repository classifies Python executable templates as
migration/reference-only. AI/advisory Python and bounded Rust/PyO3 control-plane wrappers
stay explicit. Rust owns new strategy/config/backtest/live work plus adapter networking,
parsing, normalization, risk/execution state, and other execution-critical infrastructure.

| Need | Template / route | Lane classification |
|------|------------------|---------------------|
| Production/performance trading logic or order flow | `nt-strategy-builder-rust` / Rust `Strategy` | Rust production default |
| Existing Python strategy migration | `legacy_migration/strategy.py` | migration/reference-only; new work uses Rust |
| Stateless calculations | Rust indicator path | Python `legacy_migration/indicator.py` is migration/reference-only unless solely used by the AI advisory lane |
| Structured data between components | Rust model/data path | Python `legacy_migration/custom_data.py` is migration/reference-only unless solely used by the AI advisory lane |
| Execution algorithms | Rust exec-algo crate / PyO3 | Rust production default; Python `legacy_migration/exec_algorithm.py` is reference-only |
| Exchange/data connectivity | `adapters/` only as Rust/PyO3 control-plane wrappers | Rust core owns networking, parsing, normalization, and order entry |
| Custom fill/margin/statistics simulation | `legacy_migration/fill_model.py`, `legacy_migration/margin_model.py`, `legacy_migration/portfolio_statistic.py` | Python research/backtest only; production risk stays Rust-owned |

### Template Files

Migration templates are physically quarantined in `templates/legacy_migration/`:
- `legacy_migration/strategy.py` - migration/reference-only Python strategy example; use `nt-strategy-builder-rust` for new work
- `legacy_migration/indicator.py` - research/config custom indicator
- `legacy_migration/custom_data.py` - research/config custom data types for message bus
- `legacy_migration/exec_algorithm.py` - migration/reference-only; route execution-critical algorithms to Rust
- `legacy_migration/fill_model.py` - research/backtest custom fill simulation model
- `legacy_migration/margin_model.py` - research/backtest custom margin calculation model
- `legacy_migration/portfolio_statistic.py` - research/backtest custom portfolio statistic
- `legacy_migration/adapters/exchange.py` - migration/reference-only Python adapter; Rust/PyO3 owns current data + execution
- `legacy_migration/adapters/data_provider.py` - migration/reference-only Python live data client; current data clients are Rust/PyO3

### Model Loading (msgspec preferred)

```python
import msgspec
from pathlib import Path

class ModelState(msgspec.Struct):
    """Serializable model state."""
    weights: list[float]
    threshold: float
    version: str

class RegimeActor(Actor):
    def __init__(self, config: RegimeActorConfig) -> None:
        super().__init__(config)
        self.model: ModelState | None = None

    def on_start(self) -> None:
        # Load model using msgspec
        model_path = Path(self.config.model_path)
        with open(model_path, "rb") as f:
            self.model = msgspec.msgpack.decode(f.read(), type=ModelState)

        self.subscribe_bars(self.config.bar_type)
```

### Data Catalog Usage

```python
from nautilus_trader.persistence.catalog import ParquetDataCatalog

# Initialize catalog
catalog = ParquetDataCatalog("/path/to/catalog")

# Write data
catalog.write_data([instrument])  # Instruments
catalog.write_data(bars)          # Bars, ticks, etc.

# Read data
bars = catalog.bars(bar_types=[bar_type])
trades = catalog.trade_ticks(instrument_ids=[instrument_id])

# Use in backtest config
from nautilus_trader.config import BacktestDataConfig

data_config = BacktestDataConfig(
    catalog_path=str(catalog.path),
    data_cls="nautilus_trader.model.data:Bar",
    instrument_id="BTCUSDT-PERP.BINANCE",
)

# Custom data in catalog
data_config = BacktestDataConfig(
    catalog_path=str(catalog.path),
    data_cls=MyDataPoint,
    metadata={"some_optional_category": 1},
)
```

### ONNX Model Inference

```python
import onnxruntime as ort
import numpy as np

class MLActor(Actor):
    def __init__(self, config: MLActorConfig) -> None:
        super().__init__(config)
        self.session: ort.InferenceSession | None = None

    def on_start(self) -> None:
        self.session = ort.InferenceSession(self.config.onnx_model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        features = self._compute_features(bar)
        inputs = {self.input_name: features.astype(np.float32).reshape(1, -1)}
        outputs = self.session.run(None, inputs)
        prediction = outputs[0][0]
        self.publish_signal(name="prediction", value=float(prediction), ts_event=bar.ts_event)
```

### Feature Computation Pipeline

```python
class FeatureActor(Actor):
    def __init__(self, config: FeatureActorConfig) -> None:
        super().__init__(config)
        self.ema_fast = ExponentialMovingAverage(config.fast_period)
        self.ema_slow = ExponentialMovingAverage(config.slow_period)
        self.rsi = RelativeStrengthIndex(config.rsi_period)
        self.feature_buffer: deque[FeatureData] = deque(maxlen=config.lookback)

    def on_start(self) -> None:
        self.register_indicator_for_bars(self.config.bar_type, self.ema_fast)
        self.register_indicator_for_bars(self.config.bar_type, self.ema_slow)
        self.register_indicator_for_bars(self.config.bar_type, self.rsi)

        self.request_bars(self.config.bar_type)
        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        if not self.ema_fast.initialized or not self.rsi.initialized:
            return

        feature = FeatureData(
            ema_diff=self.ema_fast.value - self.ema_slow.value,
            rsi=self.rsi.value,
            ts_event=bar.ts_event,
            ts_init=self.clock.timestamp_ns(),
        )
        self.feature_buffer.append(feature)
        self.publish_data(FeatureData, feature)
```

### Position Sizing

```python
def calculate_position_size(
    self,
    signal_strength: float,
    volatility: float,
) -> Quantity:
    """Calculate position size based on signal and volatility."""
    account = self.portfolio.account(self.instrument.venue)
    equity = account.balance_total(self.instrument.quote_currency)

    # Risk-based sizing: risk X% of equity per trade
    risk_amount = float(equity) * self.config.risk_per_trade

    # Adjust for volatility (ATR-based)
    stop_distance = volatility * self.config.atr_multiplier
    if stop_distance <= 0:
        return self.instrument.make_qty(0)

    raw_size = risk_amount / stop_distance

    # Scale by signal strength
    adjusted_size = raw_size * abs(signal_strength)

    # Clamp to instrument limits
    min_qty = float(self.instrument.min_quantity)
    max_qty = float(self.instrument.max_quantity or 1e9)
    final_size = max(min_qty, min(adjusted_size, max_qty))

    return self.instrument.make_qty(final_size)
```

### Multi-Timeframe Data

```python
class MultiTimeframeStrategy(Strategy):
    def __init__(self, config: MTFConfig) -> None:
        super().__init__(config)
        self.bar_1m: Bar | None = None
        self.bar_5m: Bar | None = None
        self.bar_1h: Bar | None = None

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)

        # Define bar types
        self.bar_type_1m = BarType.from_str(f"{self.config.instrument_id}-1-MINUTE-LAST-EXTERNAL")
        self.bar_type_5m = BarType.from_str(f"{self.config.instrument_id}-5-MINUTE-LAST-INTERNAL@1-MINUTE-EXTERNAL")
        self.bar_type_1h = BarType.from_str(f"{self.config.instrument_id}-1-HOUR-LAST-INTERNAL@1-MINUTE-EXTERNAL")

        # Request historical for warmup
        self.request_bars(self.bar_type_1m)
        self.request_bars(self.bar_type_5m)
        self.request_bars(self.bar_type_1h)

        # Subscribe to live
        self.subscribe_bars(self.bar_type_1m)
        self.subscribe_bars(self.bar_type_5m)
        self.subscribe_bars(self.bar_type_1h)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.bar_type_1m:
            self.bar_1m = bar
        elif bar.bar_type == self.bar_type_5m:
            self.bar_5m = bar
        elif bar.bar_type == self.bar_type_1h:
            self.bar_1h = bar
            self._check_signals()  # Only trade on higher timeframe close

    def _check_signals(self) -> None:
        if self.bar_1m is None or self.bar_5m is None or self.bar_1h is None:
            return
        # Trading logic using all timeframes
```

### Risk Check Integration

```python
def _validate_order(self, order_side: OrderSide, quantity: Quantity) -> bool:
    """Pre-submission risk validation."""
    # Check position limits
    net_position = self.portfolio.net_position(self.instrument.id)
    if order_side == OrderSide.BUY:
        new_position = net_position + float(quantity)
    else:
        new_position = net_position - float(quantity)

    if abs(new_position) > self.config.max_position_size:
        self.log.warning(f"Order rejected: would exceed max position {self.config.max_position_size}")
        return False

    # Check daily loss limit
    realized_pnl = self.portfolio.realized_pnl(self.instrument.id)
    if realized_pnl and float(realized_pnl) < -self.config.max_daily_loss:
        self.log.warning("Order rejected: daily loss limit reached")
        return False

    return True
```
