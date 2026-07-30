# Stage 12: Rust Adapter Development

## Goal

Build a Rust-first adapter through NautilusTrader's official ten-phase sequence and stop short of
readiness whenever change-specific acceptance evidence is absent.

## Prerequisites

- Stage 11 completed
- Load `nt-adapters`, `nt-testing`, `nt-dev`, and `nt-dex-adapter` for on-chain venues

## Adapter Architecture

Rust owns protocol transports, parsing, normalization, credentials/signing, instruments, data,
execution, reconciliation, configuration, factories, and live-node registration. PyO3 is an
optional bounded projection for typed configuration, lifecycle control, and diagnostics; it does
not move execution authority into Python.

## Official Ten-Phase Sequence

### Phase 1: Define scope
Record products, environments, capabilities, restrictions, gaps, and the smallest end-to-end slice.

### Phase 2: Build the protocol core
Implement Rust HTTP/WebSocket, credentials/signing, shared types, parsing, retry, and lifecycle.

### Phase 3: Implement instruments
Implement identity, precision, provider loading, caching, and updates.

### Phase 4: Implement market data
Add requests/subscriptions, books, malformed input, unsubscribe, and reconnect behavior.

### Phase 5: Implement execution
Establish account state and reconciliation before commands; cover ambiguous outcomes and reports.

### Phase 6: Add optional venue capabilities
Add advanced orders or product slices only after the base lifecycle is stable.

### Phase 7: Complete factories and projection
Finalize Rust configs/factories, `CacheView`, clock inputs, registry wiring, and optional PyO3.

### Phase 8: Prove conformance
Run deterministic integration/spec scenarios plus controlled-venue acceptance and recovery paths.

### Phase 9: Measure performance and robustness
Benchmark confirmed hot paths and fuzz all untrusted boundaries with strong invariants.

### Phase 10: Finish documentation and operations
Reconcile capabilities and document limits, reconciliation, environments, testers, and diagnosis.

## Rust Tester References

Use the source-pinned Rust nodes under
`skills/nt-adapters/references/examples/rust_adapters/<venue>/node_data_tester.rs` and
`node_exec_tester.rs`. Run the owning testkit crate and the adapter's targeted Cargo commands; do
not infer testnet, resilience, fuzz, or operations readiness from `cargo check`.

## Exercises

1. Produce a capability matrix and initial Rust crate skeleton.
2. Implement deterministic protocol fixtures and one instrument family.
3. Prove one data stream, then one execution command with reconciliation.
4. Complete Rust factories and bounded projection.
5. Run applicable spec, controlled-venue, resilience, fuzz, benchmark, and operations gates.

## Checkpoint

You can build and validate a Rust adapter through all ten phases and state every Pending or Blocked
acceptance gate without overclaiming compilation as production readiness.
