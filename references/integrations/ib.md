NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Interactive Brokers

Interactive Brokers (IB) is a trading platform providing market access across a wide range of financial instruments, including stocks, options, futures, currencies, bonds, funds, and cryptocurrencies. NautilusTrader offers an adapter to integrate with IB using their [Trader Workstation (TWS) API](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/). The adapter provides live market data, execution, historical data, instrument loading, and optional Dockerized IB Gateway management through the same Rust implementation and Python bindings.

The TWS API is an interface to IB's standalone trading applications: TWS and IB Gateway. Both can be downloaded from the IB website. If you haven't installed TWS or IB Gateway yet, refer to the [Initial Setup](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/#tws-download) guide. In NautilusTrader, you'll establish a connection to one of these applications via the `InteractiveBrokersClient`.

Alternatively, you can start with a [dockerized version](https://github.com/gnzsnz/ib-gateway-docker) of the IB Gateway, which is particularly useful when deploying trading strategies on a hosted cloud platform.

:::note
The standalone TWS and IB Gateway applications require manually inputting username, password, and trading mode (live or paper) at startup. The dockerized version of the IB Gateway handles these steps programmatically.
:::

## Installation

Install NautilusTrader using the [installation guide](https://nautilustrader.io/latest/getting-started/installation/). The Interactive Brokers adapter and Docker gateway support are included in the Python package; no adapter-specific extra is required.

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/interactive_brokers/).

## Getting started

Before implementing your trading strategies, make sure that either TWS (Trader Workstation) or IB Gateway is running. You can log in to one of these standalone applications with your credentials, or connect programmatically via `DockerizedIBGateway`.

:::warning
Configure TWS or IB Gateway to return market data timestamps in UTC before connecting NautilusTrader. This setting must be enabled by the user in TWS/IB Gateway, as NautilusTrader is designed to work with UTC timestamps.
:::

### Connection methods

There are two primary ways to connect to Interactive Brokers:

1. **Connect to an existing TWS or IB Gateway instance**
2. **Use the dockerized IB Gateway (recommended for automated deployments)**

### Default ports

Interactive Brokers uses different default ports depending on the application and trading mode:

| Application | Paper Trading | Live Trading |
|-------------|---------------|--------------|
| TWS         | 7497          | 7496         |
| IB Gateway  | 4002          | 4001         |

### Establish connection to an existing gateway or TWS

Import the public configuration types from `nautilus_trader.adapters.interactive_brokers`. When
connecting to a pre-existing gateway or TWS, specify the `host`, `port`, and `client_id` parameters
in both the `InteractiveBrokersDataClientConfig` and `InteractiveBrokersExecutionClientConfig`:

```python
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersExecutionClientConfig

# Example for TWS paper trading (default port 7497)
data_config = InteractiveBrokersDataClientConfig(
    host="127.0.0.1",
    port=7497,
    client_id=1,
)

exec_config = InteractiveBrokersExecutionClientConfig(
    host="127.0.0.1",
    port=7497,
    client_id=1,
    account_id="DU123456",  # Your paper trading account ID
)
```

Use a distinct client ID for each process connected to the same TWS or IB Gateway session. An
execution client ID cannot be a multiple of `1000` because the adapter partitions order IDs by
`client_id % 1000`.

### Establish connection to Dockerized IB Gateway

For automated deployments, the dockerized gateway is recommended. Supply credentials in the config
or through `TWS_USERNAME` and `TWS_PASSWORD`:

```python
from nautilus_trader.adapters.interactive_brokers import DockerizedIBGateway
from nautilus_trader.adapters.interactive_brokers import DockerizedIBGatewayConfig
from nautilus_trader.adapters.interactive_brokers import TradingMode

gateway_config = DockerizedIBGatewayConfig(
    username="your_username",  # Or set TWS_USERNAME env var
    password="your_password",  # Or set TWS_PASSWORD env var
    trading_mode=TradingMode.PAPER,
    read_only_api=True,  # Set to False to allow order execution
    timeout=300,  # Startup timeout in seconds
)

# This may take a short while to start up, especially the first time
gateway = DockerizedIBGateway(gateway_config)
gateway.start_blocking()

# Inspect the container status
print(gateway.container_status())
```

Start `DockerizedIBGateway` separately, then pass its `host` and `port` to the data and execution
configs. Passing a non-`None` `dockerized_gateway` argument to either client config raises
`ValueError` because Python does not own the container lifecycle.

### Environment variables

To supply credentials to the Interactive Brokers Gateway, either pass the `username` and `password` to the `DockerizedIBGatewayConfig`, or set the following environment variables:

- `TWS_USERNAME`: Your IB account username.
- `TWS_PASSWORD`: Your IB account password.
- `TWS_ACCOUNT`: Your IB account ID (used as the fallback for `account_id`).

### Connection management

The adapter includes connection management features:

- **Automatic reconnection**: Configure retries with the `IB_MAX_CONNECTION_ATTEMPTS` environment variable.
- **Connection timeout**: Adjust the timeout with the `connection_timeout` parameter (default: 300 seconds).
- **Connection watchdog**: Monitor connection health and trigger reconnection automatically when required.
- **Graceful error handling**: Handle diverse connection scenarios with error classification.

## Overview

The Interactive Brokers adapter provides an integration with IB's TWS API. The adapter includes several major components:

### Core components

- **`InteractiveBrokersClient`**: The central client that executes TWS API requests. Manages connections, handles errors, and coordinates all API interactions.
- **`InteractiveBrokersDataClient`**: Connects to the Gateway for streaming market data including quotes, trades, and bars.
- **`InteractiveBrokersExecutionClient`**: Handles account information, order management, and trade execution.
- **`InteractiveBrokersInstrumentProvider`**: Retrieves and manages instrument definitions, including support for options and futures chains.
- **`HistoricalInteractiveBrokersClient`**: Provides methods for retrieving instruments and historical data, useful for backtesting and research.

### Supporting components

- **`DockerizedIBGateway`**: Manages dockerized IB Gateway instances for automated deployments.
- **Configuration classes**: Provide configuration options for all components.
- **`InteractiveBrokersDataClientFactory` / `InteractiveBrokersExecutionClientFactory`**: Create live data and execution clients for the node.

### Supported asset classes

The adapter supports trading across all major asset classes available through Interactive Brokers:

- **Equities**: Stocks, ETFs, and equity options.
- **Fixed income**: Bonds and bond funds.
- **Derivatives**: Futures, options, and warrants.
- **Foreign exchange**: Spot FX and FX forwards.
- **Cryptocurrencies**: Bitcoin, Ethereum, and other digital assets.
- **Commodities**: Physical commodities and commodity futures.
- **Indices**: Index products and index options.

## The Interactive Brokers client

The `InteractiveBrokersClient` is the central component of the IB adapter, overseeing a range of functions. These include establishing and maintaining connections, handling API errors, executing trades, and gathering various types of data such as market data, contract/instrument data, and account details.

The `InteractiveBrokersClient` is divided into specialized mixin classes, each handling a specific responsibility.

### Client architecture

The client uses a mixin-based architecture where each mixin handles a specific aspect of the IB API:

#### Connection management (`InteractiveBrokersClientConnectionMixin`)

- Establishes and maintains socket connections to TWS/Gateway.
- Handles connection timeouts and reconnection logic.
- Manages connection state and health monitoring.
- Supports configurable reconnection attempts via `IB_MAX_CONNECTION_ATTEMPTS` environment variable.

#### Error handling (`InteractiveBrokersClientErrorMixin`)

- Processes all API errors and warnings.
- Categorizes errors by type (client errors, connectivity issues, request errors).
- Handles subscription and request-specific error scenarios.
- Provides error logging and debugging information.

#### Account management (`InteractiveBrokersClientAccountMixin`)

- Retrieves account information and balances.
- Manages position data and portfolio updates.
- Handles multi-account scenarios.
- Processes account-related notifications.

#### Contract/instrument management (`InteractiveBrokersClientContractMixin`)

- Retrieves contract details and specifications.
- Handles instrument searches and lookups.
- Manages contract validation and verification.
- Supports complex instrument types (options chains, futures chains).

#### Market data management (`InteractiveBrokersClientMarketDataMixin`)

- Handles real-time and historical market data subscriptions.
- Processes quotes, trades, and bar data.
- Manages market data type settings (real-time, delayed, frozen).
- Handles tick-by-tick data and market depth.

#### Order management (`InteractiveBrokersClientOrderMixin`)

- Processes order placement, modification, and cancellation.
- Handles order status updates and execution reports.
- Manages order validation and error handling.
- Supports complex order types and conditions.

### Key features

- **Asynchronous operation**: All operations are fully asynchronous using Python's asyncio.
- **Error handling**: Error categorization and handling.
- **Connection resilience**: Automatic reconnection with configurable retry logic.
- **Message processing**: Efficient message queue processing for high-throughput scenarios.
- **State management**: Proper state tracking for connections, subscriptions, and requests.

:::tip
To troubleshoot TWS API incoming message issues, consider starting at the `InteractiveBrokersClient._process_message` method, which acts as the primary gateway for processing all messages received from the API.
:::

## Symbology

The `InteractiveBrokersInstrumentProvider` supports three methods for constructing `InstrumentId` instances, which can be configured via the `symbology_method` enum in `InteractiveBrokersInstrumentProviderConfig`.

### Symbology methods

#### 1. Simplified symbology (`SymbologyMethod.SIMPLIFIED`) - default

When `symbology_method` is set to `SymbologyMethod.SIMPLIFIED` (the default setting), the system uses intuitive, human-readable symbology rules:

**Format Rules by Asset Class:**

- **Forex**: `{symbol}/{currency}.{exchange}`
  - Example: `EUR/USD.IDEALPRO`
- **Stocks**: `{localSymbol}.{primaryExchange}`
  - Spaces in localSymbol are replaced with hyphens
  - Example: `BF-B.NYSE`, `SPY.ARCA`
- **Futures**: `{localSymbol}.{exchange}`
  - Individual contracts use single digit years
  - Example: `ESM4.CME`, `CLZ7.NYMEX`
- **Continuous Futures**: `{symbol}.{exchange}`
  - Represents front month, automatically rolling
  - Example: `ES.CME`, `CL.NYMEX`
- **Options on Futures (FOP)**: `{localSymbol}.{exchange}`
  - Format: `{symbol}{month}{year} {right}{strike}`
  - Example: `ESM4 C4200.CME`
- **Options**: `{localSymbol}.{exchange}`
  - All spaces removed from localSymbol
  - Example: `AAPL230217P00155000.SMART`
- **Indices**: `^{localSymbol}.{exchange}`
  - Example: `^SPX.CBOE`, `^NDX.NASDAQ`
- **Bonds**: `{localSymbol}.{exchange}`
  - Example: `912828XE8.SMART`
- **Cryptocurrencies**: `{symbol}/{currency}.{exchange}`
  - Example: `BTC/USD.PAXOS`, `ETH/USD.PAXOS`

#### 2. Raw symbology (`SymbologyMethod.RAW`)

Setting `symbology_method` to `SymbologyMethod.RAW` enforces stricter parsing rules that align directly with the fields defined in the IB API. This method provides maximum compatibility across all regions and instrument types:

**Format Rules:**

- **CFDs**: `{localSymbol}={secType}.IBCFD`
- **Commodities**: `{localSymbol}={secType}.IBCMDTY`
- **Default for Other Types**: `{localSymbol}={secType}.{exchange}`

**Examples:**

- `IBUS30=CFD.IBCFD`
- `XAUUSD=CMDTY.IBCMDTY`
- `AAPL=STK.SMART`

This configuration ensures explicit instrument identification and supports instruments from any region, especially those with non-standard symbology where simplified parsing may fail.

### MIC venue conversion

The adapter supports converting Interactive Brokers exchange codes to Market Identifier Codes (MIC) for standardized venue identification:

#### `convert_exchange_to_mic_venue`

When set to `True`, the adapter automatically converts IB exchange codes to their corresponding MIC codes:

```python
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    convert_exchange_to_mic_venue=True,  # Enable MIC conversion
    symbology_method=SymbologyMethod.SIMPLIFIED,
)
```

**Examples of MIC Conversion:**

- `CME` -> `XCME` (Chicago Mercantile Exchange)
- `NASDAQ` -> `XNAS` (Nasdaq Stock Market)
- `NYSE` -> `XNYS` (New York Stock Exchange)
- `LSE` -> `XLON` (London Stock Exchange)

#### `symbol_to_mic_venue`

Symbol-prefix to MIC venue overrides. Applied **first** in venue resolution, independent of `convert_exchange_to_mic_venue`. When a contract's symbol matches a configured prefix, that MIC venue is used; otherwise resolution uses exchange (and optionally MIC conversion if `convert_exchange_to_mic_venue` is True). Useful for OPT contracts with exchange SMART (e.g. SPX -> XCBO) and for aligning with databento-style instrument IDs.

```python
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    symbol_to_mic_venue={
        "SPX": "XCBO",  # OPT with exchange SMART -> XCBO
        "ES": "XCME",   # All ES futures/options use CME MIC
        "SPY": "ARCX",  # SPY specifically uses ARCA
    },
)
# convert_exchange_to_mic_venue can be True or False; symbol_to_mic_venue is applied first
```

#### Venue resolution and `_process_contract_details`

When loading instruments via contract dictionaries, the provider passes `venue=None` into `_process_contract_details`, so each contract detail gets its own venue (via `symbol_to_mic_venue`, validExchanges, and MIC conversion). Callers that pass a single venue string still get one venue for all details. To get per-detail resolution when you have mixed or SMART-routed results, pass `venue=None`.

### Supported instrument formats

The adapter supports various instrument formats based on Interactive Brokers' contract specifications:

#### Futures month codes

- **F** = January, **G** = February, **H** = March, **J** = April
- **K** = May, **M** = June, **N** = July, **Q** = August
- **U** = September, **V** = October, **X** = November, **Z** = December

#### Supported exchanges by asset class

**Futures Exchanges:**

- `CME`, `CBOT`, `NYMEX`, `COMEX`, `KCBT`, `MGE`, `NYBOT`, `SNFE`

**Options Exchanges:**

- `SMART` (IB's smart routing)

**Forex Exchanges:**

- `IDEALPRO` (IB's forex platform)

**Cryptocurrency Exchanges:**

- `PAXOS` (IB's crypto platform)

**CFD/Commodity Exchanges:**

- `IBCFD`, `IBCMDTY` (IB's internal routing)

### Choosing the right symbology method

- **Use `SymbologyMethod.SIMPLIFIED`** (default) for most use cases - provides clean, readable instrument IDs
- **Use `SymbologyMethod.RAW`** when dealing with complex international instruments or when simplified parsing fails
- **Enable `convert_exchange_to_mic_venue`** when you need standardized MIC venue codes for compliance or data consistency

## Instruments and contracts

In Interactive Brokers, a NautilusTrader `Instrument` corresponds to an IB [Contract](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/#contracts). The adapter represents contracts as JSON dictionaries with IB API field names (for example `secType`, `symbol`, `exchange`, `currency`, `strike`, `right`, and `lastTradeDateOrContractMonth`).

### Contract discovery

To search for contract information, use the [IB Contract Information Center](https://pennies.interactivebrokers.com/cstools/contract_info/).

### Loading instruments

There are two primary methods for loading instruments:

#### 1. Using `load_ids` (recommended)

Use `symbology_method=SymbologyMethod.SIMPLIFIED` (default) with `load_ids` for clean, intuitive instrument identification:

```python
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.adapters.interactive_brokers import SymbologyMethod

instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    symbology_method=SymbologyMethod.SIMPLIFIED,
    load_ids=frozenset([
        "EUR/USD.IDEALPRO",    # Forex
        "SPY.ARCA",            # Stock
        "ESM24.CME",           # Future
        "BTC/USD.PAXOS",       # Crypto
        "^SPX.CBOE",           # Index
    ]),
)
```

#### 2. Using `load_contracts` (for complex instruments)

Use `load_contracts` with contract dictionaries for complex scenarios like options/futures chains.
Set chain flags on a contract dictionary to use that contract as the underlying or chain seed. The
provider-level `min_expiry_days` and `max_expiry_days` values limit the contracts loaded:

```python
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersInstrumentProviderConfig

provider_config = InteractiveBrokersInstrumentProviderConfig(
    load_contracts=[
        {
            "symbol": "SPY",
            "secType": "STK",
            "exchange": "SMART",
            "currency": "USD",
            "build_options_chain": True,
        },
        {
            "symbol": "ES",
            "secType": "CONTFUT",
            "exchange": "CME",
            "currency": "USD",
            "build_futures_chain": True,
        },
    ],
    min_expiry_days=7,
    max_expiry_days=60,
)
```

When `CONTFUT` has a chain flag, the adapter qualifies it and loads the matching dated futures or
futures options. Without a chain flag, it represents IB's continuous future, which IB limits to
historical data. It cannot provide live market data or accept orders.

### Contract dictionary examples by asset class

```python
# Stocks
{"secType": "STK", "exchange": "SMART", "primaryExchange": "ARCA", "symbol": "SPY"}
{"secType": "STK", "exchange": "SMART", "primaryExchange": "NASDAQ", "symbol": "AAPL"}

# Bonds
{"secType": "BOND", "secIdType": "ISIN", "secId": "US03076KAA60"}
{"secType": "BOND", "secIdType": "CUSIP", "secId": "912828XE8"}

# Individual Options
{"secType": "OPT", "exchange": "SMART", "symbol": "SPY",
 "lastTradeDateOrContractMonth": "20251219", "strike": 500, "right": "C"}

# Options Chain (loads all strikes/expirations)
{"secType": "STK", "exchange": "SMART", "primaryExchange": "ARCA", "symbol": "SPY",
 "build_options_chain": True, "min_expiry_days": 10, "max_expiry_days": 60}

# CFDs
{"secType": "CFD", "symbol": "IBUS30"}
{"secType": "CFD", "symbol": "DE40EUR", "exchange": "SMART"}

# Individual Futures
{"secType": "FUT", "exchange": "CME", "symbol": "ES",
 "lastTradeDateOrContractMonth": "20240315"}

# Futures Chain (loads all expirations)
{"secType": "CONTFUT", "exchange": "CME", "symbol": "ES", "build_futures_chain": True}

# Options on Futures (FOP) - Individual
{"secType": "FOP", "exchange": "CME", "symbol": "ES",
 "lastTradeDateOrContractMonth": "20240315", "strike": 4200, "right": "C"}

# Options on Futures Chain (loads all strikes/expirations)
{"secType": "CONTFUT", "exchange": "CME", "symbol": "ES",
 "build_options_chain": True, "min_expiry_days": 7, "max_expiry_days": 60}

# Forex
{"secType": "CASH", "exchange": "IDEALPRO", "symbol": "EUR", "currency": "USD"}
{"secType": "CASH", "exchange": "IDEALPRO", "symbol": "GBP", "currency": "JPY"}

# Crypto
{"secType": "CRYPTO", "symbol": "BTC", "exchange": "PAXOS", "currency": "USD"}
{"secType": "CRYPTO", "symbol": "ETH", "exchange": "PAXOS", "currency": "USD"}

# Indices
{"secType": "IND", "symbol": "SPX", "exchange": "CBOE"}
{"secType": "IND", "symbol": "NDX", "exchange": "NASDAQ"}

# Commodities
{"secType": "CMDTY", "symbol": "XAUUSD", "exchange": "SMART"}

# Continuous Futures
{"secType": "CONTFUT", "exchange": "CME", "symbol": "ES"}  # -> ES.CME
{"secType": "CONTFUT", "exchange": "NYMEX", "symbol": "CL"} # -> CL.NYMEX
```

### Advanced configuration options

```python
# Options chain with custom exchange
{
    "secType": "STK",
    "symbol": "AAPL",
    "exchange": "SMART",
    "primaryExchange": "NASDAQ",
    "build_options_chain": True,
    "options_chain_exchange": "CBOE",  # Use CBOE for options instead of SMART
    "min_expiry_days": 7,
    "max_expiry_days": 45,
}

# Futures chain with specific months
{
    "secType": "CONTFUT",
    "exchange": "NYMEX",
    "symbol": "CL",  # Crude Oil
    "build_futures_chain": True,
    "min_expiry_days": 30,
    "max_expiry_days": 180,
}
```

### Continuous futures

For continuous futures contracts (using `secType='CONTFUT'`), the adapter creates instrument IDs using just the symbol and venue:

```python
# Continuous futures examples
{"secType": "CONTFUT", "exchange": "CME", "symbol": "ES"}  # -> ES.CME
{"secType": "CONTFUT", "exchange": "NYMEX", "symbol": "CL"} # -> CL.NYMEX

# With MIC venue conversion enabled
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    convert_exchange_to_mic_venue=True,
)
# Results in:
# ES.XCME (instead of ES.CME)
# CL.XNYM (instead of CL.NYMEX)
```

**Continuous Futures vs Individual Futures:**

- **Continuous**: `ES.CME` - Represents the front month contract, automatically rolls
- **Individual**: `ESM4.CME` - Specific March 2024 contract

:::note
When using `build_options_chain=True` or `build_futures_chain=True`, the `secType` and `symbol` should be specified for the underlying contract. The adapter will automatically discover and load all related derivative contracts within the specified expiry range.
:::

## Option spreads

Interactive Brokers supports option spreads through BAG contracts, which combine multiple option legs into a single tradeable instrument. NautilusTrader provides support for creating, loading, and trading option spreads.

### Creating option spread instrument IDs

Spread instrument IDs combine the individual option legs with their respective ratios. Single
parentheses mark a positive leg ratio; double parentheses mark a negative ratio. All legs must
use the same venue:

```python
from nautilus_trader.model import InstrumentId

# Long 1x "SPY C400" and short 1x "SPY C410" (double parentheses mark a negative ratio)
spread_id = InstrumentId.from_str("(1)SPY C400_((1))SPY C410.SMART")
```

### Dynamic spread loading

Option spreads must be requested before they can be traded or subscribed to for market data. Use the `request_instrument()` method to dynamically load spread instruments:

```python
# In your strategy's on_start method
def on_start(self):
    # Request the spread instrument
    self.request_instrument(spread_id)

def on_instrument(self, instrument):
    # Handle the loaded spread instrument
    self.log.info(f"Loaded spread: {instrument.id}")

    # Now you can subscribe to market data
    self.subscribe_quote_ticks(instrument.id)

    # And place orders
    order = self.order_factory.market(
        instrument_id=instrument.id,
        order_side=OrderSide.BUY,
        quantity=instrument.make_qty(1),
        time_in_force=TimeInForce.DAY,
    )
    self.submit_order(order)
```

### Spread trading requirements

1. **Load individual legs first**: Ensure the individual option legs are available before creating spreads.
2. **Request the spread instrument**: Use `request_instrument()` to load the spread before trading.
3. **Subscribe to market data**: Request quote ticks after the spread is loaded.
4. **Place orders**: Any order type can be used once the spread is available.

## Historical data and backtesting

The `HistoricalInteractiveBrokersClient` provides methods for retrieving historical data from Interactive Brokers for backtesting and research purposes.

### Supported data types

- **Bar data**: OHLCV bars with time, tick, and volume aggregations.
- **Tick data**: Trade ticks and quote ticks with microsecond precision.
- **Instrument data**: Complete contract specifications and trading rules.

### Historical data client

`HistoricalInteractiveBrokersClient` connects with an instrument provider and data client config:

```python
from nautilus_trader.adapters.interactive_brokers import HistoricalInteractiveBrokersClient
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersInstrumentProvider
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.adapters.interactive_brokers import MarketDataType

provider = InteractiveBrokersInstrumentProvider(
    InteractiveBrokersInstrumentProviderConfig(load_all=True),
)

config = InteractiveBrokersDataClientConfig(
    host="127.0.0.1",
    port=7497,
    client_id=1,
    market_data_type=MarketDataType.DELAYED_FROZEN,  # Use delayed data if no subscription
)

client = HistoricalInteractiveBrokersClient(provider, config)
```

Its async Python methods support `request_instruments` for contract and instrument discovery,
`request_bars` for one or more bar specifications, and `request_ticks` for historical trade or
bid-ask ticks.

### Retrieving instruments

#### Basic instrument retrieval

```python
# Define contracts as JSON dictionaries
contracts = [
    {"secType": "STK", "symbol": "AAPL", "exchange": "SMART", "primaryExchange": "NASDAQ"},
    {"secType": "STK", "symbol": "MSFT", "exchange": "SMART", "primaryExchange": "NASDAQ"},
    {"secType": "CASH", "symbol": "EUR", "currency": "USD", "exchange": "IDEALPRO"},
]

# Request instrument definitions
instruments = await client.request_instruments(contracts=contracts)
```

#### Option chain retrieval with catalog storage

You can download entire option chains using `request_instruments` in your strategy, with the added benefit of saving the data to the catalog by passing `"update_catalog": True` in `params`:

```python
# In your strategy's on_start method
def on_start(self):
    self.request_instruments(
        venue=IB_VENUE,
        params={
            "update_catalog": True,
            "ib_contracts": (
                # SPY options
                {
                    "secType": "STK",
                    "symbol": "SPY",
                    "exchange": "SMART",
                    "primaryExchange": "ARCA",
                    "build_options_chain": True,
                    "min_expiry_days": 7,
                    "max_expiry_days": 30,
                },
                # QQQ options
                {
                    "secType": "STK",
                    "symbol": "QQQ",
                    "exchange": "SMART",
                    "primaryExchange": "NASDAQ",
                    "build_options_chain": True,
                    "min_expiry_days": 7,
                    "max_expiry_days": 30,
                },
                # ES futures options
                {
                    "secType": "CONTFUT",
                    "exchange": "CME",
                    "symbol": "ES",
                    "build_options_chain": True,
                    "min_expiry_days": 0,
                    "max_expiry_days": 60,
                },
                # SPX index options
                {
                    "secType": "IND",
                    "symbol": "SPX",
                    "exchange": "CBOE",
                    "build_options_chain": True,
                    "min_expiry_days": 0,
                    "max_expiry_days": 5,
                },
                # ES futures chain and futures options
                {
                    "secType": "CONTFUT",
                    "exchange": "CME",
                    "symbol": "ES",
                    "build_futures_chain": True,
                    "build_options_chain": True,
                    "min_expiry_days": 0,
                    "max_expiry_days": 2,
                },
                # ESTX50 index options (Eurex)
                {
                    "secType": "IND",
                    "exchange": "EUREX",
                    "symbol": "ESTX50",
                    "build_options_chain": True,
                    "min_expiry_days": 0,
                    "max_expiry_days": 2,
                },
            ),
        },
    )
```

### Retrieving historical bars

```python
import datetime

# Request historical bars
bars = await client.request_bars(
    bar_specifications=[
        "1-MINUTE-LAST",    # 1-minute bars using last price
        "5-MINUTE-MID",     # 5-minute bars using midpoint
        "1-HOUR-LAST",      # 1-hour bars using last price
        "1-DAY-LAST",       # Daily bars using last price
    ],
    start_date_time=datetime.datetime(2023, 11, 1, 9, 30),
    end_date_time=datetime.datetime(2023, 11, 6, 16, 30),
    contracts=contracts,
    use_rth=True,  # Regular Trading Hours only
    timeout=120,   # Request timeout in seconds
)
```

### Retrieving historical ticks

```python
# Request historical tick data (use tick_type="TRADES" or "BID_ASK" for quote ticks)
ticks = await client.request_ticks(
    tick_type="TRADES",
    start_date_time=datetime.datetime(2023, 11, 6, 9, 30),
    end_date_time=datetime.datetime(2023, 11, 6, 16, 30),
    contracts=contracts,
    use_rth=True,
    timeout=120,
)
```

### Bar specifications

The adapter supports various bar specifications:

#### Time-based bars

- `"1-SECOND-LAST"`, `"5-SECOND-LAST"`, `"10-SECOND-LAST"`, `"15-SECOND-LAST"`, `"30-SECOND-LAST"`
- `"1-MINUTE-LAST"`, `"2-MINUTE-LAST"`, `"3-MINUTE-LAST"`, `"5-MINUTE-LAST"`, `"10-MINUTE-LAST"`, `"15-MINUTE-LAST"`, `"20-MINUTE-LAST"`, `"30-MINUTE-LAST"`
- `"1-HOUR-LAST"`, `"2-HOUR-LAST"`, `"3-HOUR-LAST"`, `"4-HOUR-LAST"`, `"8-HOUR-LAST"`
- `"1-DAY-LAST"`, `"1-WEEK-LAST"`, `"1-MONTH-LAST"`

#### Price types

- `LAST` - Last traded price
- `MID` - Midpoint of bid/ask
- `BID` - Bid price
- `ASK` - Ask price

### Complete example

```python
import asyncio
import datetime

from nautilus_trader.adapters.interactive_brokers import HistoricalInteractiveBrokersClient
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersInstrumentProvider
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.persistence import ParquetDataCatalog


async def download_historical_data():
    # Initialize client from an instrument provider and data client config
    provider = InteractiveBrokersInstrumentProvider(
        InteractiveBrokersInstrumentProviderConfig(load_all=True),
    )
    config = InteractiveBrokersDataClientConfig(
        host="127.0.0.1",
        port=7497,
        client_id=5,
    )
    client = HistoricalInteractiveBrokersClient(provider, config)

    # Define contracts as JSON dictionaries
    contracts = [
        {"secType": "STK", "symbol": "AAPL", "exchange": "SMART", "primaryExchange": "NASDAQ"},
        {"secType": "CASH", "symbol": "EUR", "currency": "USD", "exchange": "IDEALPRO"},
    ]

    # Request instruments
    instruments = await client.request_instruments(contracts=contracts)

    # Request historical bars
    bars = await client.request_bars(
        bar_specifications=["1-HOUR-LAST", "1-DAY-LAST"],
        start_date_time=datetime.datetime(2023, 11, 1, 9, 30),
        end_date_time=datetime.datetime(2023, 11, 6, 16, 30),
        contracts=contracts,
        use_rth=True,
    )

    # Request tick data
    ticks = await client.request_ticks(
        tick_type="TRADES",
        start_date_time=datetime.datetime(2023, 11, 6, 14, 0),
        end_date_time=datetime.datetime(2023, 11, 6, 15, 0),
        contracts=contracts,
    )

    # Save to catalog
    catalog = ParquetDataCatalog("./catalog")
    catalog.write_data(instruments)
    catalog.write_data(bars)
    catalog.write_data(ticks)

    print(f"Downloaded {len(instruments)} instruments")
    print(f"Downloaded {len(bars)} bars")
    print(f"Downloaded {len(ticks)} ticks")


# Run the example
if __name__ == "__main__":
    asyncio.run(download_historical_data())
```

### Data limitations

Be aware of Interactive Brokers' historical data limitations:

- **Rate Limits**: IB enforces rate limits on historical data requests
- **Data Availability**: Historical data availability varies by instrument and subscription level
- **Market Data Permissions**: Some data requires specific market data subscriptions
- **Time Ranges**: Maximum lookback periods vary by bar size and instrument type

### Best practices

1. **Use Delayed Data**: For backtesting, `MarketDataType.DELAYED_FROZEN` is often sufficient
2. **Batch Requests**: Group multiple instruments in single requests when possible
3. **Handle Timeouts**: Set appropriate timeout values for large data requests
4. **Respect Rate Limits**: Add delays between requests to avoid hitting rate limits
5. **Validate Data**: Always check data quality and completeness before backtesting

:::warning
Interactive Brokers enforces pacing limits; excessive historical-data or order requests trigger pacing violations and IB can disable the API session for several minutes.
:::

## Live trading

Live trading with Interactive Brokers wires `InteractiveBrokersDataClientFactory` and
`InteractiveBrokersExecutionClientFactory` into a `LiveNode` (see
[Complete trading node configuration](#complete-trading-node-configuration)). The clients resolve
instruments through the `InteractiveBrokersInstrumentProvider`.

### Architecture overview

The live trading setup consists of three main components:

1. **InstrumentProvider**: Manages instrument definitions and contract details
2. **DataClient**: Handles real-time market data subscriptions
3. **ExecutionClient**: Manages orders, positions, and account information

### InstrumentProvider configuration

The `InteractiveBrokersInstrumentProvider` provides access to financial instrument data from IB. It supports loading individual instruments, options chains, and futures chains.

#### Basic configuration

```python
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.adapters.interactive_brokers import SymbologyMethod

instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    symbology_method=SymbologyMethod.SIMPLIFIED,
    build_futures_chain=False,  # Set to True if fetching futures chains
    build_options_chain=False,  # Set to True if fetching options chains
    min_expiry_days=10,         # Minimum days to expiry for derivatives
    max_expiry_days=60,         # Maximum days to expiry for derivatives
    convert_exchange_to_mic_venue=False,  # Use MIC codes for venue mapping
    cache_validity_days=1,      # Cache instrument data for 1 day
    load_ids=frozenset([
        # Individual instruments using simplified symbology
        "EUR/USD.IDEALPRO",     # Forex
        "BTC/USD.PAXOS",        # Cryptocurrency
        "SPY.ARCA",             # Stock ETF
        "V.NYSE",               # Individual stock
        "ESM4.CME",             # Future contract (single digit year)
        "^SPX.CBOE",            # Index
    ]),
    load_contracts=[
        # Complex instruments as JSON contract dictionaries
        {"secType": "STK", "symbol": "AAPL", "exchange": "SMART", "primaryExchange": "NASDAQ"},
        {"secType": "CASH", "symbol": "GBP", "currency": "USD", "exchange": "IDEALPRO"},
    ],
)
```

#### Advanced configuration for derivatives

```python
# Configuration for options and futures chains
advanced_config = InteractiveBrokersInstrumentProviderConfig(
    symbology_method=SymbologyMethod.SIMPLIFIED,
    build_futures_chain=True,   # Enable futures chain loading
    build_options_chain=True,   # Enable options chain loading
    min_expiry_days=7,          # Load contracts expiring in 7+ days
    max_expiry_days=90,         # Load contracts expiring within 90 days
    load_contracts=[
        # Load SPY options chain
        {
            "secType": "STK",
            "symbol": "SPY",
            "exchange": "SMART",
            "primaryExchange": "ARCA",
            "build_options_chain": True,
        },
        # Load ES futures chain
        {
            "secType": "CONTFUT",
            "exchange": "CME",
            "symbol": "ES",
            "build_futures_chain": True,
        },
    ],
)
```

#### Filtering security types

Use `filter_sec_types` to ignore specific IB `secType` values. Any contract whose `secType` matches an entry in this frozenset is skipped with a warning (for example unsupported types such as `WAR` or `IOPT`):

```python
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    load_ids=frozenset(["SPY.ARCA"]),
    filter_sec_types=frozenset({"WAR", "IOPT"}),  # Opt out from unsupported asset types
)
```

### Integration with external data providers

The Interactive Brokers adapter can be used alongside other data providers for enhanced market data coverage. When using multiple data sources:

- Use consistent symbology methods across providers
- Consider using `convert_exchange_to_mic_venue=True` for standardized venue identification
- Ensure instrument cache management is handled properly to avoid conflicts

### Data client configuration

The `InteractiveBrokersDataClient` interfaces with IB for streaming and retrieving real-time market data. Upon connection, it configures the [market data type](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/#delayed-market-data) and loads instruments based on the `InteractiveBrokersInstrumentProviderConfig` settings.

#### Supported data types

- **Quote Ticks**: Real-time bid/ask prices and sizes
- **Trade Ticks**: Real-time trade prices and volumes
- **Bar Data**: Real-time OHLCV bars (1-second to 1-day intervals)
- **Market Depth**: Level 2 order book data (where available)

#### Market data types

Interactive Brokers supports several market data types:

- `REALTIME`: Live market data (requires market data subscriptions)
- `DELAYED`: 15-20 minute delayed data (free for most markets)
- `DELAYED_FROZEN`: Delayed data that doesn't update (useful for testing)
- `FROZEN`: Last known real-time data (when market is closed)

#### Basic data client configuration

```python
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers import MarketDataType

data_client_config = InteractiveBrokersDataClientConfig(
    host="127.0.0.1",
    port=7497,  # TWS paper trading port
    client_id=1,
    use_regular_trading_hours=True,  # RTH only for stocks
    market_data_type=MarketDataType.DELAYED_FROZEN,  # Use delayed data
    ignore_quote_tick_size_updates=False,  # Include size-only updates
    instrument_provider=instrument_provider_config,
    connection_timeout=300,  # 5 minutes
    request_timeout=60,      # 1 minute
)
```

#### Advanced data client configuration

```python
# Configuration for production with real-time data
production_data_config = InteractiveBrokersDataClientConfig(
    host="127.0.0.1",
    port=4001,  # IB Gateway live trading port
    client_id=1,
    use_regular_trading_hours=False,  # Include extended hours
    market_data_type=MarketDataType.REALTIME,  # Real-time data
    ignore_quote_tick_size_updates=True,  # Reduce tick volume
    handle_revised_bars=True,  # Handle bar revisions
    instrument_provider=instrument_provider_config,
    connection_timeout=300,
    request_timeout=60,
)
```

### Data client configuration options

| Option                          | Default                                         | Description |
|---------------------------------|-------------------------------------------------|-------------|
| `instrument_provider`           | `InteractiveBrokersInstrumentProviderConfig()`  | Instrument provider settings controlling which contracts load at startup. |
| `host`                          | `127.0.0.1`                                     | Hostname or IP for TWS/IB Gateway. |
| `port`                          | `None`                                          | Port for TWS/IB Gateway (`7497`/`7496` for TWS, `4002`/`4001` for IBG). |
| `client_id`                     | `1`                                             | Unique client identifier used when connecting to TWS/IB Gateway. |
| `use_regular_trading_hours`     | `True`                                          | Request bars limited to regular trading hours when `True`. |
| `market_data_type`              | `REALTIME`                                      | Market data feed type (`REALTIME`, `DELAYED`, `DELAYED_FROZEN`, etc.). |
| `ignore_quote_tick_size_updates`| `False`                                         | Suppress quote ticks where only size changes when `True`. |
| `handle_revised_bars`           | `False`                                         | When `True`, processes bar revisions from IB (bars can be updated after initial publication). |
| `dockerized_gateway`            | `None`                                          | Reserved; passing a non-`None` value raises `ValueError` (start the gateway separately and pass `host`/`port`). |
| `connection_timeout`            | `300`                                           | Seconds to wait for the initial API connection. |
| `request_timeout`               | `60`                                            | Seconds to wait for historical data requests before timing out. |

#### Notes

- **`use_regular_trading_hours`**: When `True`, only requests data during regular trading hours. Primarily affects bar data for stocks.
- **`ignore_quote_tick_size_updates`**: When `True`, filters out quote ticks where only the size changed (not price), reducing data volume.
- **`handle_revised_bars`**: When `True`, processes bar revisions from IB (bars can be updated after initial publication).
- **`connection_timeout`**: Maximum time to wait for initial connection establishment.
- **`request_timeout_secs`**: Maximum time to wait for historical data requests.

### Execution client configuration options

| Option                                  | Default                                         | Description |
|-----------------------------------------|-------------------------------------------------|-------------|
| `instrument_provider`                   | `InteractiveBrokersInstrumentProviderConfig()`  | Instrument provider settings controlling which contracts load at startup. |
| `host`                                  | `127.0.0.1`                                     | Hostname or IP for TWS/IB Gateway. |
| `port`                                  | `None`                                          | Port for TWS/IB Gateway (`7497`/`7496` for TWS, `4002`/`4001` for IBG). |
| `client_id`                             | `1`                                             | Unique client identifier used when connecting to TWS/IB Gateway. |
| `account_id`                            | `None`                                          | Interactive Brokers account identifier (falls back to `TWS_ACCOUNT` env var). |
| `dockerized_gateway`                    | `None`                                          | Reserved; passing a non-`None` value raises `ValueError` (start the gateway separately and pass `host`/`port`). |
| `connection_timeout`                    | `300`                                           | Seconds to wait for the initial API connection. |
| `request_timeout`                       | `60`                                            | Seconds to wait for request responses (contract details, etc.). |
| `fetch_all_open_orders`                 | `False`                                         | When `True`, pulls open orders for every API client ID (not just this session). |
| `track_option_exercise_from_position_update` | `False`                                    | Subscribe to real-time position updates to detect option exercises when `True`. |

### Execution client configuration

The `InteractiveBrokersExecutionClient` handles trade execution, order management, account information, and position tracking. It provides order lifecycle management and real-time account updates.

#### Supported functionality

- **Order Management**: Place, modify, and cancel orders
- **Order Types**: Market, limit, stop, stop-limit, trailing stop, and more
- **Account Information**: Real-time balance and margin updates
- **Position Tracking**: Real-time position updates and P&L
- **Trade Reporting**: Execution reports and fill notifications
- **Risk Management**: Pre-trade risk checks and position limits

#### Supported order types

The adapter supports most Interactive Brokers order types:

- **Market Orders**: `OrderType.MARKET`
- **Limit Orders**: `OrderType.LIMIT`
- **Stop Orders**: `OrderType.STOP_MARKET`
- **Stop-Limit Orders**: `OrderType.STOP_LIMIT`
- **Market-If-Touched**: `OrderType.MARKET_IF_TOUCHED`
- **Limit-If-Touched**: `OrderType.LIMIT_IF_TOUCHED`
- **Trailing Stop Market**: `OrderType.TRAILING_STOP_MARKET`
- **Trailing Stop Limit**: `OrderType.TRAILING_STOP_LIMIT`
- **Market-on-Close**: `OrderType.MARKET` with `TimeInForce.AT_THE_CLOSE`
- **Limit-on-Close**: `OrderType.LIMIT` with `TimeInForce.AT_THE_CLOSE`

#### Time in force options

- **Day Orders**: `TimeInForce.DAY`
- **Good-Till-Canceled**: `TimeInForce.GTC`
- **Immediate-or-Cancel**: `TimeInForce.IOC`
- **Fill-or-Kill**: `TimeInForce.FOK`
- **Good-Till-Date**: `TimeInForce.GTD`
- **At-the-Open**: `TimeInForce.AT_THE_OPEN`
- **At-the-Close**: `TimeInForce.AT_THE_CLOSE`

#### Batch operations

| Operation          | Supported | Notes                                        |
|--------------------|-----------|----------------------------------------------|
| Batch Submit       | ✓         | Submit multiple orders in single request.    |
| Batch Modify       | ✓         | Modify multiple orders in single request.    |
| Batch Cancel       | ✓         | Cancel multiple orders in single request.    |

#### Position management

| Feature              | Supported | Notes                                        |
|--------------------|-----------|----------------------------------------------|
| Query positions     | ✓         | Real-time position updates.                  |
| Position mode       | ✓         | Net vs separate long/short positions.       |
| Leverage control    | ✓         | Account-level margin requirements.          |
| Margin mode         | ✓         | Portfolio vs individual margin.             |

#### Order querying

| Feature              | Supported | Notes                                        |
|--------------------|-----------|----------------------------------------------|
| Query open orders   | ✓         | List all active orders.                      |
| Query order history | ✓         | Historical order data.                       |
| Order status updates| ✓         | Real-time order state changes.              |
| Trade history       | ✓         | Execution and fill reports.                 |

#### Contingent orders

| Feature              | Supported | Notes                                        |
|--------------------|-----------|----------------------------------------------|
| Order lists         | ✓         | Atomic multi-order submission.               |
| OCO orders          | ✓         | One-Cancels-Other with customizable OCA types (1, 2, 3). |
| Bracket orders      | ✓         | Parent-child order relationships. |
| Conditional orders  | ✓         | Advanced order conditions and triggers.     |

#### Basic execution client configuration

```python
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersExecutionClientConfig

exec_client_config = InteractiveBrokersExecutionClientConfig(
    host="127.0.0.1",
    port=7497,  # TWS paper trading port
    client_id=1,
    account_id="DU123456",  # Your IB account ID (paper or live)
    instrument_provider=instrument_provider_config,
    connection_timeout=300,
)
```

When registering the client on a `LiveNode`, pass routing through
`LiveNodeBuilder.add_exec_client(..., routing=RoutingConfig(default=True))` to route all orders
through this client.

#### Advanced execution client configuration

```python
# Production configuration
production_exec_config = InteractiveBrokersExecutionClientConfig(
    host="127.0.0.1",
    port=4001,  # IB Gateway live trading port
    client_id=1,
    account_id=None,  # Will use TWS_ACCOUNT environment variable
    instrument_provider=instrument_provider_config,
    connection_timeout=300,
)
```

#### Account ID configuration

The `account_id` parameter is crucial and must match the account logged into TWS/Gateway:

```python
# Option 1: Specify directly in config
exec_config = InteractiveBrokersExecutionClientConfig(
    account_id="DU123456",  # Paper trading account
    # ... other parameters
)

# Option 2: Use environment variable
import os
os.environ["TWS_ACCOUNT"] = "DU123456"
exec_config = InteractiveBrokersExecutionClientConfig(
    account_id=None,  # Will use TWS_ACCOUNT env var
    # ... other parameters
)
```

#### Order params

The execution adapter supports `params["exchange"]` on order submit, order list submit, and
order modification commands. Use it to override the IB contract exchange for routing the current
order while preserving the cached instrument contract:

```python
self.submit_order(order, params={"exchange": "IEX"})
```

Leave `exchange` unset, or set it to an empty string, to use the cached contract exchange.

#### Order tags and advanced features

The adapter supports IB-specific order attributes through order tags. Pass them as a tag prefixed
with `IBOrderTags:` followed by a JSON object. The adapter overlays recognized IB order fields and
supports price, time, margin, execution, volume, and percent-change conditions:

```python
import json

ib_attributes = {
    "allOrNone": True,          # All-or-none order
    "ocaGroup": "MyGroup1",     # One-cancels-all group
    "ocaType": 1,               # Cancel with block
    "activeStartTime": "20240315 09:30:00 EST",  # GTC activation time
    "activeStopTime": "20240315 16:00:00 EST",   # GTC deactivation time
    "goodAfterTime": "20240315 09:35:00 EST",    # Good after time
}
tags = [f"IBOrderTags:{json.dumps(ib_attributes)}"]

# Apply tags to an order
order = order_factory.limit(
    instrument_id=instrument.id,
    order_side=OrderSide.BUY,
    quantity=instrument.make_qty(100),
    price=instrument.make_price(100.0),
    tags=tags,
)
```

#### OCA (one-cancels-all) orders

The adapter provides support for OCA orders through the `ocaGroup` and `ocaType` order attributes
in the `IBOrderTags:` JSON payload.

### Basic OCA configuration

```python
import json

# Create OCA configuration
oca_attributes = {
    "ocaGroup": "MY_OCA_GROUP",
    "ocaType": 1,  # Type 1: Cancel All with Block (recommended)
}
oca_tags = [f"IBOrderTags:{json.dumps(oca_attributes)}"]

# Apply to bracket orders
bracket_order = order_factory.bracket(
    instrument_id=instrument.id,
    order_side=OrderSide.BUY,
    quantity=instrument.make_qty(100),
    tp_price=instrument.make_price(110.0),
    sl_trigger_price=instrument.make_price(90.0),
    tp_tags=oca_tags,  # Must explicitly add OCA tags
    sl_tags=oca_tags,  # Must explicitly add OCA tags
)
```

### Advanced OCA configuration

You can specify different OCA types and behaviors through `ocaType`:

```python
import json

# Create custom OCA configuration
custom_oca_attributes = {
    "ocaGroup": "MY_CUSTOM_GROUP",
    "ocaType": 2,  # Use Type 2: Reduce with Block
}
custom_oca_tags = [f"IBOrderTags:{json.dumps(custom_oca_attributes)}"]

# Apply to individual orders
order = order_factory.limit(
    instrument_id=instrument.id,
    order_side=OrderSide.BUY,
    quantity=instrument.make_qty(100),
    price=instrument.make_price(100.0),
    tags=custom_oca_tags,
)
```

### OCA types

Interactive Brokers supports three OCA types:

| Type | Name | Behavior | Use Case |
|------|------|----------|----------|
| **1** | Cancel All with Block | Cancel all remaining orders with block protection | **Default** - Safest option, prevents overfills |
| **2** | Reduce with Block | Proportionally reduce remaining orders with block protection | Partial fills with overfill protection |
| **3** | Reduce without Block | Proportionally reduce remaining orders without block protection | Fastest execution, higher overfill risk |

#### Multiple orders in same OCA group

```python
import json

# Create multiple orders with the same OCA group
oca_attributes = {
    "ocaGroup": "MULTI_ORDER_GROUP",
    "ocaType": 3,  # Use Type 3: Reduce without Block
}
oca_tags = [f"IBOrderTags:{json.dumps(oca_attributes)}"]

order1 = order_factory.limit(
    instrument_id=instrument.id,
    order_side=OrderSide.BUY,
    quantity=instrument.make_qty(50),
    price=instrument.make_price(99.0),
    tags=oca_tags,
)

order2 = order_factory.limit(
    instrument_id=instrument.id,
    order_side=OrderSide.BUY,
    quantity=instrument.make_qty(50),
    price=instrument.make_price(101.0),
    tags=oca_tags,
)
```

### OCA configuration requirements

OCA functionality is **only** available through explicit configuration through the `IBOrderTags:`
JSON payload: OCA settings must be explicitly specified in order tags.

### Conditional orders

The adapter supports Interactive Brokers conditional orders through the `conditions` list in the
`IBOrderTags:` JSON payload. Conditional orders allow you to specify criteria that must be met
before an order is transmitted or cancelled.

#### Supported condition types

- **Price Conditions**: Trigger based on price levels
- **Time Conditions**: Trigger based on specific times
- **Volume Conditions**: Trigger based on traded volume
- **Execution Conditions**: Trigger based on trades of a specific instrument
- **Margin Conditions**: Trigger based on account margin levels
- **Percent Change Conditions**: Trigger based on percentage price changes

#### Basic conditional order example

```python
import json

# Create a price condition: trigger when SPY goes above $250
price_condition = {
    "type": "price",
    "conId": 265598,  # SPY contract ID
    "exchange": "SMART",
    "isMore": True,  # Trigger when price is greater than threshold
    "price": 250.00,
    "triggerMethod": 0,  # Default trigger method
    "conjunction": "and",
}

# Create order tags with condition
ib_attributes = {
    "conditions": [price_condition],
    "conditionsCancelOrder": False,  # Transmit order when condition is met
}
order_tags = [f"IBOrderTags:{json.dumps(ib_attributes)}"]

# Apply to order
order = order_factory.limit(
    instrument_id=instrument.id,
    order_side=OrderSide.BUY,
    quantity=instrument.make_qty(100),
    price=instrument.make_price(251.00),
    tags=order_tags,
)
```

#### Multiple conditions with logic

```python
# Create multiple conditions with AND/OR logic
conditions = [
    {
        "type": "price",
        "conId": 265598,
        "exchange": "SMART",
        "isMore": True,
        "price": 250.00,
        "triggerMethod": 0,
        "conjunction": "and",  # AND with next condition
    },
    {
        "type": "time",
        "time": "20250315-09:30:00",
        "isMore": True,
        "conjunction": "or",  # OR with next condition
    },
    {
        "type": "volume",
        "conId": 265598,
        "exchange": "SMART",
        "isMore": True,
        "volume": 10000000,
        "conjunction": "and",
    },
]

ib_attributes = {
    "conditions": conditions,
    "conditionsCancelOrder": False,
}
order_tags = [f"IBOrderTags:{json.dumps(ib_attributes)}"]
```

#### Condition parameters

**Price Condition:**

- `conId`: Contract ID of the instrument to monitor
- `exchange`: Exchange to monitor (e.g., "SMART", "NASDAQ")
- `isMore`: True for >=, False for <=
- `price`: Price threshold
- `triggerMethod`: Trigger method for price conditions
- `conjunction`: Logical connection to the next condition ("and"/"or")

**Time Condition:**

- `time`: Time string in UTC format "YYYYMMDD-HH:MM:SS" (e.g., "20250315-09:30:00")
- `isMore`: True for after time, False for before time

**Volume Condition:**

- `conId`: Contract ID of the instrument to monitor
- `exchange`: Exchange to monitor
- `isMore`: True for >=, False for <=
- `volume`: Volume threshold

**Execution Condition:**

- `symbol`: Symbol to monitor for trades
- `secType`: Security type (e.g., "STK", "OPT", "FUT")
- `exchange`: Exchange to monitor

**Margin Condition:**

- `percent`: Margin cushion percentage threshold
- `isMore`: True for >=, False for <=

**Percent Change Condition:**

- `conId`: Contract ID of the instrument to monitor
- `exchange`: Exchange to monitor
- `isMore`: True for >=, False for <=
- `changePercent`: Percentage change threshold

### Complete trading node configuration

Setting up a complete trading environment involves wiring the IB data and execution clients into a `LiveNode` (the shared pattern is documented in [index.md](index.md#live-node-wiring)). These examples mirror the upstream `examples/live/interactive_brokers` scripts at the pinned revision.

#### Paper trading configuration

```python
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientFactory
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersExecutionClientConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersExecutionClientFactory
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.adapters.interactive_brokers import MarketDataType
from nautilus_trader.adapters.interactive_brokers import SymbologyMethod
from nautilus_trader.common import Environment
from nautilus_trader.live import LiveNode
from nautilus_trader.model import TraderId

# Instrument provider configuration
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    symbology_method=SymbologyMethod.SIMPLIFIED,
    load_ids=frozenset([
        "EUR/USD.IDEALPRO",
        "GBP/USD.IDEALPRO",
        "SPY.ARCA",
        "QQQ.NASDAQ",
        "AAPL.NASDAQ",
        "MSFT.NASDAQ",
    ]),
)

# Data client configuration
data_client_config = InteractiveBrokersDataClientConfig(
    host="127.0.0.1",
    port=7497,  # TWS paper trading
    client_id=1,
    use_regular_trading_hours=True,
    market_data_type=MarketDataType.DELAYED_FROZEN,
    instrument_provider=instrument_provider_config,
)

# Execution client configuration
exec_client_config = InteractiveBrokersExecutionClientConfig(
    host="127.0.0.1",
    port=7497,  # TWS paper trading
    client_id=1,
    account_id="DU123456",  # Your paper trading account
    instrument_provider=instrument_provider_config,
)

# Create and configure the trading node
trader_id = TraderId("PAPER-TRADER-001")

node = (
    LiveNode.builder("PAPER-TRADER-001", trader_id, Environment.LIVE)
    .with_timeout_connection(90)
    .with_timeout_reconciliation(5)
    .with_timeout_portfolio(5)
    .with_timeout_disconnection_secs(5)
    .with_delay_post_stop_secs(2)
    .add_data_client(None, InteractiveBrokersDataClientFactory(), data_client_config)
    .add_exec_client(None, InteractiveBrokersExecutionClientFactory(), exec_client_config)
    .build()
)

if __name__ == "__main__":
    try:
        node.run()
    finally:
        node.dispose()
```

For IB-standard bar-open timestamps and sequence validation, build the node from a `LiveNodeConfig` (`LiveNode.build`) with `data_engine=LiveDataEngineConfig(time_bars_timestamp_on_close=False, validate_data_sequence=True)`; both options remain on the pinned `LiveDataEngineConfig`.

## Live trading with Dockerized gateway

```python
import os

from nautilus_trader.adapters.interactive_brokers import DockerizedIBGatewayConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientFactory
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersExecutionClientConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersExecutionClientFactory
from nautilus_trader.adapters.interactive_brokers import MarketDataType
from nautilus_trader.adapters.interactive_brokers import TradingMode
from nautilus_trader.common import Environment
from nautilus_trader.live import LiveNode
from nautilus_trader.model import TraderId

# Dockerized gateway configuration
dockerized_gateway_config = DockerizedIBGatewayConfig(
    username=os.environ.get("TWS_USERNAME"),
    password=os.environ.get("TWS_PASSWORD"),
    trading_mode=TradingMode.LIVE,  # TradingMode.PAPER or TradingMode.LIVE
    read_only_api=False,  # Allow order execution
    timeout=300,
)

# Data client with dockerized gateway
data_client_config = InteractiveBrokersDataClientConfig(
    client_id=1,
    use_regular_trading_hours=False,  # Include extended hours
    market_data_type=MarketDataType.REALTIME,
    instrument_provider=instrument_provider_config,
    dockerized_gateway=dockerized_gateway_config,
)

# Execution client with dockerized gateway
exec_client_config = InteractiveBrokersExecutionClientConfig(
    client_id=1,
    account_id=os.environ.get("TWS_ACCOUNT"),  # Live account ID
    instrument_provider=instrument_provider_config,
    dockerized_gateway=dockerized_gateway_config,
)

# Live trading node
trader_id = TraderId("LIVE-TRADER-001")

node = (
    LiveNode.builder("LIVE-TRADER-001", trader_id, Environment.LIVE)
    .add_data_client(None, InteractiveBrokersDataClientFactory(), data_client_config)
    .add_exec_client(None, InteractiveBrokersExecutionClientFactory(), exec_client_config)
    .build()
)
```

### Multi-client configuration

For advanced setups, you can configure multiple clients with different purposes:

```python
# Separate data and execution clients with different client IDs
data_client_config = InteractiveBrokersDataClientConfig(
    host="127.0.0.1",
    port=7497,
    client_id=1,  # Data client uses ID 1
    market_data_type=MarketDataType.REALTIME,
    instrument_provider=instrument_provider_config,
)

exec_client_config = InteractiveBrokersExecutionClientConfig(
    host="127.0.0.1",
    port=7497,
    client_id=2,  # Execution client uses ID 2
    account_id="DU123456",
    instrument_provider=instrument_provider_config,
    routing=RoutingConfig(default=True),
)
```

`RoutingConfig` is exported flat from `nautilus_trader.live` and is accepted as the optional `routing` argument of `add_data_client`/`add_exec_client`.

### Multiple IB execution clients for different accounts

NautilusTrader supports using multiple Interactive Brokers execution clients simultaneously, each connected to a different IB account. This is useful when you need to trade with multiple accounts, such as:

- Separate accounts for different strategies
- Paper trading and live trading accounts running simultaneously
- Multiple managed accounts under the same IB login

To configure multiple IB execution clients, register one execution client per account with `add_exec_client`, each under a unique client name. Each config specifies a different `account_id`:

```python
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersDataClientFactory
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersExecutionClientConfig
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersExecutionClientFactory
from nautilus_trader.adapters.interactive_brokers import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.adapters.interactive_brokers import MarketDataType
from nautilus_trader.adapters.interactive_brokers import SymbologyMethod
from nautilus_trader.common import Environment
from nautilus_trader.live import LiveNode
from nautilus_trader.live import RoutingConfig
from nautilus_trader.model import TraderId

# Shared instrument provider configuration
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    symbology_method=SymbologyMethod.SIMPLIFIED,
)

# Data client (shared across all accounts)
data_client_config = InteractiveBrokersDataClientConfig(
    host="127.0.0.1",
    port=7497,
    client_id=1,
    market_data_type=MarketDataType.REALTIME,
    instrument_provider=instrument_provider_config,
)

trader_id = TraderId("MULTI-ACCOUNT-001")

node = LiveNode.builder("MULTI-ACCOUNT-001", trader_id, Environment.LIVE)

# Single data client shared across accounts
node = node.add_data_client(
    None,
    InteractiveBrokersDataClientFactory(),
    data_client_config,
)

# Multiple execution clients, one per account
node = node.add_exec_client(
    "IB-PAPER",  # First account: Paper trading account
    InteractiveBrokersExecutionClientFactory(),
    InteractiveBrokersExecutionClientConfig(
        host="127.0.0.1",
        port=7497,
        client_id=2,  # Unique IB API client ID
        account_id="DU123456",  # Paper trading account ID
        instrument_provider=instrument_provider_config,
        routing=RoutingConfig(default=False),  # Not default
    ),
)

node = node.add_exec_client(
    "IB-LIVE",  # Second account: Live trading account
    InteractiveBrokersExecutionClientFactory(),
    InteractiveBrokersExecutionClientConfig(
        host="127.0.0.1",
        port=7497,
        client_id=3,  # Unique IB API client ID
        account_id="U987654",  # Live account ID
        instrument_provider=instrument_provider_config,
        routing=RoutingConfig(default=True),  # Set as default
    ),
)

node = node.add_exec_client(
    "IB-ACCOUNT3",  # Third account: Another managed account
    InteractiveBrokersExecutionClientFactory(),
    InteractiveBrokersExecutionClientConfig(
        host="127.0.0.1",
        port=7497,
        client_id=4,  # Unique IB API client ID
        account_id="U456789",  # Another account ID
        instrument_provider=instrument_provider_config,
        routing=RoutingConfig(default=False),
    ),
)

node = node.build()
```

**Key points for multiple IB execution clients:**

1. **Unique client names**: Register each execution client under a unique client name passed to `add_exec_client` (e.g., `"IB-PAPER"`, `"IB-LIVE"`). This name becomes the `account_issuer` for that client.

2. **Unique client IDs**: Each execution client must use a different `client_id` (2, 3, 4, etc.). IB Gateway/TWS requires each API connection to use a unique client ID.

3. **Account ID**: Each execution client must specify a different `account_id` matching the account logged into IB Gateway/TWS.

4. **Account identifiers**: The system creates `AccountId` instances like:
   - `AccountId("IB-PAPER-DU123456")`
   - `AccountId("IB-LIVE-U987654")`
   - `AccountId("IB-ACCOUNT3-U456789")`

5. **Routing**: Orders and queries are automatically routed to the correct execution client based on:
   - Explicit `client_id` in the command
   - `account_id` issuer (for `QueryAccount` commands or orders with account_id set)
   - Default client (the one `add_exec_client` call that passes `routing=RoutingConfig(default=True)`)

6. **Portfolio queries**: When querying portfolio properties, you can specify either:
   - `account_id` for account-specific queries: `portfolio.realized_pnls(account_id=AccountId("IB-PAPER-DU123456"))`
   - `venue` for aggregated queries across all accounts with that venue: `portfolio.realized_pnls(venue=Venue("IB-PAPER"))`

**Example: Using multiple IB execution clients in a strategy:**

```python
from nautilus_trader.model import AccountId, ClientId
from nautilus_trader.trading import Strategy

class MultiAccountStrategy(Strategy):
    """Example strategy using multiple IB accounts."""

    def on_start(self):
        # Define account IDs for easy reference
        self.paper_account = AccountId("IB-PAPER-DU123456")
        self.live_account = AccountId("IB-LIVE-U987654")

        # Query paper account balance
        paper_account_state = self.cache.account(self.paper_account)
        if paper_account_state:
            self.log.info(f"Paper account balance: {paper_account_state.balance_total()}")

        # Query live account balance
        live_account_state = self.cache.account(self.live_account)
        if live_account_state:
            self.log.info(f"Live account balance: {live_account_state.balance_total()}")

    def submit_order_to_paper(self, order):
        """Submit order to paper trading account."""
        self.submit_order(order, client_id=ClientId("IB-PAPER"))

    def submit_order_to_live(self, order):
        """Submit order to live trading account."""
        self.submit_order(order, client_id=ClientId("IB-LIVE"))

    def check_paper_pnl(self, instrument_id):
        """Check realized PnL for paper account."""
        pnl = self.portfolio.realized_pnl(
            instrument_id=instrument_id,
            account_id=self.paper_account
        )
        return pnl

    def check_live_pnl(self, instrument_id):
        """Check realized PnL for live account."""
        pnl = self.portfolio.realized_pnl(
            instrument_id=instrument_id,
            account_id=self.live_account
        )
        return pnl
```

**Example: Querying account information with multiple IB clients:**

```python
from nautilus_trader.model import AccountId, Venue

# Query specific account
paper_account = cache.account(AccountId("IB-PAPER-DU123456"))
live_account = cache.account(AccountId("IB-LIVE-U987654"))

# Query account using account_id (preferred method)
paper_account_by_id = cache.account(AccountId("IB-PAPER-DU123456"))

# Alternative: Query account using account_id parameter (also works)
paper_account_via_account_id = cache.account_for_venue(
    account_id=AccountId("IB-PAPER-DU123456")
)

# Query portfolio properties by account
paper_realized_pnl = portfolio.realized_pnl(
    instrument_id=instrument_id,
    account_id=AccountId("IB-PAPER-DU123456")
)

# Query portfolio properties aggregated across all IB accounts
# Note: This aggregates across all accounts with the same venue
all_ib_realized_pnl = portfolio.realized_pnls(venue=Venue("IB"))
```

### Running the trading node

```python
def run_trading_node():
    """Run the trading node with proper error handling."""
    node = None
    try:
        # Build the node with one of the configurations above
        node = build_node()

        # Add your strategies here
        # node.add_strategy(YourStrategy())

        # Run the node
        node.run()

    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if node:
            node.dispose()

if __name__ == "__main__":
    run_trading_node()
```

### Additional configuration options

#### Environment variables

Set these environment variables for easier configuration:

```bash
export TWS_USERNAME="your_ib_username"
export TWS_PASSWORD="your_ib_password"
export TWS_ACCOUNT="your_account_id"
export IB_MAX_CONNECTION_ATTEMPTS="5"  # Optional: limit reconnection attempts
```

#### Logging configuration

```python
from nautilus_trader.common import LogLevel, LoggerConfig

# Enhanced logging configuration (pass as `logging` to a LiveNodeConfig)
logging_config = LoggerConfig(
    stdout_level=LogLevel.INFO,
    component_levels={
        "InteractiveBrokersClient": "DEBUG",
        "InteractiveBrokersDataClient": "INFO",
        "InteractiveBrokersExecutionClient": "INFO",
    },
)
```

You can find additional examples here: <https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/interactive_brokers>

## Troubleshooting

### Common connection issues

#### Connection refused

- **Cause**: TWS/Gateway not running or wrong port
- **Solution**: Verify TWS/Gateway is running and check port configuration
- **Default Ports**: TWS (7497/7496), IB Gateway (4002/4001)

#### Authentication errors

- **Cause**: Incorrect credentials or account not logged in
- **Solution**: Verify username/password and ensure account is logged into TWS/Gateway

#### Client ID conflicts

- **Cause**: Multiple clients using the same client ID
- **Solution**: Use unique client IDs for each connection

#### Market data permissions

- **Cause**: Insufficient market data subscriptions
- **Solution**: Use `MarketDataType.DELAYED_FROZEN` for testing or subscribe to required data feeds

### Error codes

Interactive Brokers uses specific error codes. Common ones include:

- **200**: No security definition found
- **201**: Order rejected - reason follows
- **202**: Order cancelled
- **300**: Can't find EId with ticker ID
- **354**: Requested market data is not subscribed
- **2104**: Market data farm connection is OK
- **2106**: HMDS data farm connection is OK

### Performance optimization

#### Reduce data volume

```python
# Reduce quote tick volume by ignoring size-only updates
data_config = InteractiveBrokersDataClientConfig(
    ignore_quote_tick_size_updates=True,
    # ... other config
)
```

#### Connection management

```python
# Set reasonable timeouts
config = InteractiveBrokersDataClientConfig(
    connection_timeout=300,  # 5 minutes
    request_timeout_secs=60,      # 1 minute
    # ... other config
)
```

#### Memory management

- Use appropriate bar sizes for your strategy
- Limit the number of simultaneous subscriptions
- Consider using historical data for backtesting instead of live data

### Best practices

#### Security

- Never hardcode credentials in source code
- Use environment variables for sensitive information
- Use paper trading for development and testing
- Set `read_only_api=True` for data-only applications

#### Development workflow

1. **Start with Paper Trading**: Always test with paper trading first
2. **Use Delayed Data**: Use `DELAYED_FROZEN` market data for development
3. **Implement Proper Error Handling**: Handle connection losses and API errors gracefully
4. **Monitor Logs**: Enable appropriate logging levels for debugging
5. **Test Reconnection**: Test your strategy's behavior during connection interruptions

#### Production deployment

- Use dockerized gateway for automated deployments
- Implement proper monitoring and alerting
- Set up log aggregation and analysis
- Use real-time data subscriptions only when necessary
- Implement circuit breakers and position limits

#### Order management

- Always validate orders before submission
- Implement proper position sizing
- Use appropriate order types for your strategy
- Monitor order status and handle rejections
- Implement timeout handling for order operations

### Debugging tips

#### Enable debug logging

```python
from nautilus_trader.common import LogLevel, LoggerConfig

logging_config = LoggerConfig(
    stdout_level=LogLevel.DEBUG,
    component_levels={
        "InteractiveBrokersClient": "DEBUG",
    },
)
```

#### Monitor connection status

```python
# Check connection status in your strategy
if not self.data_client.is_connected:
    self.log.warning("Data client disconnected")
```

#### Validate instruments

```python
# Ensure instruments are loaded before trading
instruments = self.cache.instruments()
if not instruments:
    self.log.error("No instruments loaded")
```

### Support and resources

- **IB API Documentation**: [TWS API Guide](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/)
- **NautilusTrader Examples**: [GitHub Examples](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/interactive_brokers)
- **IB Contract Search**: [Contract Information Center](https://pennies.interactivebrokers.com/cstools/contract_info/)
- **Market Data Subscriptions**: [IB Market Data](https://www.interactivebrokers.com/en/pricing/market-data-pricing.php)

## Contributing

:::info
For additional features or to contribute to the Interactive Brokers adapter, please see our
[contributing guide](https://github.com/nautechsystems/nautilus_trader/blob/develop/CONTRIBUTING.md).
:::