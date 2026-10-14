---
mission: nt-v2-hardening-20261014
status: implemented-pending-shipping-approval
spec-deltas: []
---

# NT V2 hardening implementation manifest

NT v2 compatibility note: legacy Cython/v1 terms and references/guides path fragments in this whole file are migration/reference-only audit citations, not production routing; prefer current Rust v2/PyO3 and LiveNode guidance.

## Baseline and boundaries

- Mission worktree: `mission/harden-nt-v2-20261014`, based on `5d1dd11`; Phase 1 findings commit: `f62b950`.
- Upstream baseline: `81d0449da0e353d702d88019dc73d231d67923cd` to `52eef7955cbdb8d95667c838c3e43907e0da8e9a`: 292 reviewed commits and 1,578 unique paths.
- Upstream source remains unchanged. The disposable writable checkout owns all builds.
- Shipping remains unapproved; this manifest is not a merge, push, or release authorization.

## Finding-specific implementation map

| Finding | Primary changed or verified surface | Required verification |
| --- | --- | --- |
| NT-2026-10-14-001 | `skills/nt-dev/references/guides` / `releases.md:86` | `python3 -m pytest -q tests/test_v2_inventory_pins_versions.py` green against the moved pin; no `2.0.0rc5` claims remain under `skills/nt-dev`. |
| NT-2026-10-14-002 | `tools/upstream_baseline.py:3` | `python3 tools/check_upstream_freshness.py --format json` exits 0; `python3 tools/check_dev_guide_snapshot_sync.py` passes; `python3 tools/check_skill_g2_harnesses.py --check-cards --check-card-declarations` passes. |
| NT-2026-10-14-003 | `skills/nt-signals/references/guides` / `indicators_guide.md:60` | overlay pinned by `tests/test_v2_current_develop_overlays.py`; constructor claims verified against tip source. |
| NT-2026-10-14-004 | `skills/nt-model/references/api/model/tick_scheme.md:3` | overlay present and cited from the model skill; export list verified at tip. |
| NT-2026-10-14-005 | `skills/nt-testing/references/guides` / `spec_data_testing.md:845` | overlay present; types verified at tip. |
| NT-2026-10-14-006 | `skills/nt-live/SKILL.md:342` | overlay present in live skill; config field verified at tip. |
| NT-2026-10-14-007 | `skills/nt-data/references/guides` / `cache_operations.md:342` | overlay present; record types verified at tip. |
| NT-2026-10-14-008 | `skills/nt-backtest/SKILL.md:57` | overlay present; symbols verified at tip. |
| NT-2026-10-14-009 | `skills/nt-trading/SKILL.md:306` | overlay present; restatement module verified at tip. |
| NT-2026-10-14-010 | `skills/nt-data/SKILL.md:180` | overlay present; config struct verified at tip. |
| NT-2026-10-14-011 | `skills/nt-dev/SKILL.md:295` | no `3.12-3.14` support claims remain; requires-python claim matches tip. |
| NT-2026-10-14-012 | `skills/nt-dev/SKILL.md:296` | no unscoped `1.98.1` claims remain in current-development guidance; tokens updated in validators and tests. |
| NT-2026-10-14-013 | `skills/nt-backtest/references/guides` / `benchmarking.md:210` | guide no longer provisions env-v2 with Python 3.12. |
| NT-2026-10-14-014 | `skills/nt-data/references/concepts/data.md:632` | local concept text no longer claims migration-free legacy catalog operation; migration workflow referenced. |
| NT-2026-10-14-015 | `skills/nt-data/references/concepts/data.md:769` | storage-option table matches the tip contract; rejection rules stated. |
| NT-2026-10-14-016 | `skills/nt-data/references/concepts/data.md:819` | overlay present; codec mapping verified at tip. |
| NT-2026-10-14-017 | `skills/nt-model/references/guides` / `value_type_patterns.md:443` | both files carry the precision-boundary qualification. |
| NT-2026-10-14-018 | `skills/nt-trading/references/concepts/execution.md:462` | execution concept carries the qualified contract. |
| NT-2026-10-14-019 | `skills/nt-trading/references/concepts/orders.md:46` | caveat present in orders concept. |
| NT-2026-10-14-020 | `skills/nt-trading/references/concepts/positions.md:404` | caveat present in positions concept. |
| NT-2026-10-14-021 | `skills/nt-live/SKILL.md:300` | live skill carries the semantics. |
| NT-2026-10-14-022 | `skills/nt-live/references/guides` / `reconciliation.md:27` | reconciliation guide carries the contracts. |
| NT-2026-10-14-023 | `skills/nt-testing/references/guides` / `testing.md:153` | testing guide carries the current-develop note. |
| NT-2026-10-14-024 | `skills/nt-dev/references/guides` / `rust_conventions.md:1` | rule present in nt-dev conventions. |
| NT-2026-10-14-025 | `tools/check_dev_guide_snapshot_sync.py:60` | `python3 tools/check_dev_guide_snapshot_sync.py` passes at the moved pin. |
| NT-2026-10-14-026 | `skills/nt-data/references/concepts/data.md:392` | data concepts carry the zoned-time guidance. |
| NT-2026-10-14-027 | `skills/nt-model/references/concepts/instruments.md:154` | instruments concept carries the registration workflow. |
| NT-2026-10-14-028 | `skills/nt-signals/references/guides` / `indicators_guide.md:280` | example threshold matches the v2 scale. |
| NT-2026-10-14-029 | `references/integrations/derive.md:80` | overlay present in both mirrors; no unscoped v2 endpoint claims remain. |
| NT-2026-10-14-030 | `references/integrations/derive.md:26` | overlay present; recovery contracts stated. |
| NT-2026-10-14-031 | `references/integrations/polymarket.md:738` | current-develop Polymarket guidance no longer teaches RTDS as current. |
| NT-2026-10-14-032 | `references/integrations/polymarket.md:734` | mirrored execution sections carry the refreshed contracts. |
| NT-2026-10-14-033 | `references/integrations/lighter.md:79` | limitations section matches the tip contract. |
| NT-2026-10-14-034 | `references/integrations/kraken.md:248` | Kraken mirror carries the checksum and history contracts. |
| NT-2026-10-14-035 | `references/integrations/hyperliquid.md:354` | Hyperliquid mirror carries the refreshed contracts. |
| NT-2026-10-14-036 | `references/integrations/bybit.md:23` | Bybit mirror carries the additions. |
| NT-2026-10-14-037 | `references/integrations/blockchain.md:1` | blockchain mirror carries the retention contract. |
| NT-2026-10-14-038 | `references/integrations/architect_ax.md:22` | AX mirror carries the additions. |
| NT-2026-10-14-039 | `references/integrations/betfair_v2.md:1` | betfair_v2 overlay records the reviewed commits. |
| NT-2026-10-14-040 | `references/integrations/databento.md:17` | Databento mirror carries the additions. |
| NT-2026-10-14-041 | `references/integrations/tardis.md:5` | Tardis mirror carries the requirement. |
| NT-2026-10-14-042 | `references/integrations/index.md:10` | both inventories list CoinAPI. |
| NT-2026-10-14-043 | `references/integrations/ib.md:73` | IB mirror carries the migration note. |
| NT-2026-10-14-044 | `references/integrations/okx.md:40` | OKX mirror carries the new defaults. |
| NT-2026-10-14-045 | `references/integrations/binance.md:5` | examples match the tip syntax. |
| NT-2026-10-14-046 | `skills/nt-strategy-builder-rust/SKILL.md:104` | trait sketch matches the pinned trait; no `external_order_claims` declarations remain in current guidance. |
| NT-2026-10-14-047 | `skills/nt-strategy-builder-rust/SKILL.md:263` | guidance states the split explicitly. |
| NT-2026-10-14-048 | `skills/nt-signals/SKILL.md:196` | claim removed; registration taught on Portfolio. |
| NT-2026-10-14-049 | `skills/nt-data/SKILL.md:155` | ordering claim corrected. |
| NT-2026-10-14-050 | `tools/check_legacy_labelling.py:44` | python3 -m pytest -q tests/test_legacy_labelling.py and python3 tools/check_legacy_labelling.py both exit 0. |
| NT-2026-10-14-051 | `skills/nt-testing/SKILL.md` | bounded Price property example compiles at the pin. |
| NT-2026-10-14-052 | `skills/nt-implement/SKILL.md` | distinct py_value binding follows the pinned getter pattern. |
| NT-2026-10-14-053 | `skills/nt-backtest/SKILL.md` | Instrument trait imported for fill-model methods. |
| NT-2026-10-14-054 | `skills/nt-data/SKILL.md` | built BarDataWrangler API exercised successfully. |
| NT-2026-10-14-055 | `skills/nt-adapters/SKILL.md` | built external factory classes exercised successfully. |
| NT-2026-10-14-056 | `skills/nt-adapters/references/guides` / `official_adapter_spec.md` | Rust data/execution phases match the pinned ownership contract. |
| NT-2026-10-14-057 | `skills/nt-learn/curriculum/11-testing-quality.md` | audit premise retracted: BitMEX tester mirrors exist and references restored; cutover and link suites pass. |
| NT-2026-10-14-058 | `skills/nt-model/SKILL.md` | signed Price/Money and unsigned Quantity distinction verified at the pin. |
| NT-2026-10-14-059 | `skills/nt-signals/SKILL.md` | registration receiver corrected to DataActorCore; 122 routing/guidance tests passed. |
| NT-2026-10-14-060 | `skills/nt-strategy-builder/SKILL.md` | BacktestEngine/BacktestNode vs LiveNode routing split verified; 122 routing tests passed. |

## Evidence observed so far

- Pinned Python build: `make build-debug` exited 0. Prior disk-exhausted attempts are failures, not evidence. Mission incremental intermediates were removed after installing the built runtime.
- Python migration G2: 113 passed, 6 skipped; the scoped strategy contract separately passed 3 tests.
- Audit corrections and sync tests: 117 passed; Findings schema passed.
- Guide/routing/quality regressions: 80 passed, 3 skipped before the final legacy-symbol correction.
- Legacy validator correction: failing current Derive V3 export regression observed; all 33 legacy tests, legacy validator, and developer-guide sync then passed.
- Built-runtime manual exercise: BarDataWrangler with a bar-type string and both external adapter factory classes passed.
- Additional root-skill audit corrections: 125 existing regression/quality tests passed; subsequent finding/legacy checks passed with 51 tests.

- Final G2 regeneration over the finalized readiness cards: full harness execution exited 0 for all 17 skills at 52eef7955c; card validation follows in the closing battery.
- Complete artifact audit closed with all 651 inventoried artifacts reviewed (470 full reads, 157 byte-identical upstream snapshots, 23 label-normalized snapshots, 1 structural JSON review); zero unreviewed entries.
- All 60 findings closed with per-finding phase-3-specific receipts (490 governance receipts validated).

## Source-review corrections

Initial review reports contained API mistakes corrected against actual pinned source: ROC public constructor retains Option<bool>; option identity uses OptionContractSpec/OptionInstrumentId; calendar configuration is time_bars_time_zone; reconciliation uses avg_px_open_reconciliation; PositionAdjusted has no balance_impact; tick schemes have no Python unregister export. Rust ibapi is 5.0.0 while the Python package remains 4.0.1.

