# Implementation Manifest — harden-nt-v2-20260919

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

Mission worktree: `/home/mok/projects/nautilus-trader-dev-skill-mission-20260919` (branch `mission/harden-nt-v2-20260919` off `main` at `b0b7dc1`; upstream NautilusTrader untouched, read-only).

## Upstream status

- Pin moved: `5e4be2edbf496afcfc5d0aa3a798496fa4493f2f` → `9bafb63e7d75ab7033aff2e04cd6b4d45d14e9b7` (develop; 178 commits / 1254 paths, eleventh transition recorded in `references/upstream-delta-review.json`).
- Rust toolchain pin: 1.98.1 (unchanged across this transition; upstream `rust-toolchain.toml` identical at both pins).
- Python runtime at pin: `nautilus-trader-2.0.0rc6` built editable (`make sync && make build-debug`, debuginfo disabled) in the disposable checkout `/tmp/nt-disposable-9bafb63e7`; the read-only pinned cache at `~/.cache/nautilus-trader-dev-skill/nautilus_trader-pinned` was checked out at the pin but never built into or committed to during evidence work.
- Workspace dependency versions taught in examples: 0.63 → 0.64.

## Changed paths by Finding ID (one commit per segment)

| Finding | Impact | Commit | Scope |
|---|---|---|---|
| NT-2026-09-19-001 | P1 | d000b4a (+ G2 evidence commit pending) | Pin move: UPSTREAM_COMMIT, delta-review manifest (178 deltas), 22 developer-guide snapshots (3 new pages), CURRENT_SYNC_DATE, citation sweep, version bumps, exec-spec digest fixture, inventory/release-lane fixtures |
| NT-2026-09-19-002 | P1 | d000b4a, 4621ccd | Mirror re-sync: developer-guide snapshot set + curated-mirror pin citations |
| NT-2026-09-19-003 | P1 | 4621ccd | Contracts: callback-dispatch ordering/reentrancy, queued-callback lifecycle, actor state filters, msgbus reentry |
| NT-2026-09-19-004 | P1 | 017196c | OrderBookDepth10 → OrderBookDepth family renames; tardis `"depth"` value; snapshot25 25-level semantics; guard test `tests/test_v2_current_api_spellings.py` |
| NT-2026-09-19-005 | P1 | 017196c | NautilusDataType verified current at pin (no change; guarded) |
| NT-2026-09-19-006 | P1 | d000b4a, 017196c | TestClock → VirtualClock example re-sync; e2e green at pin |
| NT-2026-09-19-007 | P1 | 4621ccd | Order accounting (events() read-only, avg_px fold), reversal-fill split, netting reopen cost |
| NT-2026-09-19-008 | P1 | 4621ccd | Adapter config layouts: Hyperliquid parameter order, Databento/Tardis URL overrides |
| NT-2026-09-19-009 | P2 | 4621ccd | Coverage: Binance RPI, Polymarket v2/session/wallet, Lighter 64-bit/use_gtd, sandbox inbound latency, capnp schemas, Python custom adapters |
| NT-2026-09-19-010 | P2 | 4621ccd | Adapter behavior: OKX recovery/tradeQuoteCcy/DST, Hyperliquid fail-closed/instruments/commission |
| NT-2026-09-19-011 | P2 | 4621ccd | Backtest semantics: precision relaxation, request warnings, trailing-stop policy |
| NT-2026-09-19-012 | P2 | 4621ccd | Serialization: arrow-display feature, catalog validation, Parquet refactor pointer |

## Verification record (this session, at the mission tree)

- `python3 -m pytest -q` (excluding compile/e2e subsets during segment runs): 392 passed, 10 skipped (sanctioned migration-reference and runtime-dependent skips).
- `python3 -m pytest tests/test_rust_first_end_to_end.py -q` with cargo on PATH: 8 passed at pin 9bafb63e7d.
- Validators: `check_dev_guide_sync`, `check_dev_guide_snapshot_sync`, `check_rust_trading_reference_sync`, `check_legacy_labelling`, `check_upstream_freshness --format json`, `check_findings_schema`, `check_governance_receipts` — all exit 0.
- G2: `python3 tools/check_skill_g2_harnesses.py --execute --upstream-root /tmp/nt-disposable-9bafb63e7` — per-skill PASS lines recorded in `references/g2-evidence/*.json` at the new pin (see G2 evidence commit).

spec-deltas: []

## Residuals

NT v2 compatibility note: the legacy v1 items below are migration/reference-only audit context, not active guidance.

- `nt-strategy-builder` remains migration/reference-only by charter.
- Legacy v1 DEX template test skips are sanctioned (NT-2026-09-05-145).
- `references/api_reference/` mirrors were last fully regenerated at pin `4692bac`; this cycle's renames were hand-corrected in the affected book pages and no other stale API surface was identified by the delta review.
