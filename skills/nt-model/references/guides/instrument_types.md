NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Instrument Types Reference Guide

Complete catalog of all instrument types in NautilusTrader with fields, creation patterns,
and Rust equivalents.

## Instrument Model

The Python surface is flat: there is no Python `Instrument` base class and no
per-type submodules. Every instrument type is a concrete class exported
directly from `nautilus_trader.model`:

```
BettingInstrument      FuturesContract
BinaryOption           FuturesSpread
Cfd                    IndexInstrument
Commodity              OptionContract
CryptoFuture           OptionSpread
CryptoFuturesSpread    PerpetualContract
CryptoOption           TokenizedAsset
CryptoOptionSpread
CryptoPerpetual
CurrencyPair
Equity
SyntheticInstrument (formula-derived; not a tradable instrument)
```

`SyntheticInstrument` is not part of the tradable instrument family; it has its own
formula-based pricing model backed by a Rust core.

On the Rust side, `InstrumentAny` (`crates/model/src/instruments/any.rs:33`) is an
`enum_dispatch` enum over the 18 tradable instrument types, and the `Instrument`
trait (`crates/model/src/instruments/mod.rs`) defines the shared surface
(`base_currency()`, `settlement_currency()`, `cost_currency()`, `activation_ns()`,
`expiration_ns()`, and more). `InstrumentAny` is Rust-side only -- it is not exposed
to Python.

## Common Instrument Fields

All concrete instrument classes expose these common fields as constructor
parameters and/or read-only properties:

### Required fields

| Field               | Type            | Description                                              |
|---------------------|-----------------|----------------------------------------------------------|
| `instrument_id`     | `InstrumentId`  | Unique ID in `{SYMBOL}.{VENUE}` format                  |
| `raw_symbol`        | `Symbol`        | Native/local symbol assigned by the venue                |
| `asset_class`       | `AssetClass`    | EQUITY, FX, CRYPTOCURRENCY, COMMODITY, INDEX, etc.       |
| `instrument_class`  | `InstrumentClass` | SPOT, FUTURE, FUTURES_SPREAD, OPTION, OPTION_SPREAD, SWAP |
| `quote_currency`    | `Currency`      | The quote currency                                       |
| `is_inverse`        | `bool`          | Quantity expressed in quote currency units                |
| `price_precision`   | `int`           | Decimal precision for prices                             |
| `size_precision`    | `int`           | Decimal precision for trade sizes                        |
| `size_increment`    | `Quantity`      | Minimum size increment                                   |
| `multiplier`        | `Quantity`      | Contract value multiplier (determines tick value)        |
| `margin_init`       | `Decimal`       | Initial margin requirement (% of order value)            |
| `margin_maint`      | `Decimal`       | Maintenance margin (% of position value)                 |
| `maker_fee`         | `Decimal`       | Fee rate for liquidity makers (% of order value)         |
| `taker_fee`         | `Decimal`       | Fee rate for liquidity takers (% of order value)         |
| `ts_event`          | `uint64`        | UNIX timestamp (nanoseconds) when event occurred         |
| `ts_init`           | `uint64`        | UNIX timestamp (nanoseconds) when object initialized     |

### Optional fields

| Field              | Type       | Description                         |
|--------------------|------------|-------------------------------------|
| `price_increment`  | `Price`    | Minimum price increment (tick size) |
| `lot_size`         | `Quantity` | Standard/board lot unit size        |
| `max_quantity`     | `Quantity` | Maximum allowable order quantity    |
| `min_quantity`     | `Quantity` | Minimum allowable order quantity    |
| `max_notional`     | `Money`    | Maximum order notional value        |
| `min_notional`     | `Money`    | Minimum order notional value        |
| `max_price`        | `Price`    | Maximum allowable quoted price      |
| `min_price`        | `Price`    | Minimum allowable quoted price      |
| `tick_scheme_name` | `str`      | Name of a registered tick scheme    |
| `info`             | `dict`     | Additional instrument information   |

### Key common properties and methods

- `type_name` -- class name string for the instrument type
- `instrument_id` -- the `InstrumentId`; use `instrument_id.symbol` and
  `instrument_id.venue` for the symbol and venue portions
- `symbol` / `venue` -- direct getters for the symbol and venue of the
  instrument's `InstrumentId` (drift-window addition; see
  `python/nautilus_trader/model/__init__.pyi` instrument classes at the pin)
- `make_price(value)` -- round a value to the instrument's price precision
- `make_qty(value, round_down=False)` -- round a value to the instrument's size precision
- `notional_value(quantity, price, use_quote_for_inverse=False)` -- calculate notional value
- `next_bid_price(value, num_ticks)` / `next_ask_price(value, num_ticks)` -- tick-scheme
  aware price stepping (returns `None` past the tick scheme bounds)
- `next_bid_prices(value, num_ticks)` / `next_ask_prices(value, num_ticks)` -- batch
  tick-stepped prices as `Decimal` lists
- `settlement_currency` -- property on instrument classes that define one
  (e.g., `CryptoPerpetual`, `CryptoFuture`, `PerpetualContract`)

## Individual Instrument Types

### Equity
**Class**: `nautilus_trader.model.Equity`
**Asset class**: `EQUITY` | **Instrument class**: `SPOT`

Additional required: `currency`, `price_increment`; optional: `lot_size` (pinned
`lot_size` property returns `Quantity | None`, `python/nautilus_trader/model/__init__.pyi:304`)
Additional optional: `isin` (ISIN code), `max_quantity`, `min_quantity`
Fixed: `size_precision=0`, `size_increment=1`, `multiplier=1`, `is_inverse=False`

### CurrencyPair
**Class**: `nautilus_trader.model.CurrencyPair`
**Asset class**: auto-detected (`CRYPTOCURRENCY` if either currency is crypto, else `FX`)
**Instrument class**: `SPOT`

Additional required: `base_currency`, `quote_currency`, `price_increment`, `size_increment`
Additional optional: `multiplier`, `lot_size`, all quantity/notional/price limits
Key property: `base_currency` -- the base currency of the pair
Fixed: `is_inverse=False`

### Commodity
**Class**: `nautilus_trader.model.Commodity`
**Asset class**: caller-specified | **Instrument class**: `SPOT`

Additional required: `asset_class`, `quote_currency`, `price_increment`, `size_increment`
Additional optional: `lot_size`, all quantity/notional/price limits
Fixed: `is_inverse=False`

### IndexInstrument
**Class**: `nautilus_trader.model.IndexInstrument`
**Asset class**: `INDEX` | **Instrument class**: `SPOT`

A spot/cash index. Not directly tradable; used as a reference price.
Additional required: `currency`, `price_increment`, `size_increment`, `size_precision`
Fixed: `is_inverse=False`, `multiplier=1`, `margin_init=0`, `margin_maint=0`

### FuturesContract
**Class**: `nautilus_trader.model.FuturesContract`
**Asset class**: caller-specified | **Instrument class**: `FUTURE`

Additional required: `asset_class`, `currency`, `price_increment`, `multiplier`, `lot_size`, `underlying` (str), `activation_ns`, `expiration_ns`
Additional optional: `exchange` (MIC code)
Properties: `activation_ns`, `expiration_ns` (UNIX nanoseconds), plus drift-window `activation_utc` / `expiration_utc` (`datetime`, UTC)
Fixed: `size_precision=0`, `size_increment=1`, `is_inverse=False`

### FuturesSpread
**Class**: `nautilus_trader.model.FuturesSpread`
**Asset class**: caller-specified | **Instrument class**: `FUTURES_SPREAD`

Additional required: `asset_class`, `currency`, `price_increment`, `multiplier`, `lot_size`, `underlying`, `strategy_type` (str), `activation_ns`, `expiration_ns`
Additional optional: `exchange`
Note: Supports negative prices.

### CryptoPerpetual
**Class**: `nautilus_trader.model.CryptoPerpetual`
**Asset class**: `CRYPTOCURRENCY` | **Instrument class**: `SWAP`

Additional required: `base_currency`, `quote_currency`, `settlement_currency`, `is_inverse`, `price_increment`, `size_increment`
Additional optional: `multiplier`, `lot_size`, all quantity/notional/price limits
Key properties: `is_quanto` (auto-calculated when settlement != base and settlement != quote), `settlement_currency`
Notional value: `notional_value(quantity, price, use_quote_for_inverse=False)` handles quanto and inverse settlement

### CryptoFuture
**Class**: `nautilus_trader.model.CryptoFuture`
**Asset class**: `CRYPTOCURRENCY` | **Instrument class**: `FUTURE`

Additional required: `underlying` (Currency), `quote_currency`, `settlement_currency`, `is_inverse`, `activation_ns`, `expiration_ns`, `price_increment`, `size_increment`
Additional optional: `multiplier`, `lot_size`, all quantity/notional/price limits
Properties: `activation_ns`, `expiration_ns`

### CryptoFuturesSpread
**Class**: `nautilus_trader.model.CryptoFuturesSpread`
**Asset class**: `CRYPTOCURRENCY` | **Instrument class**: `FUTURES_SPREAD`

Additional required: `underlying` (Currency), `quote_currency`, `settlement_currency`, `is_inverse`, `strategy_type` (str), `activation_ns`, `expiration_ns`, `price_increment`, `size_increment`
Additional optional: `multiplier`, `lot_size`, all quantity/notional/price limits
Note: Supports negative prices.

### CryptoOption
**Class**: `nautilus_trader.model.CryptoOption`
**Asset class**: `CRYPTOCURRENCY` | **Instrument class**: `OPTION`

Additional required: `underlying` (Currency), `quote_currency`, `settlement_currency`, `is_inverse`, `option_kind` (PUT/CALL), `strike_price`, `activation_ns`, `expiration_ns`, `price_increment`, `size_increment`
Additional optional: `multiplier`, `lot_size`, all limits

### CryptoOptionSpread
**Class**: `nautilus_trader.model.CryptoOptionSpread`
**Asset class**: `CRYPTOCURRENCY` | **Instrument class**: `OPTION_SPREAD`

Additional required: `underlying` (Currency), `quote_currency`, `settlement_currency`, `is_inverse`, `strategy_type` (str), `activation_ns`, `expiration_ns`, `price_increment`, `size_increment`
Additional optional: `multiplier`, `lot_size`, all limits
Note: Supports negative prices.

### PerpetualContract
**Class**: `nautilus_trader.model.PerpetualContract`
**Asset class**: caller-specified (any) | **Instrument class**: `SWAP`

Asset-class agnostic perpetual swap (FX, equities, commodities, indexes, crypto).
Additional required: `underlying` (str), `asset_class`, `quote_currency`, `settlement_currency`, `is_inverse`, `price_increment`, `size_increment`
Additional optional: `base_currency`, `multiplier`, `lot_size`, all limits

### OptionContract
**Class**: `nautilus_trader.model.OptionContract`
**Asset class**: caller-specified | **Instrument class**: `OPTION`

Additional required: `asset_class`, `currency`, `price_increment`, `multiplier`, `lot_size`, `underlying`, `option_kind` (PUT/CALL), `strike_price`, `activation_ns`, `expiration_ns`
Additional optional: `exchange`
Note: Supports negative prices.

### OptionSpread
**Class**: `nautilus_trader.model.OptionSpread`
**Asset class**: caller-specified | **Instrument class**: `OPTION_SPREAD`

Additional required: `asset_class`, `currency`, `price_increment`, `multiplier`, `lot_size`, `underlying`, `strategy_type`, `activation_ns`, `expiration_ns`
Additional optional: `exchange`
Note: Supports negative prices.

### BinaryOption
**Class**: `nautilus_trader.model.BinaryOption`
**Asset class**: caller-specified | **Instrument class**: `OPTION`

Additional required: `asset_class`, `currency`, `price_increment`, `size_increment`, `activation_ns`, `expiration_ns`
Additional optional: `outcome` (str), `description` (str), `max_quantity`, `min_quantity`

### Cfd
**Class**: `nautilus_trader.model.Cfd`
**Asset class**: auto-detected (like CurrencyPair) | **Instrument class**: `CFD`

Additional required: `quote_currency`, `price_increment`, `size_increment`
Additional optional: `base_currency`, `lot_size`, all limits

### TokenizedAsset
**Class**: `nautilus_trader.model.TokenizedAsset`
**Asset class**: caller-specified | **Instrument class**: `SPOT`

Additional required: `base_currency`, `quote_currency`, `price_increment`, `size_increment`
Additional optional: `multiplier`, `lot_size`, all limits
Key properties: `base_currency`, `is_quanto`

### BettingInstrument
**Class**: `nautilus_trader.model.BettingInstrument`
**Asset class**: `ALTERNATIVE` | **Instrument class**: `SPORTS_BETTING`

Unique fields: `venue_name`, `event_type_id`, `event_type_name`, `competition_id`, `competition_name`, `event_id`, `event_name`, `event_country_code`, `event_open_date`, `betting_type`, `market_id`, `market_name`, `market_start_time`, `market_type`, `selection_id`, `selection_name`, `selection_handicap`
The instrument ID is auto-generated from venue + market/selection data.

## SyntheticInstrument (Special)

**Class**: `nautilus_trader.model.SyntheticInstrument`
**Not** part of the tradable `InstrumentAny` family (Rust-side only)

Derives prices from component instruments using a mathematical formula.
The ID is always `{symbol}.SYNTH`.

### Required fields

| Field             | Type                 | Description                             |
|-------------------|----------------------|-----------------------------------------|
| `symbol`          | `Symbol`             | The synthetic's symbol                  |
| `price_precision` | `uint8`              | Max 9                                   |
| `components`      | `list[InstrumentId]` | At least 2 component instrument IDs     |
| `formula`         | `str`                | Mathematical expression using components|
| `ts_event`        | `uint64`             | UNIX timestamp (nanoseconds)            |
| `ts_init`         | `uint64`             | UNIX timestamp (nanoseconds)            |

### Key methods

- `calculate(inputs: list[float]) -> Price` -- compute synthetic price from component prices
- `change_formula(formula: str)` -- update the derivation formula at runtime
- `components` (property) -- list of component InstrumentId values
- `formula` (property) -- the current formula string

### Constraints

- `price_precision` must be <= 9
- Must have at least 2 component instruments
- Formula is validated against components at creation time
- Components should already exist in the cache before defining the synthetic
- Currently not safe for serialization via the standard library serializer

## Common Creation Patterns

### From dict (deserialization)

Every instrument type provides `from_dict()` and `to_dict()` static methods:

```python
values = {
    "id": "AAPL.XNAS",
    "raw_symbol": "AAPL",
    "currency": "USD",
    "price_precision": 2,
    "price_increment": "0.01",
    "lot_size": "1",
    "ts_event": 0,
    "ts_init": 0,
    "info": {},
}
equity = Equity.from_dict(values)
```

### From Rust

No per-object conversion API exists: the classes exported from `nautilus_trader.model`
are the PyO3 bindings over the Rust instrument structs (a single compiled surface).
When reconstructing value types from raw fields, use `Price.from_raw(raw, precision)`
and `Quantity.from_raw(raw, precision)`, which preserve the exact fixed-point
representation without float conversion.

### Manual construction

```python
from nautilus_trader.model import Equity, InstrumentId, Symbol, Currency, Price, Quantity

equity = Equity(
    instrument_id=InstrumentId.from_str("AAPL.XNAS"),
    raw_symbol=Symbol("AAPL"),
    currency=Currency.from_str("USD"),
    price_precision=2,
    price_increment=Price.from_str("0.01"),
    lot_size=Quantity.from_int(1),
    ts_event=0,
    ts_init=0,
)
```

## Rust Equivalents

Each Python instrument has a corresponding Rust struct in `crates/model/src/instruments/`:

| Python class         | Rust module                         | Rust struct            |
|----------------------|-------------------------------------|------------------------|
| `BettingInstrument`  | `instruments::betting`              | `BettingInstrument`    |
| `BinaryOption`       | `instruments::binary_option`        | `BinaryOption`         |
| `Cfd`                | `instruments::cfd`                  | `Cfd`                  |
| `Commodity`          | `instruments::commodity`            | `Commodity`            |
| `CryptoFuture`       | `instruments::crypto_future`        | `CryptoFuture`         |
| `CryptoFuturesSpread`| `instruments::crypto_futures_spread`| `CryptoFuturesSpread`  |
| `CryptoOption`       | `instruments::crypto_option`        | `CryptoOption`         |
| `CryptoOptionSpread` | `instruments::crypto_option_spread` | `CryptoOptionSpread`   |
| `CryptoPerpetual`    | `instruments::crypto_perpetual`     | `CryptoPerpetual`      |
| `CurrencyPair`       | `instruments::currency_pair`        | `CurrencyPair`         |
| `Equity`             | `instruments::equity`               | `Equity`               |
| `FuturesContract`    | `instruments::futures_contract`     | `FuturesContract`      |
| `FuturesSpread`      | `instruments::futures_spread`       | `FuturesSpread`        |
| `IndexInstrument`    | `instruments::index_instrument`     | `IndexInstrument`      |
| `OptionContract`     | `instruments::option_contract`      | `OptionContract`       |
| `OptionSpread`       | `instruments::option_spread`        | `OptionSpread`         |
| `PerpetualContract`  | `instruments::perpetual_contract`   | `PerpetualContract`    |
| `SyntheticInstrument`| `instruments::synthetic`            | `SyntheticInstrument`  |
| `TokenizedAsset`     | `instruments::tokenized_asset`      | `TokenizedAsset`       |

The Rust side also defines:
- `InstrumentAny` enum (`instruments::any`) -- an `enum_dispatch` wrapper over the 18
  tradable instrument types (Rust-side only, not exposed to Python)
- `validate_instrument_common()` -- shared validation logic for all instruments
- `TickSchemeRule` trait and `FixedTickScheme` -- tick stepping logic
- Stubs module (`instruments::stubs`) for test fixtures (behind `test` or `stubs` feature flag)

## Expiring Instruments

Instrument classes that expire carry `activation_ns` and `expiration_ns`
(Unix-nanosecond) fields on the flat `nautilus_trader.model` classes, and expose
drift-window `activation_utc` / `expiration_utc` properties returning UTC
`datetime` objects (`crates/model/src/python/instruments/mod.rs`
`impl_instrument_utc_getters` at the pin). The Rust
side models expiry through the instrument definitions in `crates/model/src/instruments/`;
no Python-side instrument-class set constants are exported at the pinned baseline.
