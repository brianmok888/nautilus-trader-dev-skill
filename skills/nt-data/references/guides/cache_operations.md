NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Cache Operations Reference

## Overview

The `Cache` class (`nautilus_trader.common.Cache`) is the central in-memory store for all
market and execution data in NautilusTrader. Strategies and actors access it directly through
`self.cache` (a `Cache` instance) in any strategy or actor.

The cache holds instruments, orders, positions, accounts, ticks, bars, order books, and arbitrary
key-value pairs. It maintains a rich set of indexes that enable fast filtering
by venue, instrument, strategy, account, and order/position status.

---

## Cache Configuration (CacheConfig)

**Module**: `nautilus_trader.common`

```python
from nautilus_trader.common import CacheConfig

config = CacheConfig(
    encoding=None,  # SerializationEncoding | None -- serialization encoding
    timestamps_as_iso8601=None,  # True -> ISO 8601 strings; False -> UNIX nanos
    buffer_interval_ms=None,  # ms between pipelined/batched transactions (10-1000 recommended)
    bulk_read_batch_size=None,  # chunk size for bulk reads (helps with Redis provider limits)
    use_trader_prefix=True,  # prefix keys with "trader-"
    use_instance_id=False,  # include trader instance ID in keys
    flush_on_start=False,  # flush backing store on startup
    drop_instruments_on_reset=True,  # clear instrument cache on reset
    tick_capacity=10_000,  # max deque length for quote/trade ticks per instrument
    bar_capacity=10_000,  # max deque length for bars per bar type
    save_market_data=None,  # persist market data (ticks/bars) to the backing store
    persist_account_events=None,  # write account events to the backing store
)
```

Key points:
- `tick_capacity` / `bar_capacity` control how many recent ticks or bars are kept in memory per
  instrument or bar type. Older entries are automatically evicted from the front of the deque.
- Setting `buffer_interval_ms` enables pipelined/batched writes to the database adapter, reducing
  I/O overhead at the cost of slightly delayed persistence.
- `flush_on_start=True` wipes all data in the backing store on each startup -- useful for
  development but dangerous in production.

---

## Instrument Queries

```python
# Single instrument by ID
instrument = self.cache.instrument(instrument_id)

# All instrument IDs, optionally filtered by venue
ids = self.cache.instrument_ids(venue=None)

# All instruments, optionally filtered by venue
instruments = self.cache.instruments(venue=None)

# Synthetic instruments
synthetic = self.cache.synthetic(instrument_id)
synthetic_ids = self.cache.synthetic_ids()
```

---

## Market Data Queries

### Ticks

```python
# Latest quote tick (index=0 is most recent, negative indexes go back)
tick = self.cache.quote(instrument_id, index=0)
ticks = self.cache.quotes(instrument_id)  # full series as list
count = self.cache.quote_count(instrument_id)
has = self.cache.has_quote_ticks(instrument_id)

# Trade ticks -- same pattern
tick = self.cache.trade(instrument_id, index=0)
ticks = self.cache.trades(instrument_id)
count = self.cache.trade_count(instrument_id)
has = self.cache.has_trade_ticks(instrument_id)
```

### Bars

```python
bar = self.cache.bar(bar_type, index=0)
bars_list = self.cache.bars(bar_type)
count = self.cache.bar_count(bar_type)
has = self.cache.has_bars(bar_type)
```

### Order Books

```python
book = self.cache.order_book(instrument_id)
own_book = self.cache.own_order_book(instrument_id)
update_count = self.cache.book_update_count(instrument_id)
has = self.cache.has_order_book(instrument_id)
```

### Prices and Cross Rates

```python
from nautilus_trader.model.enums import PriceType

price = self.cache.price(instrument_id, PriceType.MID)

xrate = self.cache.get_xrate(venue, from_currency, to_currency, PriceType.MID)
mark_xrate = self.cache.get_mark_xrate(from_currency, to_currency)
```

### Crypto-Specific Data

```python
mark = self.cache.mark_price(instrument_id)
marks = self.cache.mark_prices(instrument_id)

idx = self.cache.index_price(instrument_id)
idxs = self.cache.index_prices(instrument_id)

fr = self.cache.funding_rate(instrument_id)
frs = self.cache.funding_rates(instrument_id)

# Counts and presence checks
mark_count = self.cache.mark_price_count(instrument_id)
index_count = self.cache.index_price_count(instrument_id)
funding_count = self.cache.funding_rate_count(instrument_id)
has_marks = self.cache.has_mark_prices(instrument_id)
has_index = self.cache.has_index_prices(instrument_id)
has_funding = self.cache.has_funding_rates(instrument_id)
```

---

## Account Queries

```python
account = self.cache.account(account_id)
account = self.cache.account_for_venue(venue)
aid = self.cache.account_id(venue)
```

---

## Order Queries

All order query methods accept optional filters: `venue`, `instrument_id`, `strategy_id`, `side`, `account_id`.

```python
order = self.cache.order(client_order_id)
orders = self.cache.orders(
    venue=None, instrument_id=None, strategy_id=None, account_id=None, side=None
)
open_orders = self.cache.orders_open(...)
closed = self.cache.orders_closed(...)
emulated = self.cache.orders_emulated(...)
inflight = self.cache.orders_inflight(...)
for_position = self.cache.orders_for_position(position_id)

# Counts
self.cache.orders_open_count(...)
self.cache.orders_closed_count(...)
self.cache.orders_emulated_count(...)
self.cache.orders_inflight_count(...)
self.cache.orders_total_count(...)

# Status checks
self.cache.order_exists(client_order_id)
self.cache.is_order_open(client_order_id)
self.cache.is_order_closed(client_order_id)
self.cache.is_order_emulated(client_order_id)
self.cache.is_order_inflight(client_order_id)
self.cache.is_order_pending_cancel_local(client_order_id)

# ID lookups
self.cache.client_order_id(venue_order_id)
self.cache.venue_order_id(client_order_id)
self.cache.client_id(client_order_id)
```

### Order Lists

```python
order_list = self.cache.order_list(order_list_id)
order_lists = self.cache.order_lists(venue=None, instrument_id=None, strategy_id=None)
exists = self.cache.order_list_exists(order_list_id)
```

### Exec Algorithm Queries

```python
orders = self.cache.orders_for_exec_algorithm(exec_algorithm_id, ...)
spawn_orders = self.cache.orders_for_exec_spawn(exec_spawn_id)
total_qty = self.cache.exec_spawn_total_quantity(exec_spawn_id)
filled_qty = self.cache.exec_spawn_total_filled_qty(exec_spawn_id)
leaves_qty = self.cache.exec_spawn_total_leaves_qty(exec_spawn_id)
```

---

## Position Queries

All position query methods accept optional filters: `venue`, `instrument_id`, `strategy_id`, `side`, `account_id`.

```python
position = self.cache.position(position_id)
position = self.cache.position_for_order(client_order_id)
pid = self.cache.position_id(client_order_id)

positions = self.cache.positions(...)
open_positions = self.cache.positions_open(...)
closed_positions = self.cache.positions_closed(...)

self.cache.positions_open_count(...)
self.cache.positions_closed_count(...)
self.cache.positions_total_count(...)

self.cache.position_exists(position_id)
self.cache.is_position_open(position_id)
self.cache.is_position_closed(position_id)

# Snapshots
snapshots = self.cache.position_snapshots(position_id=None, account_id=None)
snapshot_bytes = self.cache.position_snapshot_bytes(position_id)
self.cache.snapshot_position(position)
```

---

## General Key-Value Store

The cache provides a general key-value store for persisting custom strategy/actor state.
Values are byte payloads represented as sequences of ints at the Python boundary:

```python
self.cache.add("my_key", [0, 1, 2])  # Sequence[int] (byte payload)
value = self.cache.get("my_key")  # list[int] | None
```

When a backing store is configured, these values are persisted through the
infrastructure backing store (see below).

---

## Durable Backing Stores (`nautilus_trader.infrastructure`)

**Module**: `nautilus_trader.infrastructure`

Durable cache backing at the pinned tree is provided by the `nautilus_infrastructure`
crate (Rust: `crates/infrastructure/src/{redis,sql}`) and exposed to Python through
`nautilus_trader.infrastructure`:

- `PostgresCacheConfig(host, port, username, password, database)` -- PostgreSQL cache
  backing. The SQL implementation lives in `crates/infrastructure/src/sql/`
  (`pg.rs`, `cache.rs`), including bulk loaders such as `load_all()`,
  `load_currencies()`, `load_instruments()`, `load_synthetics()`, and `load_orders()`.
- `RedisCacheConfig` -- Redis cache backing (`crates/infrastructure/src/redis/cache.rs`).
- `RedisMessageBusConfig` / `RedisMessageBusBacking` / `RedisMessageBusFactory` --
  Redis-backed message bus (publish/stream/close; `crates/infrastructure/src/redis/msgbus.rs`).
- `PostgresConnectOptions` -- explicit Postgres connection options
  (`host`, `port`, `user`, `password`, `database`).

Whether market data is written through to the backing store is controlled by
`CacheConfig.save_market_data`; account events by `CacheConfig.persist_account_events`.

---

## Cache Population: Backtest vs Live

### Backtest

During backtesting, the engine populates the cache differently:

1. **Instruments**: Added by the `BacktestEngine` before the run starts. The data engine feeds
   instruments into the cache when processing historical data.
2. **Market data**: Ticks and bars flow through the data engine into the cache as the backtest
   clock advances. The deque capacity (`tick_capacity`, `bar_capacity`) limits memory usage.
3. **Orders/Positions**: Created during the backtest as the strategy submits orders. The simulated
   exchange fills orders and the execution engine updates the cache.
4. **No durable backing**: Backtests typically run without a backing store configured. All
   state lives purely in memory and is discarded after the run.

### Live

In live trading, the cache is populated from two sources:

1. **Backing-store restore**: On startup, the infrastructure backing store (Postgres or Redis;
   see above) loads persisted currencies, instruments, accounts, orders, and positions into the
   cache and its in-memory indexes are rebuilt from the loaded records.
2. **Live data feeds**: As market data and execution events arrive, the cache is updated in real
   time. Changes are simultaneously written through to the configured backing store (market data
   only when `CacheConfig.save_market_data` is enabled).
3. **Reconciliation**: The execution engine reconciles cached order/position state against the
   venue's reported state during startup.

### Backing-Store Restore Sequence (Rust)

The Rust backing stores (`crates/infrastructure/src/{sql,redis}/cache.rs`)
restore state on startup through typed bulk loaders, conceptually:

```
load_all()           # Load all general state from the backing store
  -> load_currencies()
  -> load_instruments()
  -> load_synthetics()
  -> load_orders()
  -> load_positions()
# loaded records repopulate the in-memory indexes
```

---

## Option Greeks and Pools

Option greeks are a model data type at the pinned tree (`model.OptionGreeks`):
actors and strategies subscribe with `subscribe_option_greeks(...)` and receive
them via `on_option_greeks`; pricing uses the `GreeksCalculator` helper
(`instrument_greeks(...)`). AMM pool state has typed cache lookups:

```python
pool = self.cache.pool(instrument_id)
profiler = self.cache.pool_profiler(instrument_id)
```

The legacy `add_greeks`/`greeks`/`add_yield_curve`/`yield_curve` opaque-object
store no longer exists.
