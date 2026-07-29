---
name: nt-adapters
description: "Use when working with exchange or data provider adapters, HTTP/WebSocket clients, instrument providers, or venue integration in NautilusTrader."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-adapters

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; current-develop drift is version-scoped in `README.md`. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 25 tests. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | 2026-07-29: `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-adapters` passed the skill domain's scoped examples and owners against `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; schema-v2 provenance is recorded in `references/g2-evidence/nt-adapters.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 tests. |
| G4 Lane and API shape | Classify migration-only Python, active AI/advisory Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py -k 'lane or python or rust or current_develop'` passed 13 tests; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-29: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 356 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'` passed 24 tests. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md` records the post-fix audit; `uv run python tools/check_skill_g2_harnesses.py --check-cards` validates all 18 cards and evidence artifacts. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Adapter gates: Rust owns HTTP/WebSocket networking, request signing, parsing, normalization, subscription/order state, and reconnect logic; Python/PyO3 is only the control/config exposure. Before `Pass`, run adapter unit/spec tests, `cargo nextest`, `cargo clippy`, `cargo deny`, and `scripts/fuzz-adapter.sh`/fuzz targets for parsers or protocol changes.

## What This Skill Covers

NautilusTrader **adapter domain** — exchange/data provider integrations following a layered architecture with Rust core for networking and Python layer for platform integration.

**Python modules**: `adapters/*`, `adapters/_template/`, and PyO3 exports where an adapter is Rust/v2-only.
**Rust crates**: adapter crates plus `nautilus_network` and `nautilus_cryptography`.

**Current official integrations (GitHub `develop` snapshot)**: AX, Betfair, Binance, BitMEX, Bybit, Coinbase, Databento, Deribit, Derive, dYdX, Hyperliquid, Interactive Brokers, Kraken, Lighter, OKX, Polymarket, Tardis. Local reference snapshots may include non-upstream or retired adapters; do not treat those as current official support without checking the integration index.

## When To Use

- Configuring an existing adapter for live trading
- Building a new exchange or data provider adapter
- Customizing instrument providers
- Working with HTTP/WebSocket client patterns
- Understanding adapter testing specifications
- Venue-specific data parsing or execution logic

## When NOT To Use

- **Live node system config** → use `nt-live`
- **Strategy logic** → use `nt-trading`
- **Data persistence** → use `nt-data`
- **Domain model types** → use `nt-model`
- **Testing spec details** → use `nt-testing` (DataTesterConfig/ExecTesterConfig)

## Adapter Architecture

## Current adapter contract

Read `references/developer_guide/contracts/adapter_contract.md` before creating
or reviewing adapter code.

Current high-risk rules:

- Use `nautilus_network::http::HttpClient` in Rust HTTP examples.
- Use `get_runtime().spawn()` for Python-runtime-sensitive async Rust paths;
  do not teach `tokio::spawn()` as the default from Python-driven adapter code.
- Keep Python data and execution client methods aligned with current
  command/request object signatures.
- Treat `InstrumentProvider.load_all_async()` as the required v1.227-era method;
  override targeted methods only for venue-specific semantics or efficiency.
- Use adapter `environment` enums instead of removed legacy environment flags; for Binance and Kraken, use `Live` / `LIVE` naming rather than stale `Mainnet` / `MAINNET` enum variants.
- Convert venue millisecond timestamps at parser boundaries with `millis_to_nanos`; `ts_event` is the converted venue timestamp and `ts_init` is `clock.get_time_ns()`.
- When adapter examples touch data-engine bar settings, use `time_bars_origin_offset`; never reintroduce stale `time_bars_origins`.
- Require data tester and execution tester evidence for adapter readiness; execution tests should include marketable limit coverage via `limit_aggressive` and rejected modify coverage via `test_modify_rejected` when the venue supports those paths.
- For WebSocket handlers that receive the connected client after construction,
  queue `SetClient` before publishing the command channel or marking the
  connection active.
- For single-endpoint authenticated streams, keep auth-token rotation in the
  outer client, stop refresh tasks with `CancellationToken`, and replay current
  account subscriptions after refresh.
- Treat transport, timeout, send, retry, parse, and whole-batch failures as
  ambiguous outcome failures unless the venue returns an explicit per-order
  rejection.

Adapters follow a layered architecture:

- **Rust core** — networking clients, parsing, rate limiting, request signing
- **Python layer** — integration with platform's data and execution engines

### Rust Core Structure

```
crates/adapters/your_adapter/
├── src/
│   ├── common/              # Shared types and utilities
│   │   ├── consts.rs        # Venue constants / broker IDs
│   │   ├── credential.rs    # API key storage and signing helpers
│   │   ├── enums.rs         # Venue enums mirrored in REST/WS payloads
│   │   ├── error.rs         # Adapter-level error aggregation
│   │   ├── models.rs        # Shared model types
│   │   ├── parse.rs         # Shared parsing helpers
│   │   ├── retry.rs         # Retry classification
│   │   ├── urls.rs          # Environment & product aware base-url resolvers
│   │   └── testing.rs       # Fixtures reused across unit tests
│   ├── http/                # HTTP client implementation
│   │   ├── client.rs        # HTTP client with authentication
│   │   ├── error.rs         # HTTP-specific error types
│   │   ├── models.rs        # Structs for REST payloads
│   │   ├── parse.rs         # Response parsing functions
│   │   └── query.rs         # Request and query builders
│   ├── websocket/           # WebSocket implementation
│   │   ├── client.rs        # WebSocket client
│   │   ├── dispatch.rs      # Execution event dispatch and order routing
│   │   ├── enums.rs         # WebSocket-specific enums
│   │   ├── error.rs         # WebSocket-specific error types
│   │   ├── messages.rs      # Streaming payload types
│   │   └── parse.rs         # Stream message parsing
│   ├── python/              # PyO3 bindings
│   │   ├── mod.rs           # Module exports
│   │   └── ...              # Per-component bindings
│   ├── config.rs            # Adapter configuration (Python-facing)
│   ├── factories.rs         # Client factories
│   └── lib.rs               # Crate root
├── tests/                   # Integration tests
└── Cargo.toml
```

### Python Layer Structure

```
nautilus_trader/adapters/your_adapter/
├── __init__.py
├── config.py                # DataClientConfig, ExecClientConfig, InstrumentProviderConfig
├── factories.py             # DataClientFactory, ExecClientFactory
├── providers.py             # InstrumentProvider
├── data.py                  # DataClient / MarketDataClient
├── execution.py             # ExecutionClient
└── http/                    # HTTP client wrapper (if needed)
```

## Adapter Implementation Sequence

Follow this dependency-driven order. Each phase builds on the previous one. **Implement the Rust core before any Python layer.**

### Phase 1: Rust Core Infrastructure

| Step | Component | Description |
|------|-----------|-------------|
| 1.1 | HTTP error types | Define HTTP-specific error enum with retryable/non-retryable variants |
| 1.2 | HTTP client | Implement credentials, request signing, rate limiting, retry logic |

### Rate-limit and unknown-outcome policy

- Scope shared venue caps through one limiter per actual venue window; do not
  duplicate a shared cap across separate REST/WebSocket/poller limiters.
- Bound inflight command concurrency with a closed-loop gate, not only a send
  rate limiter.
- Treat an execution-path rate-limit response as an unknown outcome unless the
  command is idempotent or the venue proves it was not processed; leave order
  state open for reconciliation instead of emitting a terminal rejection.

| 1.3 | HTTP API models | Define request/response structs for REST endpoints |
| 1.4 | HTTP parsing | Convert venue responses to Nautilus domain models |
| 1.5 | WebSocket error types | Define WebSocket-specific error enum |
| 1.6 | WebSocket client | Connection lifecycle, authentication, heartbeat, reconnection |
| 1.7 | WebSocket messages | Define streaming payload types |
| 1.8 | WebSocket parsing | Convert stream messages to Nautilus domain models |
| 1.9 | Python bindings | Expose Rust functionality via PyO3 |

**Milestone**: Rust crate compiles, unit tests pass, HTTP/WebSocket clients can authenticate and stream/request raw data.

### Phase 2: Instrument Definitions

| Step | Component | Description |
|------|-----------|-------------|
| 2.1 | Instrument parsing | Parse venue instrument definitions into Nautilus types |
| 2.2 | Instrument provider | Implement `InstrumentProvider` to load, filter, and cache instruments |
| 2.3 | Symbol mapping | Handle venue-specific symbol formats and Nautilus `InstrumentId` conversion |

### Phase 3: Market Data

| Step | Component | Description |
|------|-----------|-------------|
| 3.1 | Data subscriptions | Subscribe to trade ticks, quote ticks, bars, order book updates |
| 3.2 | Historical data | Request historical bars, trades, quotes via REST |
| 3.3 | Order book management | Maintain L2/L3 order book from delta stream |

### Phase 4: Order Execution

| Step | Component | Description |
|------|-----------|-------------|
| 4.1 | Order submission | Submit market, limit, stop orders via REST/WebSocket |
| 4.2 | Order management | Cancel, modify, track order state |
| 4.3 | Fill handling | Process trade reports, update positions |

### Phase 5: Advanced Features

Account management, position tracking, funding rate handling, etc.

### Phase 6: Configuration & Factories

Wire everything into the platform via config types and factory patterns.

### Phase 7: Testing & Documentation

Data testing (DataTesterConfig), execution testing (ExecTesterConfig), documentation.

## Python Usage

### Configure Existing Adapter

```python
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig, BinanceExecClientConfig

data_config = BinanceDataClientConfig(
    api_key="...",
    api_secret="...",
    account_type=BinanceAccountType.USDT_FUTURE,
)

exec_config = BinanceExecClientConfig(
    api_key="...",
    api_secret="...",
    account_type=BinanceAccountType.USDT_FUTURE,
)
```

### Use InstrumentProvider

```python
# Instrument discovery happens automatically when adapter connects
# Access instruments via cache:
instruments = self.cache.instruments(venue=Venue("BINANCE"))
instrument = self.cache.instrument(InstrumentId.from_str("ETHUSDT-PERP.BINANCE"))
```

### Adapter Configuration Pattern

Each adapter follows the same config pattern:
- `{Adapter}DataClientConfig` — data feed configuration
- `{Adapter}ExecClientConfig` — execution configuration
- `{Adapter}InstrumentProviderConfig` — instrument discovery settings

## Python Extension

### Customize Instrument Provider

```python
from nautilus_trader.adapters.binance.providers import BinanceInstrumentProvider

class MyInstrumentProvider(BinanceInstrumentProvider):
    async def load_all_async(self, filters=None):
        await super().load_all_async(filters)
        # Add custom instrument filtering/transformation
```

## Rust Usage

### Using Adapters with Rust LiveNode

```rust
use nautilus_live::node::LiveNode;
use nautilus_model::identifiers::Venue;

let node = LiveNode::builder()
    .add_adapter(MyAdapterConfig::default())
    .add_strategy(MyStrategy::new(config))
    .build()?;

node.run().await?;
```

### Adapter Factory Pattern (Rust)

Each adapter implements a factory trait that creates data and execution clients:

```rust
pub trait AdapterFactory {
    fn create_data_client(&self, config: &AdapterConfig) -> Result<Box<dyn DataClient>>;
    fn create_exec_client(&self, config: &AdapterConfig) -> Result<Box<dyn ExecClient>>;
}
```

### Available Rust Adapters

Do not hard-code an adapter count: the integration inventory changes across
release and `develop`. Check the official integration index and
`crates/adapters/` at the selected upstream commit, then verify each adapter's
data/execution completeness independently.

### Environment Variables

```bash
# Per-adapter credentials follow this pattern
{VENUE}_API_KEY=xxx
{VENUE}_API_SECRET=xxx
{VENUE}_PASSPHRASE=xxx  # OKX, Bybit
```

## Rust Extension

### Build New Adapter in Rust

Follow the implementation sequence above. Key patterns:

**HTTP Client**:
```rust
use nautilus_network::http::HttpClient as NautilusHttpClient;

pub struct HttpClient {
    client: NautilusHttpClient,
    credential: Credential,
    rate_limit: RateLimit,
}

impl HttpClient {
    pub async fn sign_request(&self, method: Method, path: &str, body: &str) -> Request { ... }
}
```

**WebSocket Client**:
```rust
pub struct WebSocketClient {
    url: Url,
    credential: Credential,
    subscription_state: Shared<SubscriptionState>,
}
```

**Message Routing**: Follow the `raw → msg → out` naming convention:
- `raw`: Raw bytes from WebSocket
- `msg`: Parsed venue-specific message
- `out`: Nautilus domain model

### Factory Implementation

```rust
// crates/adapters/your_adapter/src/factories.rs
pub fn register(config: YourAdapterConfig) -> AdapterRegistry {
    AdapterRegistry::new()
        .data_client(YourDataClientFactory::new(config.clone()))
        .exec_client(YourExecClientFactory::new(config))
}
```

### PyO3 Bindings (Optional)

```rust
// crates/adapters/your_adapter/src/python/mod.rs
#[pymodule]
fn your_adapter(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<YourAdapterConfig>()?;
    m.add_function(wrap_pyfunction!(create_client, m)?)?;
    Ok(())
}
```

## Rust Adapter Patterns

### Common Code (`common/`)

The `common/` directory contains shared types used by both HTTP and WebSocket:

- `consts.rs` — Venue constants (broker IDs, default timeouts)
- `credential.rs` — API key storage, signing helpers
- `enums.rs` — Venue enums (order types, time-in-force, account types)
- `error.rs` — Adapter-level error aggregation
- `parse.rs` — Shared parsing helpers (timestamp conversion, string normalization)
- `retry.rs` — Retry classification (which errors are retryable)
- `urls.rs` — Environment-aware URL resolution (testnet vs mainnet)

### Symbol Normalization

```rust
// common/symbol.rs
pub fn normalize_symbol(raw: &str) -> String {
    // Convert venue-specific symbol format to Nautilus convention
    raw.replace("USDT", "-PERP")  // e.g., BTCUSDT → BTC-PERP
}
```

### Configuration Builder Pattern

```rust
// config.rs follows builder + default pattern
#[derive(Debug, Clone)]
pub struct YourAdapterConfig {
    pub api_key: Option<String>,
    pub api_secret: Option<String>,
    pub base_url: Option<String>,
    pub testnet: bool,
}

impl Default for YourAdapterConfig {
    fn default() -> Self { ... }
}
```

**Field type rules**:
- Required fields: `String` (no `Option`)
- Optional fields: `Option<String>`, default via `Default`
- Python constructors: Always `#[new]` with defaults

### HTTP Client Patterns

**Parser functions**: Each HTTP endpoint has a dedicated parser:
```rust
pub fn parse_instrument(response: &str) -> Result<Vec<InstrumentAny>> { ... }
pub fn parse_order_response(response: &str) -> Result<Order> { ... }
```

**Method naming**: `{verb}_{resource}` — e.g., `get_instruments`, `post_order`, `delete_order`

**Query builders**: Separate query parameter construction:
```rust
pub struct GetOrdersQuery {
    pub symbol: Option<String>,
    pub order_id: Option<u64>,
    pub limit: Option<u32>,
}
```

### WebSocket Client Patterns

**Connection state tracking**:
```rust
pub struct SubscriptionState {
    subscribed: HashSet<String>,
    pending: HashSet<String>,
}
```

**Message routing**: `WsDispatchState` maps incoming messages to handlers
**Backpressure**: Use bounded channels, drop stale messages
**Split architectures**: Separate WebSocket connections for data vs execution
**SetClient handoff**: Queue `HandlerCommand::SetClient(client)` before
publishing a replacement command sender or setting active state, so queued
Subscribe/order commands cannot reach a handler with `inner == None`.
**Auth-token rotation**: If public and authenticated channels share one endpoint
with expiring subscribe tokens, mint tokens in the outer client, re-subscribe
account channels on a timer, and cancel the refresh loop with `CancellationToken`.

### Task Management

```rust
// Use the Nautilus runtime for live DataClient/ExecutionClient trait paths
get_runtime().spawn(async move { ... });

// Graceful shutdown via CancellationToken
let token = CancellationToken::new();
get_runtime().spawn(async move {
    tokio::select! {
        _ = work() => {},
        _ = token.cancelled() => {},
    }
});
```

**Critical**: Never use get_runtime().block_on() inside trait method implementations.
Never use `get_runtime().block_on()` inside live `DataClient` or
`ExecutionClient` trait method implementations; spawn work and
return immediately. `get_runtime().block_on()` is only valid outside an ambient
Tokio runtime, such as PyO3 methods, binaries, dedicated background threads,
`block_in_place` bridges, or tests. Do not teach `tokio::spawn()` as the default
from Python-driven adapter code; use `get_runtime().spawn()` so task ownership
follows Nautilus runtime expectations.

## Key Conventions

### Adapter Testing

- Use DataTesterConfig for data flow validation (see `nt-testing`)
- Use ExecTesterConfig for execution lifecycle testing (see `nt-testing`)
- Cover ambiguous outcome failures in adapter tests: do not emit terminal reject
  events for unknown submit/cancel/modify/batch outcomes unless the venue reports
  an explicit per-order rejection.
- Rust unit tests in `#[cfg(test)] mod tests` within source files
- Integration tests in `tests/` directory

### Adapter Naming

- Crate: `nautilus-{venue}` (e.g., `nautilus-binance`)
- Config: `{Venue}Config`, `{Venue}DataClientConfig`, `{Venue}ExecClientConfig`
- Client: `{Venue}HttpClient`, `{Venue}WebSocketClient`
- Factory: `{Venue}DataClientFactory`, `{Venue}ExecClientFactory`

### Factory Pattern

All adapters use factory registration:
```python
# Python factories
config.adapters.live.add("BINANCE", BinanceLiveDataClientFactory, BinanceLiveExecClientFactory)
```

### Channel Naming

Follow `raw → msg → out` convention:
- `raw`: Raw bytes from network
- `msg`: Parsed venue-specific message type
- `out`: Nautilus domain model

### Type Qualification

Use fully qualified types in adapter code for clarity:
```rust
nautilus_model::identifiers::InstrumentId  // not just InstrumentId
```

### String Interning

For frequently repeated strings (symbols, venues), use string interning for performance.

### Testing Helpers

Every adapter provides `common/testing.rs` with fixture helpers:
```rust
pub fn test_instrument_id() -> InstrumentId { ... }
pub fn test_credential() -> Credential { ... }
```

### Documentation

Rust adapter code must include:
- `///` doc comments on all public types and functions
- `//!` module-level docs
- Examples in doc comments when non-trivial

## References

- `references/developer_guide/adapters.md` — Official adapter development guide
- `references/developer_guide/contracts/adapter_contract.md` — Current adapter contract
- `references/api/` — Per-adapter API documentation
- `references/examples/` — Per-adapter runnable examples
- `references/integrations/` — Per-adapter integration docs
