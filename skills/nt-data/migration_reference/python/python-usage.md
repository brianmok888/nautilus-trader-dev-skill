# Python Usage

> **Migration/reference-only.** This Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-data` skill.


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

### Develop-only cache history introspection

Current `origin/develop` commit
[`aabb824cb377d62ea7ff6a7ce9489a92c705580a`](https://github.com/nautechsystems/nautilus_trader/commit/aabb824cb377d62ea7ff6a7ce9489a92c705580a),
which is newer than this repository's pinned G2 baseline, adds the following Rust
`CacheApi`/`Cache` pairs for bounded market-data histories:

- `mark_price_count` / `has_mark_prices`
- `index_price_count` / `has_index_prices`
- `funding_rate_count` / `has_funding_rates`
- `instrument_status_count` / `has_instrument_statuses`

These accessors are available at the pinned baseline `ac22d5cf4` (see the current-lane guidance in this skill's SKILL.md). Use the `*_count` result as the authoritative count and the
matching `has_*` method for the non-empty predicate; both return zero/false for
a missing history.
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
