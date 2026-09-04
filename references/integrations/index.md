# Integrations

NautilusTrader uses modular *adapters* to connect to trading venues and data providers, translating raw APIs into a unified interface and normalized domain model.

The following integrations are currently supported:

| Name                                                                         | ID                    | Type                    | Status                                                  | Docs                     |
| :--------------------------------------------------------------------------- | :-------------------- | :---------------------- | :------------------------------------------------------ | :----------------------- |
| [AX Exchange](https://architect.exchange)                                    | `AX`                  | Perpetuals Exchange     | ![status](https://img.shields.io/badge/stable-green)    | [Guide](architect_ax.md) |
| [Betfair](https://betfair.com)                                               | `BETFAIR`             | Sports Betting Exchange | ![status](https://img.shields.io/badge/stable-green)    | [Guide](betfair_v2.md) · [legacy](betfair.md)|
| [Binance](https://binance.com)                                               | `BINANCE`             | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](binance.md)      |
| [Coinbase](https://coinbase.com)                                             | `COINBASE`            | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)   | [Guide](coinbase.md)     |
| [BitMEX](https://www.bitmex.com)                                             | `BITMEX`              | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](bitmex.md)       |
| [Blockchain](blockchain.md)                                                 | `BLOCKCHAIN`          | DeFi Data Provider      | ![status](https://img.shields.io/badge/stable-green)    | [Guide](blockchain.md)   |
| [Bybit](https://www.bybit.com)                                               | `BYBIT`               | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](bybit.md)        |
| [Databento](https://databento.com)                                           | `DATABENTO`           | Data Provider           | ![status](https://img.shields.io/badge/stable-green)    | [Guide](databento.md)    |
| [Deribit](https://www.deribit.com)                                           | `DERIBIT`             | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](deribit.md)      |
| [Derive](https://www.derive.xyz/)                                             | `DERIVE`              | Crypto Exchange (DEX)   | ![status](https://img.shields.io/badge/beta-yellow)     | [Guide](derive.md)      |
| [dYdX](https://dydx.exchange/)                                               | `DYDX`                | Crypto Exchange (DEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](dydx.md)         |
| [Hyperliquid](https://hyperliquid.xyz)                                       | `HYPERLIQUID`         | Crypto Exchange (DEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](hyperliquid.md)  |
| [Interactive Brokers](https://www.interactivebrokers.com)                    | `INTERACTIVE_BROKERS` | Brokerage (multi-venue) | ![status](https://img.shields.io/badge/stable-green)    | [Guide](ib.md)           |
| [Kraken](https://kraken.com)                                                 | `KRAKEN`              | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](kraken.md)       |
| [Lighter](https://lighter.xyz)                                             | `LIGHTER`             | Crypto Exchange (DEX)   | ![status](https://img.shields.io/badge/beta-yellow)     | [Guide](lighter.md)     |
| [Lighter on Robinhood](https://robinhoodchain.lighter.xyz)                  | `LIGHTER_ROBINHOOD`   | Crypto Exchange (DEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](lighter.md)     |
| [OKX](https://okx.com)                                                       | `OKX`                 | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](okx.md)          |
| [Polymarket](https://polymarket.com)                                         | `POLYMARKET`          | Prediction Market (DEX) | ![status](https://img.shields.io/badge/stable-green)    | [Guide](polymarket.md)   |
| [Tardis](https://tardis.dev)                                                 | `TARDIS`              | Crypto Data Provider    | ![status](https://img.shields.io/badge/stable-green)    | [Guide](tardis.md)       |

- **ID**: The default client ID for the integrations adapter clients.
- **Type**: The type of integration (often the venue type).

## Live node wiring

Every Rust-backed integration page below registers its adapter clients through the shared
`LiveNode.builder(...)` API (the current v2 wiring). NT v2 compatibility note: legacy Python
`TradingNode` snippets, where retained anywhere, are migration context only. The pattern,
shown with the Derive adapter (see [derive.md](derive.md) for the full example):

```python
from decimal import Decimal

from nautilus_trader.adapters.derive import DeriveDataClientConfig
from nautilus_trader.adapters.derive import DeriveDataClientFactory
from nautilus_trader.adapters.derive import DeriveEnvironment
from nautilus_trader.adapters.derive import DeriveExecutionClientConfig
from nautilus_trader.adapters.derive import DeriveExecutionClientFactory
from nautilus_trader.common import Environment
from nautilus_trader.live import LiveNode
from nautilus_trader.model import AccountId
from nautilus_trader.model import TraderId

trader_id = TraderId("TESTER-001")

data_config = DeriveDataClientConfig(
    environment=DeriveEnvironment.TESTNET,
    currencies=["ETH", "BTC"],
)

exec_config = DeriveExecutionClientConfig(
    account_id=AccountId("DERIVE-001"),
    environment=DeriveEnvironment.TESTNET,
    max_fee_per_contract=Decimal("1000"),
)

node = (
    LiveNode.builder("DERIVE-001", trader_id, Environment.LIVE)
    .add_data_client(None, DeriveDataClientFactory(), data_config)
    .add_exec_client(None, DeriveExecutionClientFactory(), exec_config)
    .build()
)
```

Swap in each venue's flat `nautilus_trader.adapters.<venue>` exports: the pinned adapter package
exposes `{Venue}DataClientConfig`/`{Venue}ExecutionClientConfig` and
`{Venue}DataClientFactory`/`{Venue}ExecutionClientFactory`. Pass the config directly to
`add_data_client`/`add_exec_client`; pass `None` as the client name to use the adapter default.

## Status

- `planned`: Planned for future development.
- `building`: Under construction and likely not in a usable state.
- `beta`: Completed to a minimally working state and in a 'beta' testing phase.
- `stable`: Stabilized feature set and API, the integration has been tested by both developers and users to a reasonable level (some bugs may still remain).

## Implementation goals

The primary goal of NautilusTrader is to provide a unified trading system for
use with a variety of integrations. To support the widest range of trading
strategies, priority will be given to *standard* functionality:

- Requesting historical market data.
- Streaming live market data.
- Reconciling execution state.
- Submitting standard order types with standard execution instructions.
- Modifying existing orders (if possible on an exchange).
- Canceling orders.

The implementation of each integration aims to meet the following criteria:

- Low-level client components should match the exchange API as closely as possible.
- The full range of an exchange's functionality (where applicable to NautilusTrader) should *eventually* be supported.
- Exchange specific data types will be added to support the functionality and return types which are reasonably expected by a user.
- Actions unsupported by an exchange or NautilusTrader will be logged as a warning or error when invoked.

## API unification

All integrations must conform to NautilusTrader’s system API, requiring normalization and standardization:

- Symbols should use the venue’s native symbol format unless disambiguation is required (e.g., Binance Spot vs. Binance Futures).
- Timestamps must use UNIX epoch nanoseconds. If milliseconds are used, field/property names should explicitly end with `_ms`.
