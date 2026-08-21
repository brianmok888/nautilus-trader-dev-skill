# Findings — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Current evidence-backed findings and closure state. -->
<!-- Does NOT contain: session history, plans, or external attestations. -->

Review date: 2026-08-21
Reviewed upstream develop: `2114cf6f761429e0adb5ca9596fcd7b895b16011`
Pinned G2 baseline: `6e59fd74eaacacbb7410936f1766bd89fcce6f59`

NT v2 compatibility note: Legacy migration/reference-only Cython v1 terms and obsolete `references/guides` paths in this whole file are audit evidence, not active guidance.

## Open findings

[NT-2026-08-21-01] [P1] [CLOSED] V2 compliance: Lighter integration guides teach the removed `--run`/`--live-orders` tester opt-in convention that current develop replaced with immediate startup.
  file: skills/nt-adapters/references/integrations/lighter.md:34
  evidence: upstream commits `e8daa045ab` and `7214db4239` standardized Python testers for immediate startup; develop tip `docs/integrations/lighter.md:36-50` documents module-level constants with the execution tester placing real orders by default (`dry_run=False`) and a top-of-module warning.
  fix: update both guide copies to the current tester convention (module-level constants, immediate connect on run, explicit `dry_run=False` warning) with a develop-only boundary note.
  closure: `grep -n '--run\|--live-orders' skills/nt-adapters/references/integrations/lighter.md references/integrations/lighter.md` returns no active-convention teaching and `python3 tools/check_legacy_labelling.py` passes.
  closure: `python3 -m pytest -q tests/test_v2_guidance_hardening.py::test_lighter_guides_teach_current_tester_startup_convention` passes; `python3 tools/check_legacy_labelling.py` passes.

[NT-2026-08-21-02] [P1] [CLOSED] V2 compliance: adapter spec names removed `WebSocketConfig.heartbeat_msg`; current develop renamed it `heartbeat_payload` (with `heartbeat` → `heartbeat_interval_secs`).
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:1074
  evidence: upstream commits `74d57e7e05` and `70ce722a4e`; RELEASES notes "Changed `WebSocketConfig.heartbeat` to `heartbeat_interval_secs` and `heartbeat_msg` to `heartbeat_payload`".
  fix: rename the field in the text-ping guidance and add a develop-only boundary note (pinned baseline retains the old spelling).
  closure: `grep -n 'heartbeat_msg' skills/nt-adapters/references/guides/official_adapter_spec.md` returns no uncorrected hit.
  closure: `python3 -m pytest -q tests/test_v2_guidance_hardening.py::test_network_config_guides_use_current_field_names` passes; no uncorrected `heartbeat_msg` hit in the spec.

[NT-2026-08-21-03] [P1] [CLOSED] V2 compliance: Betfair integration references teach removed `stream_idle_timeout_ms`; current develop renamed the pair to `stream_heartbeat_secs`/`stream_heartbeat_timeout_secs`.
  file: skills/nt-adapters/references/integrations/betfair_v2.md:279
  evidence: upstream commit `74d57e7e05` renamed `crates/adapters/betfair/src/config.rs:85-86` to `stream_heartbeat_secs` and `stream_heartbeat_timeout_secs`; the same stale table is mirrored at `references/integrations/betfair_v2.md:279` and `:306`.
  fix: update both config tables with the current field names and a develop-only boundary note.
  closure: `grep -rn 'stream_idle_timeout_ms' skills/ references/` returns no uncorrected hit.
  closure: `python3 -m pytest -q tests/test_v2_guidance_hardening.py::test_network_config_guides_use_current_field_names` passes; `grep -rn 'stream_idle_timeout_ms' skills/ references/` returns only the boundary note's pre-rename wording.

[NT-2026-08-21-04] [P1] [CLOSED] Validation: durable G2 evidence hashes are stale for nt-architect, nt-implement, and nt-review, leaving the repository red on main.
  evidence: `python3 tools/check_skill_g2_harnesses.py --check-cards` exits 1 naming those three skills at baseline `bd8118a8`; `python3 -m pytest -q` fails `tests/test_skill_g2_harnesses.py::test_current_readiness_evidence_matches_owned_content` (1 failed, 470 passed).
  fix: re-execute the three harnesses via `python3 tools/check_skill_g2_harnesses.py --execute --skill <skill>` against the pinned upstream to regenerate evidence with current owned-content hashes.
  closure: `--check-cards` exits 0 and the pytest evidence test passes.
  closure: `python3 tools/check_skill_g2_harnesses.py --check-cards` and `--check-card-declarations` exit 0; `python3 -m pytest -q` reports 475 passed.

[NT-2026-08-21-05] [P2] [CLOSED] Improvement: current-develop `LiveNode` Python hosted async execution (`run_async` owned/hosted run modes) is not covered by live-operation guidance.
  evidence: upstream commit `e166a5e57c` adds `LiveNode.run_async` and replaces Python `start`/`poll` with owned and hosted run modes (docs/concepts/python.md, docs/concepts/live.md).
  fix: add a develop-only overlay note to the live-operation skill describing hosted async execution and its blocking-cache restriction.
  closure: the overlay section exists citing commit `e166a5e57c` and `python3 tools/check_legacy_labelling.py` passes.
  closure: `python3 -m pytest -q tests/test_v2_guidance_hardening.py::test_live_guide_covers_hosted_async_run_modes` passes; `python3 tools/check_legacy_labelling.py` passes.

[NT-2026-08-21-06] [P2] [CLOSED] Improvement: the fallible `ExecutionClient::calculate_commission` contract (fail-closed on `Err`) is not covered by adapter guidance.
  evidence: upstream commit `68975d9347` changed the hook to `anyhow::Result<Option<Money>>` and documented fail-closed commission semantics in `docs/developer_guide/adapters.md`.
  fix: add a develop-only overlay note to the adapter spec commission guidance describing the three outcomes and the fail-closed rule.
  closure: the overlay section exists citing commit `68975d9347`.
  closure: `python3 -m pytest -q tests/test_v2_guidance_hardening.py::test_adapter_spec_covers_fallible_commission_contract` passes.

[NT-2026-08-21-07] [P2] [OPEN] Pin deferral: the reproducible G2 pin `6e59fd74` is 560 commits behind reviewed develop tip `2114cf6f`.
  evidence: `python3 tools/check_upstream_freshness.py --format json` reports develop `drifted`, `commits_ahead` 560, `pinned_is_ancestor` true, manifest reviewed through `2114cf6f`.
  fix: move `UPSTREAM_COMMIT` to the reviewed tip and refresh every pin-citing layer when a full G2 re-execution window is available; until then no gate `Pass` claim may depend on behavior newer than the pin.
  closure: pin equals the reviewed tip with all 17 G2 evidence files re-executed, or a dated re-run decision supersedes this record.

## Follow-up TODO

- [ ] [NT-2026-08-21-07] Move the G2 pin to the reviewed develop tip and re-execute all 17 harnesses (target re-run date: 2026-09-21).

## Closed findings

[NT-2026-08-16-01] [P0] [CLOSED] Rust conversion correctness: custom-data guidance falsely describes current custom data as Python-only and recommends Python by default.
  file: skills/nt-signals/references/guides/custom_data_patterns.md:302
  evidence: upstream `03062cce6372d3c7e9044b39b181a50cc07a067e` defines Rust `CustomDataTrait`/`CustomData` in `crates/model/src/data/custom.rs:386` and the bounded Python registration API in `crates/model/src/python/data/mod.rs:514`.
  fix: replace the Python-only default with Rust-first `CustomDataTrait`/`CustomData` guidance and describe `register_custom_data_class` only as the explicit Python-defined boundary.
  closure: `python3 -m pytest -q tests/test_v2_guidance_hardening.py` and no active Python-only/default claim at the recorded file lines.

[NT-2026-08-16-02] [P1] [CLOSED] V2 path drift: the DEX skill names removed `nautilus_trader/adapters/_template` as the canonical adapter skeleton.
  file: skills/nt-dex-adapter/SKILL.md:253
  evidence: upstream `03062cce6372d3c7e9044b39b181a50cc07a067e` has no such path; `docs/developer_guide/adapters.md:104` places Rust adapters under `crates/adapters/<adapter>` and Python projections under `python/nautilus_trader/adapters/<adapter>`.
  fix: point to the current Rust adapter layout and wiring guidance.
  closure: `test ! -e "$NT_UPSTREAM_ROOT/nautilus_trader/adapters/_template"` and the stale path is absent from the skill.

[NT-2026-08-16-03] [P1] [CLOSED] V2 path drift: execution-algorithm guidance names nonexistent `crates/exec-algo`.
  file: skills/nt-implement/SKILL.md:163
  evidence: upstream `03062cce6372d3c7e9044b39b181a50cc07a067e` defines `ExecutionAlgorithm` in `crates/trading/src/algorithm/mod.rs:91` and integrates it in `crates/live/src/node/mod.rs:116`.
  fix: route ownership to `crates/trading/src/algorithm/` and current LiveNode integration.
  closure: the obsolete path is absent and `python3 -m pytest -q tests/test_v2_guidance_hardening.py` passes.

[NT-2026-08-16-04] [P1] [CLOSED] V2 path drift: backtest guidance treats `matching_core.rs` as a directory and recommends an unsupported arbitrary extension point.
  file: skills/nt-backtest/SKILL.md:297
  evidence: upstream `03062cce6372d3c7e9044b39b181a50cc07a067e` owns matching core at `crates/execution/src/matching_core.rs:1`; no `matching_core/` directory exists.
  fix: use the exact file path and require changes to follow existing matching-engine contracts rather than advertising an extension point.
  closure: the stale directory path is absent and `python3 -m pytest -q tests/test_v2_guidance_hardening.py` passes.

[NT-2026-08-16-05] [P1] [CLOSED] V2 path drift: duplicated DST guidance names removed `crates/live/src/manager.rs`.
  file: skills/nt-adapters/references/guides/rust.md:543
  evidence: upstream `03062cce6372d3c7e9044b39b181a50cc07a067e` has no such file; the same stale claim exists at `skills/nt-dev/references/guides/rust_conventions.md:543`.
  fix: synchronize both copies to the actual current `check-dst-conventions` scope.
  closure: `python3 tools/check_dev_guide_sync.py --check` passes and the stale path is absent.

[NT-2026-08-16-06] [P1] [CLOSED] NT v2 compatibility note: removed migration-link drift in four instrument references targets the historical Cython `margin.pyx` path although margin accounting is Rust/PyO3.
  file: skills/nt-model/references/concepts/instruments.md:308
  evidence: upstream `03062cce6372d3c7e9044b39b181a50cc07a067e` defines `MarginAccount` in `crates/model/src/accounts/margin.rs:67` and its PyO3 surface in `crates/model/src/python/account/margin.rs:37`; duplicates exist in nt-architect, nt-implement, and nt-review.
  fix: replace every removed Cython link with the current Rust implementation and PyO3 binding paths.
  closure: `python3 tools/check_legacy_labelling.py` passes and no `accounting/accounts/margin.pyx` link remains.

[NT-2026-08-16-07] [P1] [CLOSED] Current-develop contract gap: PyO3 actor subscription guidance omits the mandatory registration precondition.
  file: references/developer_guide/testing.md:401
  evidence: upstream commit `949207b053b040feaff273dff9ad36b796a0e2a9ea` adds `ensure_registered()` to public `subscribe_*` methods in `crates/common/src/python/actor.rs:1601`.
  fix: document and test that public PyO3 subscription entry points reject calls before actor registration.
  closure: a repository guidance regression and focused current-develop source contract test pass.

[NT-2026-08-16-08] [P1] [CLOSED] Current-develop contract gap: adapter guidance omits endpoint-scoped socket reconnect registration and outcomes.
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:896
  evidence: upstream commit `03062cce6372d3c7e9044b39b181a50cc07a067e` adds `SocketReconnectRegistry` in `crates/common/src/clients/socket.rs:87` and `ReconnectSocket` outcomes in `crates/common/src/messages/system/socket.rs:56`.
  fix: document endpoint registration lifetime, selected-endpoint reconnect, and accepted/already-pending/unavailable outcomes.
  closure: a static guidance regression and focused current-develop source contract test pass.

[NT-2026-08-16-09] [P2] [CLOSED] Current-develop improvement: benchmark guidance omits the canonical backtest workload matrix.
  file: skills/nt-dev/SKILL.md:390
  evidence: upstream commit `f3a0bed303bc8a6d9f83138742d085966ffd47d0` adds the canonical matrix to `docs/developer_guide/benchmarking.md` and `crates/backtest/benches/engine/canonical.rs`.
  fix: require canonical workload identifiers, parameters, profile metadata, and baseline comparison for backtest performance claims.
  closure: a validator test proves the canonical workload contract is present.

[NT-2026-08-16-10] [P2] [CLOSED] Current-develop improvement: DEX guidance does not classify the upstream blockchain execution slice.
  file: skills/nt-dex-adapter/SKILL.md:90
  evidence: upstream commits `e45b99b8e63506242582e50320c88534ca3d32fd..53ee1bff` add the EVM execution slice documented in `docs/integrations/blockchain.md`, including wallet preflight, reservation precision, transaction lifecycle, RPC trust boundaries, and `WalletAccount` integration.
  fix: add a version-scoped blockchain overlay with exact ownership, safety, and deterministic test boundaries.
  closure: guidance and source-contract regressions cover wallet/account ownership, reservation arithmetic, chain identity, nonce, signing, persistence, and transaction state.

[NT-2026-08-16-11] [P1] [CLOSED] Evidence freshness: the developer-guide sync gate is red because every source snapshot is older than its 14-day policy.
  file: tools/check_dev_guide_sync.py:65
  evidence: `python3 tools/check_dev_guide_sync.py --check` exits 1 on 2026-08-16; `CURRENT_SYNC_DATE` is `2026-07-28` while `SOURCE_STALE_AFTER_DAYS` is 14.
  fix: refresh the pinned source snapshot metadata and any changed source bodies against the pinned G2 baseline, preserving current-develop overlays separately.
  closure: `python3 tools/check_dev_guide_sync.py --check` and `python3 tools/check_dev_guide_snapshot_sync.py` pass.

[NT-2026-08-16-12] [P1] [CLOSED] Evidence freshness: the upstream delta review ends at an older develop revision and makes the freshness gate fail closed.
  file: references/upstream-delta-review.json:5
  evidence: `python3 tools/check_upstream_freshness.py` reports reviewed commit `90b3d71b...` does not match resolved develop `03062cce...`; 85 intervening commits were classified in this audit.
  fix: regenerate the complete pinned-to-reviewed manifest through `03062cce6372d3c7e9044b39b181a50cc07a067e`.
  closure: `python3 tools/check_upstream_freshness.py --format json` exits zero.

[NT-2026-08-16-13] [P1] [CLOSED] Validation environment: the default upstream root points at moving develop while pinned validators require the G2 commit.
  file: tools/upstream_baseline.py:7
  evidence: the full suite reports pinned-checkout mismatches when default root `/home/mok/.cache/nautilus-trader-dev-skill/nautilus_trader` is at `03062cce...`; `/home/mok/.cache/nautilus-trader-dev-skill/nautilus_trader-pinned` is at required `6e59fd74...` and still exposes `origin/develop`.
  fix: make the portable default resolve the dedicated pinned checkout while retaining `NT_UPSTREAM_ROOT` override and moving-ref freshness inspection.
  closure: the full pytest suite passes without an environment override.

NT v2 compatibility note: the following finding records removed Python v1-era names as migration evidence only.

[NT-2026-08-16-18] [P1] [CLOSED] Python v2 guidance: the serialization guide presented nonexistent `serialization.arrow`, `ArrowSerializer`, `register_arrow`, and `wranglers_v2` APIs as current.
  file: skills/nt-data/references/guides/serialization_patterns.md:9
  evidence: pinned commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59` exposes only the flat `nautilus_trader.serialization` PyO3 module plus flat `nautilus_trader.persistence` wranglers; no `serialization/arrow` or `persistence/wranglers_v2` package exists.
  fix: rewrite the guide around `get_arrow_schema_map`, `*_to_arrow_record_batch_bytes`, and `process_record_batch_bytes`, while retaining removed Cython wranglers only as migration-labelled context.
  closure: built pinned v2 runtime successfully round-trips a `QuoteTick` through `quotes_to_arrow_record_batch_bytes` and `QuoteTickDataWrangler.process_record_batch_bytes`; owner and legacy-labelling regressions pass.

[NT-2026-08-16-14] [P1] [CLOSED] Legacy lint fail-open: a readiness card containing G1 suppresses scanning of the entire root skill.
  file: tools/check_legacy_labelling.py:49
  evidence: a temporary `SKILL.md` with a normal readiness card plus unlabelled `v1 LegacyApi` guidance exits 0 because lines 49-54 skip the file.
  fix: remove the readiness-card file exemption and let only locally labelled legacy lines pass.
  closure: a regression fixture proves the card no longer suppresses unrelated content and `python3 tools/check_legacy_labelling.py` passes.

[NT-2026-08-16-15] [P1] [CLOSED] NT v2 compatibility note: migration-lint fail-open leaves instructional Markdown below skill subdirectories outside the mandatory scanner's scope.
  file: tools/check_legacy_labelling.py:14
  evidence: a temporary `skills/nt-example/references/example.md` containing unlabelled `cdef`, `cimport`, and `.pyx` guidance exits 0 because only `skills/**/SKILL.md` is globbed and canonical errors are filtered to that scope.
  fix: scan instructional Markdown recursively under `skills/` as well as `references/` and `templates/`.
  closure: a regression fixture fails for unlabelled nested skill guidance and the real-tree lint passes.


[NT-2026-08-16-17] [P2] [CLOSED] Prose correctness: an nt-implement boundary sentence contains a dangling fragment from a partial lane edit.
  file: skills/nt-implement/SKILL.md:45
  evidence: the shipped sentence ends `outside this repository., off execution-critical paths.`.
  fix: remove the dangling fragment and keep the strict repository boundary.
  closure: the sentence is grammatical and the V2 guidance regression suite passes.

## Closed in current working tree

2026-08-21 — P1 — MODIFIED: aligned Lighter tester guidance with the immediate-startup convention (e8daa045ab, 7214db4239) — files: skills/nt-adapters/references/integrations/lighter.md, references/integrations/lighter.md, tests/test_v2_guidance_hardening.py

2026-08-21 — P1 — MODIFIED: renamed WebSocketConfig and Betfair stream timing fields to current develop spellings (70ce722a4e, 74d57e7e05) — files: skills/nt-adapters/references/guides/official_adapter_spec.md, skills/nt-adapters/references/integrations/betfair_v2.md, references/integrations/betfair_v2.md, tests/test_v2_guidance_hardening.py

2026-08-21 — P2 — MODIFIED: added develop-only overlays for LiveNode hosted run modes (e166a5e57c) and the fallible calculate_commission contract (68975d9347) — files: skills/nt-live/references/guides/run_rust_live_trading.md, skills/nt-adapters/references/guides/official_adapter_spec.md, tests/test_v2_guidance_hardening.py

2026-08-21 — P1 — MODIFIED: refreshed stale G2 durable evidence for nt, nt-adapters, nt-architect, nt-implement, nt-live, nt-review against pinned 6e59fd74ea — files: references/g2-evidence/*.json

2026-08-10 — P1 — MODIFIED: replaced obsolete or phantom Rust API guidance with pinned V2 builders, factories, imports, macro contracts, and strategy facades — files: skills/nt-adapters/SKILL.md, skills/nt-backtest/SKILL.md, skills/nt-data/SKILL.md, skills/nt-model/SKILL.md, skills/nt-signals/SKILL.md, skills/nt-trading/SKILL.md, tests/test_v2_guidance_hardening.py

2026-08-10 — P1 — REMOVED: deleted completed cleanup plan/design artifacts and added a repository-boundary regression — files: docs/cleanup-plan.md, docs/cleanup-design.md, tests/test_repository_scope_cleanup.py

2026-08-10 — P2 — MODIFIED: removed stale supporting configuration, completed Indicator and lifecycle guidance, and corrected router/handler contracts — files: pytest.ini, skills/nt-dev/SKILL.md, skills/nt-implement/SKILL.md, skills/nt-live/SKILL.md, skills/nt/SKILL.md, skills/nt-trading/SKILL.md

2026-08-10 — P2 — MODIFIED: realigned all 17 readiness cards to the mandatory G0-G7 contract and refreshed all durable G2 evidence — files: skills/*/SKILL.md, tools/check_dev_guide_sync.py, tools/check_legacy_labelling.py, tests/test_dev_guide_sync.py, tests/test_skill_g2_harnesses.py, references/g2-evidence/*.json

2026-08-10 — P2 — MODIFIED: built the exact pinned Python V2 environment and closed the final strategy-builder G2 blocker with fresh passing evidence — files: skills/nt-strategy-builder/SKILL.md, references/g2-evidence/nt-strategy-builder.json, tests/test_skill_g2_harnesses.py, docs/tracking/Components.md, docs/tracking/Findings.md

### Current-develop review through 2026-08-10

- [P1 closed] Reviewed all 27 commits from `9ca072e2d98ae623f14ecaa5b336398f5d25de34` through `90b3d71b0e2e5ec8fa4b366cbf68a8f04996b4c1`; `references/upstream-delta-review.json` records exact changed paths and affected files or no-impact rationales.
- [P2 closed] Added persistent cache factory and queue-pressure observability contracts to `nt-live`.
- [P2 closed] Added typed retry, Polymarket heartbeat, and BitMEX decommissioning contracts to `nt-adapters`.
- [P2 closed] Added retained post-window data and bounded no-data horizon semantics to `nt-backtest`.
- [P2 closed] Added stake-weighted betting position and indicator reset-state invariants to `nt-model` and `nt-signals`.
- Regression evidence: `tests/test_current_develop_guidance.py` and `tests/test_upstream_freshness.py`.

## Previous closure baseline

### Repository scope matches the master prompt

- Removed completed plans, reconciliation reports, handoffs, generated agent state, obsolete cutover-attestation tooling, and stale scaffolding.
- Rewrote the `nt` router and current repository indexes to cover NautilusTrader development only.
- Preserved upstream NautilusTrader as read-only evidence rather than an implementation target.

### Current upstream review incorporated

- Reviewed `origin/develop` through `90b3d71b0e2e5ec8fa4b366cbf68a8f04996b4c1`.
- Recorded 265 exact commits in `references/upstream-delta-review.json`, oldest first, with changed paths and affected-file mappings or no-impact rationales.
- Updated `nt-testing` for current Rust data and execution tester APIs while retaining explicit pin/current version boundaries.

### Python test environment split is fail-closed

- The static DEX compliance test is the sole explicit host-Python allowlist entry.
- All runtime API tests continue to require the pinned upstream interpreter and report setup guidance when it is absent.

## Current closure gates

- Full repository pytest suite.
- Developer-guide, snapshot, Rust-reference, legacy-labelling, and freshness validators.
- All 17 retained G0-G7 cards and G2 evidence hashes.
- NT-only repository boundary tests and manual router inspection.

No readiness claim is valid until those gates pass in the final working tree.
