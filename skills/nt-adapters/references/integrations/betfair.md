NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Betfair (cleared v1 guide)

NT v2 compatibility note: this v1 guide is superseded by `betfair_v2.md` as the primary
Betfair guide for all current Rust v2 work (user-directed cutover, 2026-08-26). The v1
Python-adapter wiring content that lived here was cleared; it is migration/reference-only
history, never a production path.

- All current Betfair work: [`betfair_v2.md`](betfair_v2.md) — the Rust adapter surface
  (`crates/adapters/betfair`), tracked against the pinned baseline `ac22d5cf4`.
- NT v2 compatibility note: the pinned upstream `docs/integrations/betfair.md` (pin `ac22d5cf`)
  is the current v2 Rust-adapter guide (Rust adapter exposed to Python at
  `nautilus_trader.adapters.betfair`); treat it as the authoritative upstream reference, not
  v1 wiring history.
- Betfair terminal-order-identity behavior landed upstream at commit `8ecab1ce9`
  ("Retain Betfair terminal order identity"), included in the pin.
- NT v2 compatibility note: v1 → v2 migration material lives under
  `skills/nt-strategy-builder/migration_reference/python/` (migration/reference-only).
