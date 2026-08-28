# Migration/reference Python model guidance

NT v2 compatibility note: legacy Cython/v1 guidance in this file is migration/reference-only; prefer Rust v2/PyO3 for new work.
> Migration/reference-only; not a production default. Rust owns production behavior.

## Python Usage

### v1.227.0 model deltas

- `InstrumentId::parse_parent_components` and `InstrumentClass` parent suffix conversion helpers are exposed via PyO3.
- Rust cache model accessors may return scoped wrapper newtypes (`OrderRef`, `AccountRef`, `PositionRef`) rather than raw references; request owned snapshots when values cross async/event boundaries.

### Identifiers

```python
from nautilus_trader.model.identifiers import (
    InstrumentId,
    Venue,
    Symbol,
    TraderId,
    StrategyId,
)

instrument_id = InstrumentId.from_str("ETHUSDT-PERP.BINANCE")
venue = Venue("BINANCE")
symbol = Symbol("ETHUSDT-PERP")

# Identifier components
instrument_id.venue  # Venue("BINANCE")
instrument_id.symbol  # Symbol("ETHUSDT-PERP")
```

### Value Types

```python
from nautilus_trader.model.objects import Price, Quantity, Money, Currency

# Price with precision
price = Price.from_str("1850.50")
price = Price(1850.50, precision=2)

# Quantity with precision
qty = Quantity.from_str("1.5")
qty = Quantity(1.5, precision=1)

# Money
balance = Money(10_000, Currency.from_str("USD"))
balance = Money.from_str("10000 USD")

# Arithmetic
total = price * qty  # Returns float
```

### Instruments

```python
from nautilus_trader.model.instruments import (
    CurrencyPair,
    Equity,
    CryptoPerpetual,
    FuturesContract,
)

# Instruments are typically loaded from adapters or created for backtests
# Access via cache:
instrument = self.cache.instrument(instrument_id)

# Key properties:
instrument.id  # InstrumentId
instrument.venue  # Venue
instrument.base_currency  # Currency (for pairs)
instrument.quote_currency  # Currency
instrument.price_precision  # int
instrument.size_precision  # int
instrument.lot_size  # Quantity
instrument.min_quantity  # Quantity
instrument.max_quantity  # Quantity
instrument.min_price  # Price
instrument.max_price  # Price

# Create quantity/price with correct precision:
qty = instrument.make_qty(1.5)
price = instrument.make_price(1850.50)
```

**18 `InstrumentAny` variants:**
- `BettingInstrument` — betting markets
- `BinaryOption` — binary options
- `Cfd` — contracts for difference
- `Commodity` — commodities
- `CryptoFuture` — crypto dated futures
- `CryptoFuturesSpread` — crypto futures spreads
- `CryptoOption` — crypto options
- `CryptoOptionSpread` — crypto option spreads
- `CryptoPerpetual` — crypto perpetual swaps
- `CurrencyPair` — FX pairs (EUR/USD)
- `Equity` — stocks
- `FuturesContract` — dated futures
- `FuturesSpread` — futures spreads
- `IndexInstrument` — indices
- `OptionContract` — dated options
- `OptionSpread` — option spreads
- `PerpetualContract` — generic perpetual contracts
- `TokenizedAsset` — tokenized assets

SyntheticInstrument is separate from `InstrumentAny` and is not one of these variants.

### Enums

```python
from nautilus_trader.model.enums import (
    OrderSide,  # BUY, SELL
    OrderType,  # MARKET, LIMIT, STOP_MARKET, STOP_LIMIT, etc.
    TimeInForce,  # GTC, IOC, FOK, GTD, DAY
    PositionSide,  # LONG, SHORT, FLAT
    OmsType,  # HEDGING, NETTING
    AccountType,  # CASH, MARGIN
    OrderStatus,  # INITIALIZED, SUBMITTED, ACCEPTED, FILLED, CANCELED, etc.
    BarAggregation,  # TICK, SECOND, MINUTE, HOUR, DAY, etc.
    PriceType,  # BID, ASK, MID, LAST
    BookType,  # L1_MBP, L2_MBP, L3_MBO
)
```

### Currencies

```python
from nautilus_trader.model.currencies import BTC, ETH, USD, USDT

# Or dynamically:
currency = Currency.from_str("USD")
```

## Python Extension

### SyntheticInstrument

```python
from nautilus_trader.model.instruments import SyntheticInstrument

# Define a synthetic instrument from a formula combining other instruments
synthetic = SyntheticInstrument(
    symbol=Symbol("SPREAD-1"),
    price_precision=2,
    components=[instrument_id_1, instrument_id_2],
    formula="(component_0 - component_1)",
)
```

### Custom Tick Schemes

```python
from nautilus_trader.model.tick_scheme import TickScheme

# Define custom tick schemes for instruments with non-uniform tick sizes
```
