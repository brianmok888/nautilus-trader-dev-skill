# Findings — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Current evidence-backed findings and closure state. -->
<!-- Does NOT contain: session history, plans, or external attestations. -->

Review date: 2026-08-25
Reviewed upstream develop: `8ecab1ce90d9790b1e18e162842decbae4d9de57`
Pinned G2 baseline: `8ecab1ce90d9790b1e18e162842decbae4d9de57`

Delta review of the 44 develop commits between the previous pin `d2b62d35a74f7f9fc4d419c29b5b2b37a71e190c` and this tip is recorded in `references/upstream-delta-review.json` history and Findings.md; the pin move to the reviewed tip is tracked as [NT-2026-08-25-01].

NT v2 compatibility note: Legacy migration/reference-only Cython/v1 terms and obsolete `references/guides` paths in this whole file are audit evidence, not active guidance; prefer current Rust/PyO3 V2 APIs.

## Open findings

[NT-2026-08-25-01] [P1] [CLOSED 2026-08-26] Upstream drift: 44 develop commits ahead of the pin, including renames and API shifts on taught surfaces.
  file: tools/upstream_baseline.py:4; references/upstream-delta-review.json
  evidence: `python3 tools/check_upstream_freshness.py --format json` at the refreshed cache reports develop tip `8ecab1ce90d9790b1e18e162842decbae4d9de57`, 44 commits ahead of pin `d2b62d35a74f7f9fc4d419c29b5b2b37a71e190c`; per-commit delta review recorded in `references/upstream-delta-review.json`.
  fix: move `UPSTREAM_COMMIT` to the reviewed tip, collapse the delta manifest to the new pin, refresh every pin-citing layer (README baseline line, dev-guide snapshots, rust-trading example mirror, G2 evidence re-execution).
  closure: `python3 tools/check_upstream_freshness.py --format json` exits 0 at the new pin with all sync checkers green.
  closure-proof 2026-08-26: re-executed this session - `python3 tools/check_upstream_freshness.py --format json` exits 0 (pin == reviewed develop tip `73d4dd5b3`); all 17 G2 harnesses re-executed PASS at the new pin (`NT_UPSTREAM_ROOT=.../nautilus_trader-build CARGO_TARGET_DIR=.../target-mission python3 tools/check_skill_g2_harnesses.py --execute --upstream-root .../nautilus_trader-build`, exit 0); sync checkers green: check_dev_guide_snapshot_sync, check_rust_trading_reference_sync, check_dev_guide_sync, check_legacy_labelling; rename fallout tracked and closed as NT-2026-08-25-08.

[NT-2026-08-25-02] [P1] [CLOSED 2026-08-25] Machine-synced mirrors stale against the reviewed tip.
  file: references/developer_guide/adapters.md; references/developer_guide/coding_standards.md; references/developer_guide/spec_exec_testing.md; skills/nt-trading/references/examples/rust_trading/examples/ (4 strategy files)
  evidence: develop commits `3907750e2` (execution naming: `LiveExecClientConfig`→`ExecutionClientConfig`, `LiveExecEngineConfig`→`LiveExecutionEngineConfig`, `LiveDataClientConfig`→`DataClientConfig`) and `51f641d5c` (adapter client config renames) changed `docs/developer_guide/{adapters,coding_standards,spec_exec_testing}.md`; commit `8d314696e` (Strategy cancel-all scope) changed `crates/trading/src/examples/strategies/{composite_market_maker,delta_neutral_vol,grid_mm,hurst_vpin_directional}/strategy.rs` mirrored under `skills/nt-trading/references/examples/rust_trading/examples/`.
  fix: refresh the three developer-guide snapshots from the tip and mirror the four upstream strategy example files byte-for-byte.
  closure: `python3 tools/check_dev_guide_snapshot_sync.py` and `python3 tools/check_rust_trading_reference_sync.py` exit 0 against the moved pin.
  closure-proof 2026-08-25: `python3 tools/check_dev_guide_snapshot_sync.py` -> 'Developer guide snapshot bodies match pinned upstream.'; `python3 tools/check_rust_trading_reference_sync.py` -> 'Rust trading references match pinned upstream examples.'

[NT-2026-08-25-03] [P1] [CLOSED 2026-08-25] Active-lane guide teaches removed V2 config name `LiveExecEngineConfig` without any legacy label.
  file: skills/nt-adapters/references/guides/spec_exec_testing.md; skills/nt-testing/references/guides/spec_exec_testing.md
  evidence: symbol `LiveExecEngineConfig` is absent from the reviewed tip tree (`git grep` over `python/nautilus_trader` and `crates` at `73d4dd5b` returns nothing); develop commit `3907750e2` renamed it to `LiveExecutionEngineConfig`; neither guide file carries an NT v2 compatibility note or migration label.
  fix: update the guide text to the current `LiveExecutionEngineConfig` name (or label retained legacy context per Handguard #5).
  closure: `python3 tools/check_legacy_labelling.py` (with the extended removed-symbol detector from [NT-2026-08-25-04]) exits 0 with the corrected guides.
  closure-proof 2026-08-25: `python3 tools/check_legacy_labelling.py` exits 0 with the guides teaching `LiveExecutionEngineConfig` (skills/nt-adapters + skills/nt-testing spec_exec_testing.md).

[NT-2026-08-25-04] [P1] [CLOSED 2026-08-25] Legacy-labelling gate cannot detect v1/V2-removed Python symbols, so unlabelled drift passes the gate.
  file: tools/check_legacy_labelling.py; tools/check_dev_guide_sync.py (canonical `_check_unlabelled_legacy_guidance`)
  evidence: gate is green at `b30ca0c` while 25 unlabelled files teach symbols absent from the reviewed tip (currency audit 2026-08-25; two audit hits excluded as false positives — `skills/nt-trading/references/guides/write_rust_actor.md` defines its own `SpreadMonitor` example and `skills/nt-adapters/references/examples/bybit/README_options_data_collector.md` configures its own `BybitOptionsDataCollectorConfig`): `references/concepts/{actors,backtesting,execution,orders,portfolio,reports,strategies,visualization}.md`, `references/integrations/{derive,polymarket}.md`, per-skill copies under `skills/nt-{adapters,backtest,model,signals,testing,trading}/references/`, teaching removed modules such as `nautilus_trader.backtest.engine`, `nautilus_trader.backtest.models`, `nautilus_trader.core.rust.model`, and removed types `LiveExecEngineConfig`, `FillModelConfig`, `ImportableFillModelConfig`, `DeriveExecClientConfig`; detector patterns cover only Cython tokens, `.pyx`, `v1`, and `TradingNode`.
  fix: extend the detector with the removed-symbol set verified absent at the pinned/reviewed V2 baseline, honouring file-level and proximate labels; TDD with a failing case first.
  closure: new pytest wrapper in `tests/test_legacy_labelling.py` fails on unlabelled removed symbols and passes labelled ones; `python3 tools/check_legacy_labelling.py` exits 0 after the [NT-2026-08-25-05] labelling fix.
  closure-proof 2026-08-25: tests/test_legacy_labelling.py 29 passed (failing-first: removed-symbol, fence-label, current-symbol cases); `python3 tools/check_legacy_labelling.py` exits 0.

[NT-2026-08-25-05] [P1] [CLOSED 2026-08-25] 25 retained v1 mirror files lack the required legacy/migration label (Handguard invariant #5).
  file: references/concepts/{actors,backtesting,execution,orders,portfolio,reports,strategies,visualization}.md; references/integrations/{derive,polymarket}.md; skills/nt-adapters/references/guides/spec_exec_testing.md; skills/nt-adapters/references/integrations/{derive,polymarket}.md; skills/nt-backtest/references/concepts/backtesting.md; skills/nt-model/references/concepts/value_types.md; skills/nt-signals/references/concepts/{portfolio,reports,visualization}.md; skills/nt-testing/references/guides/spec_exec_testing.md; skills/nt-trading/references/concepts/{actors,execution,orders,portfolio,strategies}.md; skills/nt-trading/references/guides/testing.md
  evidence: 2026-08-25 currency audit against reviewed tip `73d4dd5b` — each listed file teaches imports/types that do not exist at the tip and carries no `NT v2 compatibility note`, `migration/reference-only`, or `legacy:` label (compare labelled peers `references/concepts/cache.md`, `data.md`, `instruments.md`, `logging.md`, `message_bus.md`).
  fix: add the file-level NT v2 compatibility note used by the labelled peers (or refresh the mirror from current upstream docs where the file is machine-synced); guides in active lanes get the current V2 names instead where noted in [NT-2026-08-25-03].
  closure: extended `python3 tools/check_legacy_labelling.py` exits 0 across the full scope.
  closure-proof 2026-08-25: `python3 tools/check_legacy_labelling.py` exits 0 across references/concepts, references/integrations, and all per-skill mirrors (22 file-level notes + labelled v1-only fences).

[NT-2026-08-25-06] [P2] [CLOSED 2026-08-25] `official_adapter_spec.md` socket-reconnect overlay cites a pre-drift commit and moved code location.
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:954-962
  evidence: overlay cites develop commit `03062cce6372d3c7e9044b39b181a50cc07a067e`; the feature landed via reviewed-tip commit `0fafbd12f` with `ReconnectRequestOutcome` defined at `crates/network/src/mode.rs:251` and re-exported as `SocketReconnectRequestOutcome` at `crates/live/src/socket.rs:36` (`SocketReconnectRegistry` still in `crates/live/src/socket.rs`).
  fix: refresh the overlay cite to `0fafbd12f` and correct the source-path mention.
  closure: updated text cites `0fafbd12f` and current paths; `python3 tools/check_legacy_labelling.py` and skill gates remain green.
  closure-proof 2026-08-25: official_adapter_spec.md socket overlay cites `0fafbd12f` with crates/network/src/mode.rs and crates/live/src/socket.rs paths; `python3 tools/check_legacy_labelling.py` exits 0.

[NT-2026-08-25-07] [P2] [CLOSED 2026-08-25] `run_pinned_v2_pytest.py` failure hint references a nonexistent `make sync-v2` target.
  file: tools/run_pinned_v2_pytest.py:41-44
  evidence: upstream Makefile at pin `d2b62d35` and at reviewed tip `73d4dd5b` exposes `make sync` (line 292) and `make build-debug`/`build` (lines 314-321); no `sync-v2` target exists.
  fix: point the FileNotFoundError hint at `make sync && make build-debug` in the pinned upstream checkout.
  closure: hint text updated; `python3 -m pytest -q tests/` green.
  closure-proof 2026-08-25: run_pinned_v2_pytest.py hint now `make sync && make build-debug` (targets verified in upstream Makefile lines 292/314); upstream venv built and importable via those targets.

[NT-2026-08-25-08] [P1] [CLOSED 2026-08-26] Pinned-tip rename `XExecClientConfig` -> `XExecutionClientConfig` (upstream `3907750e2` "Standardize execution naming", inside the reviewed delta) left active-lane guidance teaching imports that no longer resolve at pin `73d4dd5b3`.
  file: docs/end_to_end_guide.md:71,89; skills/nt-adapters/references/examples/rust_adapters/*/node_exec_tester.rs:32-92; references/integrations/{binance,bitmex,bybit,coinbase,deribit,derive,dydx,hyperliquid,ib,kraken,lighter,okx,polymarket}.md; skills/nt-adapters/references/integrations (mirrors); skills/nt-adapters/references/concepts/live.md; skills/nt-live/references/guides/deployment_patterns.md
  evidence: failing `tests/test_rust_first_end_to_end.py::test_primary_live_node_source_compiles_against_pinned_upstream` (E0432 unresolved import `nautilus_okx::config::OKXExecClientConfig`); upstream crate exports at pin: `OKXExecutionClientConfig` (crates/adapters/okx/src/config.rs:202), and the v2 Python package exports `XExecutionClientConfig` for every adapter (python/nautilus_trader/adapters/*/__init__.py).
  fix: guide fence now mirrors upstream `docs/how_to/run_rust_live_trading.md` (renamed symbol, `trader_id` sourced from `LiveNode::builder`, factory-collapse form); 12 rust_adapters example mirrors re-synced byte-for-byte from upstream examples (node_exec_tester x10 incl. bitmex, node_grid_mm x2); 158 unlabelled v2-active Python/Rust guidance occurrences renamed, 36 v1/legacy TradingNode-labelled occurrences intentionally retained, each under its NT v2 compatibility note; derive.md v2 live-node fences rewritten to the collapsed-factory form (`DeriveExecutionClientConfig(account_id=...)` passed directly to `add_exec_client`, wrapper `DeriveExecFactoryConfig` removed upstream) (v2 Python has no TradingNodeConfig/exec_clients — verified absent in the pinned python package).
  closure: `python3 -m pytest -q tests/test_rust_first_end_to_end.py tests/test_exec_spec_current_overlay.py` 11 passed (exec-spec snapshot hash tripwire re-pinned to the re-synced snapshot); `python3 tools/check_legacy_labelling.py` and `python3 tools/check_dev_guide_sync.py` exit 0.
  closure-proof 2026-08-26: re-executed this session: 11 passed, LEGACY_OK, DEVGUIDE_OK; compile gate proves the okx fence against the pinned crate.

[NT-2026-08-23-06] [P0] [CLOSED] Pressure review: active inline examples and contracts invented or retained removed V2 APIs.
  file: skills/nt-backtest/SKILL.md; skills/nt-data/SKILL.md; skills/nt-architect/SKILL.md; skills/nt-adapters/SKILL.md; references/developer_guide/contracts/adapter_contract.md
  evidence: pinned `d2b62d35a74f7f9fc4d419c29b5b2b37a71e190c` `crates/execution/src/models/fill.rs`, `crates/backtest/src/config.rs`, `crates/common/src/providers.rs`, and `crates/common/src/actor/data_actor.rs`.
  fix: taught the real `FillModel`/`FillModelAny` seam, removed the invented persistence backend and removed decorator, corrected signal publication, and replaced `load_all_async` with the required provider methods.
  closure: `python3 -m pytest -q tests/test_pressure_review_regressions.py` exits 0.

[NT-2026-08-23-07] [P1] [CLOSED] Pressure review: runtime routing, serialization, and upstream-workspace boundaries could route agents to false-green or unsafe workflows.
  NT v2 compatibility note: the legacy routing evidence in this finding is migration/reference-only.
  file: skills/nt/SKILL.md; skills/nt-dev/SKILL.md; skills/nt-strategy-builder/SKILL.md; docs/serialization.md; skills/nt-strategy-builder/tests/conftest.py; skills/nt-dex-adapter/tests/test_backtest_integration.py
  evidence: pinned package version `2.0.0rc4`, absence of `msgspec` from the pinned workspace, and the repository read-only upstream invariant.
  fix: added runtime/language classification and migration/reference-only legacy routing, disposable writable upstream-worktree rules, pinned-runtime test guards, and removed the unsupported serialization recommendation.
  closure: `python3 -m pytest -q tests/test_pressure_review_regressions.py` exits 0.

[NT-2026-08-23-01] [P0] [CLOSED] Rust conversion correctness: the retained `nt-signals` analysis source snapshot lagged the pinned Rust/PyO3 crate.
  file: skills/nt-signals/references/rust/analysis/
  evidence: pinned `d2b62d35a74f7f9fc4d419c29b5b2b37a71e190c` `crates/analysis/` contains the current statistics, snapshot, and PyO3 modules that the older retained tree omitted.
  fix: mirrored the complete pinned `crates/analysis` tree and added deterministic byte-for-byte snapshot coverage.
  closure: `python3 -m pytest -q tests/test_rust_analysis_reference_sync.py` exits 0.

[NT-2026-08-23-02] [P1] [CLOSED] V2 compliance: the canonical actor and adapter examples used nonexistent current APIs.
  file: skills/nt-architect/SKILL.md; skills/nt-adapters/SKILL.md
  evidence: pinned `d2b62d35a74f7f9fc4d419c29b5b2b37a71e190c` `crates/common/examples/greeks_actor_example.rs`, `crates/common/src/factories/client.rs`, and `examples/quickstarts/lighter-rust-data-client/src/main.rs`.
  fix: replaced the actor sketch with `DataActorCore`/`nautilus_actor!`/`CustomData`/`publish_data`, replaced `AdapterRegistry` with separate current factory traits and `LiveNode` registration, and documented the complete lifecycle callbacks.
  closure: `python3 -m pytest -q tests/test_current_v2_contracts.py` exits 0.

[NT-2026-08-23-03] [P1] [CLOSED] V2 compliance: Betfair replacement and ambiguous command-recovery guidance predated develop commit `79fb940dc794b953570ad5ac76f4f1e6b68ea93f`.
  file: references/integrations/betfair.md; references/integrations/betfair_v2.md; skills/nt-adapters/references/integrations/betfair.md; skills/nt-adapters/references/integrations/betfair_v2.md
  evidence: pinned `d2b62d35a74f7f9fc4d419c29b5b2b37a71e190c` `docs/integrations/betfair.md` and `crates/adapters/betfair/src/execution.rs`.
  fix: refreshed the canonical guide and documented logical-order identity, terminal replacement outcomes, stable request correlation, bounded retries, and pending reconciliation.
  closure: mirrored reference pairs are byte-identical and `python3 tools/check_upstream_freshness.py --format json` exits 0.

[NT-2026-08-23-04] [P1] [CLOSED] Upstream standards: active guidance retained U+2011 after current develop prohibited non-ASCII hyphens.
  file: skills/**/*.md; references/**/*.md
  evidence: upstream `d2b62d35a74f7f9fc4d419c29b5b2b37a71e190c` `.pre-commit-hooks/check_unicode_typography.sh`.
  fix: normalized active guidance to ASCII hyphens and added a repository regression gate.
  closure: `python3 -m pytest -q tests/test_ascii_typography.py` exits 0.

[NT-2026-08-23-05] [P1] [CLOSED] Durable tracking could drift from the delta manifest and retained skill inventory.
  file: docs/tracking/Components.md; tests/test_upstream_freshness.py
  evidence: the stale `reviewed exactly through` SHA survived two prior pin moves while all prior validators passed.
  fix: synchronized current tracking metadata and added manifest/skill-inventory assertions.
  closure: `python3 -m pytest -q tests/test_upstream_freshness.py` exits 0.

[NT-2026-08-22-09] [P2] [CLOSED] Pin deferral: the pinned G2 baseline `baa667bc` lags the reviewed develop tip `98e6c39d8` by one adapter-scoped commit (Betfair socket-state reporting and reconnect control).
  file: tools/upstream_baseline.py:4
  evidence: `python3 tools/check_upstream_freshness.py --format json` exits 0 with the delta recorded in `references/upstream-delta-review.json`; the socket-state layer is documented as a current-develop overlay in both `betfair_v2.md` copies.
  fix: executed the full pin move in the r3 cycle: pinned checkout and writable build worktree checked out at 98e6c39d8, Python venv rebuilt, all 17 G2 harnesses re-executed, snapshot frontmatter and citation layers moved to the new pin, overlay relabeled as in-pin behavior.
  status: closed by the r3 pin move; `python3 tools/check_upstream_freshness.py --format json` exits 0 with reviewed_commit == pinned_commit == 98e6c39d8.

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
  closure: `python3 -m pytest -q tests/test_v2_guidance_hardening.py::test_network_config_guides_use_current_field_names` passes; `grep -rn 'stream_idle_timeout_ms' skills/ references/` returns zero hits (exit 1).

[NT-2026-08-21-04] [P1] [CLOSED] Validation: G2 durable-evidence hashes drifted out of sync with owned skill content during this mission (preflight manifest refresh plus mission edits), leaving `--check-cards` red mid-mission.
  evidence: at the clean baseline commit `bd8118a8` every G2 check passes (clean-clone reproduction: `--check-cards` exit 0; `tests/test_skill_g2_harnesses.py::test_current_readiness_evidence_matches_owned_content` passes; the baseline suite's single failure is `tests/test_upstream_freshness.py::test_required_develop_ref_contains_current_nightly_history`, closed by the preflight manifest refresh). The uncommitted preflight refresh of `references/upstream-delta-review.json` invalidated owned-content hashes for the skills owning `references/` (nt-architect, nt-implement, nt-review); mission edits to `tests/test_v2_guidance_hardening.py` and `skills/nt-adapters`/`skills/nt-live` content extended the mismatch to nt, nt-adapters, and nt-live.
  fix: re-execute the six affected harnesses via `python3 tools/check_skill_g2_harnesses.py --execute --skill <skill>` against the pinned upstream and commit the refreshed evidence.
  correction: an earlier revision of this record wrongly described the red as pre-existing on main; the independent post-fix review disproved that with a clean-clone reproduction and this record was rewritten.
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

[NT-2026-08-21-07] [P2] [CLOSED] Pin deferral: the reproducible G2 pin `6e59fd74` was 560 commits behind the reviewed develop tip; superseded by the 2026-08-22 pin move to `baa667bc`.
  evidence: `python3 tools/check_upstream_freshness.py --format json` exits 0 with `pinned_commit` = reviewed tip `baa667bc3c57cd3f639d9722b6fd592e4fcde36f`; G2 evidence files re-executed against the new pin.
  fix: moved `UPSTREAM_COMMIT` to `baa667bc`, re-copied developer-guide snapshots, refreshed version cites, and re-executed the G2 harnesses.
  closure: pin equals the reviewed tip; all G2 evidence files re-executed against `baa667bc` (see `references/g2-evidence/`).

[NT-2026-08-21-08] [P2] [CLOSED] Residual: the migration/reference-labelled v1 Betfair guide states current-tense Rust differences contradicted by the reviewed develop tip rename.
  file: references/integrations/betfair.md:496
  evidence: `references/integrations/betfair.md:482,496,518,535` teach `stream_heartbeat_ms` as what "Rust currently requires"; upstream commit `74d57e7e05` renamed the pair at the reviewed tip `2114cf6f76`. The file is v1 migration/reference-labelled and outside NT-2026-08-21-03's declared scope (the v2 guide copies).
  fix: scope the v1 guide's "Current Rust differences" blocks to the pinned baseline; upstream commit `74d57e7e05` renamed the pair on both the Rust and Python surfaces (tip `2114cf6f76` `python/nautilus_trader/adapters/betfair/__init__.pyi:58-95` uses `stream_heartbeat_secs=5`), so the requirement above is historical for current develop.
  closure: `python3 -m pytest -q tests/test_v2_guidance_hardening.py::test_v1_betfair_guides_scope_heartbeat_claims_to_pinned_baseline` passes; both v1 copies carry pinned-baseline scoping notes citing `74d57e7e05`; `python3 tools/check_legacy_labelling.py` passes.

[NT-2026-08-26-01] [P1] [OPEN] Upstream drift: develop tip advanced 5 commits past the pin (`73d4dd5b3` → `8ecab1ce9`), touching taught Rust surfaces (betfair execution identity, polymarket REST reconciliation, shared execution reconciliation core).
  file: tools/upstream_baseline.py:4; references/upstream-delta-review.json
  evidence: `python3 tools/check_upstream_freshness.py --format json` at the refreshed cache reports develop tip `8ecab1ce90d9790b1e18e162842decbae4d9de57`, 5 commits ahead of pin `8ecab1ce90d9790b1e18e162842decbae4d9de57`; per-commit delta review recorded in `references/upstream-delta-review.json` (5 commits, 37 paths; no Rust `examples/` paths changed).
  fix: move `UPSTREAM_COMMIT` to the reviewed tip, sync the two changed integration mirrors (`betfair.md` 62 lines, `polymarket.md` 11 lines, both layers), refresh pin citations, re-execute G2 evidence at the new pin.
  closure: `python3 tools/check_upstream_freshness.py --format json` exits 0 at the new pin with all sync checkers and the full suite green.

[NT-2026-08-26-02] [P1] [CLOSED 2026-08-26] The Betfair v2 Rust-surface tracker (`betfair_v2.md`) is stale against `8ecab1ce9`, which landed exactly the behaviors the tracker exists to track.
  file: references/integrations/betfair_v2.md:24-27,71-87,125; skills/nt-adapters/references/integrations/betfair_v2.md (mirror)
  evidence: upstream `8ecab1ce9` "Retain Betfair terminal order identity" routes late fills/voids through retained local order identity, restores closed order identity from cache across reconnects, bounds correlation/customer-refs/dedup/replaced-IDs, resolves replace state across REST/OCM/reconciliation, and reconciles terminal replace/reduction reports without duplicates; `crates/execution/src/reconciliation/orders.rs` changed in the same delta (shared core). The tracker's "Current Rust status" rows (reconciliation scope, post-reconnect halt, external order filtering) and the OCM/reconciliation section describe pre-`8ecab1ce9` behavior and carry no row for terminal order identity retention.
  fix: re-verify each tracker row against `8ecab1ce9` sources (`crates/adapters/betfair/src/execution.rs`, `stream/ocm.rs`, `crates/execution/src/reconciliation/orders.rs`), update stale rows, add the identity-retention behavior, and refresh both file copies.
  closure: every tracker row cites verified `8ecab1ce9` behavior; `python3 tools/check_dev_guide_sync.py` and `python3 tools/check_legacy_labelling.py` stay green.
  closure-proof 2026-08-26: terminal-order-identity row added citing `crates/adapters/betfair/src/execution.rs` (`OcmState::DEDUP_RETENTION`, most-recent 10,000 closed cached orders seeded into OCM state); reconciliation-scope and post-reconnect rows marked resolved/cutover-done against the upstream `8ecab1ce9` doc; customerOrderRef section carries the tracked-order collision wording. Gates: `check_dev_guide_sync.py`, `check_legacy_labelling.py` exit 0; `tests/test_v2_current_develop_overlays.py` green (cutover commit 990b5a5).
  2026-08-26 — P1 — MODIFIED: tracker refreshed at 8ecab1ce9 and made the primary guide — files: references/integrations/betfair_v2.md, skills/nt-adapters/references/integrations/betfair_v2.md

[NT-2026-08-26-03] [P1] [CLOSED 2026-08-26] Rust-first routing gap: the Betfair v2 guide is unreachable from active guidance — every route lands on the v1 guide.
  file: references/integrations/index.md:10; skills/nt-adapters/SKILL.md
  evidence: `references/integrations/index.md:10` (byte-sync-enforced mirror, uneditable) routes Betfair → `betfair.md` (v1 Python-adapter guide, migration/reference-only once the cutover lands); no `skills/**/SKILL.md` references `betfair_v2.md` (`grep -rln betfair_v2 skills/` → empty; only `docs/tracking/Findings.md` and `tests/test_v2_current_develop_overlays.py` mention it). An agent following nt-adapters guidance therefore reads v1 wiring with no pointer to the Rust surface, violating the Rust-first default (master-prompt constraints; `docs/tracking/Handguard.md` invariant #5 spirit).
  decision (user, 2026-08-26): full cutover — v2 over v1. `betfair_v2.md` becomes the primary Betfair guide; v1 is cleared from active routing and demoted to labelled migration/reference-only. `betfair_v2.md`'s header pre-plans this ("can replace `betfair.md` with small edits instead of a full rewrite").
  fix: execute the cutover — update `betfair_v2.md` tracker rows against the new pin, stamp `betfair.md` (both layers) with a supersession label routing Rust v2 work to the v2 guide, flip every editable active route (SKILL.md guidance, cross-links) to `betfair_v2.md`; the byte-synced index row stays as-is (sync-enforced) but every skill-layer route that chooses a guide names v2 first.
  NT v2 compatibility note: v1 routing below is migration audit context; the cutover demotes it to migration/reference-only.
  closure: every active route reaches `betfair_v2.md` first; `betfair.md` carries the supersession/migration-reference label; `python3 tools/check_legacy_labelling.py`, `python3 tools/check_dev_guide_sync.py`, and routing tests stay green.
  closure-proof 2026-08-26 (cutover commit 990b5a5): index.md (both layers) Betfair row links `betfair_v2.md` as Guide with the v1 stub kept as `[legacy](betfair.md)`; `check_dev_guide_sync.py` CURRENT_INTEGRATION_GUIDES now enforces the v2 guide link (betfair_v2.md replaces betfair.md — the enforcement contract, not the mirror, changed); `skills/nt-adapters/SKILL.md` routes Betfair work to `betfair_v2.md` first; v1 files cleared to labelled supersession stubs. `tests/test_v2_current_develop_overlays.py::test_betfair_v2_is_primary_and_v1_cleared` and `::test_nt_adapters_routes_betfair_v2_first` green.
  2026-08-26 — P1 — MODIFIED: executed the user-directed cutover (v2 primary, v1 cleared to labelled stubs) — files: references/integrations/betfair.md, skills/nt-adapters/references/integrations/betfair.md, references/integrations/index.md, skills/nt-adapters/references/integrations/index.md, skills/nt-adapters/SKILL.md

[NT-2026-08-26-04] [P2] [CLOSED 2026-08-26] The polymarket mirror is stale against `0541a2189`/`ccc80cdb2`; upstream's guide is already Rust-first, so this is pure mirror drift with no v2 overlay needed.
  file: references/integrations/polymarket.md; skills/nt-adapters/references/integrations/polymarket.md
  evidence: upstream `docs/integrations/polymarket.md` states "The adapter is implemented in Rust and exposed to Python" (line 9) and "direct WebSocket, provider, data client, and execution client types are Rust-only" (line 84) — no `polymarket_v2.md` split is warranted; the delta changed 11 lines (order-recovery clarification, REST report binding to account/instrument).
  fix: fold the mirror refresh into the NT-2026-08-26-01 pin-move segment (byte-sync both layers).
  closure: `python3 tools/check_dev_guide_sync.py` exits 0 with both mirrors matching the reviewed tip.
  closure-proof 2026-08-26: both layers carry the upstream `8ecab1ce9` order-recovery wording (base-denominated `LIMIT` validation, "no known client association" fallback) and the authoritative Fees section; `python3 tools/check_dev_guide_sync.py` exits 0. Also fixed pre-existing layer divergence: the skills layer taught `Crypto 0.072` where upstream says `0.07`.
  2026-08-26 — P2 — MODIFIED: refreshed both polymarket mirrors to the reviewed tip and aligned the Fees section across layers — files: references/integrations/polymarket.md, skills/nt-adapters/references/integrations/polymarket.md

## Follow-up TODO

- [ ] [NT-2026-08-21-07] Move the G2 pin to the reviewed develop tip and re-execute all 17 harnesses (target re-run date: 2026-09-21).

[NT-2026-08-23-09] [P1] [CLOSED] Active Rust actor and fill-model examples used non-compiling publication and custom-model contracts.
  file: skills/nt-architect/SKILL.md; skills/nt-backtest/SKILL.md
  evidence: latest upstream `DataActor::publish_signal(name, value, ts_event)` and `FillModelHandle`/required orderbook method contracts.
  fix: corrected the actor call/return and replaced the nonexistent `FillModelAny::Custom` path with the complete `FillModel` plus `FillModelHandle` contract.

[NT-2026-08-23-10] [P1] [CLOSED] Active custom-data guidance used removed Python APIs and the wrong Rust Arrow registry owner.
  file: skills/nt-signals/SKILL.md; skills/nt-signals/references/guides/custom_data_patterns.md; skills/nt-data/SKILL.md; docs/serialization.md
  evidence: latest upstream `register_custom_data_class`, `nautilus_model::data::register_arrow`, and `ParquetDataCatalog::write_custom_data_batch` contracts.
  fix: documented explicit JSON/Arrow callbacks, model-owned registration, failure before registration, and catalog round trips.

[NT-2026-08-23-11] [P1] [CLOSED] DEX guidance exposed legacy Python execution as current and collapsed pool identity/fee semantics.
  file: skills/nt-dex-adapter/SKILL.md; skills/nt-dex-adapter/rules/dos_and_donts.md
  evidence: upstream blockchain integration uses Rust signer secret references, pool contract/protocol IDs, and taker-fee-only AMM mapping.
  fix: quarantined the Python rules file and added canonical Rust custody, unique pool identity, and AMM fee requirements.

[NT-2026-08-23-12] [P1] [CLOSED] Live reconciliation guide pointed to removed Python modules and obscured fail-closed startup behavior.
  file: skills/nt-live/references/guides/reconciliation.md
  evidence: latest Rust execution reconciliation, network retry, LiveNodeConfig, and startup orchestration modules.
  fix: rewrote the guide around current Rust owners and explicit startup abort semantics.

[NT-2026-08-23-13] [P1] [CLOSED] Testing guidance missed timestamp scale checks and recommended polling/nonexistent async helpers.
  file: skills/nt-testing/SKILL.md; skills/nt-testing/references/guides/testing.md; skills/nt-adapters/SKILL.md
  evidence: upstream TestKit specifies Unix-nanosecond plausibility and message validation.
  fix: added scale-failure rules and exact-event async completion with bounded timeouts only as guards.

[NT-2026-08-23-14] [P1] [CLOSED] Learning and shared docs used nonexistent crate versions, invalid serialization syntax, and wrong setup commands.
  file: docs/end_to_end_guide.md; docs/serialization.md; skills/nt-learn/curriculum/01-setup.md; skills/nt-learn/curriculum/09-full-rust-trading.md
  evidence: crates.io publishes the `0.62` family; upstream root bootstrap is `make sync`; source uses the checked-in Rust toolchain.
  fix: aligned the published release lane, bootstrap, toolchain, and source-backed serialization examples.

[NT-2026-08-23-15] [P1] [CLOSED] Active implementation/model guidance used nonexistent Make targets, the wrong logging facade, and an incorrect enum discriminant.
  file: skills/nt-dev/SKILL.md; skills/nt-implement/SKILL.md; skills/nt-model/SKILL.md
  evidence: upstream Makefile, `log::` conventions, and `InstrumentAny::Betting(BettingInstrument)` definition.
  fix: corrected commands, logging macros, and exact variant/payload naming.

[NT-2026-08-23-16] [P1] [CLOSED] Durable evidence validation accepted malformed JSON values and declaration checks could miss invalid harness definitions.
  file: tools/check_skill_g2_harnesses.py; tests/test_skill_g2_harnesses.py
  evidence: booleans compare equal to integers in Python and prior checks omitted strict timestamps/durations.
  fix: added strict boolean/integer/timestamp/duration validation and regression coverage for harness declaration validation.

[NT-2026-08-23-17] [P1] [CLOSED] Mirrored OKX exec-tester example lacked the upstream `DRY_RUN` real-funds safety gate.
  file: skills/nt-adapters/references/examples/rust_adapters/okx/node_exec_tester.rs
  evidence: upstream `d2b62d35a7` `crates/adapters/okx/examples/node_exec_tester.rs` adds `DRY_RUN` gating, a real-funds warning header, and `maybe_open_position_on_start_qty` wiring; the retained mirror still taught the unguarded `open_position_on_start_qty` flow last synced at `f725e184`.
  fix: synced the mirrored example byte-for-byte to the reviewed tip.
  closure: mirror diff against `git show d2b62d35a7:crates/adapters/okx/examples/node_exec_tester.rs` is empty; `python3 -m pytest -q` exits 0.

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
2026-08-25 — P1 — MODIFIED: moved the pinned baseline to develop `73d4dd5b3` (44-commit delta reviewed and recorded), refreshed the three drift-affected developer-guide snapshots and the rust_trading examples mirror, and updated every pin-citing layer while preserving historical overlay citations — files: tools/upstream_baseline.py, README.md, docs/tracking/Components.md, references/upstream-delta-review.json, references/developer_guide/*.md, skills/**, tests/test_pressure_review_regressions.py
2026-08-25 — P1 — MODIFIED: extended the legacy-labelling gate with removed-v2-symbol detection (fence-aware labels, migration_reference exemption), labelled 22 retained v1 concept/integration mirrors, corrected renamed config guidance (LiveExecutionEngineConfig / DataClientConfig / ExecutionClientConfig), and labelled v1-only fences with current Rust contract pointers — files: tools/check_legacy_labelling.py, tests/test_legacy_labelling.py, references/concepts/*.md, references/integrations/*.md, skills/nt-{adapters,backtest,model,signals,testing,trading}/**, tools/run_pinned_v2_pytest.py
2026-08-22 — P2 — MODIFIED: moved the pinned G2 baseline to develop 98e6c39d8 (Betfair socket-state reporting and reconnect control), relabeled the betfair_v2 overlay as in-pin behavior, reset the delta manifest, and re-executed all 17 G2 harnesses — files: tools/upstream_baseline.py, README.md, docs/tracking/Components.md, docs/tracking/Findings.md, references/upstream-delta-review.json, references/developer_guide/*.md, skills/**, references/integrations/betfair_v2.md, tests/test_exec_spec_current_overlay.py

2026-08-22 — P2 — MODIFIED: added current-develop overlays for Betfair socket-state endpoints (`betfair-data-streams`/`betfair-user-streams`), `SocketReconnectRegistry` targeted reconnect with auth/subscription replay, and execution gating until replacement-stream reconciliation (upstream `98e6c39d83`) — files: skills/nt-adapters/references/integrations/betfair_v2.md, references/integrations/betfair_v2.md, tests/test_v2_current_develop_overlays.py, references/upstream-delta-review.json

2026-08-22 — P3 — FIXED: check_dev_guide_sync now skips nested .worktrees checkouts when scanning markdown, so gate results no longer depend on untracked sibling worktree copies — files: tools/check_dev_guide_sync.py, tests/test_dev_guide_sync.py

2026-08-22 — P2 — CORRECTED: reconciled independent-review misses from the baa667bc pin move — Findings.md header still pinned to 6e59fd74 full-sha, five integration/adapter guides still labelling in-pin commits (74d57e7e05, 70ce722a4e, e8daa045ab, 7214db4239, 68975d9347, e166a5e57c) as develop-only overlays, nt-testing full-sha historical boundary, stale release_security helper/test names — files: docs/tracking/Findings.md, skills/nt-testing/SKILL.md, skills/nt-adapters/references/guides/official_adapter_spec.md, skills/nt-live/references/guides/run_rust_live_trading.md, skills/nt-adapters/references/integrations/{betfair,betfair_v2,lighter}.md, references/integrations/{betfair,betfair_v2,lighter}.md, tools/check_dev_guide_sync.py, tests/test_dev_guide_sync.py

2026-08-21 — P2 — MODIFIED: scoped the v1 Betfair guides' current-tense stream-heartbeat claims to the pinned baseline (NT-2026-08-21-08) — files: references/integrations/betfair.md, skills/nt-adapters/references/integrations/betfair.md, tests/test_v2_guidance_hardening.py


2026-08-21 — P1 — MODIFIED: aligned Lighter tester guidance with the immediate-startup convention (e8daa045ab, 7214db4239) — files: skills/nt-adapters/references/integrations/lighter.md, references/integrations/lighter.md, tests/test_v2_guidance_hardening.py

2026-08-21 — P1 — MODIFIED: renamed WebSocketConfig and Betfair stream timing fields to current develop spellings (70ce722a4e, 74d57e7e05) — files: skills/nt-adapters/references/guides/official_adapter_spec.md, skills/nt-adapters/references/integrations/betfair_v2.md, references/integrations/betfair_v2.md, tests/test_v2_guidance_hardening.py

2026-08-21 — P2 — MODIFIED: added develop-only overlays for LiveNode hosted run modes (e166a5e57c) and the fallible calculate_commission contract (68975d9347) — files: skills/nt-live/references/guides/run_rust_live_trading.md, skills/nt-adapters/references/guides/official_adapter_spec.md, tests/test_v2_guidance_hardening.py

2026-08-21 — P1 — MODIFIED: refreshed stale G2 durable evidence for nt, nt-adapters, nt-architect, nt-implement, nt-live, nt-review against pinned 6e59fd74ea — files: references/g2-evidence/*.json

2026-08-21 — P1 — CORRECTED: rewrote the NT-2026-08-21-04 record after the independent review disproved its baseline-red evidence claim; tightened the NT-03 closure observation; recorded the v1 Betfair residual as NT-2026-08-21-08 — files: docs/tracking/Findings.md

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

2026-08-23 — P0 — MODIFIED: synchronized the retained Rust analysis crate and corrected active V2 actor, fill-model, data, and adapter contracts — files: skills/nt-signals/references/rust/analysis/, skills/nt-architect/SKILL.md, skills/nt-backtest/SKILL.md, skills/nt-data/SKILL.md, skills/nt-adapters/SKILL.md
2026-08-23 — P1 — MODIFIED: refreshed Betfair recovery guidance, ASCII typography, runtime routing, upstream-worktree safety, and durable validation — files: references/integrations/betfair.md, references/integrations/betfair_v2.md, skills/nt/SKILL.md, skills/nt-dev/SKILL.md, tests/
2026-08-23 — P1 — MODIFIED: synced the mirrored OKX exec tester to the reviewed tip's DRY_RUN safety gate — files: skills/nt-adapters/references/examples/rust_adapters/okx/node_exec_tester.rs
2026-08-23 — P2 — MODIFIED: advanced the reproducible baseline and all pin-derived snapshots/evidence to reviewed develop `d2b62d35a7` — files: tools/upstream_baseline.py, references/developer_guide/, references/g2-evidence/, docs/tracking/
