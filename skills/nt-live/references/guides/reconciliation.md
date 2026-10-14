# Reconciliation in NautilusTrader

## Reconciliation at reviewed tip `52eef7955c`

The current guide is `docs/concepts/execution/reconciliation.md`, organized
by [what runs](https://nautilustrader.io/docs/latest/concepts/execution/reconciliation/#what-runs),
[operational use](https://nautilustrader.io/docs/latest/concepts/execution/reconciliation/#operational-use)
and [reconciliation algorithm](https://nautilustrader.io/docs/latest/concepts/execution/reconciliation/#reconciliation-algorithm).
Use the current [fill and position reconciliation](https://nautilustrader.io/docs/latest/concepts/execution/reconciliation/#fill-and-position-reconciliation)
and [price metadata](https://nautilustrader.io/docs/latest/concepts/execution/reconciliation/#reconciling-positions-with-prices) sections.
Order/fill evidence normally precedes position inference. A missing position
report is not evidence of flat exposure: explicitly bounded historical fills
without an in-scope position report update orders only, not positions or portfolio
economics. Empty-cache position recovery without order/fill history requires
`avg_px_open`. Disabling `generate_missing_orders` does not bypass startup
validation; report/instrument filters still apply.

`PositionStatusReport.avg_px_open_reconciliation` defaults to MATCH.
OPENING_ONLY marks a differently computed entry average (for example remaining
FIFO lots), skips the side's startup entry-price comparison but retains quantity
checks. Opening/reversing uses the reported average; increasing/reducing uses
the cached average, so reduction does not book synthetic trading PnL. One
OPENING_ONLY report makes the whole side's weighted average incomparable.
`avg_px_open_precision` adds one unit at the side's coarsest declared precision
to the 0.01% comparison tolerance. Synthetic fills cannot reconstruct missing
historical PnL. Reconciliation drops a FillReport when its trade ID is already
recorded, even if price/quantity differs. Same-trade price restatement belongs
to the core OrderFilled stream, not this report path; order avg_px alone cannot
establish it. Synthetic fills cannot reconstruct
unknown fee history. Sources: upstream
`docs/concepts/execution/{index,reconciliation}.md`.

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
