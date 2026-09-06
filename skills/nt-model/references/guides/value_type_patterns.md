NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Value Type Patterns Reference Guide

Comprehensive guide to NautilusTrader's core value types: Price, Quantity, Money,
Currency, and AccountBalance. Covers precision handling, construction patterns,
arithmetic, and Rust interop.

## Architecture Overview

All numeric value types use **fixed-point arithmetic** backed by Rust. Values are stored
as scaled integers internally (`raw` field), avoiding floating-point rounding issues.

| Type             | Module                               | Signed | Has Currency | Range                                |
|------------------|--------------------------------------|--------|--------------|--------------------------------------|
| `Quantity`       | `nautilus_trader.model`              | No     | No           | [0, 34_028_236_692_093]              |
| `Price`          | `nautilus_trader.model`              | Yes    | No           | [-17_014_118_346_046, 17_014_118_346_046] |
| `Money`          | `nautilus_trader.model`              | Yes    | Yes          | [-17_014_118_346_046, 17_014_118_346_046] |
| `Currency`       | `nautilus_trader.model`              | N/A    | N/A          | N/A                                  |
| `AccountBalance` | `nautilus_trader.model`              | N/A    | Yes          | N/A                                  |

## Precision Handling

### Standard vs High-Precision Mode

NautilusTrader supports two precision modes, determined at compile time via the Rust core:

- **Standard mode**: `FIXED_PRECISION = 9`, `FIXED_SCALAR = 1_000_000_000`
- **High-precision mode**: `FIXED_PRECISION = 16`, `FIXED_SCALAR = 10_000_000_000_000_000`

Check the active mode at runtime:

```python
from nautilus_trader.model import HIGH_PRECISION, FIXED_PRECISION, FIXED_SCALAR

print(f"High precision: {HIGH_PRECISION}")
print(f"Fixed precision: {FIXED_PRECISION}")
print(f"Fixed scalar: {FIXED_SCALAR}")
```

### Raw Representation

All values are stored as scaled integers. The `raw` property exposes this:

```python
price = Price.from_str("1.23456")
print(price.raw)  # Scaled integer (e.g., 1234560000 in standard mode)
print(price.precision)  # 5
```

The relationship is: `display_value = raw / FIXED_SCALAR`

The `raw` value must be a valid multiple of the scale factor for the given precision
(divisible by `10^(FIXED_PRECISION - precision)`).

### Precision Bytes

The `PRECISION_BYTES` constant indicates how many bytes are used for precision
storage in the underlying Rust types.

## Quantity

Non-negative value for trade sizes, order amounts, and positions.

### Construction Patterns

```python
from nautilus_trader.model import Quantity

# From float + explicit precision
qty = Quantity(100.5, precision=1)  # "100.5"

# From string (precision inferred from decimal places)
qty = Quantity.from_str("100.50")  # precision=2

# From integer (precision=0)
qty = Quantity.from_int(100)  # "100"

# From raw fixed-point value (advanced/internal use)
qty = Quantity.from_raw(1005000000000, 1)  # "100.5" in standard mode

# From Decimal (precision inferred)
from decimal import Decimal

qty = Quantity.from_decimal(Decimal("100.50"))  # precision=2

# Zero value
qty = Quantity.zero(precision=2)  # "0.00"
```

### Key Properties

- `raw` -- the raw scaled integer representation
- `precision` -- number of decimal places (uint8)

### Conversion Methods

- `as_decimal()` -- returns Python `Decimal`
- `as_double()` -- returns `float`
- `to_formatted_str()` -- returns underscore-separated string (e.g., "1_000_000.50")

### Arithmetic

```python
qty1 = Quantity(100, precision=0)
qty2 = Quantity(50, precision=0)

# Quantity + Quantity -> Quantity (preserves max precision)
result = qty1 + qty2  # Quantity("150")

# Quantity - Quantity -> Quantity (raises ValueError if result would be negative)
result = qty1 - qty2  # Quantity("50")

# Quantity * anything -> Decimal (or float if either operand is float)
result = qty1 * 2  # Decimal("200")
result = qty1 * 2.0  # float 200.0

# Quantity / anything -> Decimal (or float)
result = qty1 / qty2  # Decimal("2")
```

**Important**: Subtraction (`__sub__`) raises `ValueError` if the result would be
negative. For clamping subtraction use `saturating_sub(other)`, which returns the
zero-clamped `Quantity` result (pinned `python/nautilus_trader/model/__init__.pyi:6190`;
Rust `crates/model/src/types/quantity.rs:334`).

### Constraints

- Value must be >= 0 (non-negative)
- Precision must be <= `FIXED_PRECISION` (9 or 16)
- Value must be <= `QUANTITY_MAX` (34_028_236_692_093)

## Price

Signed value for market prices, quotes, and price levels. Can be negative (e.g., options).

### Construction Patterns

```python
from nautilus_trader.model import Price

# From float + explicit precision
price = Price(1.2345, precision=4)

# From string (precision inferred)
price = Price.from_str("1.2345")

# From integer (precision=0)
price = Price.from_int(100)

# From raw fixed-point value (advanced/internal use)
price = Price.from_raw(12345000000000, 4)

# From Decimal (precision inferred)
from decimal import Decimal

price = Price.from_decimal(Decimal("1.2345"))
```

### Arithmetic

Same patterns as Quantity:
- `Price + Price -> Price`
- `Price - Price -> Price` (can produce negative results, unlike Quantity)
- `Price * anything -> Decimal` (or float)
- `Price / anything -> Decimal` (or float)

### Comparisons

Price supports all comparison operators (`<`, `<=`, `>`, `>=`, `==`).
Comparisons work across Price, Quantity, and Decimal types by converting to Decimal internally.

### Key Differences from Quantity

- **Signed**: Can represent negative values (range includes negatives)
- **Subtraction always produces a result** (can be negative, unlike Quantity)
- Range: `PRICE_MIN` to `PRICE_MAX`

## Money

A Price-like value paired with a Currency denomination.

### Construction Patterns

```python
from nautilus_trader.model import Money, Currency

usd = Currency.from_str("USD")

# From value + currency
money = Money(1000.50, usd)

# From string ("amount CURRENCY" format)
money = Money.from_str("1000.50 USD")

# From raw fixed-point value + currency
money = Money.from_raw(10005000000000, usd)

# From Decimal + currency
from decimal import Decimal

money = Money.from_decimal(Decimal("1000.50"), usd)
```

### Key Properties

- `raw` -- raw scaled integer
- `currency` -- the `Currency` object

### Arithmetic

Money arithmetic enforces currency matching:

```python
usd1 = Money(100, Currency.from_str("USD"))
usd2 = Money(50, Currency.from_str("USD"))

# Money + Money -> Money (currencies must match)
result = usd1 + usd2  # Money(150.00, USD)

# Money - Money -> Money (currencies must match, can be negative)
result = usd2 - usd1  # Money(-50.00, USD)

# Money * scalar -> Decimal (or float)
result = usd1 * 2  # Decimal("200.00")
```

Comparing or adding Money with different currencies raises a `Condition` error.

### String Representation

```python
money = Money(1234567.89, Currency.from_str("USD"))
str(money)  # "1234567.89 USD"
money.to_formatted_str()  # "1_234_567.89 USD"
```

## Currency

Represents a medium of exchange with a fixed decimal precision.

### Construction

```python
from nautilus_trader.model import Currency, CurrencyType

# Look up a pre-registered currency (fiat + common crypto in the internal map)
usd = Currency.from_str("USD")
btc = Currency.from_str("BTC")

# Strict mode: raises for unknown codes (no auto-creation)
result = Currency.from_str("UNKNOWN", strict=True)  # ValueError

# Non-strict mode (default): unknown codes auto-create as crypto with precision=8
token = Currency.from_str("MYTOKEN")  # Auto-created, precision=8, type=CRYPTO

# Manual construction
custom = Currency(
    code="GOLD",
    precision=6,
    iso4217=0,
    name="Gold Token",
    currency_type=CurrencyType.CRYPTO,
)
```

### Key Properties

- `code` -- currency code string (e.g., "USD", "BTC")
- `name` -- full currency name
- `precision` -- decimal precision for this currency (determines Money display)
- `iso4217` -- ISO 4217 numeric code (0 for non-standard/crypto)
- `currency_type` -- `CurrencyType.FIAT` or `CurrencyType.CRYPTO`

### Static Utility Methods

- `Currency.is_fiat(code)` -- check if a code is a fiat currency
- `Currency.is_crypto(code)` -- check if a code is a cryptocurrency
- `Currency.register(currency, overwrite=False)` -- register in internal map

## Currency Registry and Custom Currencies

The system maintains a single global currency map in Rust (the same map the PyO3
bindings use), pre-populated with common fiat and crypto currencies. There is no
separate `currencies` module of constants: obtain registered currencies with
`Currency.from_str`:

```python
from nautilus_trader.model import Currency

usd = Currency.from_str("USD")
print(usd.precision)  # 2
btc = Currency.from_str("BTC")
print(btc.precision)  # 8
```

### Built-in Fiat Currencies

AUD, BRL, CAD, CHF, CNY, CNH, CZK, DKK, EUR, GBP, HKD, HUF, ILS, INR, JPY,
KRW, MXN, NOK, NZD, PLN, RUB, SAR, SEK, SGD, THB, TRY, USD, XAG, XAU, ZAR

### Built-in Crypto Currencies

1INCH, AAVE, ACA, ADA, ARB, AVAX, BCH, BIO, BNB, BRZ, BSV, BTC, BUSD, XBT,
CRV, and many more (50+ crypto currencies pre-registered).

### Registering Custom Currencies

Register custom currencies in the global internal map with
`Currency.register(currency, overwrite=False)` (a no-op if the code already exists
and `overwrite` is `False`):

```python
from nautilus_trader.model import Currency, CurrencyType

custom = Currency(
    code="XCOIN",
    precision=6,
    iso4217=0,
    name="X Coin",
    currency_type=CurrencyType.CRYPTO,
)

# Registers in the Rust internal map shared with the PyO3 bindings
Currency.register(custom, overwrite=False)
```

## AccountBalance

Represents an account balance with total, locked, and free amounts.

### Construction

```python
from nautilus_trader.model import AccountBalance, Money, Currency

usd = Currency.from_str("USD")

balance = AccountBalance(
    total=Money(10000, usd),
    locked=Money(2500, usd),
    free=Money(7500, usd),
)
```

### Constraints

- All three Money values must use the same currency
- `total - locked == free` (enforced at construction)

### Properties

- `total` -- total account balance
- `locked` -- balance locked by pending orders
- `free` -- balance available for trading
- `currency` -- the denomination currency

### Serialization

```python
d = AccountBalance.to_dict(balance)
# {"type": "AccountBalance", "total": "10000.00 USD", "locked": "2500.00 USD", "free": "7500.00 USD"}

restored = AccountBalance.from_dict(d)
```

## Instrument Properties

Instruments expose their specifications through the same value types, keeping precision
handling uniform across the model (pinned
`python/nautilus_trader/model/instruments/__init__.pyi`):

- Precision and increments: `price_precision` / `size_precision` (`int`) with the
  matching `price_increment` (`Price`) and `size_increment` (`Quantity`).
- Sizing: `multiplier` and `lot_size` (`Quantity`); optional exchange limits
  `max_quantity` / `min_quantity` (`Quantity | None`), `max_notional` /
  `min_notional` (`Money | None`), and `max_price` / `min_price` (`Price | None`).
- Margins and fees: `margin_init`, `margin_maint`, `maker_fee`, `taker_fee` -- all
  `decimal.Decimal` values crossed from `rust_decimal` on the Rust side.
- Dated instruments (e.g. `FuturesContract`, `OptionContract`, `CryptoOption`)
  expose activation and expiry twice: `activation_utc` / `expiration_utc` as
  `datetime.datetime` properties for display, and `activation_ns` /
  `expiration_ns` as raw Unix-nanosecond `int` properties; constructors take the
  `*_ns` values.
- Optional fields stay `None`-able: `isin` (`str | None`), `tick_scheme`
  (`str | None`); the raw exchange definition is available as the `info` dict.

## Rust to Python Conversion Patterns

### Raw reconstruction: from_raw

The Python value types are the PyO3 bindings over the Rust types, so there is no
per-object conversion layer. Use `from_raw` when reconstructing from raw
fixed-point fields (for example when parsing adapter payloads) to avoid float
conversion entirely:

```python
price = Price.from_raw(12345000000000, 4)
qty = Quantity.from_raw(1005000000000, 1)
money = Money.from_raw(123456789, usd)
```

`from_raw(raw, precision)` preserves the exact fixed-point representation across
the Rust/Python boundary; `from_str` parses the canonical string form.

### Currency lookup

Currency objects cross the boundary directly; look up registered currencies by
code with `Currency.from_str(code)` (auto-creating unknown codes as crypto unless
`strict=True`).

### Decimal bridge

Rust uses `rust_decimal::Decimal` for margin/fee fields. These convert through
Python's `Decimal`:

```python
margin_init = equity.margin_init  # decimal.Decimal (Rust rust_decimal crossed to Python Decimal)
```

## Rust Type Equivalents

The Rust types live in `crates/model/src/types/`:

| Python type      | Rust type          | Rust raw type  |
|------------------|--------------------|----------------|
| `Price`          | `Price`            | `i128` (signed)|
| `Quantity`       | `Quantity`         | `u128` (unsigned)|
| `Money`          | `Money`            | `i128` (signed)|
| `Currency`       | `Currency`         | struct with code, precision, iso4217, name, type |

The Rust side also provides:
- `FIXED_PRECISION` and `FIXED_SCALAR` constants
- `price_new()`, `quantity_new()`, `money_new()` -- FFI constructors
- `price_from_raw()`, `quantity_from_raw()`, `money_from_raw()` -- raw constructors
- `currency_register()`, `currency_to_cstr()`, `currency_code_to_cstr()` -- registry/conversion functions

## Common Patterns and Gotchas

### Float interaction

When any operand in arithmetic is a `float`, the result is a `float`:

```python
qty = Quantity(100, precision=0)
result = qty * 1.5  # float: 150.0 (not Decimal)
result = qty * Decimal("1.5")  # Decimal: 150.0
```

Prefer `Decimal` over `float` to maintain precision in calculations.

### Precision mismatch in addition/subtraction

When adding or subtracting two values with different precisions, the result
uses the **maximum** precision of the two operands:

```python
p1 = Price.from_str("1.23")  # precision=2
p2 = Price.from_str("0.001")  # precision=3
result = p1 + p2  # precision=3, value="1.231"
```

### Quantity cannot go negative

```python
q1 = Quantity(10, precision=0)
q2 = Quantity(20, precision=0)

q1 - q2  # ValueError: subtraction would result in negative value
```

### Money currency enforcement

```python
usd = Money(100, Currency.from_str("USD"))
eur = Money(100, Currency.from_str("EUR"))

usd + eur  # Raises Condition error: currency != other.currency
usd == eur  # Raises Condition error: currency != other.currency
```
