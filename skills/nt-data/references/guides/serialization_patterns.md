NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Serialization Patterns Reference

## Overview

NautilusTrader v2 exposes Arrow serialization from the flat PyO3 module
`nautilus_trader.serialization`. The public API produces Arrow IPC stream bytes for core market-data
and event types. Matching wranglers in `nautilus_trader.persistence` consume those bytes and return
native NautilusTrader objects.

Use the public module owners directly:

```python
from nautilus_trader.persistence import QuoteTickDataWrangler
from nautilus_trader.serialization import (
    get_arrow_schema_map,
    quotes_to_arrow_record_batch_bytes,
)
```

There is no public `nautilus_trader.serialization.arrow` package, `ArrowSerializer` class, or
`register_arrow()` registry in the pinned v2 Python API.

---

## Built-in Arrow Schemas

**Module**: `nautilus_trader.serialization`

Call `get_arrow_schema_map(data_cls)` to inspect the schema metadata exported for a supported
NautilusTrader data type:

```python
from nautilus_trader.model import PRECISION_BYTES, QuoteTick
from nautilus_trader.serialization import get_arrow_schema_map

schema_map = get_arrow_schema_map(QuoteTick)
assert PRECISION_BYTES > 0
```

Treat the returned mapping as the source of truth for the pinned runtime. Core market-data schemas
include the following fields:

| Type | Key Fields |
|------|-----------|
| `OrderBookDelta` | action, side, price, size, order_id, flags, sequence, ts_event, ts_init |
| `OrderBookDepth10` | bid/ask prices, sizes and counts for levels 0..9, flags, sequence, ts_event, ts_init |
| `QuoteTick` | bid_price, ask_price, bid_size, ask_size, ts_event, ts_init |
| `TradeTick` | price, size, aggressor_side, trade_id, ts_event, ts_init |
| `Bar` | open, high, low, close, volume, ts_event, ts_init |
| `MarkPriceUpdate` | instrument_id, value, ts_event, ts_init |
| `IndexPriceUpdate` | instrument_id, value, ts_event, ts_init |

Prices and quantities use the model's fixed-precision representation. When constructing an Arrow
table outside NautilusTrader, match the schema returned by `get_arrow_schema_map()` exactly instead
of inventing a parallel schema.

---

## Serialization API

### Rust serializer functions

The flat `nautilus_trader.serialization` module exports these Arrow IPC writers:

| Function | Data Type |
|----------|-----------|
| `bars_to_arrow_record_batch_bytes()` | `Bar` |
| `book_deltas_to_arrow_record_batch_bytes()` | `OrderBookDelta` |
| `book_depth10_to_arrow_record_batch_bytes()` | `OrderBookDepth10` |
| `index_prices_to_arrow_record_batch_bytes()` | `IndexPriceUpdate` |
| `instrument_closes_to_arrow_record_batch_bytes()` | `InstrumentClose` |
| `instrument_status_to_arrow_record_batch_bytes()` | `InstrumentStatus` |
| `mark_prices_to_arrow_record_batch_bytes()` | `MarkPriceUpdate` |
| `option_greeks_to_arrow_record_batch_bytes()` | `OptionGreeks` |
| `pyobjects_to_arrow_record_batch_bytes()` | supported generic PyO3 objects |
| `quotes_to_arrow_record_batch_bytes()` | `QuoteTick` |
| `trades_to_arrow_record_batch_bytes()` | `TradeTick` |

The module also exports `instrument_status_from_arrow_record_batch_bytes()` and
`option_greeks_from_arrow_record_batch_bytes()` for those corresponding Rust-backed types.

### Reading IPC bytes with PyArrow

```python
import pyarrow as pa

from nautilus_trader.serialization import quotes_to_arrow_record_batch_bytes

ipc_bytes = quotes_to_arrow_record_batch_bytes(ticks)
with pa.ipc.open_stream(ipc_bytes) as reader:
    table = reader.read_all()
```

### Round-tripping through a PyO3 wrangler

```python
from nautilus_trader.persistence import QuoteTickDataWrangler
from nautilus_trader.serialization import quotes_to_arrow_record_batch_bytes

wrangler = QuoteTickDataWrangler(
    instrument_id="EUR/USD.SIM",
    price_precision=5,
    size_precision=0,
)

ipc_bytes = quotes_to_arrow_record_batch_bytes(ticks)
restored_ticks = wrangler.process_record_batch_bytes(ipc_bytes)
```

---

## Data Wranglers

### V2 wranglers (PyO3)

**Module**: `nautilus_trader.persistence`

The v2 wranglers accept Arrow IPC stream bytes and return native PyO3 model objects. Their public
constructors take raw IDs and precision values; `BarDataWrangler` takes a bar-type string instead of
an instrument ID.

| Wrangler | Output Type | Constructor Args |
|----------|-------------|------------------|
| `OrderBookDeltaDataWrangler` | `list[OrderBookDelta]` | instrument_id, price_precision, size_precision |
| `OrderBookDepth10DataWrangler` | `list[OrderBookDepth10]` | instrument_id, price_precision, size_precision |
| `QuoteTickDataWrangler` | `list[QuoteTick]` | instrument_id, price_precision, size_precision |
| `TradeTickDataWrangler` | `list[TradeTick]` | instrument_id, price_precision, size_precision |
| `BarDataWrangler` | `list[Bar]` | bar_type, price_precision, size_precision |

Each class exposes `process_record_batch_bytes(data: bytes)`. The pinned API does not expose
`from_instrument()`, `from_schema()`, `from_pandas()`, `from_arrow()`, or `ts_init_delta` helpers.

### V2 wrangler pipeline

For external data:

1. Normalize IDs, timestamps and numeric precision at the ingestion boundary.
2. Build a PyArrow table whose schema matches `get_arrow_schema_map(data_cls)`.
3. Write the table as an Arrow IPC stream with `pa.ipc.new_stream()`.
4. Pass the resulting bytes to `process_record_batch_bytes()`.

```python
import pyarrow as pa

from nautilus_trader.persistence import QuoteTickDataWrangler

# `table` must already match the QuoteTick Arrow schema.
sink = pa.BufferOutputStream()
with pa.ipc.new_stream(sink, table.schema) as writer:
    writer.write_table(table)

wrangler = QuoteTickDataWrangler("EUR/USD.SIM", 5, 0)
ticks = wrangler.process_record_batch_bytes(sink.getvalue().to_pybytes())
```

If you need simulated ingestion latency, set or transform `ts_init` before writing the Arrow table;
the v2 wranglers do not add a `ts_init_delta` themselves.

---

## Common Patterns

### Reading Nautilus Arrow data from Parquet

```python
import pyarrow as pa
import pyarrow.parquet as pq

from nautilus_trader.persistence import BarDataWrangler

# The Parquet schema must match the Bar Arrow schema.
table = pq.read_table("bars.parquet")
sink = pa.BufferOutputStream()
with pa.ipc.new_stream(sink, table.schema) as writer:
    writer.write_table(table)

wrangler = BarDataWrangler(
    bar_type="EUR/USD.SIM-1-MINUTE-BID-EXTERNAL",
    price_precision=5,
    size_precision=0,
)
bars = wrangler.process_record_batch_bytes(sink.getvalue().to_pybytes())
```

### Writing serialized data to Parquet

```python
import pyarrow as pa
import pyarrow.parquet as pq

from nautilus_trader.serialization import quotes_to_arrow_record_batch_bytes

ipc_bytes = quotes_to_arrow_record_batch_bytes(ticks)
with pa.ipc.open_stream(ipc_bytes) as reader:
    table = reader.read_all()

pq.write_table(table, "quotes.parquet")
```

---

## NT v2 compatibility note: removed Cython wranglers (migration)

NT v2 compatibility note: the following Cython/v1 API is retained only as migration material for
older integrations. Do not use it for new v2 work.

**Legacy module (removed from the pinned v2 package)**: `nautilus_trader.persistence.wranglers`

NT v2 compatibility note: for migration, the former Cython wranglers accepted an `Instrument` and pandas DataFrames directly:

| Legacy Wrangler | Output Type | Legacy Input |
|-----------------|-------------|--------------|
| `OrderBookDeltaDataWrangler(instrument)` | `list[OrderBookDelta]` | DataFrame with action, side, price, size, order_id, flags, sequence |
| `QuoteTickDataWrangler(instrument)` | `list[QuoteTick]` | DataFrame with bid/ask prices and optional sizes |
| `TradeTickDataWrangler(instrument)` | `list[TradeTick]` | DataFrame with price, quantity, trade_id and optional side |
| `BarDataWrangler(bar_type, instrument)` | `list[Bar]` | DataFrame with OHLC and optional volume |

These legacy classes used methods such as `.process(df, ts_init_delta=0, is_raw=False)` and
`.process_bar_data(...)`. For v2, normalize the input yourself, write Arrow IPC bytes, and call the
flat `nautilus_trader.persistence` wrangler described above.
