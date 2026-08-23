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
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `f725e184dbd2f7432b5c7b9458b4ef6d1f85fd5f`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-adapters` passed the skill domain's scoped examples and owners against `f725e184dbd2f7432b5c7b9458b4ef6d1f85fd5f`; schema-v2 provenance is recorded in `references/g2-evidence/nt-adapters.json`. A G2 `cargo check` result is compilation only; it is not spec, testnet, resilience, fuzz, or operations acceptance evidence. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-adapters.json`; repository closure is summarized in `docs/tracking/Findings.md`. |


Adapter gates: Rust owns HTTP/WebSocket networking, request signing, parsing, normalization, subscription/order state, and reconnect logic; Python/PyO3 is only the control/config exposure. Before `Pass`, run adapter unit/spec tests, `cargo nextest`, `cargo clippy`, `cargo deny`, and `scripts/fuzz-adapter.sh`/fuzz targets for parsers or protocol changes.

## Rust production lane

Rust owns production adapter behavior: HTTP/WebSocket transport, authentication and signing, protocol parsing, normalization into Nautilus model types, rate and inflight limits, subscription and order state, reconnect/replay, and ambiguous-outcome reconciliation. Build adapter crates in dependency order, keep fixed-point and timestamp conversion at parser boundaries, and prove readiness with unit/spec tests plus parser fuzzing where inputs are untrusted.

```rust
use nautilus_common::enums::Environment;
use nautilus_live::node::LiveNode;

let mut node = LiveNode::builder(trader_id, Environment::Live)?
    .add_data_client(None, Box::new(data_factory), Box::new(data_config))?
    .add_exec_client(None, Box::new(exec_factory), Box::new(exec_config))?
    .build()?;
node.add_strategy(strategy)?;
node.run().await?;
```

## PyO3 control-plane lane

PyO3 exposes Rust-owned adapter configuration, factory construction, status, and lifecycle controls. Bind in the owning adapter crate's `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates that submodule. Keep networking, signing, parsing, subscriptions, order routing, risk decisions, and reconnect state in Rust; Python must not become an execution authority or liveness dependency.

```rust
use pyo3::prelude::*;

#[pyclass(frozen)]
struct AdapterConfigBinding {
    inner: AdapterConfig,
}

#[pymethods]
impl AdapterConfigBinding {
    #[getter]
    fn environment(&self) -> &str {
        self.inner.environment.as_ref()
    }
}
```

## Migration/reference lane

Quarantined Python examples and prior Python adapter guidance live under `migration_reference/python/` and `references/examples/migration_reference/`. They are migration/reference-only, never the production default.

## Source-pinned upstream lane

Use `references/developer_guide/adapters.md` and `references/developer_guide/rust.md` as the source-pinned upstream snapshots at commit `f725e184dbd2f7432b5c7b9458b4ef6d1f85fd5f`. Preserve their provenance and compare later APIs explicitly rather than silently replacing pinned guidance.

## What This Skill Covers

NautilusTrader **adapter domain** — exchange/data provider integrations with
Rust-owned networking, parsing, state, and engine integration plus a bounded
PyO3 configuration/inspection surface.

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
- Implement the current required `InstrumentProvider` methods: `load_all`, `load_ids`, and `load`;
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

Current-develop retry contract (upstream commits
`77868193d234f7022cac1e14e1c72a419a958665` and
`6e7f5e28a735e564114830bdbbd3083124c52c4f`): use the shared
`RetryManager` only when its cancellation and backoff model fits. Map its typed
`RetryError` variants without losing cause: `Canceled`, `OperationTimeout`,
`ElapsedBudgetExceeded`, and `InvalidConfiguration`. Keep venue
error classification in `should_retry`; do not silently turn terminal venue
errors into retryable transport failures.

Current venue safety overlays:

- Polymarket heartbeat mode sends immediately after execution readiness and
  every five seconds. Each heartbeat response returns a replacement ID; store
  it for the next request, stop only on an explicit stop flag, fail startup if
  the first heartbeat fails, and treat a later failure as execution-channel
  loss. Source: upstream develop commit
  `276e5410115edb40baac9270876c970550c086ee`.
- BitMEX is scheduled to close on 23 September 2026 at 04:00 UTC. Treat the
  adapter as migration-only for new deployments and verify the current venue
  status before planning production use. Source: upstream develop commit
  `90b3d71b0e2e5ec8fa4b366cbf68a8f04996b4c1`.

Adapters follow a layered architecture:

- **Rust core** — networking, parsing, rate limiting, signing, engine integration, and execution state
- **PyO3 control plane** — validated configuration and read-only diagnostics

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

Follow the official dependency structure below. The phases organize work; they are not release
gates. A market-data-only adapter can omit execution, and a product can complete the sequence before
another product begins. Keep the capability matrix current throughout.

### Phase 1: Define scope

Record products, environments, account modes, data types, order/report capabilities, venue
restrictions, protocol boundaries, known gaps, and the smallest end-to-end slice and test plan.

### Phase 2: Build the protocol core

Add the Rust crate and implement environments, URLs, credentials, signing, shared types, HTTP and
WebSocket models, deterministic parsers/serializers, retry classification, authentication,
heartbeats, and transport lifecycle.

### Rate-limit and unknown-outcome policy

- Scope shared venue caps through one limiter per actual venue window; do not
  duplicate a shared cap across separate REST/WebSocket/poller limiters.
- Bound inflight command concurrency with a closed-loop gate, not only a send
  rate limiter.
- Treat an execution-path rate-limit response as an unknown outcome unless the
  command is idempotent or the venue proves it was not processed; leave order
  state open for reconciliation instead of emitting a terminal rejection.

### Phase 3: Implement instruments

Implement bidirectional symbol identity, every supported instrument family, definition loading and
caching, fresh requests, and supported definition updates with complete precision and contract data.

### Phase 4: Implement market data

Build one public stream and instrument first, then add advertised requests/subscriptions while
preserving venue time, correlation, order-book boundaries, unsubscribe, malformed-input, and
reconnect behavior.

### Phase 5: Implement execution

Establish account identity, initial state, private streams, and reconciliation before order flow;
then add submit, cancel, modify, report generation, deduplication, event ordering, and ambiguous
outcome handling.

### Phase 6: Add optional venue capabilities

Add advanced orders, batches, product-specific data, or split clients only after the base lifecycle
is stable, and give each capability independent fixtures, acceptance cases, and limitations.

### Phase 7: Complete factories and projection

Finalize typed configs, defaults, secret redaction, Rust factories, `CacheView` and clock inputs,
PyO3 registry projection, public package exposure, generated stubs, and boundary tests as applicable.

### Phase 8: Prove conformance

Run deterministic functional/integration scenarios plus applicable data and execution acceptance
tests on testnet or a controlled account. Exercise connection failure, reconnect, shutdown, rate
limits, and recovery, and document every skipped specification case.

### Phase 9: Measure performance and robustness

Benchmark confirmed end-to-end hot paths, then applicable signing/authentication/codecs. Fuzz every
untrusted parser, decoder, normalizer, signer, and encoder with realistic corpora and strong
invariants.

### Phase 10: Finish documentation and operations

Reconcile the capability matrix and document credentials, configuration, limits, reconciliation,
environment differences, tester entry points, generated output, examples, known gaps, and
troubleshooting.

## Rust Usage

### Using Adapters with Rust LiveNode

```rust
use nautilus_common::enums::Environment;
use nautilus_live::node::LiveNode;

let mut node = LiveNode::builder(trader_id, Environment::Live)?
    .add_data_client(None, Box::new(data_factory), Box::new(data_config))?
    .add_exec_client(None, Box::new(exec_factory), Box::new(exec_config))?
    .build()?;

node.add_strategy(MyStrategy::new(config))?;
node.run().await?;
```

### Adapter Factory Pattern (Rust)

Each adapter implements `DataClientFactory`, `ExecutionClientFactory`, or both.
The factories receive typed configuration through `ClientConfig`; data-client
construction also receives a read-only `CacheView` and clock. Register the
concrete venue factories with `LiveNode::builder(...).add_data_client(...)` and
`.add_exec_client(...)` as shown above; do not invent a combined factory trait.

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
#[derive(Debug)]
pub struct YourDataClientFactory;

#[async_trait]
impl DataClientFactory for YourDataClientFactory {
    async fn create(
        &self,
        name: String,
        config: &dyn ClientConfig,
    ) -> anyhow::Result<DataClient> {
        // Downcast the venue config and construct the live data client.
        todo!("construct {name} from the typed config")
    }
}

#[derive(Debug)]
pub struct YourExecutionClientFactory;

#[async_trait]
impl ExecutionClientFactory for YourExecutionClientFactory {
    async fn create(
        &self,
        name: String,
        config: &dyn ClientConfig,
    ) -> anyhow::Result<ExecutionClient> {
        // Downcast the venue config and construct the live execution client.
        todo!("construct {name} from the typed config")
    }
}

let mut node = LiveNode::builder(trader_id, Environment::Live)?
    .add_data_client(data_config, Box::new(YourDataClientFactory))
    .add_exec_client(exec_config, Box::new(YourExecutionClientFactory))
    .build()?;
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

Register adapter factories through Rust-owned configuration and expose only the bounded construction surface through PyO3. Prior Python factory registration is documented in `migration_reference/python/guidance.md`.

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
