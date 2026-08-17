NT v2 compatibility note: this file is a migration/reference-only Python curriculum snapshot. Do not use it for new work; the active curriculum is Rust-first.

# Stage 12: Adapter Development

## Goal

Build a complete adapter for a new exchange or data provider, following NautilusTrader's official adapter specification.

## Prerequisites

- Stage 11 completed (can write all types of tests)
- Deep understanding of Rust async programming
- Familiarity with WebSocket and HTTP client patterns
- Understanding of the NT domain model (nt-model)

## Concepts

### Adapter Architecture

Adapters follow a layered architecture:
- **Rust core** — HTTP/WebSocket clients, parsing, rate limiting
- **Python layer** — integration with NT data and execution engines

### Adapter Implementation Sequence

| Phase | Focus | Key Files |
|-------|-------|-----------|
| 1 | Define scope | Capability matrix, environments, known gaps, test plan |
| 2 | Build the protocol core | HTTP/WebSocket, credentials, signing, parsing, lifecycle |
| 3 | Implement instruments | Instrument parsing, provider, symbol mapping, precision |
| 4 | Implement market data | Requests, subscriptions, books, reconnect behavior |
| 5 | Implement execution | Account state, commands, reports, reconciliation |
| 6 | Add optional venue capabilities | Advanced orders and product-specific slices |
| 7 | Complete factories and projection | Rust configs/factories, PyO3 registry when supported |
| 8 | Prove conformance | Functional/integration specs plus controlled-venue acceptance |
| 9 | Measure performance and robustness | Benchmarks, fuzzing, recovery invariants |
| 10 | Finish documentation and operations | Capability matrix, limits, tester entry points, troubleshooting |

### Phase 1: Define scope

Record the capability matrix, environments, protocol boundaries, known gaps, and smallest
end-to-end slice.

### Phase 2: Build the protocol core

Build deterministic HTTP/WebSocket protocol clients, credentials/signing, parsers, retry
classification, and lifecycle behavior in Rust.

### Phase 3: Implement instruments

Implement complete instrument identity, precision, provider loading, caching, and updates.

### Phase 4: Implement market data

Add advertised requests and subscriptions with snapshot/delta, unsubscribe, malformed-input, and
reconnect coverage.

### Phase 5: Implement execution

Establish account state, private streams, reconciliation, commands, ambiguous outcomes, and status
reports.

### Phase 6: Add optional venue capabilities

Add advanced orders, batches, or product-specific data only after the base lifecycle is stable.

### Phase 7: Complete factories and projection

Finalize typed Rust configs/factories and bounded PyO3 registry projection when supported.

### Phase 8: Prove conformance

Run deterministic functional/integration scenarios and applicable tester specs on testnet or a
controlled account, including failure and recovery paths.

### Phase 9: Measure performance and robustness

Benchmark proven hot paths and fuzz every untrusted parser, normalizer, signer, and encoder.

### Phase 10: Finish documentation and operations

Reconcile the capability matrix and document configuration, limits, reconciliation, environments,
tester entry points, known gaps, and troubleshooting.

### Directory Structure

```
crates/adapters/your_adapter/
├── src/
│   ├── common/       # Shared types, credential, enums, parsing
│   ├── http/         # HTTP client, models, parsing, query
│   ├── websocket/    # WS client, messages, parsing, dispatch
│   ├── python/       # PyO3 bindings
│   ├── config.rs     # Adapter configuration
│   ├── factories.rs  # Client factories
│   └── lib.rs        # Crate root
├── tests/            # Integration tests
└── Cargo.toml
```

### Key Patterns

**Message routing**: `raw → msg → out` naming convention
- `raw`: Raw bytes from WebSocket
- `msg`: Parsed venue-specific message
- `out`: Nautilus domain model

**HTTP client**:
```rust
pub struct HttpClient {
    client: reqwest::Client,
    credential: Credential,
    rate_limit: RateLimit,
}
```

**WebSocket client**:
```rust
pub struct WebSocketClient {
    url: Url,
    credential: Credential,
    subscription_state: Shared<SubscriptionState>,
}
```

**Config pattern**: `{Venue}DataClientConfig`, `{Venue}ExecClientConfig`, `{Venue}InstrumentProviderConfig`

### Testing Your Adapter

Use the official testing specs:

```python
# Data testing
DataTesterConfig(client_id, instrument_ids).with_subscribe_trades()
DataTesterConfig(client_id, instrument_ids).with_subscribe_book_deltas(book_type=BookType.L2_MBP)

# Execution testing
ExecTesterConfig(strategy_id, instrument_id, client_id, order_qty).with_enable_limit_buys()
ExecTesterConfig(strategy_id, instrument_id, client_id, order_qty).with_test_reject_post_only()
```

## Exercises

1. **Study an existing adapter**: Read through `crates/adapters/binance/` and trace the data flow
2. **Implement Phase 1**: Create HTTP error types, client, and basic parsing for a test venue
3. **Add instruments**: Implement `InstrumentProvider` for your test venue
4. **Data subscriptions**: Add WebSocket subscription for trade ticks
5. **Write tests**: Create DataTesterConfig tests for your adapter
6. **Documentation**: Add Rust doc comments to all public types

## Checkpoint

You can:
- Build a new adapter following the official ten-phase implementation sequence
- Structure Rust code following NT conventions
- Wire adapter into LiveNode via factory pattern
- Write DataTesterConfig and ExecTesterConfig validation
- Document adapter code following NT standards

## Key Skills

- `nt-adapters` — full adapter architecture and patterns
- `nt-testing` — adapter testing specs
- `nt-dev` — coding standards, Rust conventions

## Next

You are now a NautilusTrader developer! 🎉

Continue contributing by:
- Adding features to existing adapters
- Improving test coverage
- Contributing to core Rust or Python modules
- Writing documentation and examples
