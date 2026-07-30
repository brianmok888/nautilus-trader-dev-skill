# Legacy Python DataTesterConfig examples

NT v2 compatibility note: legacy Cython/v1 guidance in this file is migration/reference-only; prefer Rust v2/PyO3 for new work.
> Migration/reference-only; not a production default.

```python
from nautilus_trader.test_kit.strategies.tester_data import DataTesterConfig

# Basic config
config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
)

# Constructor-keyword scenarios
config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_quotes=True,
)

config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_trades=True,
)

config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    bar_types=[bar_type],
    subscribe_bars=True,
)

# Order book variants
config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_book_deltas=True,
    book_type=BookType.L2_MBP,
)

config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_book_depth=True,
    book_type=BookType.L2_MBP,
    book_depth=10,
)

# Instrument discovery
config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    request_instruments=True,
)

config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_instrument=True,
)
```
