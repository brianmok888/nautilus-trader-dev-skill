NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Binance

Founded in 2017, Binance is one of the largest cryptocurrency exchanges in terms
of daily trading volume, and open interest of crypto assets and crypto
derivative products.

NautilusTrader provides Binance integration for live market data and execution. The adapter is
implemented in Rust and exposed to Python through the same public configurations, factories, and
data types.

Supported products:

- **Binance Spot** (including Binance US)
- **Binance USDT-Margined Futures** (crypto and TradFi perpetuals; current and next monthly and
  quarterly delivery contracts)
- **Binance Coin-Margined Futures** (perpetuals and current or next quarterly delivery contracts)

## Examples

- [Python live examples](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/binance/)
- [Rust spot examples](https://github.com/nautechsystems/nautilus_trader/tree/develop/crates/adapters/binance/examples/spot/)
- [Rust futures examples](https://github.com/nautechsystems/nautilus_trader/tree/develop/crates/adapters/binance/examples/futures/)

## Overview

The adapter exposes these public components:

- `BinanceDataClientConfig` and `BinanceExecutionClientConfig`: Live client configuration.
- `BinanceInstrumentProviderConfig`: Instrument selection, filtering, warning, and fee policy.
- `BinanceDataClientFactory` and `BinanceExecutionClientFactory`: Trading node client factories.
- `load_binance_instruments`: Standalone configured instrument discovery.
- `load_binance_order_book_deltas`: Rust-backed Binance depth CSV loading for order book wrangling.
- `BINANCE`, `BINANCE_CLIENT_ID`, `BINANCE_VENUE`, and the client-order-ID decoders: Public
  identifiers and decoding utilities.

:::note
Most users need only the configs and factories, wired into a live trading node as shown under
[Live node configuration](#live-node-configuration). The remaining components serve standalone
loading and offline decoding.
:::

Low-level HTTP and WebSocket clients, their caches, and product-specific instrument provider
objects are not exposed through the Python API. Use the live configs and factories, or the
standalone instrument loader, instead of depending on those internals.

### Standalone discovery and loading

For standalone discovery, pass the same data-client and provider configuration used by a live
client:

```python
import asyncio

from nautilus_trader.adapters.binance import BinanceDataClientConfig
from nautilus_trader.adapters.binance import BinanceInstrumentProviderConfig
from nautilus_trader.adapters.binance import BinanceProductType
from nautilus_trader.adapters.binance import load_binance_instruments

config = BinanceDataClientConfig(
    product_type=BinanceProductType.USD_M,
    instrument_provider=BinanceInstrumentProviderConfig(
        load_all=False,
        load_ids=["BTCUSDT-PERP.BINANCE"],
    ),
)
instruments = asyncio.run(load_binance_instruments(config))
```

This function supports Spot, USD-M, and COIN-M. It uses the configured environment, URLs, proxy,
receive window, Binance US mode, filters, warning policy, and commission policy. Margin is not a
supported Binance product and is rejected.

For Binance depth CSV data, call the stateless loader directly:

```python
from nautilus_trader.adapters.binance import load_binance_order_book_deltas

df = load_binance_order_book_deltas(path, nrows=1_000_000)
```

The loader preserves the source values and column order. File-open failures and invalid numeric or
side values raise `RuntimeError`.

For offline Arrow work, `get_binance_arrow_schema_map` maps a Binance data class to its Arrow
schema (field name to Arrow data type). It currently supports the `BinanceBar` class and raises an
error for unrecognized class names:

```python
from nautilus_trader.adapters.binance import BinanceBar
from nautilus_trader.adapters.binance import get_binance_arrow_schema_map

schema_map = get_binance_arrow_schema_map(BinanceBar)
```

### Product support

| Product Type                            | Supported | Notes                                     |
|-----------------------------------------|-----------|--------------------------------------------|
| Spot Markets (incl. Binance US)         | Yes         |                                            |
| Margin Accounts (Cross & Isolated)      | -         | *Not implemented.*                        |
| USDT-Margined Futures (PERP & Delivery) | Yes         | Monthly and quarterly delivery contracts. |
| Coin-Margined Futures (PERP & Delivery) | Yes         | Quarterly delivery contracts.             |

:::note
Margin account features such as borrow, repay, and isolated margin management are not implemented.
:::

:::info
Each Binance client instance handles one product type. The configs use a
singular `product_type` field, and the live factories create one data or
execution client from one config. To run Spot and Futures in the same node,
configure separate clients with distinct IDs such as `BINANCE_SPOT` and
`BINANCE_FUTURES`, then pass the matching `client_id` when a strategy subscribes
or submits orders. See the current Python examples for complete client setup.
:::

## Data types

The integration includes several custom data types:

- `BinanceTicker`: 24-hour ticker data including price and statistical information.
- `BinanceBar`: Bar data with additional volume metrics for historical and real-time use.
- `BinanceFuturesMarkPriceUpdate`: Mark price updates for Binance Futures.

See the Binance [API Reference](https://nautilustrader.io/docs/python-api-latest/adapters/binance) for full definitions.

## Symbology

Native Binance symbols are used where possible for spot and futures contracts.
Because NautilusTrader supports multi-venue trading, it must distinguish between
`BTCUSDT` the spot pair and `BTCUSDT` the perpetual futures contract (Binance
uses the same symbol for both).

Nautilus appends the `-PERP` suffix to all perpetual symbols. For example,
the Binance Futures `BTCUSDT` perpetual contract becomes `BTCUSDT-PERP`
within Nautilus.

## Order capability

The following tables detail order types, execution instructions, and
time-in-force options across Binance account types.

### Order types

| Order Type             | Spot | Margin | USDT Futures | Coin Futures | Notes                              |
|------------------------|------|--------|--------------|--------------|------------------------------------|
| `MARKET`               | ✓    | -      | ✓            | ✓            | Quote quantity support: Spot only. |
| `LIMIT`                | ✓    | -      | ✓            | ✓            |                         |
| `STOP_MARKET`          | -    | -      | ✓            | ✓            | Futures only.           |
| `STOP_LIMIT`           | ✓    | -      | ✓            | ✓            |                         |
| `MARKET_IF_TOUCHED`    | -    | -      | ✓            | ✓            | Futures only.           |
| `LIMIT_IF_TOUCHED`     | ✓    | -      | ✓            | ✓            |                         |
| `TRAILING_STOP_MARKET` | -    | -      | ✓            | ✓            | Futures only.           |

### Execution instructions

| Instruction   | Spot | Margin | USDT Futures | Coin Futures | Notes                                 |
|---------------|------|--------|--------------|--------------|---------------------------------------|
| `post_only`   | ✓    | -      | ✓            | ✓            | See restrictions below.               |
| `reduce_only` | -    | -      | ✓            | ✓            | Futures only; disabled in Hedge Mode. |

#### Post-only restrictions

Only *limit* order types support `post_only`.

| Order Type               | Spot | Margin | USDT Futures | Coin Futures | Notes                                               |
|--------------------------|------|--------|--------------|--------------|-----------------------------------------------------|
| `LIMIT`                  | ✓    | -      | ✓            | ✓            | Uses `LIMIT_MAKER` for Spot, `GTX` TIF for Futures. |
| `STOP_LIMIT`             | -    | -      | ✓            | ✓            | Futures only.                                       |

### Time in force

| Time in force | Spot | Margin | USDT Futures | Coin Futures | Notes                                      |
|---------------|------|--------|--------------|--------------|--------------------------------------------|
| `GTC`         | ✓    | -      | ✓            | ✓            | Good Till Canceled.                        |
| `GTD`         | ✓*   | -      | ✓            | ✓            | *Converted to GTC for Spot with warning.   |
| `FOK`         | ✓    | -      | ✓            | ✓            | Fill or Kill.                              |
| `IOC`         | ✓    | -      | ✓            | ✓            | Immediate or Cancel.                       |

### Advanced order features

| Feature            | Spot | Margin | USDT Futures | Coin Futures | Notes                                        |
|--------------------|------|--------|--------------|--------------|----------------------------------------------|
| Order Modification | ✓    | -      | ✓            | ✓            | Price and quantity for `LIMIT` orders only.  |
| Bracket/OCO Orders | -    | -      | -            | -            | *Planned*. Currently denied at submission.   |
| Iceberg Orders     | ✓    | -      | ✓            | ✓            | Large orders split into visible portions.    |

### Batch operations

| Operation          | Spot | Margin | USDT Futures | Coin Futures | Notes                                        |
|--------------------|------|--------|--------------|--------------|----------------------------------------------|
| Batch Submit       | ✓    | -      | ✓            | ✓            | Orders submitted individually (no batch API call). |
| Batch Modify       | -    | -      | -            | -            | Not implemented.                             |
| Batch Cancel       | -*   | -      | ✓            | ✓            | *Spot falls back to individual cancels.      |

#### Cancel all orders behavior

When calling `cancel_all_orders()` from a strategy, the adapter includes
orders in both open and inflight (SUBMITTED) states so that the adapter also
cancels orders not yet acknowledged by Binance.

**Multi-strategy safety**: When multiple strategies trade the same instrument,
the adapter compares orders owned by the requesting strategy against all orders
for that instrument. If the strategy owns all orders, a single cancel-all API
call is used. Otherwise, per-strategy cancels are sent (batch for regular
orders, individual for algo orders) to avoid affecting other strategies.

**Futures algo orders**: Conditional order types (`STOP_MARKET`, `STOP_LIMIT`,
`TAKE_PROFIT`, `TAKE_PROFIT_MARKET`, `TRAILING_STOP_MARKET`) require a
different cancel endpoint. The adapter routes these through the correct
endpoint automatically. Once an algo order triggers and becomes a regular
order, it uses the standard cancel endpoint.

**Endpoints used**:

| Account Type | Regular Orders                  | Algo Orders (batch)              | Algo Orders (individual)    |
|--------------|---------------------------------|----------------------------------|-----------------------------|
| Spot/Margin  | `DELETE /api/v3/openOrders`     | N/A                              | N/A                         |
| USDT Futures | `DELETE /fapi/v1/allOpenOrders` | `DELETE /fapi/v1/algoOpenOrders` | `DELETE /fapi/v1/algoOrder` |
| Coin Futures | `DELETE /dapi/v1/allOpenOrders` | `DELETE /dapi/v1/algoOpenOrders` | `DELETE /dapi/v1/algoOrder` |

### Position management

| Feature             | Spot | Margin | USDT Futures | Coin Futures | Notes                                       |
|---------------------|------|--------|--------------|--------------|---------------------------------------------|
| Query positions     | -    | -      | ✓            | ✓            | Real-time position updates.                 |
| Position mode       | -    | -      | ✓            | ✓            | One-Way vs Hedge mode (position IDs).       |
| Leverage control    | -    | -      | ✓            | ✓            | Dynamic leverage adjustment per symbol.     |
| Margin mode         | -    | -      | ✓            | ✓            | Cross vs Isolated margin per symbol.        |

### Risk events

| Feature              | Spot | Margin | USDT Futures | Coin Futures | Notes                                       |
|----------------------|------|--------|--------------|--------------|---------------------------------------------|
| Liquidation handling | -    | -      | ✓            | ✓            | Exchange-forced position closures.          |
| ADL handling         | -    | -      | ✓            | ✓            | Auto-Deleveraging events.                   |

Binance Futures can trigger exchange-generated orders in response to risk events:

- **Liquidations**: When insufficient margin exists to maintain a position, Binance forcibly closes it at the bankruptcy price. These orders have client IDs starting with `autoclose-`.
- **ADL (Auto-Deleveraging)**: When the insurance fund is depleted, Binance closes profitable positions to cover losses. These orders use client ID prefix `adl_autoclose`.
- **Settlements (USDT-M)**: Funding/margin settlement orders use client IDs starting with `settlement_autoclose-`.
- **Deliveries (COIN-M)**: Expiring delivery contracts auto-close with client IDs starting with `delivery_autoclose-`.
- **Insurance fund**: Takeover by the insurance fund uses status `NEW_INSURANCE` (deprecated on the public changelog but still observed on the wire).

The adapter detects these special order types via their client ID patterns
(checked before the execution type), then:

1. Logs a warning with order details for monitoring.
2. Generates a `FillReport` with correct fill details and TAKER liquidity side.
3. Generates an `OrderStatusReport` for reconciliation.

Upstream references:

- [USDT-M `ORDER_TRADE_UPDATE`](https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams/Event-Order-Update)
- [COIN-M `ORDER_TRADE_UPDATE`](https://developers.binance.com/docs/derivatives/coin-margined-futures/user-data-streams/Event-Order-Update)

The execution engine creates external orders from runtime status reports when
the order is not already in cache. This covers first-seen exchange-generated
orders (the typical case for a live liquidation or ADL event). The engine
assigns the order through the instrument's active external order claim, configured initially with
`external_order_instrument_ids` (replaceable post-registration via
`Strategy.set_external_order_instrument_ids`), or to the `EXTERNAL` strategy by default.

#### Commission estimation

When Binance omits the commission fields (`N`/`n`) from the fill event, the
Rust adapter estimates commission as `default_taker_fee * qty * price` using
the quote currency. This applies to USD-M linear contracts only. COIN-M
inverse contracts use zero commission as a fallback because the linear
formula does not account for contract size. Configure `default_taker_fee` on
`BinanceExecutionClientConfig` to match your fee tier (default: 0.0004 / 0.04%).

#### Hedge-mode position IDs

When `use_position_ids` is enabled (default), exchange-generated fill reports
include a `venue_position_id` derived from the instrument and position side
(e.g. `ETHUSDT-PERP.BINANCE-LONG`). Set `use_position_ids` to false on
`BinanceExecutionClientConfig` for virtual positions with `OmsType.HEDGING`.

:::note
The status report and fill report are emitted bundled as a single
`OrderWithFills` execution report. The engine creates the external order
from the status report and then applies the real fill, preserving the
venue's `trade_id` and `commission`. Any residual quantity not covered by
the bundled fills is closed with an inferred fill from the status report's
`avg_px`.
:::

### Order querying

| Feature             | Spot | Margin | USDT Futures | Coin Futures | Notes                                       |
|---------------------|------|--------|--------------|--------------|---------------------------------------------|
| Query open orders   | ✓    | ✓      | ✓            | ✓            | List all active orders.                     |
| Query order history | ✓    | ✓      | ✓            | ✓            | Historical order data.                      |
| Order status updates| ✓    | ✓      | ✓            | ✓            | Real-time order state changes.              |
| Trade history       | ✓    | ✓      | ✓            | ✓            | Execution and fill reports.                 |

### Contingent orders

| Feature             | Spot | Margin | USDT Futures | Coin Futures | Notes                                        |
|---------------------|------|--------|--------------|--------------|----------------------------------------------|
| Order lists         | -    | -      | -            | -            | *Not supported*.                             |
| OCO orders          | -    | -      | -            | -            | *Planned*. Currently denied at submission.   |
| Bracket orders      | -    | -      | -            | -            | *Planned*. Currently denied at submission.   |
| Conditional orders  | ✓    | ✓      | ✓            | ✓            | Stop and market-if-touched orders.           |

### Order parameters

Customize individual orders by supplying a `params` dictionary when calling
`Strategy.submit_order` (Python) or setting `Params` on a `SubmitOrder`
command (Rust). The Binance execution clients recognize:

| Parameter        | Type   | Account types     | Description |
|------------------|--------|-------------------|-------------|
| `price_match`    | `str`  | USDT/COIN Futures | Set one of Binance's `priceMatch` modes (see Price match section below) to delegate price selection to the exchange. Cannot be combined with `post_only` or iceberg (`display_qty`) instructions. |
| `close_position` | `bool` | USDT/COIN Futures | Close the entire position when the trigger fires (see Close position section below). Only valid for `StopMarket` and `MarketIfTouched` orders. Cannot be combined with `reduce_only`. |

### Price match

Binance Futures supports BBO (Best Bid/Offer) price matching via the
`priceMatch` parameter, which delegates price selection to the exchange. Limit
orders dynamically join the order book at optimal prices without specifying an
exact price level.

When using `price_match`, you submit a limit order with a reference price (for
local risk checks), and Binance determines the actual working price based on
the current market state and price match mode.

#### Valid price match values

| Value         | Behavior                                                       |
|---------------|----------------------------------------------------------------|
| `OPPONENT`    | Join the best price on the opposing side of the book.          |
| `OPPONENT_5`  | Join the opposing side price but allow up to a 5-tick offset.  |
| `OPPONENT_10` | Join the opposing side price but allow up to a 10-tick offset. |
| `OPPONENT_20` | Join the opposing side price but allow up to a 20-tick offset. |
| `QUEUE`       | Join the best price on the same side (stay maker).             |
| `QUEUE_5`     | Join the same-side queue but offset up to 5 ticks.             |
| `QUEUE_10`    | Join the same-side queue but offset up to 10 ticks.            |
| `QUEUE_20`    | Join the same-side queue but offset up to 20 ticks.            |

:::info
For more details, see the [official documentation](https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api).
:::

#### Event sequence

When an order is submitted with `price_match`:

1. Nautilus sends the order to Binance with the `priceMatch` parameter but omits the limit price from the API request.
2. Binance accepts the order and determines the actual working price.
3. Nautilus generates an `OrderAccepted` event.
4. If the Binance-accepted price differs from the reference price, Nautilus generates an `OrderUpdated` event with the actual working price.
5. The order price in the Nautilus cache now matches the Binance-accepted price.

#### Example

```python
order = strategy.order_factory.limit(
    instrument_id=InstrumentId.from_str("BTCUSDT-PERP.BINANCE"),
    order_side=OrderSide.BUY,
    quantity=Quantity.from_int(1),
    price=Price.from_str("65000"),  # Reference price for local risk checks
)

strategy.submit_order(
    order,
    params={"price_match": "QUEUE"},
)
```

:::note
If Binance accepts the order at a different price (e.g. 64,995.50), you
receive an `OrderAccepted` event followed by an `OrderUpdated` event with
the new price.
:::

### Close position

Binance Futures conditional orders support `closePosition`, which closes the entire position
when the trigger fires. Binance resolves the quantity server-side from the current position
size at trigger time.

Unlike `reduce_only`, `closePosition` adapts to position size changes, and Binance
auto-cancels the order when the position is closed by other means.

Pass `close_position` via the `params` dictionary on `StopMarket` or `MarketIfTouched` orders.
Cannot be combined with `reduce_only`.

<Tabs items={['Python', 'Rust']}>
<Tab value="Python">

```python
strategy.submit_order(order, params={"close_position": True})
```

</Tab>
<Tab value="Rust">
```rust
let params = Params::from([("close_position", true.into())]);
let cmd = SubmitOrder::new(order).with_params(params);
```
</Tab>
</Tabs>

:::info
Nautilus omits `quantity` and `reduceOnly` from the API request when `close_position` is set.
The order quantity is used only for local risk checks.
:::

### Trailing stops

For trailing stop market orders on Binance:

- Use `activation_price` (optional) to specify when the trailing mechanism activates.
- When omitted, Binance uses the current market price at submission time.
- Use `trailing_offset` for the callback rate (in basis points).

:::warning
Do not use `trigger_price` for trailing stop orders: it will fail with an
error. Use `activation_price` instead.
:::

## Link & Trade

The NautilusTrader integration ID is automatically prefixed to all
system-generated client order IDs for every order placed through the Binance
Rust adapter. This provides transparent order attribution through Binance's
[Link and Trade](https://developers.binance.com/docs/binance_link/link-and-trade)
program without requiring any user configuration.

The adapter uses a deterministic two-way encoding to compress outgoing
`ClientOrderId` values into a compact format that fits within Binance's
36-character `newClientOrderId` limit, and decodes incoming order events back
to the original ID before they reach strategies. This transformation is fully
transparent: strategies see only their original `ClientOrderId` values at all
times.

:::note
The integration ID prefix applies to all order operations including
submissions, modifications, cancellations, and status queries. Orders placed
before this support was added are handled gracefully through passthrough
decoding.
:::

:::info
This feature is currently available in the Rust adapter only. Users can opt out
by passing a custom `client_order_id` on their orders, or by removing the
encoding calls and recompiling. There is no technical limitation preventing
either approach.
:::

### Decoding client order IDs

When querying Binance directly (REST API, web UI, or your own HTTP code), the
`clientOrderId` field contains the encoded form. Two utility functions recover
the original Nautilus `ClientOrderId`:

```python
from nautilus_trader.adapters.binance import (
    decode_binance_futures_client_order_id,
    decode_binance_spot_client_order_id,
)

# Encoded ID from Binance REST response or web UI
encoded = "x-TD67BGP9-T0A4b1H2vj50H"
original = decode_binance_spot_client_order_id(encoded)
# -> "O-20260305-120000-001-001-100"

# Futures equivalent
encoded_futures = "x-aHRE4BCj-U2xK9mPqR7sT1vW3y"
original_futures = decode_binance_futures_client_order_id(encoded_futures)
```

Strings without the broker prefix pass through unchanged, so these are safe
to call on any `clientOrderId` value.

:::note
The domain-level HTTP clients (`BinanceSpotHttpClient`,
`BinanceFuturesHttpClient`) decode automatically when returning Nautilus
types such as `OrderStatusReport`. Manual decoding is only needed when
working outside the adapter: direct REST queries, the Binance web UI, or
raw venue models.
:::

## Order books

Order books can be maintained at full or partial depths. WebSocket stream
update rates differ between Spot and Futures, with Nautilus using the highest
available rate:

- **Spot**: 100ms
- **Futures**: 0ms (unthrottled)

Only one order book per instrument per trader instance is supported. When
stream subscriptions vary, the Binance data client uses the latest order book
data subscription (deltas or snapshots).

Order book snapshot rebuilds will be triggered on:

- Initial subscription of the order book data.
- Data websocket reconnects.

The sequence of events is as follows:

- Deltas will start buffered.
- Snapshot is requested and awaited.
- Snapshot response is parsed to `OrderBookDeltas`.
- Snapshot deltas are sent to the `DataEngine`.
- Buffered deltas are iterated, dropping those where the sequence number is not greater than the last delta in the snapshot.
- Deltas will stop buffering.
- Remaining deltas are sent to the `DataEngine`.

## Binance data differences

The `ts_event` field on `QuoteTick` differs between Spot and Futures. Spot
does not provide an event timestamp, so the adapter uses `ts_init` (meaning
`ts_event` and `ts_init` are identical).

## Binance specific data

Bars, mark prices, index prices, and funding rates are subscribed to in the normal way. The custom
data types below expose additional venue-specific fields that the core data types do not carry.

Binance Futures mark-price payloads preserve the venue `P` estimated settlement price in
`BinanceFuturesMarkPriceUpdate`. Nautilus also emits standard mark-price, index-price, and
funding-rate updates from the same stream. The optional USD-M `ap` moving-average field is
parsed at the transport boundary but is not exposed as domain or custom data.

### `BinanceFuturesMarkPriceUpdate`

Subscribe to `BinanceFuturesMarkPriceUpdate` (including funding rate info)
from your actor or strategy:

```python
from nautilus_trader.adapters.binance import BinanceFuturesMarkPriceUpdate
from nautilus_trader.model import DataType
from nautilus_trader.model import ClientId

# In your `on_start` method
self.subscribe_data(
    data_type=DataType(
        BinanceFuturesMarkPriceUpdate.__name__, metadata={"instrument_id": self.instrument.id}
    ),
    client_id=ClientId("BINANCE"),
)
```

Received `BinanceFuturesMarkPriceUpdate` objects are passed to your `on_data`
method. Check the type, as this method handles all custom/generic data.

```python
def on_data(self, data):
    # First check the type of data
    if isinstance(data, BinanceFuturesMarkPriceUpdate):
        # Do something with the data
```

## Funding rates

The Rust adapter emits `FundingRateUpdate` as a first-class data type through
`subscribe_funding_rates`. The data comes from the
[Mark Price Stream](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Mark-Price-Stream)
WebSocket endpoint, which provides the current funding rate and next funding
time alongside mark and index prices. All three subscriptions
(`subscribe_mark_prices`, `subscribe_index_prices`, `subscribe_funding_rates`)
share a single `@markPrice@1s` stream with ref-counted subscription management.

Historical funding rates are available through `request_funding_rates`, which queries the
[Get Funding Rate History](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History)
REST endpoint (`GET /fapi/v1/fundingRate` for USD-M, `GET /dapi/v1/fundingRate` for COIN-M).
Each history row maps to a `FundingRateUpdate` with `ts_event` set to the funding time. The
`next_funding_ns` field is `None` for historical rows because the endpoint does not provide it.

The `interval` field on `FundingRateUpdate` is `None` for Binance because the
Mark Price Stream does not include a funding interval field. Binance exposes
`fundingIntervalHours` through the
[Get Funding Rate Info](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-Info)
REST endpoint, but the adapter does not consume it.

## Instrument status polling

The data clients periodically poll Binance `exchangeInfo` to detect changes in
instrument trading status. When a symbol transitions between states (e.g.
Trading to Halt, or Trading to Delivering for a futures contract approaching
expiry), the adapter emits an `InstrumentStatus` event.

The polling interval defaults to 3600 seconds (60 minutes) and is configurable
via `instrument_status_poll_secs` in the data client config. Set to `0` to
disable polling entirely.

On initial connect, the adapter seeds its status cache from the exchange info
response without emitting events. Only subsequent polls that detect a status
change emit `InstrumentStatus` events. If a symbol disappears from exchange
info (e.g. after delisting or contract expiry), the adapter emits
`NotAvailableForTrading`.

### Status mapping

#### Spot

| Binance status     | MarketStatusAction         |
|--------------------|----------------------------|
| Trading            | Trading                    |
| EndOfDay           | Close                      |
| Halt               | Halt                       |
| Break              | Pause                      |
| NonRepresentable   | NotAvailableForTrading     |

#### Futures (USD-M)

| Binance status     | MarketStatusAction         |
|--------------------|----------------------------|
| Trading            | Trading                    |
| PendingTrading     | PreOpen                    |
| PreTrading         | PreOpen                    |
| PostTrading        | PostClose                  |
| EndOfDay           | Close                      |
| Halt               | Halt                       |
| AuctionMatch       | Cross                      |
| Break              | Pause                      |

#### Futures (COIN-M)

| Binance status     | MarketStatusAction         |
|--------------------|----------------------------|
| Trading            | Trading                    |
| PendingTrading     | PreOpen                    |
| PreDelivering      | PreClose                   |
| Delivering         | Close                      |
| Delivered          | Close                      |
| PreSettle          | PreClose                   |
| Settling           | Close                      |
| Close              | Close                      |
| PreDelisting       | PreClose                   |
| Delisting          | Suspend                    |
| Down               | NotAvailableForTrading     |

:::note
Only instruments that are in a tradable state at connect time are tracked.
Symbols that start in a non-trading state (e.g. halted at connect) do not
appear in the instruments cache, so status transitions for them are not
monitored.
:::

## Rate limiting

Binance uses an interval-based rate limiting system where request weight is
tracked per fixed time window (every minute, resetting at :00 seconds). Each
API endpoint has an assigned weight cost, and total weight usage is tracked
per IP address.

### Global weight limits

These are the primary limits shared across all endpoints:

| Account Type | Weight Limit | Interval |
|--------------|--------------|----------|
| Spot/Margin  | 6,000        | 1 minute |
| Futures      | 2,400        | 1 minute |

### Endpoint weight costs

Some endpoints have higher weight costs per request:

| Endpoint                  | Weight | Notes                                  |
|---------------------------|--------|----------------------------------------|
| `/api/v3/order`           | 1      | Spot order placement.                  |
| `/api/v3/allOrders`       | 20     | Spot historical orders (expensive).    |
| `/api/v3/klines`          | 2+     | Scales with `limit` parameter.         |
| `/fapi/v1/order`          | 1      | Futures order placement.               |
| `/fapi/v1/allOrders`      | 20     | Futures historical orders (expensive). |
| `/fapi/v1/commissionRate` | 20     | Futures commission rate query.         |
| `/fapi/v1/klines`         | 5+     | Scales with `limit` parameter.         |

### WebSocket API limits

The WebSocket API (used for user data streams) shares the same weight quota as the REST API:

| Limit Type       | Value  | Notes                                 |
|------------------|--------|---------------------------------------|
| Request weight   | Shared | Counts against REST API weight quota. |
| Handshake        | 5      | Weight cost per connection attempt.   |
| Ping/pong frames | 5/sec  | Maximum ping/pong rate.               |

### Adapter behavior

The adapter uses token bucket rate limiters to approximate Binance's
interval-based limits. This reduces the risk of quota violations while
maintaining throughput for normal operations.

For endpoints with dynamic weight (e.g. `/klines` scales with the `limit`
parameter), the adapter draws a single token per call. Large history requests
may need manual pacing. Monitor the `X-MBX-USED-WEIGHT-*` response headers to
track actual usage.

:::warning
Binance returns HTTP 429 when you exceed the allowed weight. Repeated
violations trigger temporary IP bans (escalating from 2 minutes to 3 days
for repeat offenders).
:::

:::info
For the latest rate limits, query `/api/v3/exchangeInfo` (Spot) or `/fapi/v1/exchangeInfo` (Futures), or see:

- [Spot API Limits](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/limits)
- [Futures API Limits](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)

:::

## Configuration

### Data client

| Option                             | Default   | Description                                                                    |
|------------------------------------|-----------|--------------------------------------------------------------------------------|
| `product_type`                     | `Spot`    | One of `Spot`, `UsdM`, or `CoinM` (`BinanceProductType`).                       |
| `environment`                      | `Live`    | One of `Live`, `Testnet`, or `Demo` (`BinanceEnvironment`).                    |
| `base_url_http`                    | `None`    | Optional HTTP endpoint override.                                               |
| `base_url_ws`                      | `None`    | Optional market WebSocket endpoint override.                                   |
| `api_key` / `api_secret`           | `None`    | Required for Spot SBE; optional for public JSON and Futures data.              |
| `spot_market_data_mode`            | `Sbe`     | `Json` keeps the credential-free Global Spot path. Binance US requires `Json`. |
| `instrument_provider`              | default   | Loading, filters, parser-warning, and commission policy.                       |
| `instrument_refresh_interval_secs` | `3,600`   | Full catalogue refresh interval; `0` disables it.                              |
| `instrument_status_poll_secs`      | `3,600`   | Status-only exchange-info poll interval; `0` disables it.                      |
| `proxy_url`                        | `None`    | Proxy applied to HTTP and every market WebSocket connection.                   |
| `recv_window_ms`                   | `5,000`   | Signed HTTP receive window, inclusive range `1..=60000`.                       |
| `us`                               | `False`   | Route a live Spot JSON client to Binance US.                                   |
| `transport_backend`                | `Sockudo` | WebSocket transport backend.                                                   |

### Execution client

| Option                               | Default   | Description                                                             |
|--------------------------------------|-----------|--------------------------------------------------------------------------|
| `account_id`                         | Required  | Nautilus account identity.                                              |
| `product_type`                       | `Spot`    | One of `Spot`, `UsdM`, or `CoinM` (`BinanceProductType`).                |
| `environment`                        | `Live`    | One of `Live`, `Testnet`, or `Demo` (`BinanceEnvironment`).              |
| `base_url_http`                      | `None`    | Optional HTTP endpoint override.                                        |
| `base_url_ws`                        | `None`    | Optional private stream override.                                       |
| `base_url_ws_trading`                | `None`    | Optional Global Spot or USD-M WebSocket trading override.               |
| `use_ws_trading`                     | `True`    | Use Global WebSocket order entry where supported; Binance US uses HTTP. |
| `ws_trading_setup_timeout_ms`        | `10,000`  | WebSocket trading authentication and setup timeout.                     |
| `instrument_provider`                | default   | Loading, filters, parser-warning, and commission policy.                |
| `instrument_refresh_interval_secs`   | `3,600`   | Execution precision-cache refresh interval; `0` disables it.            |
| `proxy_url`                          | `None`    | Proxy applied to HTTP, private streams, and WebSocket trading.          |
| `recv_window_ms`                     | `5,000`   | Signed HTTP and WebSocket receive window, inclusive range `1..=60000`.  |
| `us`                                 | `False`   | Route a live Spot execution client to Binance US.                      |
| `api_key` / `api_secret`             | `None`    | Global uses Ed25519 WebSocket auth; Binance US uses HMAC HTTP signing.  |
| `use_gtd`                            | `True`    | Use native USD-M GTD.                                                   |
| `use_position_ids`                   | `True`    | Expose Futures IDs on order, fill, and hedge REST reports.              |
| `oms_type`                           | `None`    | `None` selects Futures netting; use `Hedging` for dual-side mode.       |
| `default_taker_fee`                  | `0.0004`  | Fallback for exchange-generated Futures fills.                          |
| `futures_leverages`                  | `None`    | Initial leverage by Futures symbol.                                     |
| `futures_margin_types`               | `None`    | Initial margin type by Futures symbol.                                  |
| `treat_expired_as_canceled`          | `False`   | Map `EXPIRED` execution events to canceled events.                      |
| `use_trade_lite`                     | `False`   | Use the lower-latency USD-M trade-lite fill stream.                     |
| `bnfcr_currency`                     | `USDT`    | Currency used to resolve `BNFCR` balances and fees.                     |
| `transport_backend`                  | `Sockudo` | WebSocket transport backend.                                            |

### Live node configuration

Use `BinanceDataClientConfig` with `BinanceDataClientFactory` and `BinanceExecutionClientConfig` with
`BinanceExecutionClientFactory`. The current Python examples show the complete
`LiveNode.builder(...)` configuration for data and execution clients (see the shared
[Live node wiring](index.md#live-node-wiring) pattern):

```python
from nautilus_trader.adapters.binance import BinanceDataClientConfig
from nautilus_trader.adapters.binance import BinanceDataClientFactory
from nautilus_trader.adapters.binance import BinanceEnvironment
from nautilus_trader.adapters.binance import BinanceExecutionClientConfig
from nautilus_trader.adapters.binance import BinanceExecutionClientFactory
from nautilus_trader.adapters.binance import BinanceProductType
from nautilus_trader.common import Environment
from nautilus_trader.live import LiveNode
from nautilus_trader.model import AccountId
from nautilus_trader.model import TraderId

trader_id = TraderId("TESTER-001")

data_config = BinanceDataClientConfig(
    product_type=BinanceProductType.USD_M,
    environment=BinanceEnvironment.TESTNET,
)

exec_config = BinanceExecutionClientConfig(
    account_id=AccountId("BINANCE-001"),
    product_type=BinanceProductType.USD_M,
    environment=BinanceEnvironment.TESTNET,
)

node = (
    LiveNode.builder("BINANCE-001", trader_id, Environment.LIVE)
    .add_data_client(None, BinanceDataClientFactory(), data_config)
    .add_exec_client(None, BinanceExecutionClientFactory(), exec_config)
    .build()
)
```

### Key types

Binance supports three API key types: **Ed25519**, **HMAC-SHA256**, and
**RSA**. The adapter auto-detects the key type from your API secret format, so
no configuration is needed.

**Ed25519 is strongly recommended.** Binance recommends Ed25519 for its
superior performance and security. A future version of NautilusTrader will
require Ed25519 exclusively.

| Key Type | Data Clients | Execution Clients | Status |
|----------|--------------|-------------------|--------|
| Ed25519  | ✓            | ✓                 | **Recommended** |
| HMAC     | ✓            | ✓                 | Deprecated, will be removed in a future version. |
| RSA      | ✓            | -                 | Deprecated, not supported for execution. |

:::tip
Switch to Ed25519 keys now. Generate an Ed25519 keypair and register it with
Binance. See [Generating Ed25519 keys](#generating-ed25519-keys) below.
:::

:::note
Ed25519 keys must be provided in unencrypted PEM format (base64-encoded ASN.1/DER).
The implementation automatically extracts the 32-byte seed from the DER structure.
Encrypted (password-protected) PEM keys are not supported. If your key is encrypted,
decrypt it first: `openssl pkey -in encrypted.pem -out decrypted.pem`
:::

#### Generating Ed25519 keys

**Option 1: OpenSSL (recommended)**

```bash
# Generate private key (PKCS#8 PEM format)
openssl genpkey -algorithm ed25519 -out binance_ed25519_private.pem

# Extract public key
openssl pkey -in binance_ed25519_private.pem -pubout -out binance_ed25519_public.pem
```

**Option 2: Binance Key Generator**

Download the [Binance Asymmetric Key Generator](https://github.com/binance/asymmetric-key-generator) from the releases page and run it to generate a keypair.

**Registering with Binance**

1. Log in to Binance and go to **Profile** -> **API Management**
2. Click **Create API** and select **Self-generated**
3. Paste the contents of your public key file (including the `-----BEGIN PUBLIC KEY-----` header/footer)
4. Configure permissions (Enable Spot & Margin Trading, etc.)

**Using with NautilusTrader**

Set the private key as your API secret:

```bash
export BINANCE_API_KEY="your-api-key-from-binance"
export BINANCE_API_SECRET="$(cat binance_ed25519_private.pem)"
```

Or pass the PEM content directly in your configuration.

:::warning
Keep your private key secure. Never share it or commit it to version control.
:::

### API credentials

Pass credentials directly to the configuration objects, or set the appropriate
environment variables (see [Environments](#environments) for per-environment
variables).

:::tip
Use Ed25519 keys for all clients. HMAC keys still work for both data and
execution clients, but Ed25519 offers better performance and will become the
only supported key type in a future version. See [Key types](#key-types).
:::

:::warning
The `BINANCE_ED25519_*` and `BINANCE_*_ED25519_*` environment variables have
been removed for Spot/Margin. For Futures, they are deprecated and will be
removed in a future version. Rename them to `BINANCE_API_KEY` /
`BINANCE_API_SECRET` (Ed25519 keys are now auto-detected).
:::

When the trading node starts, you receive confirmation of whether your
credentials are valid and have trading permissions.

### Product type

Set `product_type` using the `BinanceProductType` enum (one client per product):

- `SPOT`
- `USD_M` (USDT-margined futures)
- `COIN_M` (coin-margined futures)

:::note
`MARGIN` is not a supported Binance product and is rejected. See
[Product support](#product-support).
:::

### Base URL overrides

Override the default base URLs for both HTTP REST and WebSocket APIs. This is
useful for configuring API clusters or when Binance has provided specialized
endpoints.

### Binance US

Set `us=True` in the config to use Binance US endpoints (`False` by default).
All functionality available to US accounts behaves identically to standard
Binance.

### Environments

Binance provides three trading environments, each with separate API
credentials and endpoints. The `environment` config option selects which to
use.

| Environment | Config                  | Description                                                            |
|-------------|-------------------------|------------------------------------------------------------------------|
| **Live**    | `environment="LIVE"`    | Production trading with real funds (default).                          |
| **Demo**    | `environment="DEMO"`    | Demo Trading with simulated Spot and Futures funds.                    |
| **Testnet** | `environment="TESTNET"` | Legacy Spot and Futures test network.                                  |

#### Live (production)

The default environment for live trading with real funds. Uses your main Binance
account credentials.

```python
from nautilus_trader.adapters.binance import BinanceExecutionClientConfig
from nautilus_trader.adapters.binance import BinanceProductType
from nautilus_trader.model import AccountId

config = BinanceExecutionClientConfig(
    account_id=AccountId("BINANCE-001"),
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    product_type=BinanceProductType.SPOT,
    # environment=BinanceEnvironment.LIVE (default)
)
```

| Variable             | Description         |
|----------------------|---------------------|
| `BINANCE_API_KEY`    | Live API key.       |
| `BINANCE_API_SECRET` | Live API secret.    |

#### Demo trading

Practice trading with simulated funds on production infrastructure. Demo
accounts use the same Binance login as your live account but trade with
virtual balances.

**How to get demo credentials:**

1. Log in at [binance.com/en/demo-trading](https://www.binance.com/en/demo-trading).
2. Go to **API Management** and create a demo API key.
3. Demo keys work for Spot and Futures demo endpoints.

| Endpoint       | URL                           |
|----------------|-------------------------------|
| Spot HTTP      | `demo-api.binance.com`        |
| Spot WS        | `demo-stream.binance.com`     |
| USD-M HTTP     | `demo-fapi.binance.com`       |
| USD-M WS       | `demo-fstream.binance.com`    |
| COIN-M HTTP    | `demo-dapi.binance.com`       |
| COIN-M WS      | `demo-dstream.binance.com`    |

```python
from nautilus_trader.adapters.binance import BinanceEnvironment
from nautilus_trader.adapters.binance import BinanceExecutionClientConfig
from nautilus_trader.adapters.binance import BinanceProductType
from nautilus_trader.model import AccountId

config = BinanceExecutionClientConfig(
    account_id=AccountId("BINANCE-001"),
    api_key="YOUR_DEMO_API_KEY",
    api_secret="YOUR_DEMO_API_SECRET",
    product_type=BinanceProductType.SPOT,
    environment=BinanceEnvironment.DEMO,
)
```

| Variable                  | Description      |
|---------------------------|------------------|
| `BINANCE_DEMO_API_KEY`    | Demo API key.    |
| `BINANCE_DEMO_API_SECRET` | Demo API secret. |

#### Testnet

A legacy test network with its own user accounts, balances, and order books.
Prefer `environment=BinanceEnvironment.DEMO` for new simulated trading
setups. Spot testnet remains at `testnet.binance.vision`; futures testnet
endpoints may route through the Demo Trading infrastructure.

**How to get Spot testnet credentials:**

1. Go to [testnet.binance.vision](https://testnet.binance.vision/).
2. Log in with GitHub.
3. Generate an API key (HMAC, RSA, or Ed25519).

**Futures testnet:** Existing configs with `BinanceEnvironment.TESTNET`
continue to work, but new Futures testing should use `BinanceEnvironment.DEMO`.

```python
from nautilus_trader.adapters.binance import BinanceEnvironment
from nautilus_trader.adapters.binance import BinanceExecutionClientConfig
from nautilus_trader.adapters.binance import BinanceProductType
from nautilus_trader.model import AccountId

config = BinanceExecutionClientConfig(
    account_id=AccountId("BINANCE-001"),
    api_key="YOUR_TESTNET_API_KEY",
    api_secret="YOUR_TESTNET_API_SECRET",
    product_type=BinanceProductType.SPOT,
    environment=BinanceEnvironment.TESTNET,
)
```

| Variable                             | Description                                        |
|--------------------------------------|----------------------------------------------------|
| `BINANCE_TESTNET_API_KEY`            | Spot testnet API key.                              |
| `BINANCE_TESTNET_API_SECRET`         | Spot testnet API secret.                           |
| `BINANCE_FUTURES_TESTNET_API_KEY`    | Futures testnet API key.                           |
| `BINANCE_FUTURES_TESTNET_API_SECRET` | Futures testnet API secret.                        |

:::note
Testnet credentials are completely separate from your live account. Market
data and liquidity differ from production.
:::

### Aggregated trades

Real-time trade subscriptions use the `<symbol>@aggTrade` stream on Futures, because Binance only
publishes aggregated trades on the Futures WebSocket, and the individual `<symbol>@trade` stream on
Spot.

Historical trade requests without bounds use the recent-trades endpoint. A request with time
bounds uses aggregate trades and accepts at most 1000 records, so the source follows the request
rather than a config option. Spot passes the supplied bounds to `/api/v3/aggTrades`. Futures
accepts either bound within the last 24 hours; when both are supplied, the range must be shorter
than one hour.

### Commission rate queries

By default, Binance Futures instruments use fee tier tables based on your VIP
level. For market maker accounts with negative maker fees or when precise
rates are required, enable per-symbol commission rate queries:

```python
from nautilus_trader.adapters.binance import BinanceInstrumentProviderConfig

instrument_provider=BinanceInstrumentProviderConfig(
    load_all=True,
    query_commission_rates=True,  # Query accurate rates per symbol
)
```

When enabled, the adapter queries Binance's `/fapi/v1/commissionRate` endpoint
for each symbol in parallel during instrument loading. Useful for:

- Market maker accounts with negative maker fees.
- Accounts with custom fee arrangements.
- Exact commission rates for PnL calculations.

The adapter uses parallel requests with rate limiting (120 requests/minute,
accounting for the endpoint's weight of 20). If a query fails, it falls back
to the fee tier table.

### Parser warnings

Some Binance instruments cannot be parsed into Nautilus objects if they contain
field values beyond what the platform handles. These instruments are skipped
with a warning.

To suppress these warnings:

```python
from nautilus_trader.config import InstrumentProviderConfig

instrument_provider=InstrumentProviderConfig(
    load_all=True,
    log_warnings=False,
)
```

### Futures hedge mode

Binance Futures Hedge mode allows holding both long and short positions on the
same instrument simultaneously.

When `use_position_ids` is enabled (default), Futures order and fill reports include a
`venue_position_id` derived from the instrument and Binance position side. Hedge-mode REST position
reports use the same IDs, such as `ETHUSDT-PERP.BINANCE-LONG`. This identity is preserved through
REST history, user stream updates, stream recovery, exchange-generated fills, and tracked
`TRADE_LITE` fills.

One-way `BOTH` positions, orders, and fills remain unkeyed and use netting reconciliation. Set
`use_position_ids` to false only for virtual positions with `OmsType.HEDGING`, where the engine
manages position identity. With `use_position_ids=True`, the adapter rejects a submitted custom
position ID that differs from the canonical Binance hedge-leg ID before sending the order.

To use hedge mode, configure it on Binance, set
`oms_type=OmsType.HEDGING` on `BinanceExecutionClientConfig`, and keep `use_position_ids=True` to track
both venue position sides:

```python
from nautilus_trader.adapters.binance import BinanceExecutionClientConfig
from nautilus_trader.adapters.binance import BinanceProductType
from nautilus_trader.model import AccountId
from nautilus_trader.model import OmsType

config = BinanceExecutionClientConfig(
    account_id=AccountId.from_str("BINANCE-001"),
    product_type=BinanceProductType.USD_M,
    oms_type=OmsType.HEDGING,
    use_position_ids=True,
)
```

This configuration is required for startup reconciliation to retain the `LONG` and `SHORT` legs
separately.

If the cache contains an open Binance hedge position under a different locally generated ID, the
adapter rejects that position row and reports both the cached and expected IDs. Reconcile the cached
state before retrying startup. The adapter does not alias the old ID or create a duplicate venue
position.

## Contributing

:::info
To contribute to the Binance adapter, see the
[contributing guide](https://github.com/nautechsystems/nautilus_trader/blob/develop/CONTRIBUTING.md).
:::