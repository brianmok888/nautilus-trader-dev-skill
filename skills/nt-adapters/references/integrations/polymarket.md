# Polymarket

> **NT v2 compatibility note:** Python examples in this file are retained pre-V2 migration/reference-only content (whole file); current V2 APIs are the flat `nautilus_trader.model` / `nautilus_trader.testkit` surfaces documented in the pinned upstream docs.

Founded in 2020, Polymarket is a decentralized prediction market platform that enables
traders to speculate on event outcomes by buying and selling outcome tokens.

NautilusTrader provides a venue integration for data and execution via Polymarket's Central Limit
Order Book (CLOB) API.

Today the repository exposes two Polymarket implementations:

- The Python adapter in `nautilus_trader.adapters.polymarket`, which uses the
  [official Python CLOB V2 client library](https://github.com/Polymarket/py-clob-client-v2).
- The Rust-native adapter surface in `nautilus_trader.polymarket`, which NautilusTrader is
  consolidating toward.

:::warning
The two implementations overlap heavily, but they do not behave identically in every area.
This guide calls out the current differences where they matter.
:::

NautilusTrader supports multiple Polymarket signature types for order signing, which gives
flexibility for different wallet configurations while NautilusTrader handles signing and order
preparation.

## Installation

To install NautilusTrader with Polymarket support:

```bash
uv pip install "nautilus_trader[polymarket]"
```

To build from source with all extras (including Polymarket):

```bash
uv sync --all-extras
```

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/polymarket/).

## Binary options

A [binary option](https://en.wikipedia.org/wiki/Binary_option) is a type of financial exotic
option contract in which traders bet on the outcome of a yes-or-no proposition. If the
prediction is correct, the trader receives a fixed payout; otherwise, they receive nothing.
NautilusTrader represents Polymarket outcome tokens as `BinaryOption` instruments.

Polymarket uses **pUSD** as the collateral token for trading, [see below](#pusd) for more
information.

## Polymarket documentation

Polymarket offers resources for different audiences:

- [Polymarket Learn](https://learn.polymarket.com/): Educational content and guides for users
  to understand the platform and how to engage with it.
- [Polymarket CLOB API](https://docs.polymarket.com/trading/orders/overview): Technical
  documentation for developers interacting with the Polymarket CLOB API.

## Overview

This guide assumes a trader is setting up for both live market data feeds and trade execution.
The Polymarket integration adapter includes multiple components, which can be used together or
separately depending on the use case.

- `PolymarketWebSocketClient`: Low-level WebSocket API connectivity (built on top of the Nautilus `WebSocketClient` written in Rust).
- `PolymarketInstrumentProvider`: Instrument parsing and loading functionality for `BinaryOption` instruments.
- `PolymarketDataClient`: A market data feed manager.
- `PolymarketExecutionClient`: A trade execution gateway.
- `PolymarketDataClientFactory`: Factory for Polymarket data clients (used by the trading node builder).
- `PolymarketExecutionClientFactory`: Factory for Polymarket execution clients (used by the trading node builder).

:::note
Most users will define a configuration for a live trading node (as below),
and won't need to work with these lower-level components directly.
:::

### Python and Rust implementations

The current docs cover both the Python adapter and the Rust-native adapter surface.
The table below shows the main differences that affect behavior today.

| Area                | Python adapter                                                                | Rust adapter                                                  | Notes |
|---------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------|-------|
| Public package path | `nautilus_trader.adapters.polymarket`                                         | `nautilus_trader.polymarket`                                  | Rust is the consolidation target. |
| Order signing       | Uses `py-clob-client-v2`                                                      | Native Rust signing                                           | Python signing is slower. |
| Post-only orders    | Supported for `GTC` and `GTD` only                                            | Supported for `GTC` and `GTD` only                            | Both reject post-only with market TIF (`IOC` or `FOK`). |
| Batch submit        | Uses `POST /orders` for batchable `SubmitOrderList` requests                  | Uses `POST /orders` for batchable `SubmitOrderList` requests  | Both batch only independent limit orders, capped at 15 per request. |
| Batch cancel        | Uses `DELETE /orders`                                                         | Uses `DELETE /orders`                                         | Both align with official Polymarket docs. |
| Market unsubscribe  | Sends dynamic WebSocket `unsubscribe` messages                                | Sends dynamic WebSocket `unsubscribe` messages                | Both support subscribe and unsubscribe. |
| Data client config  | Credentials, subscription buffering, quote handling, provider config          | Base URLs, timeouts, filters, new-market discovery            | Config surfaces differ materially. |
| Exec client config  | Credentials, retries, raw WS logging, experimental trade-based order recovery | Credentials, retries, account IDs, native timeouts            | Rust does not expose every Python-only option. |

## pUSD

**pUSD** is the collateral token used for trading on Polymarket. It is a standard ERC-20 token on
Polygon, backed by USDC.

The proxy contract address is
[0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB](https://polygonscan.com/address/0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB)
on Polygon. Direct on-chain funding wraps Polygon USDC.e (bridged USDC) into pUSD
through the [CollateralOnramp](https://docs.polymarket.com/resources/contracts).
The Bridge API can also deposit supported assets from other chains and credit pUSD
after conversion.

## Wallets and accounts

To interact with Polymarket via NautilusTrader, you'll need a **Polygon**-compatible wallet (such as MetaMask).

### Signature types

Polymarket supports multiple signature types for order signing and verification:

| Signature Type | Wallet Type                    | Description | Use Case |
|----------------|--------------------------------|-------------|----------|
| `0`            | EOA (Externally Owned Account) | Standard EIP712 signatures from wallets with direct private key control. | **Default.** Direct wallet connections (MetaMask, hardware wallets, etc.). |
| `1`            | Email/Magic Wallet Proxy       | Smart contract wallet for email-based accounts (Magic Link). Only the email-associated address can execute functions. | Polymarket Proxy associated with Email/Magic accounts. Requires `funder` address. |
| `2`            | Browser Wallet Proxy           | Modified Gnosis Safe (1-of-1 multisig) for browser wallets. | Polymarket Proxy associated with browser wallets. Enables UI verification. Requires `funder` address. |

:::note
See also: [Proxy wallet](https://docs.polymarket.com/developers/proxy-wallet) in the Polymarket documentation for more details about signature types and proxy wallet infrastructure.
:::

NautilusTrader defaults to signature type 0 (EOA) but can be configured to use any of the supported signature types via the `signature_type` configuration parameter.

A single wallet address is supported per trader instance when using environment variables,
or multiple wallets could be configured with multiple `PolymarketExecutionClient` instances.

:::note
Ensure your wallet is funded with **pUSD**, otherwise you will encounter the "not enough balance
or allowance" API error when submitting orders.
:::

### Setting allowances for Polymarket contracts

Before you can start trading, you need to ensure that your wallet has allowances set for Polymarket's smart contracts.
You can do this by running the provided script located at `nautilus_trader/adapters/polymarket/scripts/set_allowances.py`.

This script is adapted from a [gist](https://gist.github.com/poly-rodr/44313920481de58d5a3f6d1f8226bd5e) created by @poly-rodr.

:::note
You only need to run this script **once** per EOA wallet that you intend to use for trading on Polymarket.
:::

This script automates the process of approving the necessary allowances for the Polymarket contracts.
It sets approvals for the pUSD collateral token and Conditional Token Framework (CTF) contract to allow the
Polymarket CLOB Exchange to interact with your funds.

Before running the script, ensure the following prerequisites are met:

- Install the web3 Python package: `uv pip install "web3==7.12.1"`.
- Have a **Polygon**-compatible wallet funded with some POL (used for gas fees).
- Set the following environment variables in your shell:
  - `POLYGON_PRIVATE_KEY`: Your private key for the **Polygon**-compatible wallet.
  - `POLYGON_PUBLIC_KEY`: Your public key for the **Polygon**-compatible wallet.

Once you have these in place, the script will:

- Approve a bounded pUSD amount for the Polymarket collateral token contract.
- Set the approval for the CTF contract, allowing it to interact with your account for trading purposes.

:::caution
Use least-privilege allowances by default. Size the pUSD approval to the intended
session or strategy budget, rotate it when the budget changes, and revoke unused
allowances from the wallet or a trusted allowance-management tool after testing or
shutdown.
:::

`MAX_INT` approvals should be treated as an explicit high-risk operator choice,
not the default. Use them only after recording operator acknowledgement that a
compromised exchange contract, proxy, script, or wallet path could spend all
approved collateral until the allowance is revoked.

Ensure that your private key and public key are correctly stored in the environment variables before running the script.
Here's an example of how to set the variables in your terminal session:

```bash
export POLYGON_PRIVATE_KEY="YOUR_PRIVATE_KEY"
export POLYGON_PUBLIC_KEY="YOUR_PUBLIC_KEY"
```

Run the script using:

```bash
python nautilus_trader/adapters/polymarket/scripts/set_allowances.py
```

### Script breakdown

The script performs the following actions:

- Connects to the Polygon network via an RPC URL (<https://polygon-rpc.com/>).
- Signs and sends a transaction to approve the maximum pUSD allowance for Polymarket contracts.
- Sets approval for the CTF contract to manage Conditional Tokens on your behalf.
- Repeats the approval process for specific addresses like the Polymarket CLOB Exchange and Neg Risk adapter.

This allows Polymarket to interact with your funds when executing trades and ensures smooth integration with the CLOB Exchange.

## API keys

To trade with Polymarket, you'll need to generate API credentials. Follow these steps:

1. Ensure the following environment variables are set:
   - `POLYMARKET_PK`: Your private key for signing transactions.
   - `POLYMARKET_FUNDER`: The wallet address (public key) on the **Polygon** network used for funding trades on Polymarket.

2. Run the script using:

   ```bash
   python nautilus_trader/adapters/polymarket/scripts/create_api_key.py
   ```

The script will generate and print API credentials, which you should save to the following environment variables:

- `POLYMARKET_API_KEY`
- `POLYMARKET_API_SECRET`
- `POLYMARKET_PASSPHRASE`

These can then be used for Polymarket client configurations:

- `PolymarketDataClientConfig`
- `PolymarketExecutionClientConfig`

## Configuration

The Python package (`nautilus_trader.adapters.polymarket`) re-exports the pinned
Rust config structs as frozen PyO3 classes. The tables below document the pinned
v2 surfaces; v1-only keys are called out below each table.

### Data client options

Class: `PolymarketDataClientConfig` (re-exported from `nautilus_trader.adapters.polymarket`).

| Option                              | Default      | Description |
|-------------------------------------|--------------|-------------|
| `instrument_config`                 | `None`       | Optional `PolymarketInstrumentProviderConfig` for instrument loading. |
| `filters`                           | `[]`         | Instrument filters applied during loading and discovery (Rust struct; installed programmatically). |
| `base_url_http`                     | `None`       | Override for the REST base URL. |
| `base_url_ws`                       | `None`       | Override for the WebSocket base URL. |
| `base_url_gamma`                    | `None`       | Override for the Gamma API base URL. |
| `base_url_data_api`                 | `None`       | Override for the Data API base URL (default `https://data-api.polymarket.com`). |
| `base_url_rtds`                     | `None`       | Override for the real-time data stream (RTDS) base URL. |
| `http_timeout_secs`                 | `None`       | HTTP request timeout (seconds). |
| `ws_timeout_secs`                   | `None`       | WebSocket timeout (seconds). |
| `ws_max_subscriptions`              | `None`       | Maximum instrument subscriptions per WebSocket connection (Polymarket limit is 500). |
| `update_instruments_interval_mins`  | `None`       | Interval (minutes) between instrument catalogue refreshes. |
| `subscribe_new_markets`             | `None`       | Subscribe to newly listed markets as they are discovered. |
| `new_market_filter`                 | `None`       | Optional filter applied to newly discovered markets before emission (Rust struct; installed programmatically). |
| `compute_effective_deltas`          | `None`       | Compute effective order book deltas for bandwidth savings. |
| `drop_quotes_missing_side`          | `None`       | Drop quotes with missing bid/ask prices instead of substituting boundary values. |
| `auto_load_missing_instruments`     | `None`       | Load instruments on demand when subscribe or request commands reference uncached instruments. |
| `auto_load_debounce_ms`             | `None`       | Debounce window (milliseconds) for coalescing concurrent runtime instrument loads. |
| `auto_load_max_retries`             | `None`       | Maximum retries for runtime instrument loads. |
| `auto_load_retry_delay_initial_secs`| `None`       | Initial delay (seconds) between runtime load retries. |
| `auto_load_retry_delay_max_secs`    | `None`       | Maximum delay (seconds) between runtime load retries. |
| `new_market_fetch_max_concurrency`  | `None`       | Maximum concurrent fetches for newly discovered markets. |
| `resolve_poll_enabled`              | `None`       | Enable polling for market resolution. |
| `resolve_poll_interval_secs`        | `None`       | Resolution poll interval (seconds). |
| `resolve_poll_grace_secs`           | `None`       | Grace window (seconds) before a market is polled for resolution. |
| `resolve_poll_max_wait_secs`        | `None`       | Maximum wait (seconds) for resolution polling. |
| `transport_backend`                 | default      | WebSocket transport backend. |
| `proxy_url`                         | `None`       | Optional proxy URL for HTTP and WebSocket transports. |

NT v2 compatibility note: the v1 `venue`, `ws_connection_initial_delay_secs`,
and `ws_connection_delay_secs` data config keys are migration/reference-only;
they are not pinned fields.

### Market resolution events

The Rust data client tracks Polymarket exposure at `condition_id` level so both
YES and NO legs close together when the venue resolves the market. Position
events add open Polymarket binary option instruments to an internal watchlist.
Data clients can also watch an instrument without a position by subscribing to
`InstrumentStatus`, `InstrumentClose`, or both. These subscriptions are
independent: a status subscription emits only the status close, while a close
subscription emits only the settlement price. Unsubscribing from one does not
remove the other.

Cached instruments establish a watch when the subscription is accepted. Missing
instruments first pass through auto-loading and the configured instrument
filters. Unsubscribing removes only that data owner; open positions retain their
independent ownership. If loading cannot produce usable metadata, no automatic
watch is created — the resolution intent is retained so an explicit manual
resolution selector can still check the condition. Transient closed-market
hydration failures are retried; once retries are exhausted the intent stays
available for manual recovery instead of being dropped.

Once a watched condition expires, the data client waits `resolve_poll_grace_secs`,
then polls Gamma every `resolve_poll_interval_secs` until the condition resolves
or `resolve_poll_max_wait_secs` elapses (see the rows above).

### Execution client options

Class: `PolymarketExecutionClientConfig` (re-exported from `nautilus_trader.adapters.polymarket`).

| Option                   | Default                                    | Description |
|--------------------------|--------------------------------------------|-------------|
| `account_id`             | `POLYMARKET-001`                           | Account identifier for this execution client. |
| `private_key`            | `None` (`POLYMARKET_PK` env)               | Wallet private key for EIP-712 signing. |
| `api_key`                | `None` (`POLYMARKET_API_KEY` env)          | CLOB API key (L2 auth). |
| `api_secret`             | `None` (`POLYMARKET_API_SECRET` env)       | CLOB API secret (L2 auth). |
| `passphrase`             | `None` (`POLYMARKET_PASSPHRASE` env)       | CLOB API passphrase (L2 auth). |
| `funder`                 | `None` (`POLYMARKET_FUNDER` env)           | pUSD funding wallet. |
| `signature_type`         | `Eoa`                                      | Signature scheme (`Eoa`, `PolyProxy`, `PolyGnosisSafe`). |
| `base_url_http`          | `None` (official CLOB endpoint)            | Override for the CLOB REST base URL. |
| `base_url_ws`            | `None` (official CLOB endpoint)            | Override for the CLOB WebSocket base URL. |
| `base_url_data_api`      | `None` (`https://data-api.polymarket.com`) | Override for the Data API base URL. |
| `http_timeout_secs`      | `60`                                       | HTTP request timeout (seconds). |
| `max_retries`            | `3`                                        | Maximum retry attempts for single-order submit/cancel requests. |
| `retry_delay_initial_ms` | `1000`                                     | Initial delay (milliseconds) between retries. |
| `retry_delay_max_ms`     | `10000`                                    | Maximum delay (milliseconds) between retries. |
| `heartbeat_enabled`      | `False`                                    | Enable WebSocket heartbeat keepalives. |
| `transport_backend`      | default                                    | WebSocket transport backend. |
| `proxy_url`              | `None`                                     | Optional proxy URL for HTTP and WebSocket transports. |
| `instrument_config`      | `None`                                     | Optional `PolymarketInstrumentProviderConfig` for instrument loading. |

NT v2 compatibility note: the v1 `trader_id`, `ack_timeout_secs`,
`generate_order_history_from_trades`, and `log_raw_ws_messages` keys are
migration/reference-only; they are not pinned fields (the trader ID arrives via
the factory's `create(trader_id, ...)`). Batch submissions via `POST /orders`
deliberately skip retry regardless of `max_retries`; the single-order path still
retries on transient failures.

### Order modification

Polymarket supports order modification as an adapter-managed cancel-replace for
open `LIMIT` orders (window commit `616980b15f`, included in pin
`6df237382eb1d8411906f9b1790fa06f8ba7aad4`). Polymarket has no in-place modify
endpoint: the execution client cancels the current venue order, reconciles its
final confirmed fills, and signs a replacement for the remaining quantity. The
`ModifyOrder.quantity` value is the absolute target for the logical order, not
the replacement leg. The replacement keeps the `ClientOrderId` and receives a
new `VenueOrderId`.

The adapter submits no replacement unless the cancel response, canceled order
state, and confirmed trade totals agree. An ambiguous cancel emits
`OrderModifyRejected`; an ambiguous replacement stays in flight under its
deterministic signed order hash so a later order update, fill, or order
reconciliation can establish it without emitting a second `OrderAccepted`. This
recovery state is not persisted across an execution-client process restart.

### Instrument provider configuration options

The instrument provider config is passed via the `instrument_config` parameter on
the data and execution client configs.

| Option               | Default | Description                                                                                    |
|----------------------|---------|------------------------------------------------------------------------------------------------|
| `load_all`           | `False` | Load all venue instruments on start. Auto-set to `True` when `event_slug_builder` is provided. |
| `load_ids`           | `None`  | Specific instrument IDs to load.                                                               |
| `filters`            | `None`  | Instrument filters.                                                                             |
| `event_slugs`        | `None`  | Specific event slugs to load.                                                                  |
| `market_slugs`       | `None`  | Specific market slugs to load.                                                                 |
| `series_ids`         | `None`  | UpDown series IDs to load.                                                                     |
| `event_slug_builder` | `None`  | `PolymarketUpDownEventSlugConfig` describing the UpDown markets to build slugs for.            |
| `use_gamma_markets`  | `None`  | Use the Gamma API for market discovery.                                                        |
| `log_warnings`       | `None`  | Log provider warnings.                                                                          |

#### Event slug builder

The `event_slug_builder` feature enables efficient loading of niche markets without downloading
the full venue catalogue. Instead of loading everything, you provide an
`event_slug_builder` config describing the UpDown markets you need:

```python
from nautilus_trader.adapters.polymarket import PolymarketInstrumentProviderConfig
from nautilus_trader.adapters.polymarket import PolymarketUpDownEventSlugConfig

# Configure with an UpDown slug builder
instrument_config = PolymarketInstrumentProviderConfig(
    event_slug_builder=PolymarketUpDownEventSlugConfig(
        assets=["BTC", "ETH"],
        interval_mins=60,
        periods=24,
    ),
)
```

NT v2 compatibility note: the v1 fully-qualified callable string
(`"mymodule:build_slugs"`) spelling for `event_slug_builder` is
migration/reference-only; the pinned parameter takes a
`PolymarketUpDownEventSlugConfig`.

### Basic setup

Register Polymarket data and execution clients on a live node with the PyO3
factories (NT v2 compatibility note: the v1 `TradingNodeConfig(data_clients={...})` flow is
migration/reference-only):

```python
from nautilus_trader.adapters.polymarket import PolymarketDataClientConfig
from nautilus_trader.adapters.polymarket import PolymarketDataClientFactory
from nautilus_trader.adapters.polymarket import PolymarketExecutionClientConfig
from nautilus_trader.adapters.polymarket import PolymarketExecutionClientFactory
from nautilus_trader.adapters.polymarket import PolymarketInstrumentProviderConfig
from nautilus_trader.live import Environment, LiveNode

data_config = PolymarketDataClientConfig(
    instrument_config=PolymarketInstrumentProviderConfig(load_all=True),
)

exec_config = PolymarketExecutionClientConfig(
    account_id="POLYMARKET-001",
    private_key=None,  # Falls back to POLYMARKET_PK
    funder=None,  # Falls back to POLYMARKET_FUNDER (required for proxy wallets)
)

node = (
    LiveNode.builder("POLYMARKET", trader_id, Environment.LIVE)
    .add_data_client(None, PolymarketDataClientFactory(), data_config)
    .add_exec_client(None, PolymarketExecutionClientFactory(), exec_config)
    .build()
)
```

## Historical data loading

The `PolymarketDataLoader` provides methods for fetching and parsing historical market data
for research and backtesting purposes. The loader integrates with multiple Polymarket APIs to provide the required data.

:::note
All data fetching methods are **asynchronous** and must be called with `await`. The loader can optionally accept an `http_client` parameter for dependency injection (useful for testing).
:::

### Data sources

The loader fetches data from three primary sources:

1. **Polymarket Gamma API** - Market metadata, instrument details, and active market listings.
2. **Polymarket CLOB API** - Market details for instrument construction.
3. **Polymarket Data API** - Historical trades and current user positions.

The current loader does **not** expose helpers for CLOB price history timeseries or order book
history snapshots.

### Method naming conventions

The loader provides two ways to access the Polymarket APIs:

| Prefix    | Type             | Use case                                                               |
|-----------|------------------|------------------------------------------------------------------------|
| `query_*` | Static methods   | API exploration without an instrument. No loader instance needed.      |
| `fetch_*` | Instance methods | Data fetching with a configured loader. Uses the loader's HTTP client. |

**Use `query_*` when** you want to explore markets, discover events, or fetch metadata
before committing to a specific instrument:

```python
# No loader needed: query the API directly
market = await PolymarketDataLoader.query_market_by_slug("some-market")
event = await PolymarketDataLoader.query_event_by_slug("some-event")
```

**Use `fetch_*` when** you have a loader instance and want to fetch data using its
configured HTTP client (for coordinated rate limiting across multiple calls):

```python
loader = await PolymarketDataLoader.from_market_slug("some-market")

# All fetch calls share the loader's HTTP client
markets = await loader.fetch_markets(active=True, limit=100)
events = await loader.fetch_events(active=True)
details = await loader.fetch_market_details(condition_id)
```

### Finding markets

Use the provided utility scripts to discover active markets:

```bash
# List all active markets
python nautilus_trader/adapters/polymarket/scripts/active_markets.py

# List BTC and ETH UpDown markets specifically
python nautilus_trader/adapters/polymarket/scripts/list_updown_markets.py
```

### Basic usage

The recommended way to create a loader is using the factory classmethods, which handle
all the API calls and instrument creation automatically:

```python
import asyncio

from nautilus_trader.adapters.polymarket import PolymarketDataLoader


async def main():
    # Create loader from market slug (recommended)
    loader = await PolymarketDataLoader.from_market_slug(
        "gta-vi-released-before-june-2026"
    )

    # Loader is ready to use with instrument and token_id set
    print(loader.instrument)
    print(loader.token_id)


asyncio.run(main())
```

For events with multiple markets (e.g., temperature buckets), use `from_event_slug`:

```python
# Returns a list of loaders, one per market in the event
loaders = await PolymarketDataLoader.from_event_slug(
    "highest-temperature-in-nyc-on-january-26"
)
```

#### Look-ahead protection for resolved markets

When constructing a loader for a market that has already resolved at backtest
build time, the venue payload includes the answer (`closed`, `closedTime`,
`umaResolutionStatus`, per-token `winner`). A strategy that reads
`cache.instrument(...).info` from `on_start` can therefore see the outcome
before the simulation runs.

Pass `sanitize_info=True` to either factory to redact those fields from
`instrument.info` before the instrument is constructed. The redacted slice is
stashed on the loader as `resolution_metadata` for post-hoc analytics
(settlement PnL, Brier scoring) without leaking it into the simulation:

```python
loader = await PolymarketDataLoader.from_market_slug(
    "some-resolved-market",
    sanitize_info=True,
)

assert "closed" not in loader.instrument.info
assert loader.resolution_metadata["closed"] is True
```

### Discovering markets and events

Use `fetch_markets()` and `fetch_events()` to discover available markets programmatically:

```python
loader = await PolymarketDataLoader.from_market_slug("any-market")

# List active markets
markets = await loader.fetch_markets(active=True, closed=False, limit=100)
for market in markets:
    print(f"{market['slug']}: {market['question']}")

# List active events
events = await loader.fetch_events(active=True, limit=50)
for event in events:
    print(f"{event['slug']}: {event['title']}")

# Get all markets within a specific event
event_markets = await loader.get_event_markets(
    "highest-temperature-in-nyc-on-january-26"
)
```

For quick exploration without creating a loader, use the static `query_*` methods
(see [Method naming conventions](#method-naming-conventions) above).

### Fetching trade history

The `load_trades()` convenience method fetches and parses historical trades in one step:

```python
import pandas as pd

# Load all available trades
trades = await loader.load_trades()

# Or filter by time range (client-side filtering)
end = pd.Timestamp.now(tz="UTC")
start = end - pd.Timedelta(hours=24)

trades = await loader.load_trades(
    start=start,
    end=end,
)
```

Alternatively, you can fetch and parse separately using the lower-level methods:

```python
condition_id = loader.condition_id

# Fetch raw trades from the Polymarket Data API
raw_trades = await loader.fetch_trades(condition_id=condition_id)

# Parse to NautilusTrader TradeTicks
trades = loader.parse_trades(raw_trades)
```

Trade data is sourced from the [Polymarket Data API](https://data-api.polymarket.com/trades),
which provides real execution data including price, size, side, and on-chain transaction hash.

:::note
The public Data API caps offset-based pagination on high-activity markets. When
this ceiling is hit the loader emits a `RuntimeWarning` and returns the trades
fetched up to the cap rather than aborting the load. Use another historical
data source if you need full coverage of a heavily traded market.
:::

### Complete backtest example

See `examples/backtest/polymarket_simple_quoter.py` for a full example:

```python
import asyncio
from decimal import Decimal

from nautilus_trader.adapters.polymarket import POLYMARKET_VENUE
from nautilus_trader.adapters.polymarket import PolymarketDataLoader
from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.examples.strategies.ema_cross_long_only import EMACrossLongOnly
from nautilus_trader.examples.strategies.ema_cross_long_only import (
    EMACrossLongOnlyConfig,
)
from nautilus_trader.model.currencies import pUSD
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.identifiers import TraderId
from nautilus_trader.model.objects import Money


async def run_backtest():
    # Initialize loader and fetch market data
    loader = await PolymarketDataLoader.from_market_slug(
        "gta-vi-released-before-june-2026"
    )
    instrument = loader.instrument

    # Load historical trades from the Polymarket Data API
    trades = await loader.load_trades()

    # Configure and run backtest
    config = BacktestEngineConfig(trader_id=TraderId("BACKTESTER-001"))
    engine = BacktestEngine(config=config)

    engine.add_venue(
        venue=POLYMARKET_VENUE,
        oms_type=OmsType.NETTING,
        account_type=AccountType.CASH,
        base_currency=pUSD,
        starting_balances=[Money(10_000, pUSD)],
    )

    engine.add_instrument(instrument)
    engine.add_data(trades)

    bar_type = BarType.from_str(f"{instrument.id}-100-TICK-LAST-INTERNAL")
    strategy_config = EMACrossLongOnlyConfig(
        instrument_id=instrument.id,
        bar_type=bar_type,
        trade_size=Decimal("20"),
    )

    strategy = EMACrossLongOnly(config=strategy_config)
    engine.add_strategy(strategy=strategy)
    engine.run()

    # Display results
    print(engine.trader.generate_account_report(POLYMARKET_VENUE))


# Run the backtest
asyncio.run(run_backtest())
```

**Run the complete example**:

```bash
python examples/backtest/polymarket_simple_quoter.py
```

### Helper functions

The adapter provides utility functions for working with Polymarket identifiers:

```python
from nautilus_trader.adapters.polymarket import get_polymarket_instrument_id

# Create NautilusTrader InstrumentId from Polymarket identifiers
instrument_id = get_polymarket_instrument_id(
    condition_id="0xcccb7e7613a087c132b69cbf3a02bece3fdcb824c1da54ae79acc8d4a562d902",
    token_id="8441400852834915183759801017793514978104486628517653995211751018945988243154",
)
```

## Contributing

:::info
For additional features or to contribute to the Polymarket adapter, please see our
[contributing guide](https://github.com/nautechsystems/nautilus_trader/blob/develop/CONTRIBUTING.md).
:::