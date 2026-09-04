NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Betfair

This page is superseded by `betfair_v2.md`, the primary Betfair guide.

NT v2 compatibility note: the pinned upstream Betfair guide is the current v2 guidance.
`docs/integrations/betfair.md` in the read-only pinned snapshot (pin `4692bac`) documents the
Rust adapter implemented in Rust and exposed to Python at `nautilus_trader.adapters.betfair`,
with `BetfairDataClientFactory`/`BetfairExecutionClientFactory` and a `LiveNode.builder(...)`
configuration example. It is authoritative current guidance, not legacy history.

- Current Betfair work: follow the pinned upstream guide above; Rust-vs-historical differences
  and migration context are tracked in [`betfair_v2.md`](betfair_v2.md) against pin `4692bac`.
- Betfair terminal-order-identity behavior landed upstream at commit `8ecab1ce9`
  ("Retain Betfair terminal order identity"), included in the pin.
- NT v2 compatibility note: v1 → v2 migration material lives under
  `skills/nt-strategy-builder/migration_reference/python/` (migration/reference-only).
