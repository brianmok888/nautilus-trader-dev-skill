NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Betfair v2

The Betfair Rust adapter is in active parity work. This page is the **primary Betfair guide**
(user-directed cutover, 2026-08-26): active Betfair routing resolves here first. The upstream
`docs/integrations/betfair.md` in the read-only pinned snapshot (pin `6df23738`) is itself the
current v2 Rust-adapter guide (Rust implementation exposed to Python at
`nautilus_trader.adapters.betfair`); treat it as the authoritative upstream reference, and this
page as the repo-local delta/cutover tracker.

This page mirrors the main section order from the pinned upstream guide. When the Rust adapter
becomes the sole primary Betfair path, this file can fold into [betfair.md](betfair.md) with
small edits instead of a full rewrite.

## Scope

- Source of truth for this page: `crates/adapters/betfair`
- Upstream reference: pinned `docs/integrations/betfair.md` (current v2 Rust-adapter guide at pin `6df23738`); repo-local entry point in [betfair.md](betfair.md)
- Purpose of this page: track the current Rust surface and the current Rust-vs-v1 differences

## Current Rust status

| Area                     | Current Rust behavior                                                                                        | Difference from `betfair.md` today                                        | Cutover work                                        |
|--------------------------|--------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|-----------------------------------------------------|
| Order types              | `MARKET` only supports `AT_THE_CLOSE`; `LIMIT` supports BSP on close flows.                                  | Stable guide is still Python shaped in this area.                         | Decide final Betfair market order model.            |
| Batch operations         | `SubmitOrderList` and `BatchCancelOrders` are implemented.                                                   | Stable guide used to mark these as unsupported.                           | Keep and promote.                                   |
| Reconciliation scope     | `reconcile_market_ids_only` uses `reconcile_market_ids`; otherwise falls back to `stream_market_ids_filter`. | The pinned upstream doc at `6df23738` documents the same coupling.          | Resolved - keep current.                             |
| Full image cache checks  | Rust uses `generate_mass_status()` at startup and on every stream reconnect; no `check_cache_against_order_image`. | Stable guide describes the Python full image cache check.                 | Add parity or document the Rust path as final.      |
| Post-reconnect halt      | `submit_order` and `submit_order_list` emit `OrderDenied STREAM_RECONCILING` while the reconcile is in flight. | Python keeps trading during reconnect.                                    | Cutover done — keep current.                        |
| Terminal order identity  | Retained local identity for up to 10,000 recent closed cached orders (`OcmState::DEDUP_RETENTION`): late fills/voids route through retained local identity, closed-order identity is restored across reconnects, and replace state resolves across REST, OCM, and startup reconciliation; terminal replace/reduction reports reconcile without duplicates; `customerOrderRef` collision checks compare against every tracked order; historical Bet IDs are suppressed once terminal. | Landed upstream at `8ecab1ce9` ("Retain Betfair terminal order identity"); the pinned upstream doc documents the same behavior. | Landed at `8ecab1ce9` - keep current.               |
| External order filtering | `ignore_external_orders` only skips OCM updates with no `rfo`.                                               | Python also uses it during full image cache checks.                       | Cutover done — keep current.                        |
| Config surface           | No `certs_dir`, no `instrument_config`, fixed keep alive, required heartbeat value.                          | Stable guide still documents the Python config surface.                   | Decide whether to add parity or bless Rust surface. |
| SSL certificates         | Stream client currently hardcodes `certs_dir=None`.                                                          | Stable guide documents certificate configuration and `BETFAIR_CERTS_DIR`. | Add support or remove from the future guide.        |

## Orders capability

### Order types

| Order Type             | Supported | Notes                                                                       |
|------------------------|-----------|-----------------------------------------------------------------------------|
| `MARKET`               | ✓*        | Rust only supports `AT_THE_CLOSE`, which maps to Betfair `MARKET_ON_CLOSE`. |
| `LIMIT`                | ✓         | Rust supports regular limit orders and BSP on close limit orders.           |
| `STOP_MARKET`          | -         | Not supported.                                                              |
| `STOP_LIMIT`           | -         | Not supported.                                                              |
| `MARKET_IF_TOUCHED`    | -         | Not supported.                                                              |
| `LIMIT_IF_TOUCHED`     | -         | Not supported.                                                              |
| `TRAILING_STOP_MARKET` | -         | Not supported.                                                              |

### Time in force

| Time in force  | Supported | Notes                                                        |
|----------------|-----------|--------------------------------------------------------------|
| `GTC`          | ✓         | Maps to Betfair `PERSIST`.                                   |
| `DAY`          | ✓         | Maps to Betfair `LAPSE`.                                     |
| `FOK`          | ✓         | Maps to Betfair `FILL_OR_KILL`.                              |
| `IOC`          | ✓         | Maps to `FILL_OR_KILL` with `min_fill_size=0`.               |
| `AT_THE_CLOSE` | ✓         | Used for Betfair BSP `LIMIT_ON_CLOSE` and `MARKET_ON_CLOSE`. |

Rust currently also accepts `LIMIT` orders in `AT_THE_OPEN` mode and routes them through Betfair
`LIMIT_ON_CLOSE` instructions. Treat that as current behavior, not a settled public contract.

### Batch operations

| Operation    | Supported | Notes                                      |
|--------------|-----------|--------------------------------------------|
| Batch Submit | ✓         | Implemented through `SubmitOrderList`.     |
| Batch Modify | -         | Not supported.                             |
| Batch Cancel | ✓         | Implemented through `BatchCancelOrders`.   |

## Execution control flow

Startup:

1. Connect the HTTP client and fetch initial account funds.
2. Seed OCM state from cached orders.
3. Connect the Betfair execution stream and subscribe to order updates.
4. Generate startup mass status from `listCurrentOrders`.
5. Reconcile order and fill reports into the execution engine.

On every stream reconnect, the same mass-status reconciliation runs over a recent
window and the adapter halts new exposure-increasing commands until it dispatches.
See [Post-reconnect reconciliation](#post-reconnect-reconciliation).

Current Rust notes:

- `stream_market_ids_filter` filters live OCM updates.
- `reconcile_market_ids_only=True` uses explicit `reconcile_market_ids`.
- When `reconcile_market_ids_only=False` and `reconcile_market_ids` is unset, Rust currently
  falls back to `stream_market_ids_filter` for startup reconciliation.
- Rust does not yet implement the Python `check_cache_against_order_image` full-image cache check.
- `ignore_external_orders=True` currently skips only OCM updates with no `rfo`.

## Session management and reconnection

Betfair sessions expire every 12-24 hours. The Rust adapter handles session recovery
automatically through three mechanisms:

| Mechanism           | Trigger                           | Action                                                               |
|---------------------|-----------------------------------|----------------------------------------------------------------------|
| Periodic keep-alive | Every 10 hours.                   | Renew session token, push to all stream watch channels.              |
| Keep-alive fallback | Keep-alive returns `LoginFailed`. | Full re-login via `reconnect()`, push fresh token to streams.        |
| Stream reconnect    | `Connection` message after drop.  | Try keep-alive, fall back to re-login on `LoginFailed`, update auth. |

Transient errors (network timeouts, 5xx responses) during keep-alive are logged and
skipped. The existing session token is preserved and the next keep-alive interval
retries. Only `LoginFailed` errors (session expiry) trigger a full re-login.

Both the data and execution clients run identical reconnection logic. Each spawns:

- A **keep-alive task** that periodically refreshes the session and pushes updated
  auth bytes to the stream watch channels.
- A **reconnect handler** that listens for `Connection` messages after a stream
  reconnect, refreshes the session, and pushes the new token.

The stream client stores auth bytes in a `tokio::sync::watch` channel. The
`post_reconnection` closure reads from this channel on each TCP reconnect, so a token
refreshed by either the keep-alive task or reconnect handler is picked up on the next
connection attempt.

The data client reconnect handler also updates the race stream auth when a race stream
is active.

NT v2 compatibility note: the socket-state and reconnect-control layer sits on top of the
session logic above and is included in the pinned baseline `6df23738` (upstream commit
`98e6c39d8` "Add Betfair socket-state reporting and reconnect control"; already present at the
earlier develop snapshot `d2b62d35a7`): the data and execution clients publish transport state on the stable
endpoint labels `betfair-data-streams` and `betfair-user-streams` (surfaced by the runner
as `SocketStateChanged` on `events.system.SocketStateChanged`), register targeted
reconnects through the `SocketReconnectRegistry` with authentication and subscription
replay, and keep the pre-existing execution reconciliation gate closed until the
replacement stream reconciles.
Older pins through `baa667bc` lack this layer; the session mechanisms above are the
complete pinned-baseline behavior there.

## Post-reconnect reconciliation

When the Betfair execution stream reconnects, the adapter assumes the cache may have
diverged from venue state during the gap (in particular, fills can complete and roll
off the unmatched book before the post-reconnect stream image arrives). It therefore
runs a mass-status reconciliation over a recent window before allowing strategies to
add new exposure.

| Step | Trigger                                        | Action                                                                                                          |
|------|------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| 1    | Second `Connection` message after stream drop. | OCM handler raises `pending_resync` and `is_reconciling`, sends a reconnect signal to the background task.      |
| 2    | Reconnect task receives signal.                | Re-asserts `is_reconciling` so a queued second reconnect halts during its own iteration too.                    |
| 3    | Reconnect task body.                           | Refreshes session, updates stream auth, fetches `getAccountFunds`, and calls `listCurrentOrders` for orders+fills. |
| 4    | Mass status built.                             | Dispatched as `ExecutionReport::MassStatus` so the engine reconciles into the cache.                            |
| 5    | Iteration ends.                                | `is_reconciling` cleared. A failed iteration also clears it (fail-open, consistent with the rest of Nautilus).  |

While `is_reconciling` is set:

- `submit_order` and `submit_order_list` emit `OrderDenied` with reason
  `STREAM_RECONCILING: post-reconnect reconciliation in progress, retry once it completes`.
- `cancel_order`, `batch_cancel_orders`, and `modify_order` pass through unchanged so a
  strategy can always reduce exposure during the window.
- Buffered OCMs that arrived during the gap are drained on the next strategy command via
  `process_pending_resync` (separate `pending_resync` flag).

If the client disconnects while a reconciliation is still in flight, `clear_resync_state`
clears `is_reconciling` so a subsequent connect/submit cycle starts clean.

The lookback window for the mass-status fetch is `stream_gap_recovery_lookback_mins`
(default `10`). It should comfortably exceed the longest expected reconnect duration so
a fill that completed mid-gap is still captured.

## Tick scheme and pricing

Betfair uses a tiered tick scheme with varying increments across price ranges:

| Price range    | Tick size |
|----------------|-----------|
| 1.01 - 2.00    | 0.01      |
| 2.00 - 3.00    | 0.02      |
| 3.00 - 4.00    | 0.05      |
| 4.00 - 6.00    | 0.10      |
| 6.00 - 10.00   | 0.20      |
| 10.00 - 20.00  | 0.50      |
| 20.00 - 30.00  | 1.00      |
| 30.00 - 50.00  | 2.00      |
| 50.00 - 100.00 | 5.00      |
| 100.00 - 1000  | 10.00     |

Minimum price is 1.01, maximum is 1000.00.

## Order modification

- Quantity modification uses `CancelOrders` with `size_reduction`.
- Price modification uses `ReplaceOrders` (cancel + new order at new price).
- Order cancellation uses `CancelOrders`.
- Cancel-all uses `cancel_orders` without market and order filters.

Current develop commit `79fb940dc794b953570ad5ac76f4f1e6b68ea93f`
preserves one logical Nautilus order across cancel-replace. The old and
replacement Bet IDs map to one `client_order_id`; success emits exactly one
`OrderUpdated` with the replacement Bet ID, suppresses the old-Bet cancel, and
orders that update before any fill already present in the replacement OCM.
`CANCELLED_NOT_PLACED` emits `OrderCanceled`, not `OrderModifyRejected`; late
fills on the canceled old Bet ID apply once without reopening the order.

Use `customerOrderRef` to correlate the logical order. Generate one
`customerRef` per REST command and reuse it unchanged across retries.
At `8ecab1ce9`, correlation, customer refs, dedup, and replaced IDs are bounded together
into the retained-identity set: a new submission whose `customerOrderRef` collides with
another **tracked order** (active or retained-closed) is denied with
`VALIDATION_FAILED: customerOrderRef <ref> collides with another tracked order` before
`OrderSubmitted` or HTTP dispatch; in an order list only the colliding leg is denied.
This behavior was reviewed through the 2026-08-28 develop transition tip `8e51f957c`
(`references/upstream-delta-review.json`, window `8ecab1ce9`..`8e51f957c`).
State-changing commands may retry at most three times within a 45-second budget,
inside Betfair's 60-second deduplication window. Treat transport failures,
timeouts, malformed success responses, HTTP 5xx, throttling/service-busy, and
documented unexpected errors as ambiguous. If the budget expires, keep the
order pending for OCM or startup reconciliation; reject only on definitive venue
evidence.
## Order stream fill handling

The execution client processes order updates from the Betfair Exchange Streaming API.
Two configuration options control how updates are filtered:

- `stream_market_ids_filter`: filters at the market level (early exit, silent skip).
- `ignore_external_orders`: filters at the order level (skips OCM updates with no `rfo`).

### Fill handling

The adapter handles several edge cases when processing fills from the stream:

- **Incremental fills**: Betfair reports cumulative matched sizes. The adapter calculates
  incremental fills by tracking the last known filled quantity per order.
- **Overfill protection**: fills that would exceed the order quantity are rejected.
- **Race conditions**: when stream fills arrive before the HTTP order response, the adapter
  caches the venue order ID immediately to ensure correct order matching.
- **Network error recovery**: when an HTTP order submission fails with a network error
  (timeout, connection reset), the order may still have been placed on the venue. The
  adapter leaves the order in SUBMITTED status and retains the customer order reference
  so the stream can confirm the order when it reconnects. API errors (where Betfair
  explicitly rejected) reject immediately.
- **Gap-window fills**: a fill that completes and rolls off the unmatched book during a
  stream disconnect is recovered by the post-reconnect mass-status reconciliation; see
  [Post-reconnect reconciliation](#post-reconnect-reconciliation).

## Rate limiting

The adapter uses separate rate limit buckets so that account state polling and
reconciliation do not throttle order placement:

| Bucket  | Default | Endpoints                                       |
|---------|---------|-------------------------------------------------|
| General | 5/s     | Account state, reconciliation, keep-alive.      |
| Orders  | 20/s    | `placeOrders`, `replaceOrders`, `cancelOrders`. |

Order status and fill report queries retry once on session errors after refreshing the
session. `TOO_MANY_REQUESTS` errors retry after a 5-second delay.

## Market version price protection

When `use_market_version=True`, each order request includes the market version last seen
by the adapter. If the market has advanced beyond that version by the time Betfair
processes the order, Betfair lapses the bet rather than matching it against a changed book.

The adapter reads the market version from the instrument's `info` dictionary, which the
Exchange Streaming API's `MarketDefinition` updates populate. Orders submitted before the
first `MarketDefinition` is received do not include a version.

## Custom data types

The Rust adapter emits the same custom data types as the Python adapter through the
market and race streams. All custom data flows automatically when subscribed to markets.

| Type                       | Stream | Description                                       |
|----------------------------|--------|---------------------------------------------------|
| `BetfairTicker`            | Market | Last traded price, traded volume, BSP indicators. |
| `BetfairStartingPrice`     | Market | Realized BSP after market close.                  |
| `BetfairSequenceCompleted` | Market | Marks end of a market change sequence.            |
| `BetfairOrderVoided`       | Order  | Voided order details (size voided, price, side).  |
| `BetfairRaceRunnerData`    | Race   | Live GPS tracking per runner (TPD).               |
| `BetfairRaceProgress`      | Race   | Sectional times, running order, jump data.        |

Race data requires Total Performance Data (TPD) coverage and a Betfair API key with TPD
access. Enable with `subscribe_race_data=True`.

## Multi-node deployment

When multiple trading nodes share a single Betfair account across different markets:

1. Set `stream_market_ids_filter` to include only that node's markets.
2. Set `ignore_external_orders=True` to suppress warnings about orders from other nodes.
3. Set `reconcile_market_ids_only=True` to limit reconciliation scope.

## Current Rust configuration

### Data client configuration

| Option                              | Default  | Notes                                         |
|-------------------------------------|----------|-----------------------------------------------|
| `account_currency`                  | Required | Betfair account currency.                     |
| `username`                          | `None`   | Falls back to `BETFAIR_USERNAME`.             |
| `password`                          | `None`   | Falls back to `BETFAIR_PASSWORD`.             |
| `app_key`                           | `None`   | Falls back to `BETFAIR_APP_KEY`.              |
| `proxy_url`                         | `None`   | Optional proxy URL for HTTP requests.         |
| `request_rate_per_second`           | `5`      | General HTTP rate limit.                      |
| `default_min_notional`              | `None`   | Optional minimum notional override.           |
| `event_type_ids`                    | `None`   | Optional navigation filter.                   |
| `event_type_names`                  | `None`   | Optional navigation filter.                   |
| `event_ids`                         | `None`   | Optional navigation filter.                   |
| `country_codes`                     | `None`   | Optional navigation filter.                   |
| `market_types`                      | `None`   | Optional navigation filter.                   |
| `market_ids`                        | `None`   | Optional navigation filter.                   |
| `min_market_start_time`             | `None`   | Optional navigation filter.                   |
| `max_market_start_time`             | `None`   | Optional navigation filter.                   |
| `stream_host`                       | `None`   | Optional stream host override.                |
| `stream_port`                       | `None`   | Optional stream port override.                |
| `stream_heartbeat_secs`             | `5`      | Keepalive cadence (default `BETFAIR_STREAM_HEARTBEAT_SECS`). |
| `stream_heartbeat_timeout_secs`     | `60`     | Dead-peer timeout; reconnects when no bytes arrive. |
| `stream_reconnect_delay_initial_ms` | `2,000`  | Initial reconnect delay.                      |
| `stream_reconnect_delay_max_ms`     | `30,000` | Maximum reconnect delay.                      |
| `stream_use_tls`                    | `True`   | Use TLS for the stream connection.            |
| `stream_conflate_ms`                | `None`   | Explicit conflation setting.                  |
| `subscription_delay_secs`           | `3`      | Delay before the first market subscription.   |
| `subscribe_race_data`               | `False`  | Subscribe to RCM updates.                     |

Rust does not yet expose `certs_dir` or `instrument_config`. Rust also uses a fixed 36,000 second
keep-alive interval.

### Execution client configuration

| Option                              | Default       | Notes                                                  |
|-------------------------------------|---------------|--------------------------------------------------------|
| `account_id`                        | `BETFAIR-001` | Account ID for the client core.                        |
| `account_currency`                  | `GBP`         | Betfair account currency.                              |
| `username`                          | `None`        | Falls back to `BETFAIR_USERNAME`.                      |
| `password`                          | `None`        | Falls back to `BETFAIR_PASSWORD`.                      |
| `app_key`                           | `None`        | Falls back to `BETFAIR_APP_KEY`.                       |
| `proxy_url`                         | `None`        | Optional proxy URL for HTTP requests.                  |
| `request_rate_per_second`           | `5`           | General HTTP rate limit.                               |
| `order_request_rate_per_second`     | `20`          | Order endpoint rate limit.                             |
| `stream_host`                       | `None`        | Optional stream host override.                         |
| `stream_port`                       | `None`        | Optional stream port override.                         |
| `stream_heartbeat_secs`             | `5`           | Keepalive cadence (default `BETFAIR_STREAM_HEARTBEAT_SECS`). |
| `stream_heartbeat_timeout_secs`     | `60`          | Dead-peer timeout; reconnects when no bytes arrive.    |
| `stream_reconnect_delay_initial_ms` | `2,000`       | Initial reconnect delay.                               |
| `stream_reconnect_delay_max_ms`     | `30,000`      | Maximum reconnect delay.                               |
| `stream_use_tls`                    | `True`        | Use TLS for the stream connection.                     |
| `stream_market_ids_filter`          | `None`        | Optional live OCM market filter.                       |
| `ignore_external_orders`            | `False`       | Only skips OCM updates with no `rfo`.                  |
| `calculate_account_state`           | `True`        | Gates periodic account state polling in Rust today.    |
| `request_account_state_secs`        | `300`         | Poll interval for account funds.                       |
| `reconcile_market_ids_only`         | `False`       | When `True`, use `reconcile_market_ids`.               |
| `reconcile_market_ids`              | `None`        | Explicit startup reconciliation market IDs.            |
| `use_market_version`                | `False`       | Attach market version to place and replace requests.   |
| `stream_gap_recovery_lookback_mins` | `10`          | Lookback window for the post-reconnect mass-status reconciliation. |

NT v2 compatibility note: the `stream_heartbeat_secs` and `stream_heartbeat_timeout_secs` names
(seconds) reflect upstream commit `74d57e7e05`, included in the pinned baseline `6df23738`;
older pins through `6e59fd74ea` used the pre-rename millisecond spellings.
Rust does not yet expose `certs_dir` or `instrument_config`.

## Cutover plan

Use this page as the transition tracker until the Rust adapter becomes the primary Betfair path.

At cutover:

1. Decide whether Rust keeps its current reconciliation filter behavior or matches the Python split.
2. Decide whether Rust adds certificate configuration and other Python config fields.
3. Decide whether Rust keeps BSP-only `MARKET` orders or adds the Python aggressive-limit path.
4. Promote this file to `betfair.md`.
5. Move any remaining Python-only notes into a short legacy note or release note.
