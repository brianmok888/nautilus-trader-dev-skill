# Reconciliation in NautilusTrader

## Purpose

Reconciliation aligns cached orders and positions with venue reports before live
execution continues. It recovers missed events, infers fills only from supported
report evidence, deduplicates recovered events, and rejects contradictory venue
state. This is safety-critical and fail-closed.

## Current Rust ownership

- `crates/execution/src/reconciliation/orders.rs` owns order-event reconciliation,
  including inferred fill creation through `create_inferred_fill`.
- `crates/execution/src/reconciliation/positions.rs` owns position reconciliation
  and tolerance checks.
- `crates/live/src/node/mod.rs` orchestrates startup reconciliation.
- `crates/network/src/retry.rs` provides `RetryManager` and `RetryError` for
  bounded retry policy; adapters must not add independent infinite retry loops.

Historical Python reconciliation and retry implementations are migration/reference-only;
current implementation ownership is Rust-only at the paths above.

## Startup contract

`LiveNodeConfig` owns reconciliation enablement, lookback windows, and timeouts;
`LiveNodeBuilder` wires those settings into the node. Startup fetches execution
reports and reconciles them before accepting new order flow. A reconciliation
failure or timeout aborts startup; it must not log-and-continue into an unknown
execution state.

Use venue order IDs, client order IDs, trade IDs, timestamps, quantities, and
instrument/account identity together. A missing field must not be guessed when
multiple outcomes are possible. Report duplicates are idempotent; conflicting
reports are errors.

## Adapter requirements

1. Persist submit/modify/cancel intent and all venue identifiers.
2. Treat transport timeout as an unknown outcome, not proof of rejection.
3. Query the venue before retrying a non-idempotent operation.
4. Emit recovered events once and in causal order.
5. Reconcile persisted state after restart before enabling submission.
6. Bound retries and surface exhaustion as an explicit terminal error.

## Testing

Cover accepted-but-response-lost, partial fill then cancel, replace races,
duplicate reports, out-of-order reports, unknown venue orders, position drift,
startup timeout, and restart recovery. Subscribe to the exact event/state change
before triggering the action; use a bounded timeout only as a failure guard.
