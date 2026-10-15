NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

## Reviewed current-develop overlay (2026-10-14)

Source: upstream `2ceb2a9a624e174a5160c10f8188afbdd57ecb99`,
`docs/integrations/architect_ax.md:43-61,229-275,596-655`.
The reviewed sections below supersede conflicting historical guidance at this pin.

## Products

The production catalog lists perpetual and dated futures contracts in these venue categories:

| Venue category   | Examples                     | Nautilus asset class |
| ---------------- | ---------------------------- | -------------------- |
| Foreign exchange | `EURUSD-PERP`, `JPYUSD-PERP` | FX                   |
| Equities         | `AAPL-PERP`, `NVDA-PERP`     | Equity               |
| Metals           | `XAU-PERP`, `XAU-2026-DEC`   | Commodity            |
| Energy           | `WTIOIL-PERP`                | Commodity            |
| Treasuries       | `UST10Y-PERP`                | Debt                 |
| Compute          | `NVDA-H100-2027-MAR`         | Alternative          |

The sandbox catalog differs. It also lists `energy_etfs` contracts such as `USO-PERP` and
`UNG-PERP`, which map to the Equity asset class, and compute perpetuals such as `OCPI-H100-PERP`.

The adapter maps a `crypto` venue category to the `CRYPTOCURRENCY` asset class, and any category it
does not recognize to `ALTERNATIVE`.


### Order book recovery

The data client tracks each order book delta subscription with the
[shared book recovery machinery](https://github.com/nautechsystems/nautilus_trader/blob/2ceb2a9a624e174a5160c10f8188afbdd57ecb99/docs/developer_guide/adapters.md#order-book-recovery-ownership). AX L2 and L3
messages carry a full snapshot and no sequence number. AX sends one immediately after each subscribe
acknowledgement, including for an empty or unchanged book. The client accepts every message as a snapshot. It
suppresses book output while a subscription write is in flight and drops frames for a book that is no longer
subscribed.

Recovery replaces the symbol's subscription with an unsubscribe and a subscribe on the same connection. The
replacement retains its current level and trade and ticker flags. AX carries all market data for a symbol on
one stream, so trades, quotes, mark prices, and instrument status for that symbol pause while the replacement
runs. Recovery starts when:

- An initial subscription write fails.
- No snapshot arrives within `book_snapshot_timeout_secs` (default 10 seconds) after the initial
  subscription write completes or the connection is re-established. A data client `connect` after
  `disconnect` counts too: the client keeps its books, and the WebSocket client replays their
  subscriptions.
- An L2 or L3 frame cannot be converted, such as an incremental (`st: false`) frame. The book stops
  emitting until a replacement snapshot arrives, and a running recovery's current attempt fails
  without waiting for its snapshot deadline.

A subscription AX rejects delivers no snapshot, so its snapshot deadline starts recovery. A
subscription the client cannot queue because the WebSocket handler has stopped starts no recovery,
and its book emits nothing. Subscribing to deltas for a book whose stream is already open replaces
the stream, so the book starts from a fresh snapshot.

Each recovery makes up to eight attempts within 180 seconds, with exponential backoff. It then retries until
it accepts a snapshot. The retry interval doubles from one minute to fifteen minutes. A running recovery
continues across reconnects with its remaining budget, and unsubscribe or shutdown cancels it. A recovery
waiting between attempts after its budget retries at once on the new connection. Recovery never ends in a
failed state.

The client does not correlate subscription acknowledgements with recovery attempts. A snapshot
queued before a replacement can complete recovery once the replacement write finishes. AX sends no
frames while a book is unchanged, so the client does not treat a silent book as stale.

Setting `book_snapshot_timeout_secs` to `0` disables snapshot deadlines. Recovery then starts only from a
failed initial write or an invalid frame. Within the retry budget, a replacement that delivers no snapshot
waits until one of these events:

- The client accepts a snapshot.
- An invalid frame fails the attempt.
- Recovery is cancelled.
- The 180-second initial budget ends.


## Implementation notes

- **Whole contracts only**: AX uses integer contract quantities. The adapter models a one-contract
  size increment and lot size, while enforcing each instrument's separate `minimum_order_size`.
  Fractional quantities generate `OrderDenied` locally.
- **Dated futures activation**: AX publishes expiration but not activation timestamps. The adapter
  uses zero for the unknown activation time and preserves that limitation in instrument metadata.
- **Rate limiting**: The adapter applies a conservative rate limit of 10 requests/second with
  automatic exponential backoff on rate limit responses.
- **Market orders**: AX does not support native market orders. The adapter uses a preview endpoint
  to determine the take-through price and submits an aggressive IOC limit order. Because the book
  can move between the preview and the submission, a simulated market order may fill partially.
- **Stop-limit orders**: The adapter rejects venue-native stop-limit submissions because sandbox
  testing did not confirm conditional semantics. Use local order emulation when a strategy
  requires a stop-limit order.
- **Order modification**: AX supports atomic order replacement via `POST /replace-order`. The execution client
  maps `modify_order` to this endpoint and records the new venue order ID it returns. The adapter rejects a
  modification locally if it carries a trigger price, because AX has no field for one. It also rejects a
  modification if the order has no venue order ID yet.
- **Funding rate polling**: The data client polls `GET /funding-rates` for each subscribed instrument at
  `funding_rate_poll_interval_mins`. It requests a seven-day lookback to find a rate across weekends and
  holidays. It emits the latest rate only when it differs from the last one emitted.
- **Cancel on disconnect**: Set `cancel_on_disconnect=True` in the execution client config
  to have the exchange cancel all open orders if the orders WebSocket disconnects.
- **Account fee rates**: Instruments do not carry maker or taker fee rates. An
  authenticated client resolves account rates from `GET /whoami` and fails to connect
  if that lookup fails. The execution client caches rates per AX account, apart from
  instruments, and refreshes them each time it connects. Automatic WebSocket reconnects
  keep the cached rates.
- **Fill commissions**: Real-time fill events from the WebSocket do not include fee data. The adapter
  estimates commission for both tracked fill events and untracked fill reports using the fill quantity,
  absolute fill price, contract multiplier, and account's maker or taker rate. It uses the trade's account ID,
  then the order's account ID if absent, or the first `/whoami` account if neither ID is present. It keeps the
  calculation in decimal arithmetic and rounds only the final fee into USD `Money`, whose precision is 2.

  A fill whose instrument or complete account fee schedule is not cached, or whose commission cannot be
  represented, is logged and skipped. Tracked order metadata remains available for reconciliation. Recovery
  depends on configured reconciliation checks or an explicit order query. Skipped fills do not trigger an
  immediate REST request.

  Reconciliation does not replace an applied commission, so a streamed estimate remains even when the
  venue-reported `/fills` fee differs. That endpoint supplies the fee for a fill that was not already applied
  from the stream. The adapter converts it with `Money::from_decimal` into USD, so a sub-cent fee such as
  `0.012188` is stored as `0.01`. An unrepresentable REST fee fails the fill-report request and mass status.
  During startup, that error prevents the node from starting.
- **Fill reconciliation window**: The `/fills` endpoint requires a bounded time range and caps the span at
  seven days. Reconciliation requests the most recent seven days of fills. Fills older than that are not
  reconciled.
- **Fill order identity**: AX can omit `order_id` for block trades and final settlement fills. The
  adapter derives a deterministic reconciliation order ID from `trade_id` for those classified
  records. Classification fields are optional for regular fills with a valid `order_id`. The adapter
  rejects rows with neither an order ID nor explicit special-fill classification, and rejects
  inconsistent classification.
- **Unfilled IOC/FOK**: AX reports an unfilled immediate order as an expiry. The adapter maps it to
  `OrderCanceled` to match NautilusTrader semantics.
- **One-tick quotes**: Example testers place post-only limits one tick from top of book.
  Those quotes can still fill. Flatten leftovers with
  `cargo run --bin ax-flatten -p nautilus-architect-ax` (`AX_IS_SANDBOX` defaults to true).
  That binary cancels all open orders on the account, then closes every position.


## Historical reference (superseded where noted above)

# AX Exchange

[AX Exchange](https://architect.exchange) is the world's first centralized and regulated exchange
for perpetual futures on traditional underlying asset classes. Operated by Architect Bermuda Ltd.
and licensed by the [Bermuda Monetary Authority (BMA)](https://www.bma.bm/), AX brings crypto-style
perpetual contracts to traditional financial markets including foreign exchange, metals, energy,
equity indices, and interest rates.

This integration supports live market data ingest and order execution with AX Exchange.

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/architect_ax/).

## Overview

This adapter is implemented in Rust and exposed to Python through PyO3 bindings. It does not
require external AX client libraries.

This guide assumes a trader is setting up for both live market data feeds, and trade execution.
The AX Exchange adapter includes multiple components, which can be used together or separately
depending on the use case.

- `AxHttpClient`: Low-level HTTP API connectivity.
- `AxMdWebSocketClient` and `AxOrdersWebSocketClient`: Low-level WebSocket connectivity for Rust
  callers.
- `AxDataClient`: A market data feed manager.
- `AxExecutionClient`: An account management and trade execution gateway.
- `AxDataClientFactory`: Factory for AX data clients.
- `AxExecutionClientFactory`: Factory for AX execution clients.

:::note
Most users will define a configuration for a live trading node (as below),
and won't need to necessarily work with these lower level components directly.
:::

## AX Exchange documentation

AX Exchange provides documentation for users which can be found at the
[Architect documentation site](https://docs.architect.exchange/).
It's recommended you also refer to the AX Exchange documentation in conjunction with this
NautilusTrader integration guide.

## Products

AX Exchange specializes in perpetual futures contracts on traditional asset classes. Perpetual
contracts never expire, eliminating rollover costs associated with standard futures.

| Asset Class      | Examples                           | Notes                        |
|------------------|------------------------------------|------------------------------|
| Foreign exchange | GBPUSD-PERP, EURUSD-PERP           | Major and minor FX pairs.    |
| Stock indices    | Equity index perpetuals            |                              |
| Metals           | XAU-PERP (gold), XAG-PERP (silver) | Precious metals perpetuals.  |
| Energy           | Crude oil, natural gas             | Energy commodity perpetuals. |
| Interest rates   | SOFR, treasury yields              | Rate perpetuals.             |

### Perpetual contracts

A perpetual contract (perpetual swap) is a derivative that tracks the price of an underlying
asset without expiring. Unlike standard futures, there is no settlement date, which eliminates
rollover costs and simplifies position management. A funding rate mechanism keeps the contract
price aligned with the underlying index price through periodic payments between long and short
holders. See the [Architect documentation](https://docs.architect.exchange/) for details on
funding rate mechanics and contract specifications.

Characteristics of AX perpetual contracts:

- **Cash-settled in USD**: No physical delivery. All profit and loss is settled in USD.
- **Funding rates**: Periodic payments keep the contract price aligned with the underlying.
- **Multiplier of 1**: Each contract represents one unit of exposure to the underlying.
- **Whole contracts only**: Fractional quantities are not supported.
- **Margin**: Initial margin is required to open a position; maintenance margin to keep it open.

In NautilusTrader, all AX instruments are represented as `PerpetualContract`, an asset-class
agnostic perpetual swap type. The asset class (FX, commodity, equity, etc.) is inferred
automatically from the underlying. The adapter uses `MARGIN` account type and `NETTING` order
management.

## Symbology

AX Exchange uses a straightforward naming convention. All instruments are perpetual futures
identified by the `-PERP` suffix appended to the underlying asset symbol.

**Format**: `{SYMBOL}-PERP`

| Underlying     | AX Symbol      | Nautilus InstrumentId |
|----------------|----------------|-----------------------|
| GBP/USD        | `GBPUSD-PERP`  | `GBPUSD-PERP.AX`      |
| EUR/USD        | `EURUSD-PERP`  | `EURUSD-PERP.AX`      |
| Gold           | `XAU-PERP`     | `XAU-PERP.AX`         |
| Silver         | `XAG-PERP`     | `XAG-PERP.AX`         |

The venue identifier is `AX`. To construct a Nautilus `InstrumentId`:

```python
from nautilus_trader.model import InstrumentId

instrument_id = InstrumentId.from_str("GBPUSD-PERP.AX")
```

## Environments

AX Exchange provides two trading environments. Configure the appropriate environment using the
`environment` parameter in your client configuration.

| Environment    | Config                                 | Description                            |
|----------------|----------------------------------------|----------------------------------------|
| **Sandbox**    | `environment=AxEnvironment.SANDBOX`    | Test environment with simulated funds. |
| **Production** | `environment=AxEnvironment.PRODUCTION` | Live trading with real funds.          |

### Sandbox

The default environment for development and testing with simulated funds.
All sandbox endpoints are resolved automatically when `environment=AxEnvironment.SANDBOX`.

#### 1. Create a sandbox account

Follow the [Architect documentation](https://docs.architect.exchange/) to create a sandbox
account. An invite code is required during registration.

#### 2. Create API keys and fund the account

Use the AX sandbox UI to generate API keys and deposit simulated funds into your account.
Store the `api_key` and `api_secret` securely.

#### 3. Set environment variables

```bash
export AX_API_KEY="your-sandbox-api-key"
export AX_API_SECRET="your-sandbox-api-secret"
```

#### 4. Configure the live node

Set `environment=AxEnvironment.SANDBOX` on the data and execution client configs. See the
[Python examples](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/architect_ax/)
for complete `LiveNode` setup.

```python
from nautilus_trader.adapters.architect_ax import AxDataClientConfig
from nautilus_trader.adapters.architect_ax import AxEnvironment

config = AxDataClientConfig(
    environment=AxEnvironment.SANDBOX,
)
```

### Production

For live trading with real funds. Requires a verified AX Exchange account.

```python
from nautilus_trader.adapters.architect_ax import AxEnvironment
from nautilus_trader.adapters.architect_ax import AxExecutionClientConfig

config = AxExecutionClientConfig(
    environment=AxEnvironment.PRODUCTION,
)
```

:::warning
Ensure you are using the correct environment before placing orders.
Sandbox is the default to prevent accidental live trading.
:::

## Market data

The adapter provides real-time market data via WebSocket subscriptions, with HTTP endpoints
for historical data backfill.

### Data types

| AX Data           | Nautilus Data Type   | Notes                                                              |
|-------------------|----------------------|--------------------------------------------------------------------|
| Order book (L1)   | `QuoteTick`          | Best bid/ask top-of-book from L1 book subscription.                |
| Order book (L2)   | `OrderBookDelta`     | Aggregated price levels.                                           |
| Order book (L3)   | `OrderBookDelta`     | Individual order quantities.                                       |
| Trades            | `TradeTick`          | Real-time trade events from L1 subscription.                       |
| Mark price        | `MarkPriceUpdate`    | Extracted from L1 ticker subscription.                             |
| Bars/candles      | `Bar`                | OHLCV data (total volume only, no buy/sell breakdown).             |
| Funding rates     | `FundingRateUpdate`  | Polled via HTTP (not real-time WebSocket); interval configurable.  |
| Instrument status | `InstrumentStatus`   | State changes (open, halted, closed) from L1 ticker subscription.  |

:::note
Historical quote tick requests are not supported by AX Exchange. Only real-time quote
data is available via WebSocket L1 book subscriptions.
:::

### Bar intervals

| Interval | Description |
|----------|-------------|
| `1s`     | 1-second    |
| `5s`     | 5-second    |
| `1m`     | 1-minute    |
| `5m`     | 5-minute    |
| `15m`    | 15-minute   |
| `1h`     | 1-hour      |
| `1d`     | 1-day       |

## Orders capability

AX Exchange supports market and limit order types with stop triggers.

### Order types

| Order Type             | Supported | Notes                                              |
|------------------------|-----------|----------------------------------------------------|
| `MARKET`               | ✓         | Execute immediately at best available price.       |
| `LIMIT`                | ✓         | Execute at specified price or better.              |
| `STOP_LIMIT`           | ✓         | Trigger a limit order when stop price is breached. |
| `LIMIT_IF_TOUCHED`     | -         | *Not currently implemented by AX Exchange*.        |
| `STOP_MARKET`          | -         | *Not supported*.                                   |
| `MARKET_IF_TOUCHED`    | -         | *Not supported*.                                   |
| `TRAILING_STOP_MARKET` | -         | *Not supported*.                                   |

### Execution instructions

| Instruction   | Supported | Notes                                               |
|---------------|-----------|-----------------------------------------------------|
| `post_only`   | ✓         | Maker-only; rejected if order would take liquidity. |
| `reduce_only` | -         | *Not supported*.                                    |

### Time in force

| Time in Force | Supported | Notes                                        |
|---------------|-----------|----------------------------------------------|
| `GTC`         | ✓         | Good Till Canceled.                          |
| `GTD`         | -         | *Not supported by AX Exchange*.              |
| `DAY`         | ✓         | Valid until end of trading day.              |
| `IOC`         | ✓         | Immediate or Cancel.                         |
| `FOK`         | ✓         | Fill or Kill.                                |
| `AT_THE_OPEN` | ✓         | Execute at market open or expire.            |
| `AT_THE_CLOSE`| ✓         | Execute at market close or expire.           |

### Advanced order features

| Feature            | Supported | Notes                                                              |
|--------------------|-----------|--------------------------------------------------------------------|
| Order modification | ✓         | Atomic replace via `POST /replace_order`. Returns a new order ID.  |
| Cancel order       | ✓         | Single order cancellation.                                         |
| Cancel all orders  | ✓         | Cancel all open orders for an instrument.                          |
| Batch cancel       | -         | *Not supported by AX Exchange*. Individual cancels used instead.   |
| Order lists        | ✓         | Sequential submission (orders submitted individually, non-atomic). |

### Position management

| Feature          | Supported | Notes                                |
|------------------|-----------|--------------------------------------|
| Query positions  | ✓         | Real-time position updates.          |
| Position mode    | -         | Netting mode only.                   |
| Cross margin     | ✓         | Cross-margin across all instruments. |

### Order querying

| Feature              | Supported | Notes                                                   |
|----------------------|-----------|---------------------------------------------------------|
| Query open orders    | ✓         | List all active orders.                                 |
| Query single order   | ✓         | By venue order ID or client order ID (any order state). |
| Order status reports | ✓         | Reconciliation from open orders; see note below.        |
| Fill reports         | ✓         | Execution and fill history.                             |

:::note
Order status reports for reconciliation are generated from the open orders endpoint.
Filled or canceled orders are not included in the reconciliation snapshot. Single-order
queries via `query_order` use the dedicated `/order-status` endpoint which works for
any order state.
:::

## Authentication

AX Exchange uses bearer token authentication:

1. API key and secret obtain a session token via `/authenticate`.
2. The session token is used as a bearer token for subsequent REST and WebSocket requests.
3. Session tokens expire after a configurable period (default: 86400 seconds).

## Configuration

### Environments and endpoints

| Environment | HTTP API (market data)                           | HTTP API (orders)                                   | Market Data WS                                   | Orders WS                                            |
|-------------|--------------------------------------------------|-----------------------------------------------------|--------------------------------------------------|------------------------------------------------------|
| Sandbox     | `https://gateway.sandbox.architect.exchange/api` | `https://gateway.sandbox.architect.exchange/orders` | `wss://gateway.sandbox.architect.exchange/md/ws` | `wss://gateway.sandbox.architect.exchange/orders/ws` |
| Production  | `https://gateway.architect.exchange/api`         | `https://gateway.architect.exchange/orders`         | `wss://gateway.architect.exchange/md/ws`         | `wss://gateway.architect.exchange/orders/ws`         |

:::info
Order management HTTP endpoints (place, cancel, order status) use a separate base URL
from market data endpoints. This is handled automatically by the adapter configuration.
:::

### Data client configuration options

| Option                             | Default   | Description                                                         |
|------------------------------------|-----------|---------------------------------------------------------------------|
| `api_key`                          | `None`    | API key; loaded from `AX_API_KEY` env var when omitted.             |
| `api_secret`                       | `None`    | API secret; loaded from `AX_API_SECRET` env var when omitted.       |
| `environment`                      | `SANDBOX` | Trading environment (`SANDBOX` or `PRODUCTION`).                    |
| `base_url_http`                    | `None`    | Override for the REST base URL.                                     |
| `base_url_ws_public`               | `None`    | Override for the market data WebSocket URL.                         |
| `base_url_ws_private`              | `None`    | Override for the orders WebSocket URL.                              |
| `proxy_url`                        | `None`    | Optional proxy URL for HTTP and WebSocket transports.               |
| `http_timeout_secs`                | `60`      | Timeout (seconds) for REST requests.                                |
| `max_retries`                      | `3`       | Maximum retry attempts for REST requests.                           |
| `retry_delay_initial_ms`           | `1000`    | Initial delay (milliseconds) between retries.                       |
| `retry_delay_max_ms`               | `10000`   | Maximum delay (milliseconds) between retries (exponential backoff). |
| `heartbeat_interval_secs`          | `20`      | Heartbeat interval (seconds) for WebSocket connections.             |
| `recv_window_ms`                   | `5000`    | Receive window (milliseconds) for signed requests.                  |
| `update_instruments_interval_mins` | `60`      | Interval (minutes) between instrument catalog refreshes.            |
| `funding_rate_poll_interval_mins`  | `15`      | Interval (minutes) between funding rate poll requests.              |

### Execution client configuration options

| Option                    | Default   | Description                                                         |
|---------------------------|-----------|---------------------------------------------------------------------|
| `api_key`                 | `None`    | API key; loaded from `AX_API_KEY` env var when omitted.             |
| `api_secret`              | `None`    | API secret; loaded from `AX_API_SECRET` env var when omitted.       |
| `environment`             | `SANDBOX` | Trading environment (`SANDBOX` or `PRODUCTION`).                    |
| `base_url_http`           | `None`    | Override for the REST base URL.                                     |
| `base_url_orders`         | `None`    | Override for the orders REST base URL.                              |
| `base_url_ws_private`     | `None`    | Override for the orders WebSocket URL.                              |
| `proxy_url`               | `None`    | Optional proxy URL for HTTP and WebSocket transports.               |
| `http_timeout_secs`       | `60`      | Timeout (seconds) for REST requests.                                |
| `max_retries`             | `3`       | Maximum retry attempts for REST requests.                           |
| `retry_delay_initial_ms`  | `1000`    | Initial delay (milliseconds) between retries.                       |
| `retry_delay_max_ms`      | `10000`   | Maximum delay (milliseconds) between retries (exponential backoff). |
| `heartbeat_interval_secs` | `30`      | Heartbeat interval (seconds) for WebSocket connections.             |
| `recv_window_ms`          | `5000`    | Receive window (milliseconds) for signed requests.                  |
| `cancel_on_disconnect`    | `false`   | Cancel all open orders when the orders WebSocket disconnects.       |

The most common use case is to configure a live node to include AX Exchange data and
execution clients. Use `AxDataClientConfig` with `AxDataClientFactory` and
`AxExecutionClientConfig` with `AxExecutionClientFactory`. The Python examples show the complete
`LiveNode.builder(...)` configuration for data and execution clients (see the shared
[Live node wiring](index.md#live-node-wiring) pattern):

```python
from nautilus_trader.adapters.architect_ax import AxDataClientConfig
from nautilus_trader.adapters.architect_ax import AxDataClientFactory
from nautilus_trader.adapters.architect_ax import AxEnvironment
from nautilus_trader.adapters.architect_ax import AxExecutionClientConfig
from nautilus_trader.adapters.architect_ax import AxExecutionClientFactory
from nautilus_trader.common import Environment
from nautilus_trader.live import LiveNode
from nautilus_trader.model import TraderId

trader_id = TraderId("TESTER-001")

data_config = AxDataClientConfig(
    environment=AxEnvironment.SANDBOX,
)

exec_config = AxExecutionClientConfig(
    environment=AxEnvironment.SANDBOX,
)

node = (
    LiveNode.builder("AX-001", trader_id, Environment.LIVE)
    .add_data_client(None, AxDataClientFactory(), data_config)
    .add_exec_client(None, AxExecutionClientFactory(), exec_config)
    .build()
)
```

For each client, pass the corresponding `api_key` and `api_secret` values to the configuration
objects, or set the following environment variables:

- `AX_API_KEY`
- `AX_API_SECRET`

:::tip
We recommend using environment variables to manage your credentials.
:::

When starting the trading node, you'll receive immediate confirmation of whether your
credentials are valid and have trading permissions.

## Implementation notes

- **Whole contracts only**: AX Exchange uses integer contract quantities. Fractional quantities
  are not supported and will be rejected.
- **Rate limiting**: The adapter applies a conservative rate limit of 10 requests/second with
  automatic exponential backoff on rate limit responses.
- **Market orders**: AX does not support native market orders. The adapter uses a preview endpoint
  to determine the take-through price and submits an aggressive IOC limit order.
- **Order modification**: AX supports atomic order replacement via `POST /replace_order`. The
  adapter maps `modify_order` to this endpoint. The exchange cancels the original order and
  creates a new one with the updated fields, returning a new order ID.
- **Cancel on disconnect**: Set `cancel_on_disconnect=True` in the execution client config
  to have the exchange cancel all open orders if the orders WebSocket disconnects.
- **Fill commissions**: Real-time fill events from the WebSocket do not include fee data.
  Commission is reported as zero for streaming fills. During reconciliation, the REST
  `/fills` endpoint provides accurate fee information.

## Contributing

:::info
For additional features or to contribute to the AX Exchange adapter, please see our
[contributing guide](https://github.com/nautechsystems/nautilus_trader/blob/develop/CONTRIBUTING.md).
:::
