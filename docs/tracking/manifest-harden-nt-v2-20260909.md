# Implementation Manifest — harden-nt-v2-20260909

Mission worktree: `/home/mok/projects/nautilus-trader-dev-skill-mission-20260909` (branch off main; upstream NautilusTrader untouched, read-only).

## Upstream status

- Pin moved: `c1a2310144` → `5e4be2edbf496afcfc5d0aa3a798496fa4493f2f` (develop; 28 commits / 422 paths, delta review in `references/upstream-delta-review.json`).
- Rust toolchain pin: 1.98.1 (required by upstream `rust-toolchain.toml` at the new pin).
- Python runtime at pin: `nautilus-trader-2.0.0rc5` built editable (`make sync && make build-debug`) in the disposable checkout `/home/mok/projects/nt-disposable-5e4be2e`; the read-only pinned cache was never written.

## Changed paths by Finding ID (one commit per segment)

| Finding | Impact | Commit | Scope |
|---|---|---|---|
| NT-2026-09-09-001 | P1 | 71c11f0, 1e90b16, 285a34d, da635d4, 37cbe80 | Pin move + citation-layer refresh + all 17 G2 evidence files regenerated (nt.json and nt-adapters.json in 285a34d; remaining 15 in da635d4) |
| NT-2026-09-09-002 | P1 | 98fdc40 | nt-dev toolchain guidance → 1.98.1 |
| NT-2026-09-09-003 | P1 | f71e126 | concepts: Python component topic-messaging facade |
| NT-2026-09-09-004 | P1 | e107ed2 | adapters: CommandFailure classification |
| NT-2026-09-09-005 | P1 | 85a402b | adapters: Bybit depth-1 quotes, shared topic ownership |
| NT-2026-09-09-006 | P1 | 1fa94e4 | adapters: Binance partial-depth snapshots |
| NT-2026-09-09-007 | P1 | 37a9d62 | adapters: Hyperliquid normalization-off local validation |
| NT-2026-09-09-008 | P1 | ccd2778 | testing: test-data preparation split |
| NT-2026-09-09-009 | P2 | 672dc93 | trading: reduce-only maintenance + OUO propagation |
| NT-2026-09-09-010 | P2 | 9bee2cf | concepts: subscription retirement/disposal |
| NT-2026-09-09-011 | P2 | af9dd0a | adapters: OKX RPI min-notional + account config |
| NT-2026-09-09-012 | P2 | f423352 | data: Postgres insert-or-replace semantics |
| NT-2026-09-09-013 | P2 | 9fee972 | nt-dev: PyO3 stale-export cleanup, Fish guidance |
| NT-2026-09-09-014 | P2 | bce1ec5 | data: fixed-point effective-scale contract |
| NT-2026-09-09-015 | P2 | be255a0 | testing: adapter env isolation + network CI gate |
| NT-2026-09-09-016 | P2 | 4cadd80 | architect: DST network simulation seams |
| NT-2026-09-09-017 | P2 | 30661f0 | concepts: instrument notional bounds |

Governance receipts: 17 phase-2 receipts under `docs/tracking/receipts/harden-nt-v2-20260909/` (commit 285a34d); the repository-wide total across all missions is 350, per `python3 tools/check_governance_receipts.py`.

## Tests and manual exercises (actual results, current tree)

- `python3 tools/check_governance_receipts.py` — validated 350 governance receipts.
- `python3 tools/check_upstream_freshness.py --format json` — exit 0 (pin == develop tip).
- `python3 tools/check_dev_guide_sync.py` — passed.
- `python3 tools/check_rust_trading_reference_sync.py` — passed.
- `python3 tools/check_legacy_labelling.py` — passed; `tests/test_legacy_labelling.py` — 32 passed.
- `python3 tools/check_skill_g2_harnesses.py --upstream-root /home/mok/projects/nt-disposable-5e4be2e --check-cards --check-card-declarations` — exit 0.
- G2 harnesses (execute mode, disposable at 5e4be2e, venv 2.0.0rc5): **17/17 PASS**, evidence regenerated in `references/g2-evidence/*.json` (nt-strategy-builder contract + upstream acceptance: 99 passed, 6 skipped — post-cutover skips expected).

## Tracker updates

`docs/tracking/Findings.md`: all 17 mission findings `[CLOSED 2026-09-09]` with per-segment correction deltas appended.

## Review findings resolved

Gate-card and declaration consistency re-checked after the evidence refresh (`--check-cards --check-card-declarations`, exit 0). No outstanding review findings.

## Spec deltas

spec-deltas: []
