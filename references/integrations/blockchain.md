# Blockchain

## Reviewed current-develop overlay (2026-10-14)

Source: upstream `52eef7955cbdb8d95667c838c3e43907e0da8e9a`,
`docs/integrations/blockchain.md:107-131,301-330,748-773,774-837,1052-1067,1164-1209`.
The reviewed sections below supersede conflicting historical guidance at this pin.

### DEX and pools

DEX integrations register:

- Factory addresses.
- Event signatures and parser functions.
- AMM type.

Pool definitions bind the chain and DEX to a pool contract address or protocol pool ID to form a
stable Nautilus instrument ID. The token pair, fee tier, tick spacing, and creation block remain
pool metadata.

When the data engine processes a pool definition, it caches and publishes a `CurrencyPair` under the same pool
instrument ID. The instrument takes its base and quote from `Pool::get_base_token` and
`Pool::get_quote_token`. Swap trade info and execution use this same token-priority orientation. The
instrument derives price and size precision from token decimals up to `FIXED_PRECISION`. Distinct pool
identifiers let same-token pools coexist in the cache and on the message bus.

Uniswap V3 and compatible concentrated-liquidity pools also use:

- `Initialize(uint160,int24)` for initial price state.
- `Mint` and `Burn` events for position and tick state replay.
- `Swap` events for live pool price movement.
- HTTP RPC final-state reads for `slot0`, liquidity, active ticks, and position data.


### Data-client surface

The public data client supports these DeFi subscriptions and requests:

| Surface           | Commands                                                           | Behavior                                                                                           |
| ----------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Blocks            | `SubscribeBlocks`, `UnsubscribeBlocks`                             | Starts or stops the shared HyperSync or WSS RPC block feed.                                        |
| Complete pool     | `SubscribePool`, `UnsubscribePool`                                 | Selects swaps, mints, burns, collects, flashes, and both fee-protocol event types.                 |
| Pool swaps        | `SubscribePoolSwaps`, `UnsubscribePoolSwaps`                       | Selects swap events for one pool instrument.                                                       |
| Liquidity updates | `SubscribePoolLiquidityUpdates`, `UnsubscribePoolLiquidityUpdates` | Selects mint and burn events for one pool instrument.                                              |
| Fee collections   | `SubscribePoolFeeCollects`, `UnsubscribePoolFeeCollects`           | Selects collect events for one pool instrument.                                                    |
| Flash events      | `SubscribePoolFlashEvents`, `UnsubscribePoolFlashEvents`           | Selects flash events for one pool instrument.                                                      |
| Pool snapshot     | `RequestPoolSnapshot`                                              | Publishes the pool definition, then a usable snapshot when cache bootstrap and validation succeed. |

Subscriptions share the underlying block and DEX event feeds. The client counts owners for each
pool address and event type, so removing one subscription does not stop a feed that another
subscription still owns. This holds when a complete pool subscription overlaps a narrower one: the
narrower event types stay active after `UnsubscribePool`, and the reverse. The data engine keeps a
pool's profiler updater until no data client has a remaining pool subscription for it.

A pool snapshot response carries the ID of its request. The data engine discards a response whose
bootstrap was canceled by a final unsubscribe, a reset, or a disconnect. Pool snapshot requests
require Postgres because bootstrap reads stored pool and event state through the cache database.

:::warning
DeFi pool definitions and account-state updates publish on typed message-bus routers. A
`subscribe_any` handler never receives them. Use `subscribe_defi_pools` and
`subscribe_account_state`, or the matching actor subscription APIs.
:::


refused. A verification, migration, reconciliation, balance, or exact amount conversion failure
keeps the client disconnected. Any loaded signer is removed, the previous complete snapshot stays
installed, and no partial wallet state is published. Duplicate token symbols also reject the
snapshot because symbols define currency identity.

The verification providers never receive signed transaction bytes and have no broadcast method.
The authoritative endpoint alone receives `eth_sendRawTransaction`. Security-critical unsigned
reads that authorize a signature, rebroadcast, or durable transition go to all three sources.
Diagnostic preflight and connect-time balance publication use the authoritative endpoint and cannot
authorize execution. This protects integrity, not order confidentiality. Operators who need route
or amount confidentiality need a separate execution design.

Published balances use `total = free` and `locked = 0`. The wallet account applies local
reservations when it derives effective free and locked balances, as described in
[Wallet accounts](https://github.com/nautechsystems/nautilus_trader/blob/52eef7955cbdb8d95667c838c3e43907e0da8e9a/docs/concepts/accounting.md#wallet-accounts).

After the client starts, `QueryAccount` republishes the installed snapshot without another RPC
read. It fails when:

- The requested account ID differs from the client account ID.
- The client has not started.
- No complete snapshot exists.

Disconnect removes the signer and aborts in-flight submission tasks. Transaction operations reject
a disconnected client before any execution RPC call.


### Supported order slice

The client accepts one market-order shape:

| Axis        | Accepted                                                                                        | Rejected                                                              |
| ----------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Chain       | The chain configured on the execution client.                                                   | An instrument venue for another chain.                                |
| DEX         | Uniswap V3.                                                                                     | Every other DEX, including PancakeSwap V3.                            |
| Pool        | An address-based pool in `Cache::pool` with a fee tier.                                         | Unknown pools, V4 pool IDs, and pools without a fee tier.             |
| Order       | A single `MarketOrder` with side `BUY` or `SELL`.                                               | Non-market orders submitted through `SubmitOrder`.                    |
| Quantity    | Base-denominated size within `max_order_amount`; a BUY also needs a matching quote-spend limit. | Quote-denominated input or an amount above either applicable ceiling. |
| Orientation | Tokens with distinct model priorities.                                                          | A pair whose tokens have equal priority and are ambiguous.            |

The `InstrumentId` selects the pool, for example
`0xC6962004f452bE9203591991D15f6b388e09E8D0.Arbitrum:UniswapV3`. Its venue must parse as `<Chain>:<DexType>`,
and its symbol must parse as an address `PoolIdentifier`. `Pool::get_base_token` and `Pool::get_quote_token`
apply the model's token-priority convention:

- Stablecoins are quote assets.
- Wrapped native assets have the next priority.
- Other tokens become base assets against them.

Equal `Token::get_token_priority` values are ambiguous and reject the order.

Venue routing admits Uniswap V3 on any configured chain whose venue matches. Swap preparation also
requires a registered Uniswap V3 deployment and factory for that chain.

Order lists deny each open order with `OrderDenied`. Modify, cancel, and batch-cancel commands reject each
referenced cached order with `OrderModifyRejected` or `OrderCancelRejected`. Cancel-all commands and order
queries log a warning without an event. Mass status returns `Ok(None)` so startup reconciliation logs and
continues. Order, fill, and position report probes return an error so LiveNode does not treat an empty answer
as absence. These paths never sign, broadcast, or persist an intent.

A swap stays `Submitted` until finality, and venue status queries cannot resolve it. The client requires
submission retention. When the in-flight check exhausts its retries, LiveNode logs a warning and keeps the
swap `Submitted` instead of rejecting it. Thus, the finalized fill or rejection still applies to that order.
If the node stops before finality, shutdown reports incomplete submission recovery for each swap submitted
during that run, and the persisted intent reconciles on the next connect. Leave open-order checks off.

Execution routing follows Nautilus's multi-venue broker pattern. The client represents a wallet and RPC
connection for one chain. Each instrument venue identifies both its chain and DEX.

A strategy may select the client explicitly through `client_id`. Node configuration may instead register the
client for instrument venues through `RoutingConfig.venues` or use it as the default execution client. After
client selection, `ExecutionClient::handles_order_venue` accepts only a venue whose parsed chain matches the
client configuration and whose DEX is supported by the client. The instrument retains its `<Chain>:<DexType>`
venue rather than being rewritten to `BLOCKCHAIN`.

The order maps to a single `exactInputSingle` call on the original Uniswap SwapRouter (the
deployment whose signature carries a deadline). `allowed_token_pairs` is directional
`(token_in, token_out)`: a SELL requires the base-to-quote pair, and a BUY requires the
quote-to-base pair. Listing only one direction does not admit the other.

| Parameter           | Source                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------ |
| `tokenIn`           | SELL: pool base token. BUY: pool quote token.                                              |
| `tokenOut`          | SELL: pool quote token. BUY: pool base token.                                              |
| `fee`               | Pool fee tier.                                                                             |
| `recipient`         | Execution wallet address.                                                                  |
| `deadline`          | Verified decision-header timestamp plus configured `deadline_seconds`.                     |
| `amountIn`          | SELL: `Quantity` as raw base units. BUY: quote input from the verified exact-output quote. |
| `amountOutMinimum`  | Derived from the verified quote at the decision height (see below).                        |
| `sqrtPriceLimitX96` | `0` (slippage is bounded by `amountOutMinimum`).                                           |


### Order events

Order submission emits only events justified by known transaction state:

| Observation                                                | Event             | Result                                                                                                                                                                                                                           |
| ---------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Failure before the persisted broadcast transition.         | `OrderDenied`     | No transaction left the client.                                                                                                                                                                                                  |
| Persisted broadcast attempt, including an ambiguous reply. | `OrderSubmitted`  | The signed intent remains the observation authority.                                                                                                                                                                             |
| Verified finalized revert.                                 | `OrderRejected`   | The stable event ID and terminal marker permit signer release.                                                                                                                                                                   |
| Finalized transaction, trace, or deployment mismatch.      | No terminal event | The client refuses to derive a fill and keeps signer ownership quarantined.                                                                                                                                                      |
| Verified finalized success with exact transaction and log. | `OrderFilled`     | Wallet refresh and marker persistence then complete the intent. A BUY that executes below the order quantity also emits `OrderCanceled` for the remainder. A BUY that executes above the order quantity reports the full output. |
| Timeout, disagreement, unavailable read, or reorg.         | No terminal event | The order stays submitted and signer ownership remains occupied.                                                                                                                                                                 |

A successful receipt at first inclusion does not emit a fill. The client waits for the stable
finalized boundary described below.


#### Finality and fills

Finality uses each source's `finalized` block tag through `eth_getBlockByNumber`, not a confirmation
count. The client:

1. Requires three identical non-null normalized receipts.
1. Matches the receipt block hash to one unanimous explicit inclusion header.
1. Waits until the minimum verified finalized height reaches the inclusion height.
1. Extends the unanimous parent-linked finalized ancestry.
1. Requires the full transaction to match the authenticated signed envelope.
1. Requires three identical `debug_traceTransaction` call trees and admits each internal call only
   when its purpose, caller, target, and call type match one manifest edge exactly. Contract
   creation and self-destruction are denied.
1. Rechecks the deployment manifest at inclusion, then commits finality evidence, receipt state,
   header ancestry, and canonical nonce advancement in one database transaction.

After on-chain execution, deployment or call-trace drift detected by the final-inclusion checks leaves signer
ownership quarantined. Those checks cannot reverse on-chain effects from a contract upgrade after the decision
block used by the final pre-sign check. This includes an upgrade after that check completes and before
transaction execution.

All three RPC sources must support the `finalized` tag. An unsupported tag fails reconciliation
closed.

For a successful swap, the full finalized transaction must match the persisted signer, nonce,
destination, calldata, and value. The receipt must contain exactly one `Swap` log from the selected
pool. A SELL requires the log's positive base input to equal the persisted amount. A BUY requires
the log's positive quote input to equal the persisted amount and a negative base output. Existing
Uniswap V3 parsing derives the executed amount. A BUY fill price is the quote spent divided by
the emitted last quantity.

The fill contains:

- The original order quantity for a SELL. For a BUY, the executed base output converted at `FIXED_PRECISION`.
  A BUY can fill more than the submitted quantity when the pool price improves. Set `allow_overfills = true`
  on the live execution engine so that fill is applied.
- The average fill price. For a BUY, quote spent divided by the emitted last quantity.
- The transaction hash as venue order ID.
- A deterministic trade ID derived from the transaction hash and log index.
- `effectiveGasPrice * gasUsed` as native-currency commission.

Before emitting the fill, the client verifies native and tracked-token state at the finalized
inclusion height through all three sources. It then publishes the stable-ID order event and wallet
account state, stores the fill marker, and releases signer ownership. A wallet refresh or event
dispatch failure keeps the finalized intent active for reconciliation.


## Historical reference (superseded where noted above)

## Core Primitives

Nautilus Trader's blockchain integration is built on foundational primitives defined in the DeFi domain model (`nautilus_model::defi`). These building blocks provide type-safe abstractions for working with EVM-based blockchains.

### Chain

The `Chain` struct represents a blockchain network with its connection endpoints and metadata. Each chain instance contains:

**Fields:**

- `name` (`Blockchain`): The blockchain network type (enum of 80+ supported chains)
- `chain_id` (`u32`): Unique EVM chain identifier (e.g., 1 for Ethereum, 42161 for Arbitrum)
- `hypersync_url` (`String`): Endpoint for high-performance Hypersync data streaming
- `rpc_url` (`Option<String>`): Optional HTTP/WSS RPC endpoint for direct node communication
- `native_currency_decimals` (`u8`): Decimal precision for the chain's native gas token (typically 18)

**Chain Retrieval:**

Chains can be retrieved by numeric ID or string name (case-insensitive):

- **By Chain ID:** Lookup using EVM chain identifier with `from_chain_id`
- **By Name:** Lookup using blockchain name (case-insensitive: "ethereum", "Ethereum", "ETHEREUM" all work) with `from_chain_name`
- **Static Instances:** Pre-configured chains available as constants

Each chain has a native currency used for gas fees. The `native_currency()` method returns a properly configured Currency instance:

| Chain Family                                    | Code | Name         | Decimals |
|-------------------------------------------------|------|--------------|----------|
| Ethereum & L2s (Arbitrum, Base, Optimism, etc.) | ETH  | Ethereum     | 18       |
| Polygon                                         | POL  | Polygon      | 18       |
| Avalanche                                       | AVAX | Avalanche    | 18       |
| BSC                                             | BNB  | Binance Coin | 18       |

## Contracts

High-performance interface for querying EVM smart contracts with type-safe Rust abstractions. Supports token metadata, DEX pools, and DeFi protocols through efficient batch operations.

### Base (Multicall3)

Batches multiple contract calls into a single RPC request using Multicall3 (`0xcA11bde05977b3631167028862bE2a173976CA11`).

- Always uses `allow_failure: true` for partial success and detailed errors
- Executes atomically in the same block
- Errors: `RpcError` (network issues), `AbiDecodingError` (decode failures)

### ERC20

Inherits from `BaseContract` to use Multicall3 for efficient batch operations. Fetches token metadata, handling non-standard implementations.

**Methods:**

- `fetch_token_info`: Single token metadata (uses multicall internally for name, symbol, decimals)
- `batch_fetch_token_info`: Multiple tokens in one multicall (3 calls per token)
- `enforce_token_fields`: Validate non-empty name/symbol

**Error Types:**

1. **`CallFailed`** - Contract missing or function not implemented -> Skip token
2. **`DecodingError`** - Raw bytes instead of ABI encoding (e.g., `0x5269636f...`) -> Skip token
3. **`EmptyTokenField`** - Function returns empty string -> Skip if enforced

**Best Practices:**

- Skip pools with any token errors
- `raw_data` field preserves original response for debugging
- Non-standard tokens often have other issues (transfer fees, rebasing)

## Configuration

| Option                          | Default | Description |
|---------------------------------|---------|-------------|
| `chain`                         | Required | `nautilus_trader.model.Chain` to synchronize (e.g., `Chain.ETHEREUM`). |
| `dex_ids`                       | Required | Sequence of `DexType` identifiers describing which DEX integrations to enable. |
| `http_rpc_url`                  | Required | HTTPS RPC endpoint used for EVM calls and Multicall requests. |
| `wss_rpc_url`                   | `None`  | Optional WSS endpoint for streaming live updates. |
| `rpc_requests_per_second`       | `None`  | Optional throttle for outbound RPC calls (requests per second). |
| `multicall_calls_per_rpc_request` | `200` | Maximum number of Multicall targets batched per RPC request. |
| `use_hypersync_for_live_data`   | `True`  | When `True`, bootstrap and stream using Hypersync for lower-latency diffs. |
| `from_block`                    | `None`  | Optional starting block height for historical backfill. |
| `pool_filters`                  | `DexPoolFilters()` | Filtering rules applied when selecting DEX pools to monitor. |
| `postgres_cache_database_config`| `None`  | Optional `PostgresConnectOptions` enabling on-disk caching of decoded pool state. |
| `proxy_url`                     | `None`  | Optional proxy URL for HTTP and WebSocket transports. |

## Contributing

:::info
For additional features or to contribute to the Blockchain adapter, please see our
[contributing guide](https://github.com/nautechsystems/nautilus_trader/blob/develop/CONTRIBUTING.md).
:::
