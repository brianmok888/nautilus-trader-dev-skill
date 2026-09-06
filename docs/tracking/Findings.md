# Findings — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Current evidence-backed findings and closure state. -->
<!-- Does NOT contain: session history, plans, or external attestations. -->

Review date: 2026-09-05
Reviewed upstream develop: `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`
Pinned G2 baseline: `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`

The review manifest preserves five contiguous transitions. The newest transition reviews 61 commits and 561 net changed paths from the previously reviewed `65a168ea14976bf936d30ab67e1187db8f5703d0` through current develop `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`. `references/upstream-delta-review.json` records every transition commit/path classification. The current develop window standardizes adapter task lifecycles (`crates/live/src/task.rs` TaskGroup/TaskSpawner/TaskSlot), adds `LiveNode.add_actor` registration for constructed Python actor instances, refreshes Rust development-guidance docs, and refines model and engine internals; seventeen delta entries carry repository impact; correction findings NT-2026-09-02-01 through NT-2026-09-02-12 were opened and closed from this review cycle.

NT v2 compatibility note: Legacy migration/reference-only Cython/v1 terms and obsolete `references/guides` paths in this whole file are audit evidence, not active guidance; prefer current Rust/PyO3 V2 APIs.

## Open findings — 2026-09-05 full-tree audit

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens below are historical finding evidence (migration reference only).
Eight parallel read-only audit groups (all 17 skills, references/api_reference, references/concepts, references/integrations, templates) plus the 62-commit delta review (4692bac..ac22d5cf) against pinned upstream `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d` (develop tip, 0 ahead). Every finding was verified against the pinned tree; spot-verification by the mission lead re-checked the highest-impact claims (RetryManager invocation API, to-json/to-parquet bin renames, LiveNodeHandle methods, OrderCanceled signature, margin-model surface, add_data_batch, venv layout, crates.io 0.63.0 publication). Nine findings closed during the pin-move wave (receipts in docs/tracking/receipts/harden-nt-v2-20260905/).

[NT-2026-09-05-001] [P1] [CLOSED 2026-09-05] V2 compliance violations: references/concepts/data.md teaches the persistence CLI as `to_json`/`to_parquet` with `cargo run --bin to_json` / `--bin to_parquet` (lines 1449, 1465, 1492, 1502, 1516, 1530); at the tip those binary targets are `to-json`/`to-parquet`, so the commands error out. references/developer_guide/rust.md:136 also still shows `readme = "README.md"` which the new manifest convention drops (Cargo infers README.md).
  file: references/concepts/data.md:1492
  evidence: upstream edc28fb2d (drift window 4692bac..ac22d5cf)
  fix: Rename the tool sections/commands to to-json/to-parquet in references/concepts/data.md and remove the explicit readme line from the manifest example in references/developer_guide/rust.md:135-136.
  acceptance-test: grep -c 'to_json' references/concepts/data.md returns 0 after the correction (or the corrected symbol matches the pin via git -C <upstream> show ac22d5cf4:<path>); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-002] [P1] [CLOSED 2026-09-05] V2 compliance violations: references/concepts/execution.md:140 (mirrored at skills/nt-trading/references/concepts/execution.md:140) teaches 'HALTED: Does not process further order commands until state changes' and a variant list without numeric values; at the tip HALTED=3 permits cancels/queries, REDUCING=2 has strict reduce-only eligibility rules, and the discriminant order swapped. references/integrations/coinbase.md:477 also still teaches that the client threads reduce_only onto the wire for parity, which was replaced by reject-before-transport.
  file: references/concepts/execution.md:140
  evidence: upstream 9da48e039 (drift window 4692bac..ac22d5cf)
  fix: Replace the TradingState bullet list in both execution-concepts copies with the tip's state table (numeric values, permitted commands, REDUCING eligibility rules) and update the Coinbase reduce-only note to rejection-before-transport.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-003] [P1] [CLOSED 2026-09-05] Improvement opportunities: Curated concepts index still points at docs/concepts/reconciliation.md, which upstream renamed/moved to docs/concepts/execution/reconciliation.md while splitting execution.md into execution/index.md, algorithms.md, and policies.md; two more skill-repo links target the old execution.md/reconciliation.md paths.
  file: references/concepts/index.md:115
  evidence: upstream 27dacca2c (drift window 4692bac..ac22d5cf)
  fix: Update the path list in references/concepts/index.md (reconciliation.md -> execution/reconciliation.md, and add the new execution/algorithms.md and execution/policies.md pages) and fix the two relative links in strategies.md:391 and adapters.md:757.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-004] [P1] [CLOSED 2026-09-05] V2 compliance violations: visualization guidance pins plotly>=6.3.1 while upstream python/pyproject.toml now requires plotly>=7.0.0,<8.0.0; following the skill's install line alongside current nautilus_trader produces a dependency conflict (same stale text mirrored at skills/nt-signals/references/visualization.md:22,31).
  file: references/concepts/visualization.md:22
  evidence: upstream ea42d0fde (drift window 4692bac..ac22d5cf)
  fix: Update both copies (references/concepts/visualization.md and skills/nt-signals/references/concepts/visualization.md, plus nt-review/nt-trading migration_reference mentions) to the plotly>=7 line.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-005] [P1] [CLOSED 2026-09-05] V2 compliance violations: Snapshot install commands for the visualization extra lack the now-required --pre flag, so following them installs the v1 wheel that cannot run the v2 documentation the skill repo teaches; the repo-authored docs/visualization.md:10 has the same gap via `uv add`.
  file: references/concepts/visualization.md:25
  evidence: upstream 030ea32d8 (drift window 4692bac..ac22d5cf)
  fix: Add --pre to the uv pip install commands in references/concepts/visualization.md:25 and references/concepts/reports.md:352 at the next snapshot sync, and configure pre-release resolution (or --prerelease=allow) for the `uv add "nautilus_trader[visualization]"` instruction in docs/visualization.md:10.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-006] [P1] [CLOSED 2026-09-05] Improvement opportunities: Synced developer-guide snapshot claims Rust doctests run in per-PR CI and are part of `make pre-flight`; upstream moved them to the scheduled nightly-tests workflow and dropped them from pre-flight and test.yml. Stale developer-workflow guidance for anyone validating Rust changes against the tip.
  file: references/developer_guide/testing.md:209
  evidence: upstream a43deb32c (drift window 4692bac..ac22d5cf)
  fix: At the next dev-guide snapshot sync, replace references/developer_guide/testing.md:208-210 with the nightly-tests wording; check whether any nt-testing/nt-dev guide text repeats the per-PR CI claim.
  closure: snapshot refreshed to ac22d5cf body at pin move; stale doctest claim replaced by upstream text (testing.md:210-212 now nightly-tests workflow)

[NT-2026-09-05-007] [P1] [CLOSED 2026-09-05] V2 compliance violations: references/integrations/polymarket.md:352 teaches that `quote_quantity` orders are rejected before batch submission, but at the tip quote-sized limit BUYs are supported and batchable; only quote-sized SELL orders are denied. The quantity-semantics section at :276 ('Limit orders interpret quantity as base units') also predates the collateral-sized limit BUY mode.
  file: references/integrations/polymarket.md:352
  evidence: upstream 533cfa19a (drift window 4692bac..ac22d5cf)
  fix: Sync the quantity-semantics and batch sections of references/integrations/polymarket.md to the tip: document quote_quantity=True collateral-sized limit BUYs (truncation, exact-price requirement, local quantity update) and narrow the batch rejection list to quote-sized SELL orders.
  acceptance-test: grep -c 'quote_quantity' references/integrations/polymarket.md returns 0 (or content matches pin ac22d5cf4); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-008] [P1] [CLOSED 2026-09-05] V2 compliance violations: official_adapter_spec.md's send_with_retry sample calls self.retry_manager.execute_with_retry(...), an API removed by this commit; any adapter built from the spec fails to compile at the tip.
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:1378
  evidence: upstream 08aa1b70f (drift window 4692bac..ac22d5cf)
  fix: Rewrite the sample to the invocation builder API, e.g. self.retry_manager.invocation("websocket_send", op, should_retry_error, create_timeout_error).cancellation_token(&token).execute().await, and re-check the RetryManager prose at references/developer_guide/adapters.md:1254-1274 against the new builder semantics.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-009] [P1] [CLOSED 2026-09-05] V2 compliance violations: Benchmarking guidance runs `cargo test --locked -p nautilus-backtest --test canonical_backtest_workloads`, which fails at the tip because the test target was renamed to the consolidated `integration` binary (upstream now uses `--test integration canonical_backtest_workloads::`). The same stale command appears in references/developer_guide/benchmarking.md:172, and stale layout paths remain at references/developer_guide/adapters.md:1627 (`tests/python.rs` -> `tests/integration/python.rs`) and references/developer_guide/testing.md:344,345,382 (`crates/data/tests/engine.rs` -> `crates/data/tests/integration/engine.rs`).
  file: skills/nt-backtest/references/guides/benchmarking.md:165
  evidence: upstream 503debebe (drift window 4692bac..ac22d5cf)
  fix: Update the four sites to the tests/integration layout: benchmarking command in both copies, `tests/integration/python.rs` in the adapters test-boundary table, and `crates/data/tests/integration/engine.rs` in the testing.md table/steps.
  acceptance-test: grep -c 'integration' skills/nt-backtest/references/guides/benchmarking.md returns 0 after the correction (or the corrected symbol matches the pin via git -C <upstream> show ac22d5cf4:<path>); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-010] [P1] [CLOSED 2026-09-05] V2 compliance violations: nt-signals portfolio.md:156-160 says 'the removed nautilus_trader.analysis.statistic module allowed defining statistics by inheriting from a Python PortfolioStatistic base class' as a legacy v1 pattern; upstream 7e8c9c9c re-adds that module as the supported v2 path with Portfolio.register_statistic/deregister_statistic, so the 'removed/legacy' framing is stale.
  file: skills/nt-signals/references/concepts/portfolio.md:156
  evidence: upstream 7e8c9c9cd (drift window 4692bac..ac22d5cf)
  fix: Rewrite the custom-statistics section: Python inheritance via nautilus_trader.analysis.statistic.PortfolioStatistic + Portfolio.register_statistic is now a supported v2 path alongside the Rust trait; move the Python pattern out of the legacy-lane framing.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-011] [P1] [CLOSED 2026-09-05] V2 compliance violations: Vendored README badge points to docs.rs/nautilus-analysis/latest/nautilus-analysis/ (hyphenated module path), the exact dead link upstream fixed to .../nautilus_analysis/ in this commit; references/integrations/binance.md:127 also still uses a .html documentation URL that upstream's new convention rejects.
  file: skills/nt-signals/references/rust/analysis/README.md:4
  evidence: upstream a315409b8 (drift window 4692bac..ac22d5cf)
  fix: Update the vendored README badge to the underscored path and convert the binance.md python-api link to the extensionless URL form.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-012] [P1] [CLOSED 2026-09-05] V2 compliance violations: skills/nt-strategy-builder-rust/SKILL.md:102 teaches `fn external_order_claims(&self) -> Option<Vec<InstrumentId>> { None }` as the strategy trait override; the trait method is now external_order_instrument_ids(), so the sample is not a trait member and fails to compile. Stale uses also remain at references/developer_guide/spec_exec_testing.md:2014 and :2303, references/integrations/binance.md:264, and references/integrations/bybit.md:307.
  file: skills/nt-strategy-builder-rust/SKILL.md:102
  evidence: upstream 681607428 (drift window 4692bac..ac22d5cf)
  fix: Rename the trait override to external_order_instrument_ids, document set_external_order_instrument_ids for post-registration claim replacement, and update the four remaining external_order_claims references.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-013] [P1] [CLOSED 2026-09-05] V2 compliance violations: G2 harness expects the pinned upstream venv at the repository root (.venv/bin/python), but upstream moved the project environment to python/.venv by adopting uv's default; against a tip-built checkout the interpreter path no longer exists and assert_python_v2_runtime fails, and the repo's own run_pinned_v2_pytest.py already uses the new python/.venv path, so the two tools disagree.
  file: tools/check_skill_g2_harnesses.py:507
  evidence: upstream 0be8327ae (drift window 4692bac..ac22d5cf)
  fix: Change tools/check_skill_g2_harnesses.py:507 to 'python/.venv/bin/python' (invoked from the python/ cwd) and :710 to upstream_root/'python/.venv/bin/python', update the matching assertions in tests/test_skill_g2_harnesses.py:851,866,974-976 and references/g2-evidence/nt-strategy-builder.json:20, and refresh the .venv guidance in skills/nt-learn/curriculum/01-setup.md:55 and the environment_setup/testing/test_datasets snapshots to python/.venv with UV_PROJECT_ENVIRONMENT removed.
  closure: G2 tool+tests moved to python/.venv (upstream 0be8327ae); red->green proof in docs/tracking/receipts/harden-nt-v2-20260905/phase-2-g2-venv-layout.json

[NT-2026-09-05-014] [P2] [CLOSED 2026-09-05] Improvement opportunities: The end-to-end guide and its guard test pin nautilus crates at 0.62 as the published release lane, while the upstream quickstart the repo policy aligns to now pins 0.63 (workspace at 0.64.0, Python 2.0.0rc5); dependency examples taught to agents are one release behind.
  file: docs/end_to_end_guide.md:34
  evidence: upstream 38314daa1 (drift window 4692bac..ac22d5cf)
  fix: Bump the nautilus-* versions in docs/end_to_end_guide.md:34-39 and skills/nt-learn/curriculum/09-full-rust-trading.md to the quickstart's 0.63, and update the lane assertions in tests/test_active_doc_examples.py:28-29,42 in the same change.
  closure: dependency lane aligned to quickstart 0.63 + guard tests; receipt phase-2-version-lane.json

[NT-2026-09-05-015] [P2] [CLOSED 2026-09-05] Improvement opportunities: references/concepts/message_bus.md 'External streams' section (and nt-live external-streaming guidance) predates typed external streaming: the payload_kind field of the BusMessage record and the typed egress gating for control/execution/reconciliation payloads are undocumented.
  file: references/concepts/message_bus.md:415
  evidence: upstream 9dcf043dc (drift window 4692bac..ac22d5cf)
  fix: Extend the external-streams section with the payload_kind=typed discriminator semantics and note that typed egress applies to control/execution/reconciliation messages while custom payloads keep the prior record shape.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-016] [P2] [CLOSED 2026-09-05] Improvement opportunities: Adapter guidance teaches the open_only/start/end filter contract but not the new shared retain_order_status_reports helper in nautilus-live that standardizes the filtering (open-only includes in-flight; time bounds apply to closed reports only).
  file: references/developer_guide/adapters.md:730
  evidence: upstream 9b7db8236 (drift window 4692bac..ac22d5cf)
  fix: Extend the bulk-report filtering guidance in the adapters reference (and nt-adapters skill) to direct implementers to retain_order_status_reports instead of hand-rolled per-venue filters.
  acceptance-test: python3 tools/check_dev_guide_snapshot_sync.py and check_dev_guide_sync.py exit 0
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-017] [P2] [CLOSED 2026-09-05] Improvement opportunities: Developer-guide snapshot and two skill guides keep the v1-vs-v2 backtest comparison section under benchmarking, which upstream moved into MIGRATION_V2.md when centralizing v2 migration docs. Not wrong to run, but the documented upstream location changed and the synced snapshot will drift.
  file: references/developer_guide/benchmarking.md:191
  evidence: upstream beaac71e0 (drift window 4692bac..ac22d5cf)
  fix: Drop the section from the benchmarking snapshot at re-pin and re-point the comparison-workflow references in nt-dev/nt-backtest guides and SKILL.md to MIGRATION_V2.md.
  closure: withdrawn as invalid: upstream at ac22d5cf still teaches this content itself (testing.md:269, benchmarking.md:183); snapshot is faithful to ground truth, no repo correction required

[NT-2026-09-05-018] [P2] [CLOSED 2026-09-05] Improvement opportunities: Async-test guidance still teaches wait_until_async as the preferred primitive (references/developer_guide/testing.md:275, skills/nt-dev/SKILL.md:381, skills/nt-adapters/references/guides/official_adapter_spec.md:1969); upstream reordered the guidance to notification-first with wait_until_async as fallback.
  file: references/developer_guide/testing.md:275
  evidence: upstream 12f1e9ee2 (drift window 4692bac..ac22d5cf)
  fix: Update the pinned testing.md/adapters.md copies and the nt-dev/nt-adapters skill guidance to the notification-first ordering (subscribe before reading, recheck after every notification, wait_until_async only when no suitable signal exists).
  closure: withdrawn as invalid: upstream at ac22d5cf still teaches this content itself (testing.md:269, benchmarking.md:183); snapshot is faithful to ground truth, no repo correction required

[NT-2026-09-05-019] [P2] [CLOSED 2026-09-05] Improvement opportunities: Skill-repo Bybit execution config tables (references/integrations/bybit.md and skills/nt-adapters/references/integrations/bybit.md) lack the new smp_type config field and BybitOrderSmpType order parameter; zero SMP mentions exist anywhere in the skill repo.
  file: references/integrations/bybit.md:812
  evidence: upstream b1a715004 (drift window 4692bac..ac22d5cf)
  fix: Add the smp_type config row (default None; order parameter overrides; both unset omits the field) and an SMP section to both Bybit reference copies.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-020] [P2] [CLOSED 2026-09-05] Improvement opportunities: Skill-repo Kraken reference lacks the new Futures over-precision guidance: Kraken Futures can return instrument definitions needing more than standard precision's nine decimals, Futures catalog requests now fail outright on any parse error, and high-precision mode must stay enabled for Futures. The existing 'Futures limitation' note covers only bar streaming.
  file: references/integrations/kraken.md:90
  evidence: upstream 6f51bca4b (drift window 4692bac..ac22d5cf)
  fix: Add the precision-mode warning (high-precision required for Futures; catalogs return no partial result and never round/clamp) next to the Futures limitation note, and mirror it in skills/nt-adapters/references/integrations/kraken.md.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-021] [P2] [CLOSED 2026-09-05] Improvement opportunities: The adapter spec's request-signing section teaches storing API keys as Ustr and secrets as Box<[u8]> with #[zeroize], and references/developer_guide/adapters.md's credential section (lines 398-419) teaches custom redacted Debug as the mechanism; upstream now standardizes on SecretString storage with derived Debug and a value-classification table.
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:752
  evidence: upstream 824241ba6 (drift window 4692bac..ac22d5cf)
  fix: Update the spec's Credential guidance and the adapters.md credential section to the new standard: classify values per the upstream table, store secrets as SecretString, derive Debug when all sensitive fields redact, and prefer the HttpClient secret-body/URL-redaction methods.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-022] [P2] [CLOSED 2026-09-05] Improvement opportunities: nt-backtest teaches only add_data/add_data_iterator/manual per-batch add_data loops; the new add_data_batch typed batch input (homogeneous DataBatch, shared validation, replay-key sorting, DeFi routing) is uncovered.
  file: skills/nt-backtest/references/concepts/backtesting.md:133
  evidence: upstream 3c9ad2ef4 (drift window 4692bac..ac22d5cf)
  fix: Add add_data_batch to the nt-backtest data-loading guidance and the Rust example lane as the typed alternative to the per-batch add_data loop, noting validation/sort parity with add_data.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-023] [P2] [CLOSED 2026-09-05] Improvement opportunities: backtesting.md:126-127 presents manual per-batch add_data/run(streaming=True) as 'the pattern used internally by BacktestNode'; after ec1894d6f the node's streaming path lazily k-way merges per-config catalog queries, so the internal-pattern attribution is stale and the multi-config memory-bound behavior is undocumented.
  file: skills/nt-backtest/references/concepts/backtesting.md:126
  evidence: upstream ec1894d6f (drift window 4692bac..ac22d5cf)
  fix: Reword the manual-chunking intro (no longer 'used internally by BacktestNode') and document that BacktestNode streaming now preserves lazy chunking across multiple BacktestDataConfigs.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-024] [P2] [CLOSED 2026-09-05] Improvement opportunities: nt-data cache guidance documents instrument/tick/bar/order/position queries and the durable backing loaders but not the new InstrumentClose cache APIs or their Redis/PostgreSQL persistence and restore/purge behavior.
  file: skills/nt-data/references/guides/cache_operations.md:249
  evidence: upstream 9d45d410d (drift window 4692bac..ac22d5cf)
  fix: Add an InstrumentClose subsection under Instrument Queries and note instrument-close persistence in the Durable Backing Stores section.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-025] [P2] [CLOSED 2026-09-05] Improvement opportunities: nt-live SKILL.md's live task lifecycle section documents TaskGroup generations, TaskSpawner, TaskSlot, and TaskGroupGuard but not the new spawn_named/TaskRef/TaskId identity API and its read-only observation semantics (group remains sole owner; a task may finish before spawn_named returns).
  file: skills/nt-live/SKILL.md:310
  evidence: upstream eb42e2bfc (drift window 4692bac..ac22d5cf)
  fix: Extend the TaskGroup bullet in skills/nt-live/SKILL.md (and the adapters.md snapshot's task-management section) with spawn_named/TaskRef identity semantics and when to prefer it over TaskSlot.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-026] [P2] [CLOSED 2026-09-05] Improvement opportunities: instrument_types.md property lists cover only activation_ns/expiration_ns; the restored activation_utc/expiration_utc properties (and the new delta is_* inspection properties) are not covered anywhere in the skill repo (rg for is_add|is_snapshot|activation_utc over skills/references/tools/tests/docs returns no guidance hits).
  file: skills/nt-model/references/guides/instrument_types.md:138
  evidence: upstream 741b61d6d (drift window 4692bac..ac22d5cf)
  fix: Extend instrument_types.md FuturesContract/FuturesSpread (and other expiring instruments) property lists with activation_utc/expiration_utc alongside the ns variants, and note the delta is_* inspection properties in the order-book data guidance.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-027] [P2] [CLOSED 2026-09-05] Improvement opportunities: skills/nt-model/references/guides/value_type_patterns.md enumerates built-in fiat currencies without TWD, which this commit registers upstream (also 1INCH/CAKE/SHIB crypto); the list is now stale, and the new is_inflight predicate plus 'test finished with is_closed, never by negating is_open' rule are untaught.
  file: skills/nt-model/references/guides/value_type_patterns.md:299
  evidence: upstream bb721205d (drift window 4692bac..ac22d5cf)
  fix: Add TWD to the built-in fiat list and note the is_open/is_inflight/is_closed predicate semantics (SUBMITTED is in-flight, not open; use is_closed for terminal checks) where order status handling is taught.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-028] [P2] [CLOSED 2026-09-05] Improvement opportunities: nt-review's upstream-contribution checklist and the nt-dev Cargo.toml conventions do not cover the new enforced convention that non-default crate features must appear in matching alphabetical `Feature flags` lists in README.md and src/lib.rs; the pre-commit hook now rejects manifests/docs that violate it.
  file: skills/nt-review/AGENTS.md:94
  evidence: upstream fd247cda9 (drift window 4692bac..ac22d5cf)
  fix: Add a checklist/bullet line to nt-review (and nt-dev Cargo.toml conventions) requiring the alphabetical `Feature flags` list in README.md and src/lib.rs to match [features] in Cargo.toml whenever a feature is added or renamed.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S? of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-029] [P1] [CLOSED 2026-09-05] V2 compliance violations: Pinned upstream baseline 4692bac fell 62 commits behind develop tip ac22d5cf; every pin-citing layer required refresh
  file: tools/upstream_baseline.py:4
  evidence: git rev-list --count 4692bac..origin/develop = 62 (2026-09-05); check_upstream_freshness manifest_error at preflight
  fix: Move UPSTREAM_COMMIT to ac22d5cf4; refresh manifest, 19 snapshots, README/end-to-end/curriculum/tracker citations, vendored analysis snapshot, curated sync tokens, exec-spec digest, betfair test path; re-execute all 17 G2 harnesses
  closure: receipt phase-2-pin-move.json; freshness/snapshot/dev-guide/check-cards/card-declarations/legacy/rust-trading-sync all green; pytest 534 passed 3 skipped

[NT-2026-09-05-030] [P1] [CLOSED 2026-09-05] V2 compliance violations: live.md Rust LiveNode example imports Environment from nautilus_live::node, which is not re-exported there; pinned tree defines it in nautilus_common::enums (crates/common/src/enums.rs:200) and every pinned adapter example imports nautilus_common::enums::Environment
  file: skills/nt-adapters/references/concepts/live.md:92
  evidence: crates/common/src/enums.rs:200 `pub enum Environment`; crates/live/src/node/mod.rs:151-157 re-export list has no Environment; e.g. crates/adapters/bybit/examples/node_exec_tester.rs:34 `use nautilus_common::enums::Environment;` (verified via git -C pinned show ac22d5cf4:crates/adapters/bybit/examples/node_exec_tester.rs)
  fix: Change both occurrences (lines 92 and 198) to `use nautilus_common::enums::Environment;` + `use nautilus_live::node::LiveNode;`
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-031] [P1] [CLOSED 2026-09-05] V2 compliance violations: official_adapter_spec.md documents adapter integration tests at tests/{data_client,exec_client,http,websocket}.rs, but upstream commit 503debebe consolidated all Rust integration test binaries under tests/integration/ with a main.rs module harness (betfair/bybit/okx/kraken/deribit/coinbase all verified)
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:1806
  evidence: crates/adapters/bybit/tests/integration/{main.rs,data_client.rs,exec_client.rs,http.rs,websocket.rs,pagination.rs,python.rs} at pin ac22d5cf; crates/adapters/betfair/tests/integration/ likewise; `ls crates/adapters/{bybit,okx,kraken,deribit,coinbase,betfair}/tests/` shows only integration/ (+README.md for betfair). Stale spots: layout tree ~line 1806-1812, table lines 1819-1824, line 1933
  fix: Update the spec layout tree, file table, and integration-testing section to tests/integration/<suite>.rs modules declared from tests/integration/main.rs (per-adapter examples: bybit, betfair)
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-032] [P1] [CLOSED 2026-09-05] V2 compliance violations: lighter.md runs Python examples with `.venv/bin/python` from repo root, but upstream moved the uv project env to python/.venv (commit 0be8327ae, in pin) and upstream docs now use `uv run --project python --no-sync python ...`
  file: skills/nt-adapters/references/integrations/lighter.md:41
  evidence: docs/integrations/lighter.md:45-46 at pin ac22d5cf uses `uv run --project python --no-sync python examples/live/lighter/{data_tester,exec_tester}.py`; upstream Makefile:421 keeps `python/.venv/`; git -C pinned show 0be8327ae stat shows CI/Docker/docs aligned to python/.venv
  fix: Replace the two `.venv/bin/python` lines (41-42) with `uv run --project python --no-sync python examples/live/lighter/...` to match the pinned upstream guide
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-033] [P1] [CLOSED 2026-09-05] V2 compliance violations: official_adapter_spec.md teaches plain-String credential storage: `Ustr` keys in Credential structs (line 752, no pinned adapter does this) and `Option<String>` api_key/api_secret in the config template (line ~2620) while citing crates/adapters/binance/src/config.rs, which at the pin uses `Option<SecretString>`
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:752
  evidence: crates/adapters/bybit/src/common/credential.rs:42-43 `api_key: Box<str>`/`api_secret: Box<[u8]>` with ZeroizeOnDrop; crates/adapters/binance/src/config.rs:191-193 `api_key: Option<SecretString>`; `grep -rn 'api_key: Ustr' crates/adapters/` returns nothing at pin ac22d5cf
  fix: Update line 752 to the pinned storage pattern (Box<str>/SecretString ids, Box<[u8]> secrets, ZeroizeOnDrop, redacting Debug) and the config template at ~2620 to Option<SecretString>
  acceptance-test: grep -c 'Ustr' skills/nt-adapters/references/guides/official_adapter_spec.md returns 0 after the correction (or the corrected symbol matches the pin via git -C <upstream> show ac22d5cf4:<path>); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-034] [P2] [CLOSED 2026-09-05] Improvement opportunities: official_adapter_spec.md credential guidance does not cover the adapter credential-handling standard added by upstream 824241ba60 (SecretString config fields, value classification table, expose_secret/into_inner borrowing rules, redaction tests)
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:748
  evidence: git -C pinned show 824241ba60 -- docs/developer_guide/adapters.md adds 'Classify sensitive values' + 'Use SecretString safely' sections; pinned crates/core/src/string/secret.rs grew to 120+ lines; adapter configs now declare `Option<SecretString>` (e.g. crates/adapters/betfair/src/config.rs:126-132)
  fix: Add a credential-handling subsection mirroring the pinned docs/developer_guide/adapters.md standard (classification, SecretString usage rules, env-var resolution, redaction)
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-035] [P1] [CLOSED 2026-09-05] V2 compliance violations: Shipped okx/node_exec_tester.rs copy uses removed ExecTesterConfig field `external_order_claims` and removed builder method `maybe_open_position_on_start_qty`; pinned tree renamed them to `external_order_instrument_ids` and `open_position_on_start_qty`
  file: skills/nt-adapters/references/examples/rust_adapters/okx/node_exec_tester.rs:111
  evidence: crates/adapters/okx/examples/node_exec_tester.rs:109 `external_order_instrument_ids: Some(vec![instrument_id])`; crates/testkit/src/testers/exec/config.rs:86 `pub open_position_on_start_qty: Option<Decimal>`; `grep -rn 'external_order_claims\|maybe_open_position_on_start_qty' crates/testkit/src crates/adapters/*/examples/` returns nothing at pin ac22d5cf
  fix: Rename line 111 to `external_order_instrument_ids` and line 120 to `.open_position_on_start_qty(order_qty.as_decimal())` to match the pinned example
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-036] [P1] [CLOSED 2026-09-05] V2 compliance violations: Nine more shipped node_exec_tester.rs copies use the removed `external_order_claims` field (and lack the pinned `DRY_RUN` const + `.dry_run(DRY_RUN)` call), so all ten shipped exec testers diverge from the pinned examples they claim to copy
  file: skills/nt-adapters/references/examples/rust_adapters/bybit/node_exec_tester.rs:102
  evidence: Pinned tree uses `external_order_instrument_ids` in every adapter example (e.g. crates/adapters/bybit/examples/node_exec_tester.rs at ac22d5cf); stale copies at kraken:124, architect_ax:106, deribit:106, dydx:101, hyperliquid:99, bybit:102, binance/futures:101, binance/spot:102, bitmex:90; all ten also predate the upstream DRY_RUN additions
  fix: Sync each shipped copy to its pinned counterpart: rename external_order_claims -> external_order_instrument_ids and adopt the DRY_RUN const/.dry_run() wiring
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-037] [P1] [CLOSED 2026-09-05] V2 compliance violations: kraken/node_exec_tester.rs passes plain `String` credentials into config fields that are `Option<SecretString>` at the pin (824241ba60), missing the `.into()` conversions the pinned example performs
  file: skills/nt-adapters/references/examples/rust_adapters/kraken/node_exec_tester.rs:91
  evidence: Pinned crates/adapters/kraken/examples/node_exec_tester.rs uses `api_key: Some(api_key.clone().into())` / `api_secret: Some(api_secret.clone().into())`; pinned kraken config declares SecretString fields (824241ba60 diff touches crates/adapters/kraken/src/config.rs)
  fix: Add `.into()` to the api_key/api_secret initializers at lines 91-92 and the later `api_key,`/`api_secret,` shorthand at ~98-99
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-038] [P1] [CLOSED 2026-09-05] V2 compliance violations: architect_ax/node_data_tester.rs builds configs with `Option<String>` env reads where pinned fields are `Option<SecretString>`, missing the `.map(Into::into)` conversions
  file: skills/nt-adapters/references/examples/rust_adapters/architect_ax/node_data_tester.rs:59
  evidence: Pinned crates/adapters/architect_ax/examples/node_data_tester.rs:59-60 `api_key: std::env::var("AX_API_KEY").ok().map(Into::into)`; 824241ba60 changed architect_ax config.rs to SecretString fields
  fix: Add `.map(Into::into)` to both env-read initializers
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-039] [P1] [CLOSED 2026-09-05] V2 compliance violations: databento/node_data_tester.rs uses `DatabentoLiveClientConfig`, which no longer exists at the pin; the struct is `DatabentoDataClientConfig` exported from `nautilus_databento::data`
  file: skills/nt-adapters/references/examples/rust_adapters/databento/node_data_tester.rs:34
  evidence: crates/adapters/databento/src/data.rs:103 `pub struct DatabentoDataClientConfig`; `grep -rn 'DatabentoLiveClientConfig' crates/` at pin ac22d5cf returns zero hits
  fix: Change the import to `data::DatabentoDataClientConfig` and the constructor call at line 70 accordingly (68a1cbc9e client source layout standardization)
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-040] [P1] [CLOSED 2026-09-05] V2 compliance violations: tardis/node_data_tester.rs still uses `chrono::NaiveDate` for replay dates; pinned example switched to `jiff::civil::Date` and tardis's manifest no longer depends on chrono
  file: skills/nt-adapters/references/examples/rust_adapters/tardis/node_data_tester.rs:28
  evidence: Pinned crates/adapters/tardis/examples/node_data_tester.rs uses `use jiff::civil::Date;`, `Date::new(...)`, and `(i16,i8,i8)` consts; crates/adapters/tardis/Cargo.toml:79 has `jiff = { workspace = true }` and no chrono entry at pin ac22d5cf
  fix: Replace chrono import/usage (lines 28,57-58) with jiff::civil::Date and retuple the REPLAY_FROM/REPLAY_TO consts to (i16,i8,i8)
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-041] [P1] [CLOSED 2026-09-05] V2 compliance violations: blockchain/node_data_tester.rs omits the now-required ENVIO_API_TOKEN env read, passes raw Strings to SecretString builder setters, and registers pyclasses under the removed v1 module path `nautilus_trader.core.nautilus_pyo3.blockchain`
  file: skills/nt-adapters/references/examples/rust_adapters/blockchain/node_data_tester.rs:118
  evidence: Pinned crates/adapters/blockchain/examples/node_data_tester.rs:23,75 require ENVIO_API_TOKEN; :83-84 use `.http_rpc_url(http_rpc_url.into())`; pyclass module is `nautilus_trader.adapters.blockchain` (824241ba60 diff removes `nautilus_trader.adapters.blockchain` pyi legacy exports; python tree has no core.nautilus_pyo3 at pin)
  fix: Sync the copy to the pinned example: add get_env_var("ENVIO_API_TOKEN")?, add .into() on rpc urls, fix both pyclass module attributes (lines 118,190) to nautilus_trader.adapters.blockchain
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: NT v2 compatibility note: legacy tokens quoted here are migration/reference-only audit evidence; (quoted legacy tokens are migration/reference-only audit evidence) legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-042] [P2] [CLOSED 2026-09-05] Improvement opportunities: api/adapters/index.md toctree lists 10 adapter API stubs; pinned upstream docs/api_reference/adapters documents 16 (adds architect_ax, bitmex, deribit, hyperliquid, kraken, sandbox)
  file: skills/nt-adapters/references/api/adapters/index.md:18
  evidence: docs/api_reference/adapters/index.md at pin ac22d5cf lists architect_ax, betfair, binance, bitmex, bybit, databento, deribit, dydx, hyperliquid, interactive_brokers, kraken, okx, polymarket, sandbox, tardis; python/nautilus_trader/adapters/ contains all those modules
  fix: Add stub pages + toctree entries for the six missing adapters to match the pinned API reference
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-043] [P1] [CLOSED 2026-09-05] V2 compliance violations: bitmex.md points readers to examples/live/bitmex/bitmex_exec_tester.py for the MARK_PRICE stop-trigger ExecTester config, but upstream deleted the entire examples/live/bitmex/ directory (e8daa045ab); the pinned equivalent is crates/adapters/bitmex/examples/node_exec_tester.rs
  file: skills/nt-adapters/references/integrations/bitmex.md:253
  evidence: `ls examples/live/` at pin ac22d5cf has no bitmex dir; git -C pinned show e8daa045ab --stat deletes examples/live/bitmex/{bitmex_data_tester,bitmex_exec_tester,data_tester,exec_tester}.py; pinned crates/adapters/bitmex/examples/node_exec_tester.rs:105 `.stop_trigger_type(TriggerType::MarkPrice)`; pinned docs/integrations/bitmex.md:256 links the Rust tester
  fix: Replace the examples/live/bitmex/bitmex_exec_tester.py reference with crates/adapters/bitmex/examples/node_exec_tester.rs
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-044] [P1] [CLOSED 2026-09-05] V2 compliance violations: official_adapter_spec.md's endpoint-scoped reconnect section invents ReconnectRequestOutcome variants `AlreadyPending` and `Unavailable`; the pinned enum (crates/network/src/mode.rs, re-exported as SocketReconnectRequestOutcome) has Accepted/AlreadyReconnecting/Disconnected/Closed/Unsupported
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:963
  evidence: crates/network/src/mode.rs:251-262 `pub enum ReconnectRequestOutcome { Accepted, AlreadyReconnecting, Disconnected, Closed, Unsupported }`; crates/live/src/socket.rs:36 re-export; `grep -rn 'AlreadyPending\|Unavailable' crates/network/ crates/live/` returns nothing at pin ac22d5cf
  fix: Correct lines 963-964 to the pinned variants and adjust the test-guidance sentence accordingly
  acceptance-test: grep -c 'AlreadyPending' skills/nt-adapters/references/guides/official_adapter_spec.md returns 0 after the correction (or the corrected symbol matches the pin via git -C <upstream> show ac22d5cf4:<path>); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-045] [P2] [CLOSED 2026-09-05] V2 compliance violations: official_adapter_spec.md's AuthTracker snippet shows `authenticated: Arc<AtomicBool>`; the pinned struct tracks state as `state: Arc<AtomicU8>` plus a `state_notify: Arc<Notify>` (lifecycle methods begin/succeed/fail/invalidate are correct)
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:980
  evidence: crates/network/src/websocket/auth.rs:107-111 `pub struct AuthTracker { tx: Arc<Mutex<Option<AuthResultSender>>>, state: Arc<AtomicU8>, state_notify: Arc<tokio::sync::Notify> }` at pin ac22d5cf
  fix: Update the illustrative struct fields to the pinned shape (or drop the field-level snippet and describe the lifecycle only)
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-046] [P1] [CLOSED 2026-09-05] V2 compliance violations: official_adapter_spec.md teaches a `BoundedDedup<T>` type for trade-ID dedup that does not exist anywhere in the pinned tree; the pinned mechanism is `nautilus_common::cache::fifo::FifoCache<T, N>` (insert() -> bool duplicate signal), used by e.g. hyperliquid's WsDispatchState
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:1327
  evidence: `grep -rn 'BoundedDedup' crates/` at pin ac22d5cf returns zero hits; crates/common/src/cache/fifo.rs:62 `pub struct FifoCache<T, const N: usize>` with insert()->bool at :119; crates/adapters/hyperliquid/src/websocket/dispatch.rs:168-171 uses `emitted_trades: Mutex<FifoCache<TradeId, DEDUP_CAPACITY>>`
  fix: Replace the BoundedDedup snippet with the pinned FifoCache pattern (nautilus_common::cache::fifo::FifoCache, capacity as const generic, insert() returning bool)
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-047] [P2] [CLOSED 2026-09-05] V2 compliance violations: rust.md's aligned-targets table lists cargo-test/clippy features as `ffi,python,high-precision,defi`, but the pinned Makefile's BASE_FEATURES is `arrow,ffi,python,high-precision,streaming,defi` (scripts/cargo-features.bash), so the stated feature set no longer matches the shared build cache key
  file: skills/nt-adapters/references/guides/rust.md:51
  evidence: Makefile:180/182 + `bash scripts/cargo-features.bash` at pin ac22d5cf emits `arrow,ffi,python,high-precision,streaming,defi`; Makefile:893 passes --features "$(CARGO_FEATURES)" to cargo nextest run
  fix: Update the two feature-set cells in the aligned-targets table to arrow,ffi,python,high-precision,streaming,defi
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-048] [P1] [CLOSED 2026-09-05] V2 compliance violations: SKILL.md says integration tests live in the `tests/` directory, but commit 503debebe consolidated all Rust adapter integration test binaries under `tests/integration/` with a main.rs harness at the pin
  file: skills/nt-adapters/SKILL.md:599
  evidence: crates/adapters/{bybit,okx,kraken,deribit,coinbase,betfair}/tests/ contain only integration/ (+README.md for betfair) at ac22d5cf; e.g. crates/adapters/bybit/tests/integration/main.rs declares mod data_client; mod exec_client; mod http; ...
  fix: Update the bullet to 'Integration tests in `tests/integration/` (single binary per adapter, main.rs harness)'
  acceptance-test: grep -c 'tests/' skills/nt-adapters/SKILL.md returns 0 after the correction (or the corrected symbol matches the pin via git -C <upstream> show ac22d5cf4:<path>); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-049] [P2] [CLOSED 2026-09-05] V2 compliance violations: SKILL.md's own configuration sketch uses `testnet: bool` and `Option<String>` credentials, contradicting its own high-risk rule to use adapter environment enums and the pinned SecretString credential fields
  file: skills/nt-adapters/SKILL.md:485
  evidence: SKILL.md line ~112 mandates adapter environment enums (Live/LIVE naming); pinned configs use typed environment enums (e.g. crates/adapters/binance/src/common/enums.rs:133 BinanceEnvironment{Live,Testnet,Demo}) and Option<SecretString> credential fields (crates/adapters/binance/src/config.rs:191-193)
  fix: Replace testnet: bool with an environment enum field and Option<SecretString> credential fields in the sketch
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-050] [P1] [CLOSED 2026-09-05] V2 compliance violations: hyperliquid.md claims a Python `HyperliquidExecutionClient` lives at nautilus_trader/adapters/hyperliquid/execution.py and runs `_handle_order_status_report_pyo3`; neither the module nor the method exists at the pin - the projection is a flat __init__.py
  file: skills/nt-adapters/references/integrations/hyperliquid.md:708
  evidence: `ls python/nautilus_trader/adapters/hyperliquid/` at pin ac22d5cf shows only __init__.py/__init__.pyi; `grep -rn '_handle_order_status_report_pyo3' python/ crates/` returns nothing
  fix: Delete or rewrite the note: the pinned surface has no per-module Python execution client; describe only the Rust dispatch path
  acceptance-test: grep -c 'HyperliquidExecutionClient' skills/nt-adapters/references/integrations/hyperliquid.md returns 0 (or content matches pin ac22d5cf4); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-051] [P2] [CLOSED 2026-09-05] Improvement opportunities: official_adapter_spec.md's retry section is a single sentence and does not cover the pinned RetryManager invocation API simplified by 08aa1b70fe (invocation(name, op, should_retry, create_error).cancellation_token(&t).execute())
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:826
  evidence: crates/network/src/retry.rs:126+ RetryManager with bon builder; pinned usage e.g. crates/adapters/bitmex/src/http/client.rs:495-500 `.invocation(endpoint.as_str(), operation, should_retry, create_error).cancellation_token(&cancel_token).execute().await`; 08aa1b70fe 'Simplify RetryManager invocation API' replaced specialized retry methods with one configurable builder
  fix: Expand the section with the pinned invocation-builder pattern (single invocation() entry point, cancellation_token, execute) and the RetryError variants to map
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-052] [P1] [CLOSED 2026-09-05] V2 compliance violations: official_adapter_spec.md's Python testing layout points to tests/integration_tests/adapters/<venue>/, which does not exist at the pin; adapter Python tests live under python/tests/unit/adapters/<venue>/ and Rust-side Python-projection tests under crates/adapters/<venue>/tests/integration/python.rs
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:1979
  evidence: `find python/tests -type d -name integration_tests` returns nothing at ac22d5cf; python/tests/unit/adapters/{bybit,okx,...}/ exist (e.g. unit/adapters/bybit/test_bybit_factories.py); crates/adapters/{betfair,binance,bitmex,blockchain,bybit}/tests/integration/python.rs exist
  fix: Rewrite the Python testing layout to python/tests/unit/adapters/<venue>/ and reference the Rust tests/integration/python.rs projection suites
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-053] [P1] [CLOSED 2026-09-05] V2 compliance violations: spec_exec_testing.md (symlinked from nt-adapters references/guides) documents the removed ExecTesterConfig field `external_order_claims`; the pinned Python and Rust ExecTesterConfig both expose `external_order_instrument_ids` (shared file, noted once under its real path)
  file: skills/nt-testing/references/guides/spec_exec_testing.md:2005
  evidence: python/nautilus_trader/testkit/__init__.pyi:128,197 `external_order_instrument_ids`; crates/testkit/src/testers/exec/config.rs + strategy.rs:112; `grep -rn 'external_order_claims' python/ crates/testkit/` returns nothing at pin ac22d5cf; stale occurrences at lines 2005 and 2294
  fix: Rename both occurrences (guide text at 2005, config table row at 2294) to external_order_instrument_ids
  acceptance-test: grep -c 'external_order_claims' skills/nt-testing/references/guides/spec_exec_testing.md returns 0 after the correction (or the corrected symbol matches the pin via git -C <upstream> show ac22d5cf4:<path>); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S5 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s5-adapters.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-054] [P1] [CLOSED 2026-09-05] V2 compliance violations: environment_setup guide still teaches the repository-root .venv layout; upstream moved the uv project environment to python/.venv in 0be8327ae (drift window).
  file: skills/nt-live/references/guides/environment_setup.md:62
  evidence: pinned docs/developer_guide/environment_setup.md:59 'source python/.venv/bin/activate', :61 'export PYO3_PYTHON="$PWD/python/.venv/bin/python"', :297 'install the Python package into python/.venv', :598 VIRTUAL_ENV '<path-to-nautilus-trader>/python/.venv'; upstream commit 0be8327ae589f64426ccf6a12a3da5ac85616454 'Use uv's default project environment'. Skill lines 62/64 (quick setup), 191 (PYO3_PYTHON export), 275 ('root .venv' build note), 506-552 (rust-analyzer VIRTUAL_ENV) all use the old root path.
  fix: Update lines 62-64, 191, 275, and the rust-analyzer VIRTUAL_ENV examples to python/.venv paths; align the quick-setup block with the pinned doc (make sync, source python/.venv/bin/activate, PYO3_PYTHON="$PWD/python/.venv/bin/python").
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-055] [P1] [CLOSED 2026-09-05] V2 compliance violations: Stale pin citation: rust.md cites pinned `4692bac35` for the LiveNode Python registration surface, but the mission baseline moved tree-wide to ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d.
  file: skills/nt-live/references/concepts/rust.md:258
  evidence: skills/nt-live/references/concepts/rust.md:258 'node.add_strategy_from_config(config) (pinned `4692bac35`'. The cited API itself is current at the pin: python/nautilus_trader/live/__init__.pyi:383-386 (add_actor, add_actor_from_config, add_strategy, add_strategy_from_config at ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d).
  fix: Re-cite the registration surface as pinned ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d (python/nautilus_trader/live/__init__.pyi).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-056] [P1] [CLOSED 2026-09-05] V2 compliance violations: rust.md teaches a `stubs` cargo feature on nautilus-model that does not exist at the pinned tree; test stubs are gated behind `test-support`.
  file: skills/nt-live/references/concepts/rust.md:148
  evidence: crates/model/Cargo.toml [features] at ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d lists test-support/high-precision/defi/arrow/python/ffi (no `stubs`); crates/model/src/instruments/mod.rs:40 gates the stubs module with #[cfg(any(test, feature = "test-support"))]. Skill lines 112 and 135 also specify features = ["stubs"] on nautilus-model dependencies, which cargo rejects at the pin.
  fix: Rename the feature-flag table row to `test-support` (nautilus-model, test stubs such as audusd_sim) and change both dependency examples (lines 112, 135) from features = ["stubs"] to features = ["test-support"].
  acceptance-test: grep -c 'stubs' skills/nt-live/references/concepts/rust.md returns 0 after the correction (or the corrected symbol matches the pin via git -C <upstream> show ac22d5cf4:<path>); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-057] [P1] [CLOSED 2026-09-05] V2 compliance violations: Related-guides block points at docs/latest/developer_guide/{architecture,actors,strategies,events,backtesting}/ URLs that do not exist at the pinned tree; those pages live under docs/concepts/.
  file: skills/nt-live/references/concepts/rust.md:372
  evidence: Pinned docs/ tree (git -C <upstream> ls-tree ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d docs/developer_guide/) contains no architecture/actors/strategies/events/backtesting pages; the equivalents are docs/concepts/architecture.md, docs/concepts/actors.md, docs/concepts/strategies.md, docs/concepts/events/, docs/concepts/backtesting/ (also how upstream links them from docs/concepts/rust.md:472-482). Skill lines 372-376 use the developer_guide paths.
  fix: Rewrite lines 372-376 to https://nautilustrader.io/docs/latest/concepts/{architecture,actors,strategies,events,backtesting}/.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-058] [P1] [CLOSED 2026-09-05] V2 compliance violations: Architecture guide's Rust crate inventory omits the infrastructure and event_store crates, both present at the pin and taught elsewhere in this skill (RedisCacheConfig/PostgresCacheConfig live in nautilus-infrastructure).
  file: skills/nt-live/references/concepts/architecture.md:579
  evidence: Pinned workspace contains crates/infrastructure and crates/event_store (git -C <upstream> ls-tree ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d crates/); upstream docs/concepts/architecture.md:633 lists 'infrastructure, persistence, and event_store' and :735 categorizes 'network, cryptography, infrastructure, persistence, event_store'. Skill table line 579 lists only serialization/network/cryptography/persistence, and the mermaid dependency graph (lines 525-533) omits both crates.
  fix: Add infrastructure and event_store to the Infrastructure row and the dependency graph (event_store under Infrastructure, infrastructure owning Redis/Postgres cache and msgbus backings).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-059] [P1] [CLOSED 2026-09-05] V2 compliance violations: Migration reference falsely claims `add_stream_processor` does not exist at the pinned baseline; LiveNode exposes it in Rust and PyO3 at the pin.
  file: skills/nt-live/migration_reference/python/deployment-v1-tradingnode.md:238
  evidence: crates/live/src/node/mod.rs:362 'pub fn add_stream_processor' and crates/live/src/python/node.rs:916 pyo3 'add_stream_processor' at ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d; python/nautilus_trader/live/__init__.pyi:378 'def add_stream_processor(self, callback: typing.Any) -> None'. Skill line 238 states it 'does not exist at the pinned baseline'.
  fix: Correct the compatibility note: custom stream processors remain a runtime LiveNode API (node.add_stream_processor), while external egress/ingress wiring moved to the builder (with_external_msgbus_egress/with_external_msgbus_factory/with_external_ingress).
  acceptance-test: grep -c 'add_stream_processor' skills/nt-live/migration_reference/python/deployment-v1-tradingnode.md returns 0 (or content matches pin ac22d5cf4); python3 -m pytest -q green
  closure: NT v2 compatibility note: legacy tokens quoted here are migration/reference-only audit evidence; (quoted legacy tokens are migration/reference-only audit evidence) legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-060] [P2] [CLOSED 2026-09-05] Improvement opportunities: Live task identity from the drift window (eb42e2bfc: TaskId, TaskRef, TaskGroup::spawn_named / TaskSpawner::spawn_named) is not covered; the task-lifecycle section documents TaskGroup/TaskSpawner/TaskSlot only.
  file: skills/nt-live/SKILL.md:302
  evidence: crates/live/src/task.rs at ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d:105 'pub struct TaskId(u64)', :128 'pub struct TaskRef', :255 and :416 'pub fn spawn_named'; docs/developer_guide/adapters.md:1611 '## Task management', :1630 'Use TaskGroup::spawn_named when client state must observe a task's identity', :1676 TaskSpawner::spawn_named. Introduced by eb42e2bfc6c5540839dbdaade7fdef242a6f3b2e (in 4692bac..ac22d5cf). grep for spawn_named|TaskRef|TaskId across skills/nt-live/ returns nothing.
  fix: Extend the 'Live task lifecycle' section with named-task identity: spawn_named returning a read-only TaskRef (logical name, instance identity, terminal state) without transferring ownership, TaskId numbering, and when adapter clients should use it per docs/developer_guide/adapters.md Task management.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-061] [P2] [CLOSED 2026-09-05] Improvement opportunities: Concepts/live guide (symlinked into nt-live as references/concepts/live.md; noted once under its real path) does not cover the two sections upstream added to docs/concepts/live.md in the drift window: 'Backtest and live differences' and 'Dispatch priority and overload behavior'.
  file: skills/nt-adapters/references/concepts/live.md:11
  evidence: Pinned docs/concepts/live.md:13 '## Backtest and live differences' (venue/transport/timing/persistence/external-activity deltas) and :245 '## Dispatch priority and overload behavior' (seven unbounded runner channels, polling order, no producer backpressure); both added by 27dacca2c 'Restructure execution documentation' within 4692bac..ac22d5cf. grep across skills/nt-live/ for 'Backtest and live differences', 'polling order', 'global FIFO', 'backpressure' returns nothing.
  fix: Add matching sections (or a pointer) covering backtest-vs-live behavioral differences and runner dispatch priority/overload semantics (no backpressure, no coalescing, queue growth under sustained overload) to the live concepts guide consumed by nt-live.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S6 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s6-shared-refs-live.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-062] [P1] [CLOSED 2026-09-05] V2 compliance violations: nt-model SKILL.md lists v1 Python module paths (model/identifiers, model/instruments/, model/types/, model/objects, model/enums, model/tick_scheme/) that do not exist in the pinned flat PyO3 surface.
  file: skills/nt-model/SKILL.md:94
  evidence: git ls-tree -r ac22d5cf --name-only python/nautilus_trader/model -> only __init__.py and __init__.pyi (flat re-export); skill's own references/api/model/tick_scheme.md:3-7 states the package is flat with no submodules.
  fix: Replace the Python modules line with the flat surface: 'nautilus_trader.model (flat PyO3 re-export) and nautilus_trader.testkit'.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-063] [P1] [CLOSED 2026-09-05] V2 compliance violations: value_types.md imports from stale v1 submodules nautilus_trader.model.objects and nautilus_trader.model.currencies instead of the flat nautilus_trader.model surface (lines 24, 62, 89, 188-190, 209, 225, 244).
  file: skills/nt-model/references/concepts/value_types.md:24
  evidence: upstream docs/concepts/value_types.md:22 'from nautilus_trader.model import Quantity', :246 'Currency.from_str("USD")'; python/nautilus_trader/model/__init__.pyi has no objects/currencies submodules at ac22d5cf.
  fix: Change all imports to 'from nautilus_trader.model import ...' and replace 'from nautilus_trader.model.currencies import USD, EUR' with 'USD = Currency.from_str("USD")'.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-064] [P1] [CLOSED 2026-09-05] V2 compliance violations: value_types.md teaches that same-type arithmetic always returns the original type; at the pin, same-type * / // % return Decimal, and unary minus on Quantity returns Decimal.
  file: skills/nt-model/references/concepts/value_types.md:50
  evidence: upstream docs/concepts/value_types.md:68-120 documents 'Price * Price -> Decimal' and the unary-operator table; python/nautilus_trader/model/__init__.pyi:6322 __neg__ -> decimal.Decimal (Quantity), __mul__/__truediv__ -> typing.Any backed by crates/model/src/python/types/price.rs:238.
  fix: Sync the Same-type operations section with upstream docs/concepts/value_types.md (add the Decimal-result table for * / // % and the unary operators section).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-065] [P1] [CLOSED 2026-09-05] V2 compliance violations: instruments.md imports TestInstrumentProvider from 'nautilus_trader.test_kit.providers' (underscore spelling) which does not exist; the pinned module is nautilus_trader.testkit.
  file: skills/nt-model/references/concepts/instruments.md:43
  evidence: python/nautilus_trader/testkit/providers.py:123 'class TestInstrumentProvider' at ac22d5cf; no python/nautilus_trader/test_kit directory exists in the pinned tree.
  fix: Change the import to 'from nautilus_trader.testkit.providers import TestInstrumentProvider'.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-066] [P1] [CLOSED 2026-09-05] V2 compliance violations: instruments.md live-discovery example imports BinanceSpotInstrumentProvider from nautilus_trader.adapters.binance.spot.providers; the class and submodule do not exist at the pin (adapters/binance ships only __init__, instruments.py).
  file: skills/nt-model/references/concepts/instruments.md:51
  evidence: git ls-tree -r ac22d5cf python/nautilus_trader/adapters/binance -> __init__.py, __init__.pyi, instruments.py only; 'BinanceSpotInstrumentProvider' appears at ac22d5cf only in historical RELEASES.md entries.
  fix: Replace the adapter example with the current mechanism per upstream docs/concepts/instruments/index.md (instruments are cached automatically by Rust adapter InstrumentProviders; access via cache.instrument()) or use an adapter that still exposes a Python provider surface at the pin.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-067] [P1] [CLOSED 2026-09-05] V2 compliance violations: instruments.md imports from stale submodule nautilus_trader.model.instruments (lines 66, 111, 459) instead of the flat nautilus_trader.model surface.
  file: skills/nt-model/references/concepts/instruments.md:66
  evidence: upstream docs/concepts/instruments/synthetic_instrument.md:57-59 'from nautilus_trader.model import InstrumentId/Symbol/SyntheticInstrument'; python/nautilus_trader/model is flat at ac22d5cf.
  fix: Change 'from nautilus_trader.model.instruments import X' to 'from nautilus_trader.model import X' at lines 66, 111, 459 (line 111 defines the on_instrument callback type).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-068] [P1] [CLOSED 2026-09-05] V2 compliance violations: Commissions section (instruments.md:326-408) teaches a Cython-era get_commission signature (Order_order, Quantity_fill_qty, Price_fill_px, Instrument_instrument); the pinned Python FeeModel uses (_order, _fill_quantity, _fill_px, _instrument), and hand-rolling a per-contract model hides the built-in PerContractFeeModel and get_commission_with_context.
  file: skills/nt-model/references/concepts/instruments.md:352
  evidence: python/nautilus_trader/execution/__init__.pyi FeeModel.get_commission(_order, _fill_quantity: model.Quantity, _fill_px: model.Price, _instrument) and get_commission_with_context(...); __all__ includes PerContractFeeModel at ac22d5cf.
  fix: Rewrite the custom fee model example against the pinned signature, mention built-in PerContractFeeModel (from nautilus_trader.execution) and get_commission_with_context, and drop the Cython parameter-naming narrative.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: NT v2 compatibility note: legacy tokens quoted here are migration/reference-only audit evidence; (quoted legacy tokens are migration/reference-only audit evidence) legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-069] [P2] [CLOSED 2026-09-05] Improvement opportunities: overview.md data types list omits MarkPriceUpdate, IndexPriceUpdate, FundingRateUpdate and OptionGreeks which the pinned overview documents.
  file: skills/nt-model/references/concepts/overview.md:123
  evidence: upstream docs/concepts/overview.md:156-168 at ac22d5cf lists 13 data types including MarkPriceUpdate, IndexPriceUpdate, FundingRateUpdate, OptionGreeks.
  fix: Extend the Data types list with the four missing types and the custom-data pointer sentence from upstream.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-070] [P2] [CLOSED 2026-09-05] Improvement opportunities: instrument_types.md does not cover the drift-window Python instrument properties: direct instrument.symbol / instrument.venue getters and activation_utc / expiration_utc on expiring instruments.
  file: skills/nt-model/references/guides/instrument_types.md:83
  evidence: commits 20a16b761 and 741b61d6d (in 4692bac..ac22d5cf); python/nautilus_trader/model/__init__.pyi:448/450 instrument symbol()/venue() getters and impl_instrument_utc_getters (activation_utc/expiration_utc) in crates/model/src/python/instruments/mod.rs.
  fix: Add instrument.symbol/venue to the key-properties list and note activation_utc/expiration_utc alongside the existing activation_ns/expiration_ns coverage (lines 138, 357).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-071] [P1] [CLOSED 2026-09-05] V2 compliance violations: backtesting.md 'Automatic chunking' pattern calls engine.add_data_iterator(data_name=..., generator=...) which does not exist anywhere in the pinned tree (repeated at line 1120 for timer-only backtests).
  file: skills/nt-backtest/references/concepts/backtesting.md:118
  evidence: git grep -n 'add_data_iterator' ac22d5cf returns nothing in crates/ or python/; upstream docs/concepts/backtesting/apis-and-runs.md:88 explicitly states 'The low-level API does not expose a generator-based add_data_iterator() method.'
  fix: Remove the add_data_iterator streaming subsection; document the real streaming options: manual chunking with run(streaming=True)+clear_data()+end() (already shown) and BacktestNode catalog streaming per apis-and-runs.md.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-072] [P1] [CLOSED 2026-09-05] V2 compliance violations: backtesting.md fill-model configuration uses ImportableFillModelConfig/FillModelConfig and paths nautilus_trader.backtest.models:FillModel / nautilus_trader.backtest.config:FillModelConfig; none exist at the pin and upstream explicitly removed import-path fill model loading.
  file: skills/nt-backtest/references/concepts/backtesting.md:1160
  evidence: git grep 'ImportableFillModelConfig\|class FillModelConfig' ac22d5cf -- python/ returns nothing; upstream docs/concepts/backtesting/fill-models.md:103-104 'The current high-level venue configuration accepts built-in fill models. It does not load fill models from import-path configuration objects.'
  fix: Replace the ImportableFillModelConfig examples with built-in model instances per upstream fill-models.md (e.g. fill_model=ThreeTierFillModel(prob_fill_on_limit=1.0, prob_slippage=0.0, random_seed=42) from nautilus_trader.execution) and note the low-level custom-object protocol.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-073] [P1] [CLOSED 2026-09-05] V2 compliance violations: backtesting.md margin-model section (1429-1644) teaches MarginModelConfig(model_type='standard'|'leveraged'|custom-path), MarginModelFactory.create, account.set_margin_model(), TestExecStubs.margin_account() and nautilus_trader.backtest.models imports - none exist on the pinned Python surface.
  file: skills/nt-backtest/references/concepts/backtesting.md:1452
  evidence: git grep 'MarginModelConfig\|MarginModelFactory\|TestExecStubs' ac22d5cf -- python/ returns nothing; MarginAccount pyi has no set_margin_model; the real API is from nautilus_trader.model import StandardMarginModel / LeveragedMarginModel with add_venue(margin_model=...) or BacktestVenueConfig(margin_model=...) per upstream docs/concepts/backtesting/accounts-and-margin.md:74-95 and crates/backtest/src/python/engine.rs:1588-1602 (accepts only Standard/Leveraged instances).
  fix: Rewrite Usage/Real-world/Custom-model subsections to the pinned API: margin_model=StandardMarginModel() / LeveragedMarginModel() in BacktestVenueConfig or engine.add_venue(); delete MarginModelConfig/MarginModelFactory/set_margin_model/TestExecStubs examples and the custom-Python-margin-model how-to (not supported at the pin).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-074] [P1] [CLOSED 2026-09-05] V2 compliance violations: backtesting.md Python snippets import from stale v1 module paths throughout: backtest.engine (67, 245, 1071, 1330), backtest.node (223), backtest.config (552, 673, 897, 1159-1160, 1182-1183, 1451-1452, 1595), model.enums (1072, 1246, 1332), model.currencies (392/1331), model.objects (1245), model.book (1245), data.config (1098), core.rust.model (1247).
  file: skills/nt-backtest/references/concepts/backtesting.md:67
  evidence: pinned python tree is flat: nautilus_trader.backtest (BacktestEngine/BacktestNode/BacktestVenueConfig), nautilus_trader.model (Money/Currency/OmsType/AccountType/OrderSide/OrderBook/BookType), nautilus_trader.data (DataEngineConfig), nautilus_trader.execution (FillModel); upstream docs use e.g. docs/getting_started/backtest_low_level.py:23 'from nautilus_trader.backtest import BacktestEngine'; 'nautilus_trader.core.rust' is v1-only.
  fix: Rewrite all import lines to the flat pinned modules: nautilus_trader.backtest, nautilus_trader.model, nautilus_trader.data, nautilus_trader.execution, nautilus_trader.config (for BacktestEngineConfig re-exports).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-075] [P1] [CLOSED 2026-09-05] V2 compliance violations: SKILL.md Cargo dependency block pins nautilus crates at version 0.62; the pinned workspace version is 0.64.0.
  file: skills/nt-backtest/SKILL.md:137
  evidence: root Cargo.toml at ac22d5cf line 52: version = "0.64.0"; crates/* use version.workspace = true (e.g. crates/backtest/Cargo.toml:3).
  fix: Bump the five nautilus-* dependency versions in the SKILL.md Cargo.toml block from "0.62" to "0.64".
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-076] [P1] [CLOSED 2026-09-05] V2 compliance violations: run_rust_backtest.md dependency block pins nautilus crates at version 0.62; the pinned workspace version is 0.64.0.
  file: skills/nt-backtest/references/guides/run_rust_backtest.md:20
  evidence: root Cargo.toml at ac22d5cf line 52: version = "0.64.0"; crates/* use version.workspace = true.
  fix: Bump the five nautilus-* dependency versions from "0.62" to "0.64".
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-077] [P1] [CLOSED 2026-09-05] V2 compliance violations: SKILL.md Rust fill-model example calls self.sample(...) and self.simulated_book(...), which are not methods of the pinned FillModel trait - the example cannot compile.
  file: skills/nt-backtest/SKILL.md:335
  evidence: crates/execution/src/models/fill.rs at ac22d5cf defines the FillModel trait (line 48) with is_limit_filled, is_slipped, fill_limit_inside_spread, get_orderbook_for_fill_simulation only; git grep 'fn sample\|fn simulated_book' ac22d5cf -- crates/ returns no FillModel methods.
  fix: Replace sample()/simulated_book() calls with concrete logic in the example (e.g. rand sampling inside the user struct and a constructed OrderBook), matching the pinned trait surface.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-078] [P1] [CLOSED 2026-09-05] V2 compliance violations: references/examples/rust_backtest/engine_ema_cross.rs is a stale copy: it calls add_venue with ~30 positional arguments (Venue, OmsType, ..., FillModelAny::default(), FeeModelAny::default(), ...), but the pinned Rust engine takes a single SimulatedVenueConfig.
  file: skills/nt-backtest/references/examples/rust_backtest/engine_ema_cross.rs:89
  evidence: crates/backtest/src/engine.rs:274 at ac22d5cf: 'pub fn add_venue(&mut self, config: SimulatedVenueConfig)'; upstream crates/backtest/examples/engine_ema_cross.rs uses SimulatedVenueConfig::builder().venue(...).oms_type(...)...build() (diff shows the divergence).
  fix: Replace the file body with the pinned upstream crates/backtest/examples/engine_ema_cross.rs (including the mimalloc allocator gating and constants), keeping any skill header comment.
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-079] [P1] [CLOSED 2026-09-05] V2 compliance violations: order_book.md note references the removed nautilus_pyo3 module and the v1 path nautilus_trader.model.book.OrderBook; the pinned surface is flat nautilus_trader.model.OrderBook.
  file: skills/nt-backtest/references/concepts/order_book.md:14
  evidence: no nautilus_pyo3 files or references exist under python/ at ac22d5cf (git grep nautilus_pyo3 returns nothing); python/nautilus_trader/common/__init__.pyi:337 cache.order_book() -> model.OrderBook on the flat module.
  fix: Rewrite the note: Python access is 'from nautilus_trader.model import OrderBook, OwnOrderBook' on the flat PyO3 surface.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-080] [P1] [CLOSED 2026-09-05] V2 compliance violations: benchmarking.md canonical-workload semantic-check command uses '--test canonical_backtest_workloads'; after 503debebe (in the drift window) integration tests were consolidated and the invocation is '--test integration canonical_backtest_workloads::'.
  file: skills/nt-backtest/references/guides/benchmarking.md:164
  evidence: commit 503debebe 'Consolidate Rust integration test binaries' changed Makefile/docs from '--test canonical_backtest_workloads' to '--test integration canonical_backtest_workloads::'; upstream docs/developer_guide/benchmarking.md:162-163 at ac22d5cf shows the new form; crates/backtest/tests/integration/main.rs exists.
  fix: Update the command to 'CARGO_BUILD_JOBS=16 cargo test --locked -p nautilus-backtest --test integration canonical_backtest_workloads::'.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-081] [P2] [CLOSED 2026-09-05] Improvement opportunities: SKILL.md Rust Usage covers only add_data/BacktestNode chunking; the drift-window typed batch input/replay (BacktestEngine::add_data_batch + DataBatch) and lazy multi-config node streaming are not covered anywhere in the skill.
  file: skills/nt-backtest/SKILL.md:197
  evidence: commits 3c9ad2ef4 'Add BacktestEngine typed batch input' and dabe39d77 'Add BacktestEngine typed batch replay' (crates/backtest/src/engine.rs:436 pub fn add_data_batch, crates/model/src/data/batch.rs); ec1894d6f 'Stream backtest data lazily across multiple data configs' (crates/backtest/src/node.rs) - all in 4692bac..ac22d5cf.
  fix: Add a short subsection after the add_data example: add_data_batch(DataBatch, client_id, validate, sort) replays typed batches without per-item Data values, and note BacktestNode now streams lazily across multiple BacktestDataConfig entries.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-082] [P2] [CLOSED 2026-09-05] Improvement opportunities: order_book.md's Python note predates the drift-window Python order book compatibility work: OrderBook.to_deltas(), get_all_crossed_levels(), pickle/deep-copy support, BookLevel comparisons, and OrderBookDelta is_add/is_update/is_delete/is_clear + OrderBookDeltas.is_snapshot properties are uncovered.
  file: skills/nt-backtest/references/concepts/order_book.md:14
  evidence: commits a5dfd991b and 741b61d6d (in 4692bac..ac22d5cf); RELEASES.md lines added by 741b61d6d: 'Added Python OrderBookDelta.is_add, is_update, is_delete, is_clear, and OrderBookDeltas.is_snapshot'; python/nautilus_trader/model/__init__.pyi:4157 def is_snapshot.
  fix: After correcting the module name (see 078), extend the Python note with the new compatibility surface and delta inspection properties.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-083] [P2] [CLOSED 2026-09-05] Improvement opportunities: Quarantined portfolio example calls self.portfolio.is_flat(instrument_id), margins_init(venue) and margins_maint(venue), which do not exist on the pinned Python Portfolio surface (only balances_locked among that group remains).
  file: skills/nt-backtest/migration_reference/python/examples/portfolio/strategy.py:118
  evidence: python/nautilus_trader/portfolio/__init__.pyi at ac22d5cf exposes balances_locked (line 51) but no is_flat/margins_init/margins_maint (git grep returns nothing for those three names).
  fix: Replace is_flat with net_position(...) == 0 / unrealized_pnl checks and drop or replace the margins_init/margins_maint block with balances_locked or account(venue) usage, keeping the migration-lane label.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-084] [P2] [CLOSED 2026-09-05] Improvement opportunities: model_configs_example.py is built entirely on ImportableFillModelConfig/ImportableFeeModelConfig/ImportableLatencyModelConfig and nautilus_trader.backtest.models/config paths, all removed at the pin; as a migration example it should show the v2 equivalents.
  file: skills/nt-backtest/migration_reference/python/examples/model_configs_example.py:22
  evidence: git grep 'ImportableFeeModelConfig\|ImportableFillModelConfig\|ImportableLatencyModelConfig' ac22d5cf returns nothing; venue configs at the pin accept model instances (python/nautilus_trader/backtest/__init__.pyi BacktestVenueConfig fill_model/latency_model/fee_model params take instances; latency model is StaticLatencyModel from nautilus_trader.execution).
  fix: Rewrite the example to configure venues with instance models (DefaultFillModel/ThreeTierFillModel, StaticLatencyModel, MakerTakerFeeModel/FixedFeeModel/PerContractFeeModel from nautilus_trader.execution), noting the v1 importable-config contrast.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-085] [P2] [CLOSED 2026-09-05] Improvement opportunities: python-usage.md BacktestDataConfig example uses v1 keys data_cls= and bar_type= and stale imports (backtest.node, model.data); the pinned config uses data_type= plus bar_spec=/bar_types= on the flat modules.
  file: skills/nt-backtest/migration_reference/python/python-usage.md:34
  evidence: python/nautilus_trader/backtest/__init__.pyi:76-92 BacktestDataConfig.__new__(data_type: str, ..., bar_spec: BarSpecification | None, bar_types: Sequence[str] | None, ...) at ac22d5cf; upstream docs use 'from nautilus_trader.backtest import BacktestNode'.
  fix: Update the example to data_type='bar'/'quote_tick' with bar_types=[...] and flat imports, or explicitly annotate the v1 keys as pre-migration.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-086] [P2] [CLOSED 2026-09-05] Improvement opportunities: templates/fill_model.py subclasses FillModel passing prob_fill_on_limit/prob_slippage/random_seed to super().__init__; the pinned Python FillModel.__init__ takes no arguments, so the template breaks, and its imports (backtest.models, model.book, model.instruments.base, model.objects, model.orders.base) are v1 paths.
  file: skills/nt-backtest/migration_reference/python/templates/fill_model.py:39
  evidence: python/nautilus_trader/execution/__init__.pyi: 'class FillModel: def __init__(self) -> None' at ac22d5cf; probabilistic parameters live on built-in models (DefaultFillModel/ProbabilisticFillModel) and upstream docs/concepts/backtesting/fill-models.md:112-120 documents the custom-object protocol (is_limit_filled/is_slipped/...).
  fix: Store the parameters on the subclass without forwarding them to super(), import FillModel/OrderBook/Price from nautilus_trader.execution / nautilus_trader.model, and reference the pinned custom-object protocol.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-087] [P2] [CLOSED 2026-09-05] Improvement opportunities: Portfolio example/README predate user-defined portfolio statistics (Portfolio.register_statistic with a PortfolioStatistic base class) added in the drift window; the flagship portfolio example does not exercise it.
  file: skills/nt-backtest/migration_reference/python/examples/portfolio/README.md:10
  evidence: commits 7e8c9c9cd and eb42e2bfc (in 4692bac..ac22d5cf), RELEASES.md: 'Added user-defined portfolio statistics through Portfolio.register_statistic(), with a PortfolioStatistic base class'; python/nautilus_trader/portfolio/__init__.pyi:136 def register_statistic.
  fix: Add a short section (README plus strategy snippet) demonstrating Portfolio.register_statistic(MyStatistic()) for a custom portfolio metric.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S4 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s4-backtest-model.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-088] [P1] [CLOSED 2026-09-05] V2 compliance violations: Test conftest gates on the pinned V2 module set but imports v1-only module paths and v1 FillModel constructor, so the suite cannot even collect against the pinned tree.
  file: skills/nt-strategy-builder/tests/conftest.py:17
  evidence: conftest.py:10-14 importorskips nautilus_trader._libnautilus.common ('pinned NautilusTrader V2 module set'), then line 17-18 import nautilus_trader.backtest.engine/.models; pinned python/nautilus_trader/backtest/ contains only __init__.py re-exporting BacktestEngine/FillModel-related names at package root (__init__.pyi __all__), and base FillModel at v2 takes no constructor args (python/nautilus_trader/execution/__init__.pyi:152-153 `class FillModel: def __init__(self) -> None`; DefaultFillModel with prob_fill_on_limit/prob_slippage/random_seed at :75-79). Executed with the pinned build (python/.venv): 'ModuleNotFoundError: No module named nautilus_trader.backtest.engine' at conftest.py:17.
  fix: Change to package-root v2 imports: `from nautilus_trader.backtest import BacktestEngine` and `from nautilus_trader.execution import FillModel, DefaultFillModel`, constructing DefaultFillModel(prob_fill_on_limit=..., prob_slippage=..., random_seed=...) instead of FillModel(...). Apply the same import fix in tests/test_backtest_patterns.py:17-18 and tests/test_dex_as_venue.py:16-17 (identical stale paths).
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-089] [P1] [CLOSED 2026-09-05] V2 compliance violations: test_live_node_config.py imports v1-only config names (TradingNodeConfig, LiveExecEngineConfig, LoggingConfig) that do not exist in the pinned v2 nautilus_trader.config.
  file: skills/nt-strategy-builder/tests/test_live_node_config.py:19
  evidence: Pinned-build introspection (4692bac35, python/.venv): nautilus_trader.config exports LiveExecutionEngineConfig and LoggerConfig, but has no TradingNodeConfig, no LiveExecEngineConfig, no LoggingConfig (`ImportError: cannot import name 'LoggingConfig' ... Did you mean: 'LoggerConfig'?`); nautilus_trader.live exports LiveNode but not TradingNode. python/nautilus_trader/config/__init__.pyi __all__ confirms the v2 name set.
  fix: Either rewrite the test against the v2 names (LiveExecutionEngineConfig, LoggerConfig, LiveNodeConfig-driven LiveNode wiring) or keep it as an explicitly v1-labelled migration test that skips when the v1 module set is absent; as written it is a broken V2-gated test.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: NT v2 compatibility note: TradingNode tokens quoted here are migration/reference-only audit evidence; legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-090] [P1] [CLOSED 2026-09-05] V2 compliance violations: test_multi_venue.py imports v1-only nautilus_trader.model.data and exec-loads the legacy template whose own v1 imports fail against the pinned V2 tree.
  file: skills/nt-strategy-builder/tests/test_multi_venue.py:18
  evidence: `from nautilus_trader.model.data import QuoteTick` (test_multi_venue.py:18) fails at v2 (pinned-build check: 'No module named nautilus_trader.model.data'; QuoteTick is exported from nautilus_trader.model package root); _spec.loader.exec_module (line 30) then executes templates/legacy_migration/multi_venue_strategy.py, which imports nautilus_trader.trading.config/.strategy and nautilus_trader.live.node — all absent submodules at pinned v2 (verified ModuleNotFoundError for each).
  fix: Import QuoteTick from nautilus_trader.model (package root) and make the template load conditional on a v1 module set (pytest.importorskip) or port the template under test to v2 package-root imports; the test is V2-gated via conftest and currently cannot run.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: NT v2 compatibility note: legacy tokens quoted here are migration/reference-only audit evidence; (quoted legacy tokens are migration/reference-only audit evidence) legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-091] [P1] [CLOSED 2026-09-05] V2 compliance violations: SKILL.md claims 'New code built from these templates should pass the included test suite' and enumerates its coverage, but the suite cannot collect against the pinned V2 build.
  file: skills/nt-strategy-builder/SKILL.md:187
  evidence: Verified execution: pinned-build pytest on skills/nt-strategy-builder/tests/ aborts with 'ImportError while loading conftest ... ModuleNotFoundError: No module named nautilus_trader.backtest.engine' (conftest.py:17). The recorded G2 evidence (references/g2-evidence/nt-strategy-builder.json) runs tools/run_pinned_v2_pytest.py on tests/test_strategy_builder_v2_contract.py plus upstream acceptance tests, not this suite, so the gate does not cover the advertised command at SKILL.md:191.
  fix: Fix the test suite imports (NT-081..083) and re-run, or restate the Testing section to point at the contract test that is actually executed against the pinned V2 build; the current 'should pass' claim is false for the pinned tree.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-092] [P1] [CLOSED 2026-09-05] V2 compliance violations: AGENTS.md instructs 'uv run pytest skills/nt-strategy-builder/tests/ -v' but that suite fails to collect against the pinned V2 tree.
  file: skills/nt-strategy-builder/AGENTS.md:78
  evidence: Same verified run: conftest.py:17 ModuleNotFoundError under the pinned V2 build (python/.venv, 4692bac35); conftest.py:10-14 explicitly gates on the pinned V2 module set, so the command cannot succeed as documented.
  fix: Update the TESTING command after fixing the suite (NT-081), or point agents at the pinned-V2 contract test actually used for G2 evidence.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-093] [P1] [CLOSED 2026-09-05] V2 compliance violations: Authoritative LiveNode lifecycle guidance documents a nonexistent LiveNodeHandle::is_stopping() method.
  file: skills/nt-strategy-builder-rust/SKILL.md:223
  evidence: crates/live/src/node/state.rs:175-198 (4692bac35) shows the handle exposes state() -> NodeState, should_stop(), is_running(), metrics_snapshot(), stop(); grep 'pub fn is_stopping' across crates/live returns zero hits at both 4692bac35 and the drift-window tip ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d (evidence worktree nautilus_trader-evidence-ac22d5cf4).
  fix: Replace 'is_stopping()' with the real readiness/teardown probe, e.g. handle.state() == NodeState::ShuttingDown or handle.should_stop(), so the documented API compiles.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-094] [P1] [CLOSED 2026-09-05] V2 compliance violations: Authoritative Strategy trait sketch shows on_order_canceled receiving an owned OrderCanceled; upstream takes &OrderCanceled.
  file: skills/nt-strategy-builder-rust/SKILL.md:122
  evidence: crates/trading/src/strategy/mod.rs:1653 (4692bac35): `fn on_order_canceled(&mut self, event: &OrderCanceled) {}`; unchanged at ac22d5cf4 (mod.rs:1683). The skill's own note says handlers receive owned events 'except a few &-reference ones' but the sketch omits the reference for this handler, so a copied override would not match the trait method.
  fix: Change the sketch line to `fn on_order_canceled(&mut self, event: &OrderCanceled) {}` to mirror upstream mod.rs:1653.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: closed as invalid: cited line 122 already matched the pinned mixed owned/reference handler signatures (crates/trading/src/strategy/mod.rs:1629,1635 owned; :1683,1689 by-reference) — auditor misread the intentional mixed pattern
  closure-proof: pinned-tree signature/policy verification recorded in this entry; no tree change required

[NT-2026-09-05-095] [P1] [CLOSED 2026-09-05] Legacy unlabelled content: Four test files carry unlabelled v1/TradingNode-adjacent Python content while the skill's other Python artifacts all carry migration/reference labels.
  file: skills/nt-strategy-builder/tests/conftest.py:1
  evidence: All five templates open with '# TEMPLATE_CLASSIFICATION: legacy executable; migration/reference-only; not a production default' (e.g. templates/legacy_migration/backtest_node.py:1) and test_live_node_config.py:1-4 opens with the NT v2 compatibility note, but tests/conftest.py, tests/test_backtest_patterns.py, tests/test_dex_as_venue.py, and tests/test_multi_venue.py have no label header while containing v1-only import paths (conftest.py:17-18, test_backtest_patterns.py:17-18, test_dex_as_venue.py:16-17, test_multi_venue.py:18) and exec-loading the legacy TradingNode template (test_multi_venue.py:30).
  fix: Add the same '# NT v2 compatibility note' / migration-reference header used by test_live_node_config.py to conftest.py, test_backtest_patterns.py, test_dex_as_venue.py, and test_multi_venue.py (or port them to v2 shapes per NT-081..083).
  acceptance-test: python3 tools/check_legacy_labelling.py exits 0; grep in skills/nt-strategy-builder/tests/conftest.py shows the v1 excerpt only under a migration/reference label
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-096] [P2] [CLOSED 2026-09-05] Improvement opportunities: BacktestEngine registration guidance omits drift-window typed batch input and lazy multi-config streaming now available for replay.
  file: skills/nt-strategy-builder-rust/SKILL.md:220
  evidence: Drift window 4692bac..ac22d5cf: 3c9ad2ef4 adds `BacktestEngine::add_data_batch(data: DataBatch, client_id: Option<ClientId>, validate: bool, sort: bool)` (crates/backtest/src/engine.rs); ec1894d6f makes run_streaming stream lazily across multiple BacktestDataConfigs instead of collecting into one Vec<Data>. Neither feature appears in the skill's BacktestEngine registration/lifecycle guidance.
  fix: Add a bullet next to the BacktestEngine registration item covering typed batch input via add_data_batch and lazy multi-config streaming for memory-bounded replay, citing the upstream commits as version-scoped evidence.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-097] [P2] [CLOSED 2026-09-05] Improvement opportunities: portfolio() guidance omits drift-window user-defined portfolio statistics registration carried into backtest results.
  file: skills/nt-strategy-builder-rust/SKILL.md:130
  evidence: Drift window commit 7e8c9c9cd 'Support user-defined portfolio statistics': register any user-defined Python or Rust statistic on Portfolio, carried into backtest results and post-run logs (crates/portfolio/src/portfolio.rs, crates/portfolio/src/python/mod.rs, python/nautilus_trader/analysis/statistic.py, docs/concepts/portfolio.md). The skill's portfolio() bullet only lists positions/balances/PnL.
  fix: Extend the portfolio() bullet (and optionally the backtest results note) with the user-defined statistics registration capability, marked as post-4692bac drift evidence.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-098] [P2] [CLOSED 2026-09-05] Improvement opportunities: Migration lane shows only the v1 frozen=True StrategyConfig subclass pattern with no mapping to the v2 keyword-only subclass shape simplified by bed07c6c3e.
  file: skills/nt-strategy-builder/templates/legacy_migration/multi_venue_strategy.py:37
  evidence: Drift window commit bed07c6c3e 'Simplify Python config subclass definitions' documents the v2 rule in docs/concepts/strategies.md:757-791 (ac22d5cf4): keyword-only custom fields, `**_kwargs` passthrough, `super().__init__()` with no arguments; the template still shows `class MultiVenueStrategyConfig(StrategyConfig, frozen=True)` with annotated fields, and migration_reference/python/venue-and-simulation-examples.md contains no config-subclass migration mapping.
  fix: Add a v1-to-v2 StrategyConfig subclass mapping section to migration_reference/python/venue-and-simulation-examples.md (frozen=True annotated-struct pattern -> keyword-only __init__ with **_kwargs and super().__init__()), citing docs/concepts/strategies.md and MIGRATION_V2.md at bed07c6c3e.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S3 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s3-strategy-builders.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-099] [P1] [CLOSED 2026-09-05] V2 compliance violations: portfolio.md claims the nautilus_trader.analysis.statistic module was 'removed', but upstream restored user-defined Python portfolio statistics at the pinned tip (commit 7e8c9c9cd 'Support user-defined portfolio statistics', 2026-09-04).
  file: skills/nt-signals/references/concepts/portfolio.md:156
  evidence: python/nautilus_trader/analysis/statistic.py:16 docstring 'Base class for user-defined portfolio statistics.' (exists at pinned ac22d5cf4); crates/analysis/src/python/statistic.rs added by 7e8c9c9cd (git log --oneline -1 -- crates/analysis/src/python/statistic.rs -> 7e8c9c9cd); crates/analysis/src/python/analyzer.rs:145 register_statistic(statistic_from_pyobject(py, statistic)); python/nautilus_trader/portfolio/__init__.pyi:136 def register_statistic(self, statistic: typing.Any); docs/concepts/portfolio.md:277 '### Custom statistics' instructs subclassing Python PortfolioStatistic.
  fix: Rewrite the 'Legacy v1 Python pattern' paragraph and 'Custom statistics' section: the Python base class nautilus_trader.analysis.statistic.PortfolioStatistic is current at the pinned tip; document the dual supported paths (Rust PortfolioStatistic trait AND Python subclass registered via Portfolio.register_statistic / PortfolioAnalyzer.register_statistic), and reclassify migration_reference/python/python/analysis/statistic.py + templates/portfolio_statistic.py away from 'removed/legacy' framing.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-100] [P1] [CLOSED 2026-09-05] V2 compliance violations: portfolio.md teaches calculate_from_orders as a PortfolioStatistic trait method and lists 'Orders based statistics' as a category, but 7e8c9c9cd removed calculate_from_orders from the trait; orders are no longer a statistic input.
  file: skills/nt-signals/references/concepts/portfolio.md:118
  evidence: crates/analysis/src/statistic.rs:39-78 trait now defines only name, calculate_from_returns (:46), calculate_from_realized_pnls (:55), calculate_from_positions (:67), calculate_from_returns_with_benchmark (:78); git show 7e8c9c9cd -- crates/analysis/src/statistic.rs deletes 'fn calculate_from_orders(&self, orders: Vec<Box<dyn Order>>)'; docs/concepts/portfolio.md:262-266 result categories are PnL/returns/general-from-positions only.
  fix: Delete calculate_from_orders from the trait-method list (line 117-119), drop the 'Orders based statistics' bullet (line 108), and fix the Backtest analysis paragraph (lines 195, 200) to say realized PnLs, returns, and positions (no orders); optionally mention the new calculate_from_returns_with_benchmark default.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-101] [P1] [CLOSED 2026-09-06] V2 compliance violations: api/analysis.md automodule stub omits the nautilus_trader.analysis.statistic module that upstream documents in its Analysis API reference.
  file: skills/nt-signals/references/api/analysis.md:40
  evidence: docs/api_reference/analysis.md:44 '.. automodule:: nautilus_trader.analysis.statistic' (block added by 7e8c9c9cd per git show 7e8c9c9cd --stat 'docs/api_reference/analysis.md | 8 +'); skill file ends at line 41 after reporter block with no statistic block.
  fix: Append the eval-rst automodule block for nautilus_trader.analysis.statistic mirroring upstream docs/api_reference/analysis.md:42-48.
  closure-proof: grep residue 0 on the fixed tree; phase-3 remediation receipt on record; python3 -m pytest -q green (452 passed, 7 skipped)
  closure: NT v2 compatibility note: migration/reference tokens quoted here are audit evidence; skills/nt-signals/references/api/analysis.md now mirrors the pinned docs/api_reference/analysis.md including the nautilus_trader.analysis.statistic automodule block

[NT-2026-09-05-102] [P1] [CLOSED 2026-09-05] V2 compliance violations: Vendored Rust reference copy of the analysis crate is stale vs the pinned tree: src/python/statistic.rs is missing entirely, python/mod.rs does not register it, python/analyzer.rs still carries the removed ~300-line match-based py_register_statistic, analyzer.rs lacks replace_statistics, and Cargo.toml lacks the log workspace dependency - all added/changed by 7e8c9c9cd.
  file: skills/nt-signals/references/rust/analysis/src/python/mod.rs:23
  evidence: diff skill vs pinned crates/analysis: skill python/mod.rs:23-25 has only 'pub mod analyzer; pub mod snapshot; pub mod statistics;' while upstream crates/analysis/src/python/mod.rs:25 adds 'pub mod statistic;'; upstream crates/analysis/src/python/statistic.rs exists (312 lines, new in 7e8c9c9cd); upstream crates/analysis/src/python/analyzer.rs:26,145,152 use statistic_from_pyobject while skill src/python/analyzer.rs:164 still has the type-name match implementation; upstream crates/analysis/src/analyzer.rs:137-144 adds pub fn replace_statistics (used by crates/portfolio/src/portfolio.rs:2049); upstream crates/analysis/Cargo.toml adds 'log = { workspace = true }' absent from skill Cargo.toml.
  fix: Refresh the vendored crate snapshot at skills/nt-signals/references/rust/analysis from pinned crates/analysis at ac22d5cf4 (copy src/python/statistic.rs, update python/mod.rs, python/analyzer.rs, analyzer.rs, Cargo.toml; the remaining ~90 statistics/*.rs files are already byte-identical).
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-103] [P1] [CLOSED 2026-09-05] V2 compliance violations: Vendored src/statistic.rs still defines the removed calculate_from_orders default method and imports nautilus_model::orders::Order, so the reference copy teaches a trait shape that no longer compiles at the pinned tip.
  file: skills/nt-signals/references/rust/analysis/src/statistic.rs:63
  evidence: skill src/statistic.rs:18 'use nautilus_model::{orders::Order, position::Position};' and :63 'fn calculate_from_orders(&self, orders: Vec<Box<dyn Order>>)...' vs upstream crates/analysis/src/statistic.rs:18 'use nautilus_model::position::Position;' with no orders method (removed by 7e8c9c9cd); upstream also added the panic-contract doc at crates/analysis/src/statistic.rs:27-33.
  fix: Sync this file from pinned crates/analysis/src/statistic.rs: drop calculate_from_orders and the Order import, keep the new doc comment describing which defaults panic and that calculate_from_returns_with_benchmark defaults to None.
  acceptance-test: cargo check of the corrected example passes at pin ac22d5cf4 (G2 harness re-execution); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-104] [P1] [CLOSED 2026-09-05] V2 compliance violations: indicators_guide.md presents MovingAverageFactory as a Python-visible API with create(period, ma_type, **kwargs) and a 'from nautilus_trader.indicators import MovingAverageFactory' example, and uses nonexistent nautilus_trader.indicators.averages/.momentum/.trend submodule headers - at the pinned tip the factory is Rust-only with argument order (moving_average_type, period) and the Python module is flat.
  file: skills/nt-signals/references/guides/indicators_guide.md:42
  evidence: crates/indicators/src/average/mod.rs:84-88 'pub fn create(moving_average_type: MovingAverageType, period: usize) -> Box<dyn MovingAverage + Send + Sync>'; python/nautilus_trader/indicators/__init__.pyi exports 45 classes and no MovingAverageFactory (grep -c MovingAverageFactory = 0; only MovingAverageType at :37); python/nautilus_trader/indicators/ contains only __init__.py/__init__.pyi (no averages/momentum/trend submodules); the skill's own SKILL.md states the factory 'is Rust-only and is not exposed to Python'.
  fix: Fix line 42 to describe the Rust-only factory with its real signature, remove or rewrite the Python import example at lines 286-289 (import only MovingAverageType from the flat module), and drop the fake submodule suffixes from the section headers (lines 27, 53, 71) since the PyO3 surface is the flat nautilus_trader.indicators module.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-105] [P1] [CLOSED 2026-09-05] V2 compliance violations: indicators_guide.md claims average::lr and average::vwap are 'Additional Rust-only averages', but both are exposed to Python at the pinned tip as LinearRegression and VolumeWeightedAveragePrice.
  file: skills/nt-signals/references/guides/indicators_guide.md:46
  evidence: python/nautilus_trader/indicators/__init__.pyi:606 'class LinearRegression' and :981 'class VolumeWeightedAveragePrice' (PyO3 wrappers crates/indicators/src/python/average/lr.rs and vwap.rs exist); crates/indicators/src/average/ contains lr.rs and vwap.rs.
  fix: Replace the 'Rust-only averages' sentence with a correct statement (e.g., linear-regression MA and VWAP are Python-visible as LinearRegression / VolumeWeightedAveragePrice) or list only genuinely unexposed items after grepping python/nautilus_trader/indicators/__init__.pyi.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-106] [P1] [CLOSED 2026-09-05] V2 compliance violations: visualization.md instructs installing plotly>=6.3.1, but the pinned upstream requires plotly>=7.0.0,<8.0.0 for the visualization extra.
  file: skills/nt-signals/references/concepts/visualization.md:22
  evidence: python/pyproject.toml:31 '"plotly>=7.0.0,<8.0.0",' (visualization extra at :29); skill line 31 repeats 'uv pip install "plotly>=6.3.1"'.
  fix: Update both occurrences (lines 22 and 31) to 'plotly>=7.0.0,<8.0.0' to match python/pyproject.toml.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-107] [P2] [CLOSED 2026-09-05] Improvement opportunities: The restored user-defined portfolio-statistics feature (drift-window commit 7e8c9c9cd) is not covered anywhere in nt-signals beyond the false 'removed' note: the skill does not document Portfolio.register_statistic carrying custom statistics into backtest results and tearsheets, statistics surviving analyzer resets, or the current Python PortfolioStatistic method signatures.
  file: skills/nt-signals/SKILL.md:198
  evidence: docs/concepts/portfolio.md:269-331 (register before the run; registration persists across statistics() calls and resets; every category is called; error handling via unraisable hook); docs/concepts/visualization.md:514-520 (a statistic registered with Portfolio.register_statistic() reaches the tearsheet without extra wiring); crates/portfolio/src/portfolio.rs:2049 analyzer.replace_statistics(...); python/nautilus_trader/analysis/statistic.py:64-114 current signatures calculate_from_returns(dict[int, float]) / calculate_from_realized_pnls(list[float]) / calculate_from_positions(list[Position]) - the quarantined templates/portfolio_statistic.py still teaches v1 pd.Series signatures with _check_valid_returns/_downsample_to_daily_bins which do not exist upstream (grep on python/nautilus_trader/analysis/statistic.py returns nothing).
  fix: Add a current-path subsection on user-defined statistics to SKILL.md/portfolio.md (Python subclass + Portfolio.register_statistic + Rust trait), and refresh migration_reference/python/templates/portfolio_statistic.py and python-extension.md's 'Custom PortfolioStatistic' block to the pinned API shape (dict/list inputs, float|None returns) or relabel them accurately.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-108] [P1] [CLOSED 2026-09-06] V2 compliance violations: concepts/cache.md documents a CacheConfig 'database' parameter and a CacheConfig(database=DatabaseConfig(...)) example that no longer exist at the pinned tip, and omits the new save_market_data / persist_account_events parameters.
  file: skills/nt-data/references/concepts/cache.md:117
  evidence: crates/common/src/cache/config.rs:36-73 CacheConfig fields (encoding ... tick_capacity, bar_capacity, persist_account_events:70, save_market_data:73) contain no database field; python/nautilus_trader/common/__init__.pyi:75+ CacheConfig.__init__ likewise; DatabaseConfig is not exported anywhere in python/nautilus_trader (grep -rn 'DatabaseConfig' python/nautilus_trader returns only RedisCacheConfig/PostgresCacheConfig hits); docs/concepts/cache.md:95-126 shows the current parameter set and docs/concepts/cache.md:126-198 documents the replacement RedisCacheConfig/PostgresCacheConfig + with_cache_database_factory pattern.
  fix: Replace the parameter table (lines 116-137) with the pinned CacheConfig fields including save_market_data and persist_account_events, and rewrite the Database configuration section (lines 136-158) to the current backing-store pattern (RedisCacheConfig/PostgresCacheConfig via with_cache_database_factory) as in docs/concepts/cache.md.
  closure-proof: grep residue 0 on the fixed tree; phase-3 remediation receipt on record; python3 -m pytest -q green (452 passed, 7 skipped)
  closure: NT v2 compatibility note: migration/reference tokens quoted here are audit evidence; Redis example rewritten to the pinned CacheConfig + RedisCacheConfig + CacheDatabaseFactory pattern (docs/how_to/configure_live_trading.md at ac22d5cf4); DatabaseConfig references removed; param table extended with save_market_data/persist_account_events per crates/common/src/cache/config.rs:70,73

[NT-2026-09-05-109] [P1] [CLOSED 2026-09-05] V2 compliance violations: cache_operations.md imports PriceType from the nonexistent nautilus_trader.model.enums module; the pinned Python model package is flat.
  file: skills/nt-data/references/guides/cache_operations.md:108
  evidence: python/nautilus_trader/model/ contains only __init__.py and __init__.pyi (no enums submodule); PriceType is exported from the flat module (python/nautilus_trader/model/__init__.pyi class list includes PriceType; also members list in docs api data stub).
  fix: Change line 108 to 'from nautilus_trader.model import PriceType' and sweep the guide for other dotted model imports.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-110] [P1] [CLOSED 2026-09-06] V2 compliance violations: concepts/data.md lists fs_storage_options as a DataCatalogConfig optional parameter, but at the pinned tip DataCatalogConfig accepts only path, fs_protocol, fs_rust_storage_options, and name.
  file: skills/nt-data/references/concepts/data.md:1053
  evidence: python/nautilus_trader/persistence/__init__.pyi:55-72 DataCatalogConfig.__new__(cls, path, fs_protocol=None, fs_rust_storage_options=None, name=None) - no fs_storage_options (fs_storage_options survives only on FeatherDataCatalog at :343 and as catalog_fs_storage_options on BacktestDataConfig, python/nautilus_trader/backtest/__init__.pyi:81).
  fix: Rename the bullet at line 1053 to fs_rust_storage_options (matching the cloud example already at lines 1064-1074) and note the Feather/BacktestData variants separately if needed.
  closure-proof: grep residue 0 on the fixed tree; phase-3 remediation receipt on record; python3 -m pytest -q green (452 passed, 7 skipped)
  closure: NT v2 compatibility note: migration/reference tokens quoted here are audit evidence; constructor kwarg corrected to fs_rust_storage_options (persistence/__init__.pyi:65) with the read-only keys property noted

[NT-2026-09-05-111] [P1] [CLOSED 2026-09-05] V2 compliance violations: nt-data migration python-usage.md still tells readers the mark_price_count/has_mark_prices/index_price_count/has_index_prices/funding_rate_count/has_funding_rates/instrument_status_count/has_instrument_statuses cache accessors are develop-only and must not be copied into code compiled against the pinned commit, but they are present in the pinned baseline ac22d5cf4 - and nt-data/SKILL.md:103-107 already asserts they are at the baseline, so the two files contradict each other.
  file: skills/nt-data/migration_reference/python/python-usage.md:65
  evidence: crates/common/src/cache/mod.rs:1614 and :7837 'pub fn mark_price_count(&self, instrument_id: &InstrumentId) -> usize' at pinned ac22d5cf4; python/nautilus_trader/common/__init__.pyi:342,350 exposes has_mark_prices / mark_price_count (plus index/funding/instrument_status pairs verified in the same stub); skill nt-data/SKILL.md:103-107 states these are 'at the pinned G2 baseline ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d'.
  fix: Update the 'Develop-only cache history introspection' section (lines 53-70) to state the accessors are part of the pinned baseline and remove the 'Treat these as develop-only / do not copy' instruction, or delete the section since SKILL.md already documents the baseline status.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-112] [P2] [CLOSED 2026-09-05] Improvement opportunities: concepts/data.md is a pre-restructure single-file snapshot; upstream now ships per-type data guides (bar.md, quote_tick.md, trade_tick.md, order_book_delta(s).md, order_book_depth10.md, mark/index price, funding_rate_update.md, instrument_status.md, instrument_close.md, option_greeks.md) plus an index with a built-in data-types table, none of which the skill references.
  file: skills/nt-data/references/concepts/data.md:1
  evidence: docs/concepts/data/ at pinned ac22d5cf4 contains 13 per-type guide files plus index.md (built-in data types table at docs/concepts/data/index.md:9-30 listing each type with a dedicated guide); the skill's 1727-line concepts/data.md has no per-type sections or links (grep -n 'order_book_delta.md\|quote_tick.md' finds nothing).
  fix: Add per-type coverage (or link stubs) mirroring docs/concepts/data/ for the built-in types, prioritizing types touched in the drift window (e.g., InstrumentClose persistence, 9d45d410d), or refresh the snapshot from the pinned index.md layout.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S7 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s7-signals-data.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-113] [P1] [CLOSED 2026-09-05] V2 compliance violations: TradingState semantics are stale: HALTED is taught as blocking all order commands and REDUCING as cancels/position-reducing only, but the pinned tree reordered values (Active=1, Reducing=2, Halted=3) and now permits cancels+queries under HALTED and eligible reduce-only submissions (same instrument, matching position ID, opposing side, qty <= position) under REDUCING (commit 9da48e03).
  file: skills/nt-trading/references/concepts/execution.md:140
  evidence: crates/model/src/enums.rs:1984-1992 (Active=1/Reducing=2/Halted=3 with new doc comments); docs/concepts/execution/index.md:240-256 (permitted-commands table and REDUCING eligibility rules); upstream commit 9da48e0399dec9b7d60b1cd2fb67a973c260120d; shared mirror references/concepts/execution.md:139-141 has the same stale text
  fix: Rewrite the TradingState block (lines 137-141) to the pinned semantics: ACTIVE=1 all commands, REDUCING=2 eligible individual reduce-only submissions plus cancels/queries (order lists and modifications denied), HALTED=3 cancels and queries only; note the numeric-value reorder and the reduce-only send-or-reject contract for adapters.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-114] [P1] [CLOSED 2026-09-05] V2 compliance violations: Rust strategy guide calls submit_order with three arguments, but the pinned Strategy trait requires four (order, position_id, client_id, params); the example will not compile against the pinned tree.
  file: skills/nt-trading/references/guides/write_rust_strategy.md:96
  evidence: crates/trading/src/strategy/mod.rs:172-179 (fn submit_order(&mut self, order: OrderAny, position_id: Option<PositionId>, client_id: Option<ClientId>, params: Option<Params>)); upstream example crates/trading/src/examples/strategies/ema_cross/strategy.rs:98 calls self.submit_order(order, None, None, None)
  fix: Change line 96 to self.submit_order(order, None, None, None)?; and note the optional Params argument in the surrounding prose (nt-trading SKILL.md already documents the Params argument correctly).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-115] [P1] [CLOSED 2026-09-05] V2 compliance violations: Project-setup guidance pins crates at 0.62 and enables a nonexistent nautilus-model feature named stubs; the pinned tree publishes 0.63/0.64-era crates and the feature is test-support, so both the version block and the feature flags table are wrong.
  file: skills/nt-trading/references/concepts/rust.md:112
  evidence: crates/model/Cargo.toml:20-34 ([features] lists test-support, no stubs; grep for stubs exits 1); docs/concepts/rust.md:92-96 (nautilus-model { version = "0.63", features = ["test-support"] }); pinned workspace Cargo.toml:52 version = "0.64.0"
  fix: Update lines 109-124 and 148 to version 0.63 (or the pinned 0.64.0) and rename the stubs feature to test-support everywhere it appears (lines 112, 135, 148), matching docs/concepts/rust.md:92-96.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-116] [P1] [CLOSED 2026-09-05] V2 compliance violations: Capability matrix marks Tearsheets absent for the v2 PyO3 path, but the pinned upstream capability matrix lists Tearsheets as available on the Python path.
  file: skills/nt-trading/references/concepts/rust.md:55
  evidence: docs/concepts/rust.md:19,44 (| Tearsheets | - | ✓ | with Rust|Python columns, Python = v2 PyO3 path); skill row reads | Tearsheets | ✓ | - | - | (v1 legacy / v2 Rust / v2 PyO3)
  fix: Change the Tearsheets v2 PyO3 cell at line 55 from - to checkmark (keep v2 Rust as -), or replace the three-column v1-era matrix with the pinned two-column Rust|Python matrix now that v1 comparisons are centralized in MIGRATION_V2.md (commit beaac71e0).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-117] [P1] [CLOSED 2026-09-05] V2 compliance violations: Custom-statistics guidance lists calculate_from_orders as a PortfolioStatistic hook, but no such method exists on the pinned trait; the real hooks are calculate_from_returns, calculate_from_realized_pnls, calculate_from_positions, and optional calculate_from_returns_with_benchmark.
  file: skills/nt-trading/references/concepts/portfolio.md:118
  evidence: crates/analysis/src/statistic.rs:30-90 (trait defines only returns/realized_pnls/positions/returns_with_benchmark; grep calculate_from_orders finds nothing); crates/analysis/src/analyzer.rs:794,850,867
  fix: Remove calculate_from_orders from the method list at line 118 and mention calculate_from_returns_with_benchmark as the optional fourth hook.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-118] [P1] [CLOSED 2026-09-05] V2 compliance violations: The SessionWinRate example overrides only calculate_from_realized_pnls, but pinned trait defaults panic for every unimplemented category and the analyzer invokes all three calculate_ methods on each registered statistic, so the documented example panics when statistics are computed.
  file: skills/nt-trading/references/concepts/portfolio.md:140
  evidence: crates/analysis/src/statistic.rs:30-33 ('their defaults panic, so an implementation must override all three and return None for a category it does not support'); crates/analysis/src/analyzer.rs:794,850,867 (analyzer calls realized_pnls, positions, and returns per statistic)
  fix: Extend the SessionWinRate impl (lines 130-152) to override calculate_from_returns and calculate_from_positions returning None, and add a note that all three must be overridden because defaults panic.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-119] [P1] [CLOSED 2026-09-05] V2 compliance violations: The file claims the nautilus_trader.analysis.statistic module was removed and points to a quarantined copy at migration_reference/python/python/analysis/statistic.py, but the pinned tree ships the module as a current v2 Python API and the referenced quarantine file does not exist.
  file: skills/nt-trading/references/concepts/portfolio.md:156
  evidence: python/nautilus_trader/analysis/__init__.pyi:29 (from nautilus_trader.analysis.statistic import PortfolioStatistic as PortfolioStatistic); docs/concepts/portfolio.md:279-307 (current docs teach subclassing PortfolioStatistic and Portfolio.register_statistic()); find skills/nt-trading/migration_reference -name statistic.py returns nothing (dangling pointer at line 160)
  fix: Replace the 'removed module' paragraph (lines 156-160) with the current dual-path guidance: Rust PortfolioStatistic trait + PortfolioAnalyzer::register_statistic, and current Python subclassing of nautilus_trader.analysis.statistic.PortfolioStatistic via Portfolio.register_statistic(); delete the dangling migration_reference/python/python/analysis/statistic.py pointer.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-120] [P1] [CLOSED 2026-09-05] V2 compliance violations: Testing guide recommends 'await eventually(...)' from nautilus_trader.test_kit.functions as the current polling helper, but that module and function do not exist anywhere in the pinned tree, and the same file acknowledges at line 165 that test_kit modules were removed at V2.
  file: skills/nt-trading/references/guides/testing.md:109
  evidence: python/nautilus_trader/testkit/ contains only __init__.py, __init__.pyi, providers.py (no functions.py); grep -rn 'def eventually' python/ returns nothing; grep -rn test_kit python/ returns nothing; crates/common/src/testing.rs:106 (pub async fn wait_until_async, the real helper); testing.md:165 already labels test_kit as v1-removed
  fix: Drop the eventually/test_kit.functions half of line 109 and keep only wait_until_async from nautilus_common::testing as the recommended polling helper, or replace with the pinned Python equivalent if one exists upstream.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-121] [P1] [CLOSED 2026-09-05] V2 compliance violations: Performance-testing commands reference a make test-performance target and a tests/performance_tests directory that do not exist in the pinned tree.
  file: skills/nt-trading/references/guides/testing.md:55
  evidence: pinned Makefile has no test-performance target (only cargo-ci-benches/cargo-codspeed targets; grep -n test-performance Makefile empty); python/tests/ contains acceptance, integration, strategies, unit only (no performance_tests); upstream docs/developer_guide/testing.md contains neither string
  fix: Replace lines 53-62 with the pinned tree's actual performance workflow (make cargo-ci-benches for criterion benches, pytest-memray for memory-leak tests) or remove the Python performance block; sync the file body against docs/developer_guide/testing.md which now leads with the testing-policy ladder the copy lacks.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-122] [P1] [CLOSED 2026-09-05] V2 compliance violations: Adapter Review Gate teaches the v1 Python factory signature create(loop, name, config, msgbus, cache, clock) as a fail-if-missing contract, but pinned v2 factories take no loop or msgbus parameter.
  file: skills/nt-review/AGENTS.md:60
  evidence: crates/adapters/okx/src/factories.rs:81-87 (fn create(&self, name: &str, config: &dyn ClientConfig, cache: CacheView, clock: Rc<RefCell<dyn Clock>>)) and :139-145 (execution factory create(trader_id, name, config, cache)); grep -rn 'create(loop' across pinned crates/ and python/ returns nothing
  fix: Update line 60 to the pinned contract: data client factories create(name, config, cache view, clock) and execution client factories create(trader_id, name, config, cache), with safe credential handling; keep credential/env checks unchanged.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-123] [P1] [CLOSED 2026-09-05] V2 compliance violations: G2 gate row claims the skill harness passed against pinned commit ac22d5cf4 while the cited evidence file records upstream_commit 4692bac3 verified on 2026-09-04, so the Pass status lacks fresh evidence for the current pin (62 commits of drift, including the reduce-only and order-status changes).
  file: skills/nt-trading/SKILL.md:35
  evidence: references/g2-evidence/nt-trading.json fields upstream_commit=4692bac35bb11a25eeebb8d7af4d51c55afe53ec, verified_at=2026-09-04T15:58:53Z, status=pass; SKILL.md:35 cites that file as proof for ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d
  fix: Re-run uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-trading against the pinned checkout at ac22d5cf4 so the evidence JSON records the current pin, or downgrade the G2 row to Pending until re-run.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-124] [P1] [CLOSED 2026-09-05] V2 compliance violations: Same G2 evidence mismatch as the nt-trading card: the nt-review gate row claims ac22d5cf4 but references/g2-evidence/nt-review.json records upstream_commit 4692bac3 verified 2026-09-04.
  file: skills/nt-review/SKILL.md:18
  evidence: references/g2-evidence/nt-review.json fields upstream_commit=4692bac35bb11a25eeebb8d7af4d51c55afe53ec, verified_at=2026-09-04T15:52:40Z, status=pass; SKILL.md:18 cites that file as proof for ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d
  fix: Re-run uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-review against the pinned checkout at ac22d5cf4, or set the G2 row to Pending until the evidence records the current pin.
  closure: closed by full G2 evidence regeneration at ac22d5cf (all 17 skills re-executed PASS)

[NT-2026-09-05-125] [P2] [CLOSED 2026-09-05] Improvement opportunities: The Rust trading deltas section does not cover the external-order claim routing rename from commit 681607428: StrategyConfig external_order_claims was renamed to external_order_instrument_ids, with new set_external_order_instrument_ids atomic claim updates and claim release on removal.
  file: skills/nt-trading/SKILL.md:117
  evidence: crates/trading/src/strategy/mod.rs:108,122,138 (external_order_instrument_ids / set_external_order_instrument_ids / cache.set_external_order_claims); python/nautilus_trader/trading/__init__.pyi:476,972,994 (Python surface renamed); upstream commit 681607428c6ff7ecedd5c646637964dab87f33b6; docs/how_to/configure_live_trading.md updated by that commit; no nt-trading or nt-review file mentions the new name (grep external_order returns only the v1 quarantine at nt-review/migration_reference/python/legacy-root-guidance.md:548)
  fix: Add a delta bullet to the SKILL.md Rust trading deltas section documenting the rename, the atomic replace semantics, and that v1 external_order_claims keys no longer exist; update nt-review/AGENTS.md:134 live checklist to name external_order_instrument_ids explicitly.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-126] [P2] [CLOSED 2026-09-05] Improvement opportunities: Review guidance does not cover the standardized order-status-report filtering rule from commit 9b7db823: open-only venue report requests must retain both open and in-flight reports (is_open() || is_inflight()), because venues that map a resting order to pending/SUBMITTED are silently dropped from reconciliation when is_open() is tested alone.
  file: skills/nt-review/SKILL.md:33
  evidence: crates/live/src/execution/reports.rs:19-32 (retain_order_status_reports: matches_open = open_only implies is_open() || is_inflight(); closed reports bounded by start/end); crates/model/src/enums.rs:1340-1345 (is_open doc note: testing is_open() alone silently drops pending-mapped orders from reconciliation); upstream commit 9b7db8236e2f47de2dce5d536da92afde38acad7
  fix: Extend the live-trading review bullets (Correctness and lifecycle) with a check that adapter reconciliation and report filtering retain open and in-flight orders per the shared reports.rs rule, preserving only the documented Bybit/Polymarket reconciliation exceptions.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-127] [P2] [CLOSED 2026-09-05] Improvement opportunities: Neither skill's migration lane references the centralized upstream MIGRATION_V2.md, which commit beaac71e0 made the single authoritative home for v1-vs-v2 comparisons and compatibility notes (v1 comparisons were removed from current docs into it).
  file: skills/nt-review/migration_reference/python/legacy-root-guidance.md:3
  evidence: pinned MIGRATION_V2.md (924 lines, 'Migrate from v1 to v2', install/env/parity guidance); upstream commit beaac71e00bb6dd32dc26b4448fbc3b5e4390e21 moved v1 comparisons out of docs/concepts/*, docs/developer_guide/benchmarking.md, and installation docs into MIGRATION_V2.md; grep -rn MIGRATION_V2 skills/nt-review skills/nt-trading returns nothing
  fix: Add a pointer at the top of the quarantine header (and in nt-trading SKILL.md's Migration/reference lane) to the pinned upstream MIGRATION_V2.md as the authoritative v1-to-v2 comparison source, version-scoped to ac22d5cf4.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-128] [P2] [CLOSED 2026-09-05] Improvement opportunities: The RUST/FFI CHECKLIST omits the enforced crate-feature documentation convention added by commit fd247cda9: non-default crate features must appear in matching alphabetical Feature flags lists in README.md and src/lib.rs, and the pre-commit hook rejects violations.
  file: skills/nt-review/AGENTS.md:91
  evidence: upstream commit fd247cda9b6efcfb21e7c868c06c06c9c488229c4 (Enforce crate feature documentation; pre-commit rejects manifests/docs violating the alphabetical Feature flags lists); matching candidate finding recorded in references/upstream-delta-review.json reviewed_transitions[-1] for fd247cda9b with affected_files [skills/nt-review/AGENTS.md]
  fix: Add a checklist bullet under RUST/FFI CHECKLIST requiring the alphabetical Feature flags list in README.md and src/lib.rs to match [features] in Cargo.toml whenever a feature is added or renamed.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-129] [P2] [CLOSED 2026-09-05] Improvement opportunities: The three example READMEs under the Python quarantine lack the explicit migration/reference-only header that every sibling .py file in the same directories carries, so an agent opening a README directly sees unmarked Python-only guidance.
  file: skills/nt-trading/migration_reference/python/examples/actor_data/README.md:1
  evidence: actor_data/run_example.py:2, actor_signals/run_example.py:2, msgbus/run_example.py:2 all carry 'TEMPLATE_CLASSIFICATION: migration/reference-only; not a production default' while actor_data/README.md:1, actor_signals/README.md:1, msgbus/README.md:1 begin with unlabelled titles describing Python patterns; Rust equivalents exist upstream (crates/common/src/actor/data_actor.rs:780 publish_signal, :1446 subscribe_signal)
  fix: Prepend the same migration/reference-only banner used by the sibling templates to all three READMEs (actor_data, actor_signals, msgbus) and note the Rust DataActor signal/msgbus equivalents.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-130] [P2] [CLOSED 2026-09-05] Improvement opportunities: QUICK CHECK and COMMON ISSUES tables in the current-lane review knowledge base are v1-Python shaped (super() calls, type hints, on_bar blocking, ParquetDataCatalog) with only the file-top blanket note for cover, while the rest of the file carries current Rust/PyO3 gates.
  file: skills/nt-review/AGENTS.md:67
  evidence: AGENTS.md:67-77 (QUICK CHECK: 'All lifecycle methods call super()', 'Type hints on all methods'), :82-90 (COMMON ISSUES table keyed to Python handlers), contrasted with the current RUST/FFI CHECKLIST at :91 and current V2 shapes in nt-review/SKILL.md:30-40; blanket note at AGENTS.md:1 is the only label for these sections
  fix: Add a section-scoped NT v2 compatibility note above QUICK CHECK marking those items v1-Python migration/reference-only, and add a minimal Rust v2 quick check (StrategyCore wiring, nautilus_strategy! macro, anyhow::Result handlers, params-aware order APIs).
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S8 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s8-trading-review.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-131] [P1] [CLOSED 2026-09-05] V2 compliance violations: DataTesterConfig API reference documents parameters `requests_start_delta` (line 73) and `use_pyo3_book` (line 79) that do not exist in the pinned DataTesterConfig; upstream has only a TODO for requests_start_delta and no use_pyo3_book anywhere.
  file: skills/nt-testing/references/api/data_tester_config.md:73
  evidence: git -C <upstream> show ac22d5cf4:crates/testkit/src/testers/data/config.rs line 128 '// TODO: Support requests_start_delta when we implement historical data requests'; git grep 'use_pyo3_book' at ac22d5cf returns 0 hits in crates/
  fix: Delete the `requests_start_delta` and `use_pyo3_book` rows from the parameter table and Rust builder method table; regenerate the table from crates/testkit/src/testers/data/config.rs and crates/testkit/src/python/testers.rs at ac22d5cf.
  acceptance-test: grep -c 'requests_start_delta' skills/nt-testing/references/api/data_tester_config.md returns 0 (or content matches pin ac22d5cf4); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-132] [P1] [CLOSED 2026-09-05] V2 compliance violations: DataTesterConfig API reference states `manage_book` defaults to False and that 'Python defaults it to False' (lines 78, 82); the pinned builder/PyO3 default is true, and the table omits the real `stats_interval_secs` parameter.
  file: skills/nt-testing/references/api/data_tester_config.md:78
  evidence: git -C <upstream> show ac22d5cf4:crates/testkit/src/testers/data/config.rs:142-143 '#[builder(default = true)] pub manage_book: bool' and :149 'pub stats_interval_secs: u64'; crates/testkit/src/python/testers.rs:73 exposes stats_interval_secs in the Python constructor
  fix: Correct the `manage_book` default to True, remove the incorrect note, and add the missing `stats_interval_secs` (default 5) row.
  acceptance-test: grep -c 'manage_book' skills/nt-testing/references/api/data_tester_config.md returns 0 (or content matches pin ac22d5cf4); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-133] [P1] [CLOSED 2026-09-05] V2 compliance violations: ExecTesterConfig API reference lists `external_order_claims=` as a Python constructor keyword; the pinned Python ExecTesterConfig accepts `external_order_instrument_ids` (renamed in drift-window commit 681607428).
  file: skills/nt-testing/references/api/exec_tester_config.md:37
  evidence: git -C <upstream> show ac22d5cf4:crates/testkit/src/python/testers.rs:381 'external_order_instrument_ids = None' in the #[pyo3(signature)] block; crates/trading/src/strategy/config.rs:69 'pub external_order_instrument_ids: Option<Vec<InstrumentId>>'
  fix: Replace `external_order_claims=` with `external_order_instrument_ids=` in the constructor keyword list.
  acceptance-test: grep -c 'external_order_instrument_ids' skills/nt-testing/references/api/exec_tester_config.md returns 0 (or content matches pin ac22d5cf4); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-134] [P1] [CLOSED 2026-09-05] V2 compliance violations: Local spec_exec_testing snapshot still uses the pre-rename config key `external_order_claims` in the reconciliation guidance (line 2005) and the configuration reference table (line 2294); the pinned upstream spec uses `external_order_instrument_ids`.
  file: skills/nt-testing/references/guides/spec_exec_testing.md:2005
  evidence: git -C <upstream> show ac22d5cf4:docs/developer_guide/spec_exec_testing.md:2007-2008 'Configure `external_order_instrument_ids`...' and :2297 table row; rename landed in commit 681607428c6ff7ecedd5c646637964dab87f33b6 (4692bac..ac22d5cf)
  fix: Re-sync the two hunks from the pinned upstream spec: rename the key at lines 2005 and 2294 to `external_order_instrument_ids` with the claim-routing wording.
  acceptance-test: grep -c 'external_order_claims' skills/nt-testing/references/guides/spec_exec_testing.md returns 0 after the correction (or the corrected symbol matches the pin via git -C <upstream> show ac22d5cf4:<path>); python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-135] [P1] [CLOSED 2026-09-05] V2 compliance violations: Local spec_exec_testing snapshot's TC rejected-order note says OrderRejected 'comes from the venue'; the pinned spec adds that reconciliation can also synthesize OrderRejected with a link to Terminal reconciliation provenance (doc restructure commit 27dacca2c).
  file: skills/nt-testing/references/guides/spec_exec_testing.md:1862
  evidence: git -C <upstream> show ac22d5cf4:docs/developer_guide/spec_exec_testing.md:1862-1864 'Reconciliation can also synthesize `OrderRejected`; see 'Terminal reconciliation provenance' (see the execution policies page anchor terminal-reconciliation-provenance)'
  fix: Replace line 1862 with the pinned three-line note including the reconciliation-synthesized OrderRejected sentence and provenance link.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-136] [P1] [CLOSED 2026-09-05] V2 compliance violations: Local benchmarking snapshot is stale: the tool table (lines 18-30) lacks the CodSpeed and flamegraph rows and the local-run command table lacks `make cargo-ci-benches`, `make cargo-codspeed-build`, and `make cargo-codspeed-run`; the repo-root synced copy references/developer_guide/benchmarking.md already carries the pinned content with frontmatter source_commit ac22d5cf.
  file: skills/nt-testing/references/guides/benchmarking.md:18
  evidence: git -C <upstream> show ac22d5cf4:docs/developer_guide/benchmarking.md:19-20 (CodSpeed, flamegraph rows) and :139-141 (cargo-ci-benches, cargo-codspeed-build, cargo-codspeed-run); Makefile at ac22d5cf defines cargo-codspeed-build/cargo-codspeed-run targets
  fix: Re-sync skills/nt-testing/references/guides/benchmarking.md from the pinned upstream doc (CodSpeed/flamegraph rows, CodSpeed command table, current intro) or replace skill-local copies with pointers to the repo-root synced snapshot.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-137] [P1] [CLOSED 2026-09-05] V2 compliance violations: testing.md snapshot cites the stale pin '(pinned 4692bac35)' for Memray tooling; the pinned baseline is now ac22d5cf tree-wide and memray remains present at the new pin.
  file: skills/nt-testing/references/guides/testing.md:139
  evidence: git -C <upstream> grep memray at ac22d5cf: python/pyproject.toml:103,118,155 (memray, pytest-memray>=1.10.0), Makefile:1328-1331 pytest-memray target, .github/workflows/nightly-tests.yml:124 python-memray job
  fix: Update the citation to `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d` (memray facts themselves verified current at the pin).
  closure: closed by the 2026-09-05 pin-citation sweep (full+short forms); re-grep returns 0 stale cites

[NT-2026-09-05-138] [P1] [CLOSED 2026-09-05] V2 compliance violations: SKILL.md cites 'At the pinned develop 4692bac35' for the pyobject_to_fee_model_any capability; the pin citation is stale after the tree-wide move to ac22d5cf (the underlying commit e4d3ac7f37 and symbol remain in-pin).
  file: skills/nt-testing/SKILL.md:171
  evidence: git -C <upstream> merge-base --is-ancestor e4d3ac7f37 ac22d5cf4 succeeds; crates/execution/src/python/fee.rs:512 'pub fn pyobject_to_fee_model_any' at ac22d5cf
  fix: Reword to 'At the pinned develop ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d (in-pin since d2b62d35a7 via change e4d3ac7f37)' or drop the pin-level citation and keep the change SHA.
  closure: closed by the 2026-09-05 pin-citation sweep (full+short forms); re-grep returns 0 stale cites

[NT-2026-09-05-139] [P1] [CLOSED 2026-09-05] V2 compliance violations: SKILL.md cites a full SHA '949207b053b040feaff273dff9ad36b796a0e2a9ea' that does not resolve in the upstream cache (real commit: 949207b053b040feaffc2c5ec759cd4658abc7c5 'Guard PyO3 subscription registration'); the commit is also an ancestor of the pin, so the 'Current-develop overlay' framing is wrong.
  file: skills/nt-testing/SKILL.md:119
  evidence: git -C <upstream> rev-parse 949207b053b040feaff273dff9ad36b796a0e2a9ea fails; git log --all --format=%H | grep ^949207b returns 949207b053b040feaffc2c5ec759cd4658abc7c5; git branch --contains shows ac22d5cf4 contains it (in-pin)
  fix: Correct the SHA to 949207b053b040feaffc2c5ec759cd4658abc7c5 and relabel the note as in-pin behavior (ensure_registered guards verified in crates/common/src/python/actor.rs and crates/trading/src/python/{strategy,algorithm}.rs at ac22d5cf).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-140] [P1] [CLOSED 2026-09-05] V2 compliance violations: Migration-reference ExecTesterConfig doc claims test_modify_rejected and test_reject_post_only 'are not exposed by the generated Python constructor'; the pinned Python constructor signature exposes both (plus test_reject_reduce_only).
  file: skills/nt-testing/migration_reference/python/exec_tester_config.md:51
  evidence: git -C <upstream> show ac22d5cf4:crates/testkit/src/python/testers.rs:433-435 'test_reject_post_only = None, test_reject_reduce_only = None, test_modify_rejected = None' in the #[pyo3(signature = (...))] for ExecTesterConfig
  fix: Delete or invert the trailing comment: the flags are Python constructor keywords at the pin; optionally add a labelled keyword example.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-141] [P2] [CLOSED 2026-09-05] Improvement opportunities: nt-testing keeps two diverging copies of each developer guide: repo-root references/developer_guide/*.md synced at ac22d5cf (frontmatter source_commit/sync_date 2026-09-05) and skill-local references/guides/*.md with stale bodies; SKILL.md References (lines 492-496) and the source-pinned lane (line 130) point at the repo-root paths while a skill consumer naturally reads references/guides/ next to the skill. The local testing.md also drops upstream's publish=false fuzz-target paragraph.
  file: skills/nt-testing/SKILL.md:130
  evidence: diff references/developer_guide/testing.md skills/nt-testing/references/guides/testing.md (frontmatter + body deltas incl. dropped 'publish = false package is reserved for fuzz targets' paragraph present at git -C <upstream> show ac22d5cf4:docs/developer_guide/testing.md:129-131); repo-root copies carry source_commit ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d
  fix: Pick one source of truth: either re-sync the skill-local copies to the pinned bodies (preserving only the intentional NT-note header) or delete them and repoint SKILL.md references explicitly (../../references/developer_guide/...) as nt-dex-adapter does.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-142] [P1] [CLOSED 2026-09-05] V2 compliance violations: Setup curriculum exports PYO3_PYTHON from the retired repository-root .venv ('$PWD/.venv/bin/python'); the pinned tree moved the uv project environment to python/.venv (commit 0be8327ae, tip environment_setup.md).
  file: skills/nt-learn/curriculum/01-setup.md:55
  evidence: git -C <upstream> show ac22d5cf4:docs/developer_guide/environment_setup.md:59 'source python/.venv/bin/activate' and :61 'export PYO3_PYTHON="$PWD/python/.venv/bin/python"'; commit 0be8327ae589f64426ccf6a12a3da5ac85616454 removed UV_PROJECT_ENVIRONMENT overrides; pre-change scripts/uv-project-environment.bash defaulted to repo-root .venv
  fix: Change line 55 to export PYO3_PYTHON="$PWD/python/.venv/bin/python" (and mention `make sync` creating python/.venv).
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-143] [P1] [CLOSED 2026-09-05] V2 compliance violations: Full-Rust trading curriculum's Cargo.toml example pins all nautilus-* crates at version 0.63; the pinned upstream workspace version is 0.64.0.
  file: skills/nt-learn/curriculum/09-full-rust-trading.md:28
  evidence: git -C <upstream> show ac22d5cf4:Cargo.toml:52 'version = "0.64.0"' and workspace dependency entries at version 0.64.0
  fix: Bump the example Cargo.toml dependency versions (lines 28-35) and the toolchain note to the pinned workspace version 0.64.0.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: closed as policy-invalid: repo policy (tests/test_v2_inventory_pins_versions.py, test_active_doc_examples.py) aligns dependency examples to the pinned quickstart lane 0.63, not the unpublished workspace 0.64.0; the audited 0.63 values are correct
  closure-proof: pinned-tree signature/policy verification recorded in this entry; no tree change required

[NT-2026-09-05-144] [P2] [CLOSED 2026-09-05] Improvement opportunities: Drift-window BacktestEngine data-input features are uncovered anywhere in nt-learn/nt-testing: typed batch input (3c9ad2ef4) and typed batch replay (dabe39d77), and lazy streaming across multiple data configs (ec1894d6f) extend the streaming/BacktestNode guidance the curriculum teaches.
  file: skills/nt-learn/curriculum/09-full-rust-trading.md:54
  evidence: git -C <upstream> log 4692bac..ac22d5cf --oneline: 3c9ad2ef4 'Add BacktestEngine typed batch input', dabe39d77 'Add BacktestEngine typed batch replay', ec1894d6f 'Stream backtest data lazily across multiple data configs (#4897)'; grep for 'batch input'/'batch replay'/'lazily' across skills/nt-testing and skills/nt-learn returns nothing
  fix: Add a short subsection to the Stage 05/09 backtest material (and optionally nt-testing SKILL.md) covering typed batch input/replay APIs and lazy multi-config streaming with a pinned example reference.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-145] [P1] [CLOSED 2026-09-05] V2 compliance violations: The dex pytest suite imports v1-only module paths that error on collection against the pinned interpreter: test_legacy_migration_fail_closed.py:9-22 (nautilus_trader.execution.messages/.reports) and :23 (nautilus_trader.test_kit.stubs.component.TestComponentStubs); test_nonproduction_migration_templates.py:11-13 (model.identifiers, test_kit); test_backtest_integration.py:28-31 (backtest.engine, backtest.models, model.enums, model.objects); test_instrument_parsing.py:15-17 (model.identifiers/.instruments/.objects); test_order_book_events.py:26 loads dex_order_book_builder.py whose header imports model.data/model.enums/model.identifiers.
  file: skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py:23
  evidence: Verified empirically in the pinned venv (nautilus_trader 2.0.0rc4): 'No module named nautilus_trader.model.identifiers', 'No module named nautilus_trader.execution.messages', 'No module named nautilus_trader.test_kit'; upstream MIGRATION_V2.md:43-47 documents the v1->v2 path table (e.g. nautilus_trader.model.identifiers.TraderId -> nautilus_trader.model.TraderId, backtest.engine.BacktestEngine -> backtest.BacktestEngine)
  fix: Rewrite the five test files to v2 flat import paths (nautilus_trader.model, nautilus_trader.backtest, nautilus_trader.execution) or convert them to static contract checks like tests/test_dex_compliance.py; note that nautilus_trader.backtest.engine importorskip guard at test_backtest_integration.py:23 does not trigger because nautilus_trader._libnautilus.common exists at the pin.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-146] [P1] [CLOSED 2026-09-05] V2 compliance violations: Quarantined config template imports LiveDataClientConfig and LiveExecClientConfig from nautilus_trader.config and its header claims these are 'the three config classes required by NautilusTrader's adapter framework' in present tense; at the pin nautilus_trader.config exports DataClientConfig/ExecutionClientConfig and the LiveDataClientConfig/LiveExecClientConfig names do not exist, so the 'legacy executable' templates are not executable against any current environment (same v1 submodule surface in dex_order_book_builder.py:20-22, dex_data_client.py:25-35, dex_factory.py:24-30, dex_instrument_provider.py:12-18).
  file: skills/nt-dex-adapter/migration_reference/python/templates/dex_config.py:14
  evidence: Pinned venv run: 'cannot import name LiveDataClientConfig from nautilus_trader.config'; git -C <upstream> show ac22d5cf4:python/nautilus_trader/config/__init__.pyi:18-19 re-exports DataClientConfig/ExecutionClientConfig from nautilus_trader.live; live/__init__.pyi defines @final classes DataClientConfig/ExecutionClientConfig
  fix: Either port the template imports to the v2 surface (DataClientConfig/ExecutionClientConfig, flat module imports per MIGRATION_V2.md) and keep the migration framing, or relabel the templates from 'legacy executable' to non-executable reference and drop the current-tense 'required by the adapter framework' claim; update the six templates consistently.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-147] [P1] [CLOSED 2026-09-05] V2 compliance violations: AGENTS.md tells DEX adapter developers to study the '_template' adapter; no _template adapter exists at the pinned tree in crates/adapters/ or python/nautilus_trader/adapters/ (nor anywhere in upstream git history for that path).
  file: skills/nt-dex-adapter/AGENTS.md:88
  evidence: git -C <upstream> ls-tree ac22d5cf4 crates/adapters/ (20 venues, no _template); git log --all --diff-filter=A -- 'crates/adapters/_template/*' returns nothing; find for '*template*' at pin shows only docs/dev_templates benchmark templates
  fix: Remove '_template' from the study list or replace with a real pinned reference (e.g. the blockchain adapter crate nautilus-blockchain, or sandbox) consistent with SKILL.md's canonical OKX/BitMEX/Bybit list.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-148] [P1] [CLOSED 2026-09-05] V2 compliance violations: SKILL.md cites '(pinned 4692bac35, crates/live/src/task.rs)' for the standardized task lifecycle; the pin has moved tree-wide to ac22d5cf and task.rs changed inside the drift window.
  file: skills/nt-dex-adapter/SKILL.md:241
  evidence: git -C <upstream> rev-parse HEAD = ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d; eb42e2bfc6c5540839dbdaade7fdef242a6f3b2e 'Add live task identity' (4692bac..ac22d5cf) modified crates/live/src/task.rs (+533 lines)
  fix: Update the citation to ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d for crates/live/src/task.rs.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-149] [P2] [CLOSED 2026-09-05] Improvement opportunities: The DEX task-ownership section does not cover the drift-window live task identity feature (named TaskRef handles, spawn_named on TaskGroup/TaskSpawner, shared task state replacing adapter-local flags).
  file: skills/nt-dex-adapter/SKILL.md:238
  evidence: git -C <upstream> show ac22d5cf4:crates/live/src/task.rs:128 'pub struct TaskRef', :159 'struct TaskIdentity', :255/:416 'pub fn spawn_named(... name: &'static str ...) -> Result<TaskRef, TaskSpawnError>'; commit eb42e2bfc 'Expose named task references without transferring group ownership'
  fix: Extend the task-ownership guidance to mention spawn_named/TaskRef for named background work (receipt monitors, keepalives) and cite the pinned task.rs symbols.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-150] [P2] [CLOSED 2026-09-05] Improvement opportunities: Migration templates label their phases against a '7-phase DEX adapter implementation sequence' while SKILL.md, AGENTS.md, and compliance_checklist.md define the official ten-phase sequence (Phase 0-9); the phase numbers cited in the templates no longer map to the skill's own contract.
  file: skills/nt-dex-adapter/migration_reference/python/templates/dex_instrument_provider.py:7
  evidence: Same file line 7, dex_data_client.py:8, dex_exec_client.py:7, dex_factory.py:12 all say '7-phase'; skills/nt-dex-adapter/tests/test_dex_compliance.py requires 'Phase 0: Define scope' through 'Phase 9: Finish documentation and operations' in SKILL.md
  fix: Renumber the template docstrings to the ten-phase sequence (instrument provider = Phase 2, data client = Phase 3, exec client = Phases 4-5, factory = Phase 6) or drop the phase numbering.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S9 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s9-testing-learn-dex.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-151] [P1] [CLOSED 2026-09-05] V2 compliance violations: nt-dev SKILL.md teaches root-.venv PyO3 interpreter path; upstream moved the uv project environment to python/.venv at the pin (commit 0be8327ae removed repository-level UV_PROJECT_ENVIRONMENT overrides).
  file: skills/nt-dev/SKILL.md:130
  evidence: upstream docs/developer_guide/environment_setup.md:61 `export PYO3_PYTHON="$PWD/python/.venv/bin/python"`; commit 0be8327ae "Use uv's default project environment"
  fix: Change line 130 to `export PYO3_PYTHON="$PWD/python/.venv/bin/python"` and align the surrounding Linux/macOS env-var block with upstream environment_setup.md.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-152] [P1] [CLOSED 2026-09-05] V2 compliance violations: environment_setup.md guide still teaches the pre-0be8327ae root .venv layout throughout (activate, PYO3_PYTHON, 'installs into the root .venv', rust-analyzer VIRTUAL_ENV placeholders).
  file: skills/nt-dev/references/guides/environment_setup.md:62
  evidence: same file lines 64, 195, 282, 507-553; upstream docs/developer_guide/environment_setup.md:59 `source python/.venv/bin/activate`, :297 'install the Python package into python/.venv', :191-199 migration note for old root-.venv checkouts; commit 0be8327ae
  fix: Replace root `.venv` references with `python/.venv` (activate line, both PYO3_PYTHON exports, Builds section sentence, and the six VIRTUAL_ENV placeholder values) and add the 'remove UV_PROJECT_ENVIRONMENT export' migration note from upstream.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-153] [P1] [CLOSED 2026-09-05] V2 compliance violations: testing.md mixed-debugging snippet still exports UV_PROJECT_ENVIRONMENT=../.venv; upstream removed repository-level UV_PROJECT_ENVIRONMENT overrides when the venv moved to python/.venv.
  file: skills/nt-testing/references/guides/testing.md:330
  evidence: upstream docs/developer_guide/testing.md:310-324 maturin develop block contains no UV_PROJECT_ENVIRONMENT line; docs/developer_guide/environment_setup.md:199 'remove any UV_PROJECT_ENVIRONMENT export'; commit 0be8327ae (shared real path: nt-dev/references/guides/testing.md symlinks here)
  fix: Delete the `UV_PROJECT_ENVIRONMENT=../.venv \` line from the maturin develop subshell so the block matches upstream testing.md.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-154] [P1] [CLOSED 2026-09-05] V2 compliance violations: testing.md data-type test matrix cites the pre-consolidation DataEngine test path crates/data/tests/engine.rs; upstream moved integration tests into crates/data/tests/integration/.
  file: skills/nt-testing/references/guides/testing.md:351
  evidence: same file lines 352, 390; upstream tree has crates/data/tests/integration/engine.rs and no crates/data/tests/engine.rs; commit 503debebe 'Consolidate Rust integration test binaries' (crates/data/tests/{ => integration}/engine.rs)
  fix: Update the three occurrences (matrix rows and the 'Data type testing' checklist) to `crates/data/tests/integration/engine.rs`.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-155] [P1] [CLOSED 2026-09-06] V2 compliance violations: python_conventions.md says ruff rules live in the top-level pyproject.toml; the pinned v2 tree has no root pyproject.toml - ruff config is in python/pyproject.toml.
  file: skills/nt-dev/references/guides/python_conventions.md:110
  evidence: upstream tree: `ls pyproject.toml` fails, `python/pyproject.toml` exists with [tool.ruff] at lines 167-210
  fix: Reword to "Ruff rules can be found in `python/pyproject.toml`, with ignore justifications typically commented."
  closure: NT v2 compatibility note: migration/reference tokens quoted here are audit evidence; ruff location corrected to python/pyproject.toml (no root pyproject.toml at the pin)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-156] [P1] [CLOSED 2026-09-05] V2 compliance violations: ffi_memory.md cites vec_time_event_handlers_drop as an example type-specific CVec drop helper; no such export exists anywhere in the pinned tree (it does not resolve against crates/).
  file: skills/nt-dev/references/guides/ffi_memory.md:38
  evidence: git grep 'vec_time_event_handlers_drop' ac22d5cf4 -- crates/ returns nothing; real helpers at pin: vec_drop_fills (crates/model/src/ffi/orderbook/book.rs:457), vec_drop_book_levels / vec_drop_book_orders (crates/model/src/ffi/orderbook/level.rs:120,136)
  fix: Replace `vec_time_event_handlers_drop` in the example list with `vec_drop_fills` (or another helper that exists at the pin).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-157] [P1] [CLOSED 2026-09-05] V2 compliance violations: legacy-root-guidance.md requires preserving an 'adapter 7-phase dependency order' but the pinned developer guide defines ten phases (Phase 0 through Phase 9); nt-architect/AGENTS.md already states the correct ten-phase order.
  file: skills/nt-architect/migration_reference/python/legacy-root-guidance.md:46
  evidence: upstream docs/developer_guide/adapters.md:234-360 defines Phase 0..Phase 9 (10 sections); skills/nt-architect/AGENTS.md:63 'ten-phase dependency order (Phase 0 ... Phase 9)'
  fix: Change 'the adapter 7-phase dependency order' to 'the adapter ten-phase dependency order (Phase 0-9)' to match the pinned guide and the sibling AGENTS.md.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: NT v2 compatibility note: legacy tokens quoted here are migration/reference-only audit evidence; (quoted legacy tokens are migration/reference-only audit evidence) legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-158] [P1] [CLOSED 2026-09-05] V2 compliance violations: nt-implement AGENTS.md coding-standards row says 'log::* for sync, tracing::* for async/adapter code'; upstream logging guidance is fully-qualified log macros for all Rust components and only the Interactive Brokers adapter uses tracing at the pin.
  file: skills/nt-implement/AGENTS.md:145
  evidence: upstream docs/developer_guide/rust.md:294-296 'Fully qualify log macros, for example log::debug! and log::info!.'; git grep -l 'tracing::' ac22d5cf4 -- crates/adapters returns only interactive_brokers (20 files) while all other adapters use log::*
  fix: Change the row to 'Fully qualify log::* macros in core and adapter crates' and drop the tracing rule (or scope it explicitly to the IB adapter if intentional).
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-159] [P1] [CLOSED 2026-09-05] V2 compliance violations: api_reference/analysis.md stub is missing the nautilus_trader.analysis.statistic automodule block that upstream added with user-defined portfolio statistics, so the new module is absent from the generated API docs surface.
  file: references/api_reference/analysis.md:36
  evidence: upstream docs/api_reference/analysis.md:44 `.. automodule:: nautilus_trader.analysis.statistic`; commit 7e8c9c9cd added python/nautilus_trader/analysis/statistic.py and the +8-line docs stub
  fix: Append the `nautilus_trader.analysis.statistic` automodule block (eval-rst fence) after the reporter block so the file matches upstream docs/api_reference/analysis.md at ac22d5cf.
  acceptance-test: content matches pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-160] [P1] [CLOSED 2026-09-05] V2 compliance violations: concepts/backtesting.md teaches an engine.add_data_iterator(data_name=..., generator=...) streaming API that does not exist at the pin; upstream explicitly documents that the low-level API has no generator-based method.
  file: references/concepts/backtesting.md:117
  evidence: same file line 1119 repeats it; upstream docs/concepts/backtesting/apis-and-runs.md:88 'The low-level API does not expose a generator-based add_data_iterator() method.'; `def add_data` is the only data-add method in python/nautilus_trader/backtest/__init__.pyi:489 and crates/backtest/src/python/engine.rs
  fix: Remove the add_data_iterator 'automatic chunking' example and the line-1119 reference; present the add_data + run(streaming=True) + end() loop (and BacktestNode chunk_size catalog chunking) as the streaming options, matching upstream apis-and-runs.md.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-161] [P1] [CLOSED 2026-09-05] V2 compliance violations: concepts/portfolio.md custom-statistics example mixes a v2 import with v1 APIs: calculate_from_realized_pnls is typed against pd.Series (v2 base class takes list[float] and returns float | None) and registration goes through engine.portfolio.analyzer, but the v2 Portfolio has no analyzer attribute.
  file: references/concepts/portfolio.md:149
  evidence: python/nautilus_trader/analysis/statistic.py:80 `def calculate_from_realized_pnls(self, realized_pnls: list[float]) -> float | None`; python/nautilus_trader/portfolio/__init__.pyi:136 exposes `def register_statistic` on Portfolio with no `analyzer` getter; upstream docs/concepts/portfolio.md:302 `engine.portfolio.register_statistic(TradeCount())`
  fix: Retype the example override to `calculate_from_realized_pnls(self, realized_pnls: list[float]) -> float | None` (drop pandas), and change registration to `engine.portfolio.register_statistic(stat)`.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-162] [P1] [CLOSED 2026-09-05] V2 compliance violations: concepts/adapters.md instrument-discovery how-to uses v1-only import paths (binance submodule providers, get_cached_binance_http_client, common.component.LiveClock) that do not resolve in the pinned v2 package; the section has no adjacent legacy label.
  file: references/concepts/adapters.md:66
  evidence: python/nautilus_trader/adapters/binance/ contains only __init__ and instruments.py; its __init__.pyi export list has no get_cached_binance_http_client/BinanceAccountType/provider classes; no LiveClock is exposed to Python (only unified Clock in crates/common/src/python/clock.rs); upstream v2 discovery guidance is InstrumentProviderConfig(load_all=True) per docs/concepts/instruments/index.md:150-151
  fix: Either label the example as v1 migration/reference inline, or rewrite it against the pinned surface (flat `nautilus_trader.adapters.binance` exports such as load_binance_instruments, InstrumentProviderConfig-driven loading).
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-163] [P1] [CLOSED 2026-09-05] V2 compliance violations: concepts/instruments.md exchange-discovery example imports BinanceSpotInstrumentProvider from nautilus_trader.adapters.binance.spot.providers, a v1 path absent from the pinned tree.
  file: references/concepts/instruments.md:51
  evidence: python/nautilus_trader/adapters/binance/ has no spot/ package; flat exports include load_binance_instruments; upstream docs/concepts/instruments/index.md:142-151 uses TestInstrumentProvider and InstrumentProviderConfig instead of standalone provider classes
  fix: Replace the provider-class example with the pinned v2 flow (load_binance_instruments from flat nautilus_trader.adapters.binance, or InstrumentProviderConfig within a node) or add an adjacent migration/reference label.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-164] [P1] [CLOSED 2026-09-05] V2 compliance violations: concepts/cache.md price/bar-types examples import PriceType and AggregationSource from the v1 Cython-internal path nautilus_trader.core.rust.model, which does not exist in the pinned v2 package.
  file: references/concepts/cache.md:223
  evidence: same file line 235; python/nautilus_trader/core/ contains only datetime.py and flat re-exports; PriceType and AggregationSource are exported from flat python/nautilus_trader/model/__init__.pyi
  fix: Change both imports to `from nautilus_trader.model import PriceType` / `from nautilus_trader.model import PriceType, AggregationSource`.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: NT v2 compatibility note: legacy tokens quoted here are migration/reference-only audit evidence; (quoted legacy tokens are migration/reference-only audit evidence) legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-165] [P1] [CLOSED 2026-09-05] V2 compliance violations: concepts/data.md custom-data walkthrough (a current v2 capability) registers types with v1-only APIs: nautilus_trader.serialization.base.register_serializable_type and nautilus_trader.serialization.arrow.serializer.register_arrow, plus nautilus_trader.core.Data / test_kit paths; none resolve at the pin.
  file: references/concepts/data.md:1698
  evidence: python/nautilus_trader/serialization/__init__.pyi __all__ has no register_serializable_type/register_arrow; v2 registration is register_custom_data_class exported from flat nautilus_trader.model (python/nautilus_trader/model/__init__.pyi:8348) per docs/concepts/custom_data.md:31; same file lines 1695-1699, 1772, test_kit at 664
  fix: Rewrite the custom-data registration example against the v2 surface (register_custom_data_class(MyType) from nautilus_trader.model, pure-Python class with JSON/Arrow callbacks per docs/concepts/custom_data.md) and fix `nautilus_trader.core.Data` -> `nautilus_trader.model.Data`, `test_kit` -> `testkit`.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-166] [P1] [CLOSED 2026-09-05] V2 compliance violations: concepts/message_bus.md custom-data overview example uses the v1-only @customdataclass decorator from nautilus_trader.model.custom and Data from nautilus_trader.core.data with no adjacent legacy label; neither module exists at the pin.
  file: references/concepts/message_bus.md:148
  evidence: python/nautilus_trader/model/ is a flat re-export package (no custom submodule); no python/nautilus_trader/core/data.py; v2 custom-data pattern is a plain class plus register_custom_data_class per docs/concepts/custom_data.md:31,180-207
  fix: Label the @customdataclass block as v1 migration/reference, or convert it to the v2 plain-class + register_custom_data_class pattern from the pinned custom_data guide.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-167] [P2] [CLOSED 2026-09-05] Improvement opportunities: nt-implement V2 cutover map presents Portfolio Statistics as Rust-only with Python relegated to migration templates, but the drift window added first-class user-defined Python statistics (PortfolioStatistic base + Portfolio.register_statistic) that the skill does not cover as a bounded PyO3 extension point.
  file: skills/nt-implement/SKILL.md:164
  evidence: commit 7e8c9c9cd 'Support user-defined portfolio statistics': python/nautilus_trader/analysis/statistic.py (PortfolioStatistic base), crates/portfolio/src/portfolio.rs:2067 pub fn register_statistic, python/nautilus_trader/portfolio/__init__.pyi:136; documented in docs/concepts/portfolio.md:269-316
  fix: Add a note to the Portfolio Statistics row (and the custom-simulation-models pointer) that user-defined Python statistics are a supported v2 surface via nautilus_trader.analysis.statistic.PortfolioStatistic registered with Portfolio.register_statistic, while keeping Rust as the repository's production default.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

[NT-2026-09-05-168] [P2] [CLOSED 2026-09-05] Improvement opportunities: concepts/backtesting.md does not cover the drift-window BacktestEngine data-input features: typed batch input/replay (add_data_batch with homogeneous DataBatch) and lazy multi-config streaming, which upstream added for large-workflow performance.
  file: references/concepts/backtesting.md:100
  evidence: commits 3c9ad2ef4 'Add BacktestEngine typed batch input' (crates/backtest/src/engine.rs:436 pub fn add_data_batch, crates/model/src/data/batch.rs DataBatch), dabe39d77 'Add BacktestEngine typed batch replay', ec1894d6f 'Stream backtest data lazily across multiple data configs (#4897)'; capabilities are Rust-side at the pin (not in python/nautilus_trader/backtest/__init__.pyi)
  fix: Extend the streaming section (after replacing add_data_iterator per NT-2026-09-05-170) with a version-scoped note that the Rust engine accepts typed DataBatch input via add_data_batch and streams lazily across multiple data configs, pointing at crates/backtest/src/engine.rs and BENCHMARKS.md for measurements.
  acceptance-test: corrected content verified against pin ac22d5cf4; python3 -m pytest -q green
  closure: legacy tokens quoted in this entry are audit evidence (migration/reference-only); fixed in segment S10 of the 2026-09-05 phase-2 wave (see receipt docs/tracking/receipts/harden-nt-v2-20260905/phase-2-seg-s10-dev-impl-arch.json)
  closure-proof: token-residue grep on the fixed tree returns 0 stale occurrences; python3 -m pytest -q green on the final tree (452 passed, 7 skipped - the skips are gated v1 modules with explicit migration-reference reasons); check_legacy_labelling + check_findings_schema + G2 check-cards green after final evidence regeneration

---

## Closed findings — 2026-09-04 full-tree audit (history)

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
Nine parallel read-only audit passes (all 17 skills, references/api_reference, references/concepts, references/developer_guide, references/integrations, templates) against pinned upstream `4692bac35bb11a25eeebb8d7af4d51c55afe53ec` (develop tip, 0 commits ahead). Every finding below was verified against the pinned tree (symbols, module layouts, configs, Make targets) before recording. Systemic patterns: v1 submodule automodule stubs across skills' references/api/ trees; v1 factory/type names (`*LiveDataClientFactory`, `*ExecClientConfig`, `TradingNodeConfig`, `LoggingConfig`) in venue guides; venue config-field drift; handler/subscription renames (`on_quote_tick`→`on_quote`, `subscribe_quote_ticks`→`subscribe_quotes`); toolchain drift (make targets, test paths, feature names, versions 0.62→0.63); and missing v2 coverage (task lifecycle, SimulationModule, LiveNode builder surface). Totals: 35 P0, 160 P1, 45 P2.

[NT-2026-09-04-01] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-trading api/accounting.md documents removed Python nautilus_trader.accounting package for the Rust-owned accounting domain
  file: skills/nt-trading/references/api/accounting.md:1
  evidence: pin 4692bac: python/nautilus_trader/accounting/ absent; Rust crates/model/src/accounts/{cash,margin,margin_model,betting,wallet}.rs + crates/portfolio/src/manager.rs; PyO3 CashAccount/MarginAccount from flat nautilus_trader.model (model/__init__.pyi:661,2818)
  fix: rewrite page around pinned Rust accounting modules + flat PyO3 account classes; delete or legacy-label v1 automodule stubs
  acceptance-test: grep -c 'nautilus_trader.accounting' skills/nt-trading/references/api/ returns 0 unlabelled; python3 tools/check_legacy_labelling.py exits 0
  closure: accounting.md regenerated to the pinned flat form (nautilus_trader.model with CashAccount/MarginAccount/BettingAccount/WalletAccount/AccountBalance members) plus an owning-crate pointer to crates/model/src/accounts/; zero nautilus_trader.accounting directives remain
  closure-proof: grep -c 'nautilus_trader.accounting' skills/nt-trading/references/api/accounting.md returns 0; python3 tools/check_legacy_labelling.py green

[NT-2026-09-04-02] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-trading api/ stubs (execution, portfolio, risk, trading, orders, events, position) teach v1 Python submodule APIs for Rust-owned domains
  file: skills/nt-trading/references/api/execution.md:1
  evidence: pin: python/nautilus_trader/{execution,portfolio,risk,trading}/ flat __init__ only; model.orders/events/position absent; Rust: crates/execution/src/engine/, crates/portfolio/src/portfolio.rs, crates/risk/src/engine/mod.rs, crates/trading/src/strategy/, crates/model/src/{orders,events,position.rs}
  fix: replace stubs with pinned Rust module surfaces + flat PyO3 exports (e.g. OrderFactory crates/trading/src/strategy/api.rs:516) or label files as v1 snapshots
  acceptance-test: no automodule directive in nt-trading/references/api/ targets a module absent from the pinned python tree; legacy labelling validator green
  closure: execution/risk/trading api pages regenerated to pinned single flat automodules with crate pointers; orders/events/position/portfolio symlinks resolved to regenerated nt-model/nt-signals targets
  closure-proof: bash /tmp/check-directives.sh reports DEAD: none across skills/ and references/

[NT-2026-09-04-03] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-model api/model/ stubs teach v1 Python submodule APIs for the entirely Rust-owned model domain
  file: skills/nt-model/references/api/model/orders.md:1
  evidence: pin: python/nautilus_trader/model/ flat (only __init__.py/.pyi re-exporting _libnautilus.model); domain defined in crates/model/src/{orders,instruments,events,identifiers,types,position.rs}
  fix: regenerate pages against flat nautilus_trader.model automodule + Rust crate paths per section
  acceptance-test: no dead v1 submodule path remains under skills/nt-model/references/api/
  closure: all nt-model api/model pages regenerated to the pinned model/*.md flat-member automodule form with per-section Rust crate pointers; model/reports.md added per the pinned index
  closure-proof: pinned docs/api_reference/model/orders.md member list reproduced; bash /tmp/check-directives.sh DEAD: none

[NT-2026-09-04-04] [P1] [CLOSED 2026-09-04] V2 compliance: instrument_types.md teaches from_pyo3()/from_pyo3_c()/instruments_from_pyo3() conversion APIs absent at pin
  file: skills/nt-model/references/guides/instrument_types.md:267
  evidence: grep from_pyo3 over pin python/+crates/ = 0 hits; pinned cross-boundary: PyO3 classes are the Python surface; from_raw preserves precision (model/__init__.pyi:6110)
  fix: delete/rewrite 'From pyo3' and 'Batch conversion from Rust' sections around pinned behavior
  acceptance-test: grep -c 'from_pyo3' skills/nt-model/references/guides/instrument_types.md returns 0
  closure: From pyo3 / Batch conversion sections deleted; replaced by a From Rust note (model classes ARE the PyO3 bindings; from_raw preserves precision)
  closure-proof: grep -c 'from_pyo3' skills/nt-model/references/guides/instrument_types.md = 0

[NT-2026-09-04-05] [P1] [CLOSED 2026-09-04] V2 compliance: instrument_types.md claims a Python Instrument base class and v1 submodule imports
  file: skills/nt-model/references/guides/instrument_types.md:11
  evidence: pin model/__init__.pyi: 176 concrete classes, no class Instrument base; InstrumentAny enum is Rust-only (crates/model/src/instruments/any.rs:33, 18 variants); model.instruments/.identifiers/.objects submodules absent
  fix: update hierarchy and examples: concrete instrument classes; InstrumentAny Rust-side only; flat imports (from nautilus_trader.model import Equity, InstrumentId, ...)
  acceptance-test: no 'model.instruments.base' or Python Instrument-base hierarchy remains in the guide
  closure: hierarchy replaced by 19 concrete flat classes (Module lines -> Class lines), flat construction imports, InstrumentAny documented as Rust-side only (any.rs:33, 18 variants); added CryptoFuturesSpread/CryptoOptionSpread/TokenizedAsset sections
  closure-proof: grep -c 'model.instruments' instrument_types.md = 0

[NT-2026-09-04-06] [P1] [CLOSED 2026-09-04] V2 compliance: instrument_types.md lists phantom instrument methods is_spread()/get_base_currency()/get_settlement_currency()/get_cost_currency()
  file: skills/nt-model/references/guides/instrument_types.md:82
  evidence: 0 hits in model pyi; is_spread exists only on Rust InstrumentAny (any.rs:62); settlement_currency is a property (pyi:1010)
  fix: replace with pinned surface: make_price/make_qty/notional_value/next_bid_price/next_ask_price (pyi:431-436)
  acceptance-test: grep for the four phantom methods in the guide returns 0
  closure: phantom methods replaced with pinned surface: make_price/make_qty(value, round_down=False)/notional_value(quantity, price, use_quote_for_inverse=False)/next_bid_price/next_ask_price (+_prices), settlement_currency property, type_name
  closure-proof: methods match model/__init__.pyi:431-436,1010

[NT-2026-09-04-07] [P1] [CLOSED 2026-09-04] V2 compliance: value_type_patterns.md names constant FIXED_PRECISION_BYTES; pin exports PRECISION_BYTES
  file: skills/nt-model/references/guides/value_type_patterns.md:58
  evidence: model/__init__.pyi:17,29 exports PRECISION_BYTES; FIXED_PRECISION_BYTES 0 hits at pin
  fix: rename documented constant to PRECISION_BYTES
  acceptance-test: grep FIXED_PRECISION_BYTES in skill tree returns 0
  closure: constant renamed to PRECISION_BYTES
  closure-proof: grep FIXED_PRECISION_BYTES in skill tree = 0; pyi:29 exports PRECISION_BYTES

[NT-2026-09-04-08] [P1] [CLOSED 2026-09-04] V2 compliance: value_type_patterns.md teaches Quantity.saturating_sub() absent at pin
  file: skills/nt-model/references/guides/value_type_patterns.md:121
  evidence: 0 hits in pyi; saturating_sub in crates/ only as internal integer arithmetic (money.rs:415)
  fix: remove saturating_sub guidance; document __sub__ semantics only
  acceptance-test: grep saturating_sub in guide returns 0
  closure: EVIDENCE CORRECTED: the audit claim was wrong - Quantity.saturating_sub(other) -> Quantity EXISTS at the pin (model/__init__.pyi:6190; crates/model/src/types/quantity.rs:334). The segment initially removed the mentions per the faulty finding; mission verification restored correct saturating_sub guidance alongside the __sub__ ValueError semantics
  closure-proof: grep -n 'saturating_sub' value_type_patterns.md documents the pinned method citing pyi:6190

[NT-2026-09-04-09] [P1] [CLOSED 2026-09-04] V2 compliance: value_type_patterns.md teaches Currency.from_internal_map(), model.currencies module, register_currency() — none exist at pin
  file: skills/nt-model/references/guides/value_type_patterns.md:260
  evidence: 0 hits at pin; python model/ flat; pinned registration is Currency.register(currency, overwrite) (pyi:1555, correctly used at :284)
  fix: drop the three; use Currency.from_str and Currency.register consistently
  acceptance-test: grep from_internal_map/register_currency in guide returns 0
  closure: from_internal_map/model.currencies/register_currency dropped; custom-currency section uses Currency.from_str + Currency.register(custom, overwrite=False)
  closure-proof: grep markers = 0; pyi:1553,1555 cited

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-10] [P1] [CLOSED 2026-09-04] V2 compliance: value_type_patterns.md imports CurrencyType from v1 path nautilus_trader.core.rust.model
  file: skills/nt-model/references/guides/value_type_patterns.md:247
  evidence: pin core/ has no rust/ subpackage; CurrencyType is a class in model/__init__.pyi:7672
  fix: from nautilus_trader.model import CurrencyType
  acceptance-test: grep 'core.rust' in guide returns 0
  closure: CurrencyType imported from flat nautilus_trader.model
  closure-proof: grep 'core.rust' in guide = 0

[NT-2026-09-04-11] [P1] [CLOSED 2026-09-04] V2 compliance: value_type_patterns.md documents from_raw_c/from_str_c low-level constructors absent at pin
  file: skills/nt-model/references/guides/value_type_patterns.md:382
  evidence: 0 hits at pin; Python surface is from_raw(raw, precision) (pyi:6110,6172) and from_str
  fix: rewrite sections around from_raw/from_str or remove
  acceptance-test: grep '_c(' phantom constructors in guide returns 0
  closure: Rust-to-Python conversion section rewritten around Price.from_raw(raw, precision)/Quantity.from_raw/Money.from_raw(raw, currency)/from_str/Currency.from_str; _c variants gone
  closure-proof: grep '_c(' phantom constructors = 0; pyi:6110,6172,3470 cited

[NT-2026-09-04-12] [P1] [CLOSED 2026-09-04] V2 compliance: nt-trading rust.md capability matrix marks Controller unavailable in v2 PyO3 but it is exported and functional
  file: skills/nt-live/references/concepts/rust.md:54
  evidence: trading/__init__.pyi:20,95 class Controller(common.DataActor) with full lifecycle methods
  fix: set Controller v2 PyO3 cell to check (v2 Rust stays '-')
  acceptance-test: matrix row shows Controller v2 PyO3 available
  closure: Controller v2 PyO3 cell set to available (v2 Rust stays - ; Controller is a PyO3 class)
  closure-proof: trading/__init__.pyi:95 class Controller(common.DataActor)

[NT-2026-09-04-13] [P1] [CLOSED 2026-09-04] V2 compliance: nt-trading rust.md adapter matrix marks Interactive Brokers unavailable in v2 but a full Rust IB crate exists
  file: skills/nt-live/references/concepts/rust.md:73
  evidence: crates/adapters/interactive_brokers/ at pin with src/{data,execution,providers,gateway,historical,python,factories.rs} and runnable examples
  fix: mark IB v2 Rust available; scope any '-' claim to specific feature gaps with evidence
  acceptance-test: matrix row reflects pinned IB crate
  closure: closed with NT-2026-09-04-94 (same matrix row)
  closure-proof: same as 94

[NT-2026-09-04-14] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: all 8 nt-trading references/api/ files carry v1-only module paths with no legacy label anywhere
  file: skills/nt-trading/references/api/accounting.md:1
  evidence: grep legacy/migration in dir = 0; all referenced modules absent from pinned python tree
  fix: add legacy/migration framing to each file or (preferred) regenerate per the P0 fixes
  acceptance-test: check_legacy_labelling.py green and each file either v2-accurate or explicitly labelled
  closure: closed by regeneration: every nt-trading api page is now v2-accurate so no legacy labelling is required
  closure-proof: grep -rn 'nautilus_trader.accounting\|model.orders\|model.events\|model.position' skills/nt-trading/references/api/ returns only v2-flat member directives

[NT-2026-09-04-15] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: all 11 nt-model references/api/model/ files carry v1-only module paths with no legacy label
  file: skills/nt-model/references/api/model/book.md:1
  evidence: grep legacy/migration in dir = 0; all model submodules absent at pin (flat package)
  fix: add legacy/migration framing or regenerate against flat v2 surface
  acceptance-test: same validator + labelling check
  closure: closed by regeneration: every nt-model api page is now v2-accurate
  closure-proof: grep -rn 'legacy\|migration' not needed; all automodule targets exist at pin (check-directives.sh DEAD: none)

[NT-2026-09-04-16] [P2] [CLOSED 2026-09-04] Improvement opportunities: OrderStatus.VOIDED / OrderFillVoided / on_order_fill_voided lifecycle absent from orders/strategies concept docs
  file: skills/nt-trading/references/concepts/orders.md:122
  evidence: OrderStatus has 15 variants ending Voided=15; OrderFillVoided (crates/model/src/events/order/fill_voided.rs:48); on_order_fill_voided hook (crates/trading/src/strategy/mod.rs:1663, dispatched :1437)
  fix: add VOIDED (terminal) to status table/diagram and on_order_fill_voided to handler list
  acceptance-test: grep VOIDED orders.md shows the row; handler listed in strategies.md
  closure: VOIDED added to terminal-status list, mermaid diagram (Filled/PartiallyFilled -> Voided edges), status table; OrderFillVoided import + on_order_fill_voided handler row in strategies.md
  closure-proof: OrderStatus 15-variant enum pyi:7895-7910; on_order_fill_voided crates/trading/src/strategy/mod.rs:1663

[NT-2026-09-04-17] [P2] [CLOSED 2026-09-04] Improvement opportunities: orders.md bracket section lacks the pinned OrderFactory::bracket builder usage
  file: skills/nt-trading/references/concepts/orders.md:685
  evidence: bracket is builder-style (crates/trading/src/strategy/api.rs:516); SKILL.md:123 records factory.bracket()...call()
  fix: add bracket example in builder form for Rust lane and labelled Python reference
  acceptance-test: bracket example present in orders.md
  closure: bracket section gained the pinned Rust builder example (order().bracket()...tp_price(...).call() -> Vec<OrderAny>) plus a labelled v1 migration note for the Python factory form
  closure-proof: builder signature at crates/trading/src/strategy/api.rs:516; return type verified against core.rs:1137 test

[NT-2026-09-04-18] [P2] [CLOSED 2026-09-04] Improvement opportunities: portfolio concept doc does not cover PortfolioSnapshot mark-to-market events
  file: skills/nt-signals/references/concepts/portfolio.md:1
  evidence: PortfolioSnapshot (crates/model/src/events/portfolio/snapshot.rs); opt-in streaming via PortfolioConfig.snapshot_interval_ms (crates/portfolio/src/config.rs:88)
  fix: add PortfolioSnapshot section (config + message-bus subscription)
  acceptance-test: section present citing pinned sources
  closure: new Portfolio snapshots section: event semantics vs AccountState, PortfolioConfig equity_curve + snapshot_interval_ms, message-bus topic events.portfolio.{account_id}, build_snapshot/snapshots accessors
  closure-proof: crates/model/src/events/portfolio/snapshot.rs:48 and crates/portfolio/src/config.rs:88 cited

[NT-2026-09-04-19] [P2] [CLOSED 2026-09-04] Improvement opportunities: adapter capability matrix omits four pinned adapter crates (coinbase, derive, lighter, blockchain)
  file: skills/nt-live/references/concepts/rust.md:62
  evidence: 19 adapter crates at pin; matrix lists 15
  fix: add the four rows with pinned v2 status
  acceptance-test: matrix lists 19 adapters
  closure: matrix lists all 19 pinned adapters with a footnote (Blockchain data-only per pin ADAPTERS.md; Blockchain/Derive/Lighter have no v1 predecessor)
  closure-proof: ls pin crates/adapters/ = 19 venues

[NT-2026-09-04-20] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-signals SKILL.md 'Python Indicator Conventions' teaches v1-only indicator authoring in current conventions, unlabelled
  file: skills/nt-signals/SKILL.md:181
  evidence: pin indicators/__init__.pyi: only @typing.final classes; no Indicator base exported; Rust trait Indicator (crates/indicators/src/indicator.rs:28)
  fix: replace section with pointer to Rust authoring (trait + crates/indicators/src/python/) or move under legacy label; delete params_init/_name_not_ratio/handle_partial bullets
  acceptance-test: section no longer teaches v1-only authoring as current
  closure: Python Indicator Conventions replaced by Rust-authoring pointer (Indicator trait + crates/indicators/src/python/ wrappers); retained v1 bullets moved under an explicit legacy label
  closure-proof: grep -c 'params_init\|_name_not_ratio\|handle_partial' skills/nt-signals/SKILL.md = 0; check_legacy_labelling.py reports no nt-signals findings

[NT-2026-09-04-21] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-signals portfolio.md teaches custom portfolio statistics via Python inheritance from dead analysis.statistic module
  file: skills/nt-signals/references/concepts/portfolio.md:114
  evidence: crates/analysis/src/statistic.rs:30 pub trait PortfolioStatistic (calculate_from_realized_pnls :50); python analysis/ has only config.py,reporter.py,tearsheet.py,themes.py
  fix: add the Rust trait as the current custom-statistic path with migration framing for the v1 pattern
  acceptance-test: guide documents Rust PortfolioStatistic trait as current path
  closure: custom-statistics section rewritten around the Rust PortfolioStatistic trait (calculate_from_realized_pnls, register_statistic) with the v1 Python-inheritance pattern labelled legacy
  closure-proof: section cites crates/analysis/src/statistic.rs:30,50 (verified at pin)

[NT-2026-09-04-22] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-signals data.md teaches custom data types via subclassing Python Data; Data is not exported at pin
  file: skills/nt-data/references/concepts/data.md:1535
  evidence: no class Data in any pinned pyi (only DataType); current surface #[custom_data] macro (crates/persistence/macros/src/lib.rs:59) + register_custom_data_class
  fix: point custom-data authoring at #[custom_data(pyo3)]/register_custom_data_class
  acceptance-test: guide shows Rust macro path as current
  closure: custom-data authoring routed to #[custom_data(pyo3)] + register_custom_data_class with requirements; v1 Data-subclassing kept only as labelled note
  closure-proof: crates/persistence/macros/src/lib.rs:59; crates/model/src/python/data/mod.rs:519

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-23] [P0] [CLOSED 2026-09-04] Rust conversion gaps: indicators_guide.md asserts the v1 Cython indicator model and claims both Cython and Rust versions exist
  file: skills/nt-signals/references/guides/indicators_guide.md:14
  evidence: find '*.pyx' at pin = 0; indicators/ is flat PyO3 re-export; Rust impls in crates/indicators/src/{average,momentum,ratio,volatility}
  fix: correct line 365 (Rust + PyO3 bindings only); mark Overview Cython statements as v1 historical
  acceptance-test: guide no longer claims current Cython indicators
  closure: Overview corrected to Rust + PyO3 @typing.final re-exports; Cython/base-class claims marked historical; closing paragraph states Rust+PyO3 is the only implementation
  closure-proof: find pin -name '*.pyx' = 0; guide no longer claims current Cython indicators

[NT-2026-09-04-24] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals SKILL.md Rust conventions name trait methods handle_quote_tick; trait methods are handle_quote/handle_trade
  file: skills/nt-signals/SKILL.md:192
  evidence: crates/indicators/src/indicator.rs:56 fn handle_quote, :60 fn handle_trade
  fix: correct to handle_bar/handle_quote/handle_trade (+ handle_delta/deltas/depth/book where relevant)
  acceptance-test: grep handle_quote_tick in Rust-conventions context returns 0
  closure: Rust conventions bullet now names handle_bar/handle_quote/handle_trade (+ delta/deltas/depth/book)
  closure-proof: matches crates/indicators/src/indicator.rs:56,60,64

[NT-2026-09-04-25] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals SKILL.md teaches nonexistent params_init, _name_not_ratio, handle_partial() as current conventions
  file: skills/nt-signals/SKILL.md:184
  evidence: 0 hits over pin crates/+python/
  fix: delete these bullets; pin exposes name/has_inputs/initialized/reset
  acceptance-test: grep for the three markers in SKILL.md returns 0
  closure: params_init/_name_not_ratio/handle_partial bullets deleted
  closure-proof: grep markers in SKILL.md = 0

[NT-2026-09-04-26] [P1] [CLOSED 2026-09-04] V2 compliance: custom_data_patterns.md calls register_custom_data_class with keyword callbacks; pinned function takes one class argument
  file: skills/nt-signals/references/guides/custom_data_patterns.md:13
  evidence: crates/model/src/python/data/mod.rs:549 register_custom_data_class(data_class); requires to_json/from_json classmethods (:567-571) + encode/decode_record_batch_py
  fix: rewrite example: class with to_json/from_json classmethod + encode/decode_record_batch_py, then register_custom_data_class(MySignal)
  acceptance-test: example matches single-arg pinned signature
  closure: example rewritten to pinned single-arg register_custom_data_class(MySignal) with to_json/from_json classmethod + encode/decode_record_batch_py
  closure-proof: matches crates/model/src/python/data/mod.rs:549,567-571

[NT-2026-09-04-27] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals SKILL.md custom-data contract says to_dict/from_dict callbacks for registration; pin requires to_json/from_json
  file: skills/nt-signals/SKILL.md:210
  evidence: mod.rs:567-571 error strings 'must have from_json(data) class method'
  fix: correct contract wording
  acceptance-test: SKILL.md names to_json/from_json
  closure: custom-data contract now to_json/from_json with single-arg registration
  closure-proof: grep 'to_dict' in SKILL.md custom-data section = 0

[NT-2026-09-04-28] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals SKILL.md stale Python module list (data/aggregation, model/data, model/book are v1 paths)
  file: skills/nt-signals/SKILL.md:52
  evidence: python data/ and model/ flat at pin
  fix: list flat nautilus_trader.{indicators,model,data,analysis}
  acceptance-test: module list matches pinned flat surfaces
  closure: module list flattened to nautilus_trader.{indicators,model,data,analysis}
  closure-proof: no data/aggregation, model/data, model/book paths remain in SKILL.md

[NT-2026-09-04-29] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals api/indicators.md automodules seven nonexistent v1 submodules
  file: skills/nt-signals/references/api/indicators.md:1
  evidence: indicators/ flat at pin; Rust modules crates/indicators/src/{average,momentum,ratio,volatility,book}
  fix: single automodule of flat nautilus_trader.indicators or Rust crate paths
  acceptance-test: no dead submodule directives remain
  closure: seven dead submodule directives replaced by the pinned single flat nautilus_trader.indicators automodule plus crates/indicators/ pointer
  closure-proof: grep 'automodule::' skills/nt-signals/references/api/indicators.md shows only nautilus_trader.indicators

[NT-2026-09-04-30] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals api/analysis.md references dead analysis.analyzer and analysis.statistic modules
  file: skills/nt-signals/references/api/analysis.md:1
  evidence: analysis/ at pin: config.py, reporter.py, tearsheet.py, themes.py; PortfolioAnalyzer is flat pyi class
  fix: flat nautilus_trader.analysis + analysis.reporter only
  acceptance-test: dead directives removed
  closure: dead analyzer/statistic directives removed; page lists flat nautilus_trader.analysis plus config/tearsheet/themes/reporter modules that exist at the pin
  closure-proof: ls pin python/nautilus_trader/analysis/ shows config.py tearsheet.py themes.py reporter.py

[NT-2026-09-04-31] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals api/book.md and api/data.md automodule dead model.book/model.data submodules
  file: skills/nt-signals/references/api/portfolio.md:1
  evidence: model/ flat at pin; book/data types are flat exports
  fix: point at flat nautilus_trader.model
  acceptance-test: dead directives removed
  closure: portfolio.md regenerated to pinned prose + flat nautilus_trader.portfolio automodule; dead portfolio.portfolio/base directives gone (book/data symlinks regenerated in nt-model)
  closure-proof: grep 'portfolio.portfolio\|portfolio.base' skills/nt-signals/references/api/ returns 0

[NT-2026-09-04-32] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals api/portfolio.md automodules dead portfolio.portfolio and portfolio.base
  file: skills/nt-signals/references/api/portfolio.md:1
  evidence: portfolio/ flat at pin (Portfolio, PortfolioConfig only)
  fix: flat nautilus_trader.portfolio only
  acceptance-test: dead directives removed
  closure: closed by the same regeneration as NT-2026-09-04-31
  closure-proof: check-directives.sh DEAD: none

[NT-2026-09-04-33] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals data.md example uses dead v1 imports (TEST_DATA_DIR top-level, adapters.binance.loaders, persistence.wranglers, test_kit)
  file: skills/nt-data/references/concepts/data.md:667
  evidence: TEST_DATA_DIR lives in testkit/providers.py:70; binance python pkg has only instruments.py; wranglers flat in persistence; module is testkit not test_kit
  fix: update to pinned flat imports (nautilus_trader.persistence, nautilus_trader.testkit.providers)
  acceptance-test: imports resolve against pinned tree
  closure: dead v1 imports replaced with pinned flat forms (testkit.providers TEST_DATA_DIR, flat persistence wranglers, load_binance_order_book_deltas)
  closure-proof: imports resolve against pin

[NT-2026-09-04-34] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals data.md uses dead persistence.catalog/config submodule paths and RotationMode
  file: skills/nt-data/references/concepts/data.md:739
  evidence: persistence/ flat + loaders.py; ParquetDataCatalog/StreamingConfig flat exports; RotationMode absent
  fix: flat nautilus_trader.persistence imports; drop RotationMode
  acceptance-test: dead paths gone
  closure: flat persistence imports complete (last catalog import fixed); RotationMode gone
  closure-proof: persistence/ flat at pin

[NT-2026-09-04-35] [P1] [CLOSED 2026-09-04] V2 compliance: nt-signals data.md teaches catalog.write_data(); pin ships typed writers + write_custom_data
  file: skills/nt-data/references/concepts/data.md:561
  evidence: persistence/__init__.pyi:110-166 typed write_* functions, :218 write_custom_data; generic write_data commented out upstream
  fix: replace write_data guidance with typed writers/write_custom_data
  acceptance-test: write_data guidance removed or labelled v1
  closure: write_data replaced with typed writers + write_custom_data; catalog operations use pinned string-name forms
  closure-proof: pyi:110-166,218,246-325

[NT-2026-09-04-36] [P1] [CLOSED 2026-09-04] V2 compliance: nt-dex SKILL.md + rules teach InstrumentProvider.load_all_async()/load_ids_async(); pinned trait is load_all/load_ids/load
  file: skills/nt-dex-adapter/SKILL.md:73
  evidence: crates/common/src/providers.rs:144 load_all(filters), :154 load_ids, :164 load; load_all_async absent from pinned pyi
  fix: rename canonical contract to load_all/load_ids/load with filters parameter
  acceptance-test: grep load_all_async in nt-dex returns 0
  closure: canonical contract renamed to load_all(filters)/load_ids(instrument_ids, filters)/load(instrument_id, filters) across SKILL.md, compliance_checklist.md, dos_and_donts.md
  closure-proof: grep -rn 'load_all_async' skills/nt-dex-adapter --include='*.md' = 0; quarantined .py v1 templates intentionally retain it as labelled migration evidence

[NT-2026-09-04-37] [P1] [CLOSED 2026-09-04] V2 compliance: nt-dex SKILL.md references list cites LiveMarketDataClient/LiveExecutionClient APIs — names absent at pin
  file: skills/nt-dex-adapter/SKILL.md:283
  evidence: pinned bases are nautilus_common::clients::DataClient/ExecutionClient (crates/common/src/clients/); target doc self-identifies as legacy v1 snapshot
  fix: cite current Rust trait bases; label live.md link legacy-v1
  acceptance-test: references cite pinned client bases
  closure: references cite crates/common/src/clients DataClient/ExecutionClient trait bases; live.md link labelled legacy v1 snapshot
  closure-proof: SKILL.md references name the Rust trait files

[NT-2026-09-04-38] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: five nt-signals references/api/*.md files carry v1-only module markers with no legacy banner
  file: skills/nt-signals/references/api/indicators.md:1
  evidence: all submodule paths absent from pinned flat tree; no label in files
  fix: add NT v2 compatibility/legacy banner to each or regenerate
  acceptance-test: each file labelled or regenerated
  closure: closed by regeneration; all five nt-signals api pages v2-accurate, no labelling needed
  closure-proof: check-directives.sh DEAD: none; check_legacy_labelling.py green

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-39] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-signals SKILL.md v1-only markers (params_init, _name_not_ratio, handle_partial, super().__init__(params=...)) outside label window
  file: skills/nt-signals/SKILL.md:184
  evidence: 0 hits at pin; top banner scoped to TradingNode references only
  fix: covered by the v2 fixes above (delete/replace markers)
  acceptance-test: check_legacy_labelling.py green; no unlabelled v1 markers remain
  closure: super().__init__(params=[...]) bullet replaced by truthful Indicator::name()/name property bullet
  closure-proof: grep 'params=[' in SKILL.md = 0

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-40] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-signals concepts/data.md scattered v1-only imports with no labelling (line-1 banner TradingNode-scoped)
  file: skills/nt-data/references/concepts/data.md:667
  evidence: dead-at-pin names as per the v2 findings
  fix: update paths (preferred) or add local legacy notes at each block
  acceptance-test: no unlabelled dead imports remain
  closure: all scattered v1 dead names fixed (flat data import, serialization/model/core ghosts confined to labelled v1 note, data_type string args)
  closure-proof: backtest pyi:76-92; sweep greps clean

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-41] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-dex SKILL.md v1-only load_all_async marker inside current adapter canonical contract, >5 lines from any note
  file: skills/nt-dex-adapter/SKILL.md:73
  evidence: trait methods at pin are load_all/load_ids/load
  fix: covered by the rename fix above
  acceptance-test: grep load_all_async returns 0
  closure: closed by the same rename as NT-2026-09-04-36
  closure-proof: grep load_all_async in nt-dex markdown = 0

[NT-2026-09-04-42] [P2] [CLOSED 2026-09-04] Improvement opportunities: nt-dex never references the upstream nautilus-blockchain crate (canonical EVM/DEX execution slice)
  file: skills/nt-dex-adapter/SKILL.md:123
  evidence: crates/adapters/blockchain/ at pin: rpc/chains/{ethereum,bsc,polygon,arbitrum}, hypersync, contracts, execution/client.rs; repo ships references/integrations/blockchain.md unlinked
  fix: add blockchain crate + integrations/blockchain.md to References and the execution overlay phase
  acceptance-test: SKILL.md cites the blockchain crate and local guide
  closure: execution overlay phase now reuses the nautilus-blockchain crate; References list gained references/integrations/blockchain.md
  closure-proof: crates/adapters/blockchain exists at pin with rpc/chains, hypersync, contracts, execution/

[NT-2026-09-04-43] [P2] [CLOSED 2026-09-04] Improvement opportunities: nt-dex AGENTS.md documents 7-phase sequence while SKILL.md/compliance checklist mandate ten phases
  file: skills/nt-dex-adapter/AGENTS.md:31
  evidence: SKILL.md:3 'official ten-phase'; rules/compliance_checklist.md '10 phases completed in order'
  fix: reconcile AGENTS.md to the ten-phase contract
  acceptance-test: phase counts consistent across the three files
  closure: AGENTS.md now documents the 10-PHASE implementation mirroring SKILL.md phase titles
  closure-proof: grep -n 'PHASE' skills/nt-dex-adapter/AGENTS.md shows ten-phase contract

[NT-2026-09-04-44] [P2] [CLOSED 2026-09-04] Improvement opportunities: MovingAverageFactory (Rust-only at pin) undocumented in any current-V2 section
  file: skills/nt-signals/SKILL.md:88
  evidence: crates/indicators/src/average/mod.rs:82 pub struct MovingAverageFactory; not in Python __all__
  fix: document MovingAverageFactory::create in SKILL.md Rust Usage
  acceptance-test: Rust Usage documents the factory
  closure: Rust Usage documents MovingAverageFactory::create(ma_type, period) with snippet, noted Rust-only
  closure-proof: crates/indicators/src/average/mod.rs:82

[NT-2026-09-04-45] [P2] [CLOSED 2026-09-04] Improvement opportunities: book/candle indicator family shipped at pin not covered in indicator tables
  file: skills/nt-signals/references/guides/indicators_guide.md:24
  evidence: crates/indicators/src/book/: BookImbalanceRatio, CandleBodySize, CandleDirection, CandleSize, CandleWickSize (all in Python __all__)
  fix: add a book/candle indicators row-group
  acceptance-test: tables include the five indicators
  closure: new Book and Candle Descriptors table lists BookImbalanceRatio and the candle family with Rust module paths
  closure-proof: all five names present in guide tables and in pinned indicators __init__.pyi __all__

[NT-2026-09-04-46] [P2] [CLOSED 2026-09-04] Improvement opportunities: tearsheet/theme surface is current v2 Python but SKILL.md frames visualization as migration-only
  file: skills/nt-signals/SKILL.md:1
  evidence: analysis/tearsheet.py: create_tearsheet(:366), create_tearsheet_from_stats(:975), register_chart(:251); Themes.py register_theme(:133)
  fix: document current tearsheet/theme API including custom-chart registry
  acceptance-test: visualization section documents current API
  closure: new Tearsheets and Themes section documents create_tearsheet/create_tearsheet_from_stats/register_chart/get_chart/list_charts/register_theme + TearsheetConfig; nt-dex visualization bullet relabelled current V2 Python
  closure-proof: analysis/tearsheet.py:251-975 and themes.py:94-188 match documented names

[NT-2026-09-04-47] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-backtest api/backtest.md documents v1 Python module layout for the Rust backtest engine, unlabelled
  file: skills/nt-backtest/references/api/backtest.md:1
  evidence: pin backtest/ flat PyO3 (BacktestEngine, BacktestNode, ...); engine is Rust crates/backtest/src/{engine.rs,node.rs,exchange.rs,modules/}; pinned docs/api_reference/backtest.md = single flat automodule
  fix: replace seven submodule directives with pinned single automodule + crates/backtest pointer
  acceptance-test: file matches pinned doc form
  closure: seven submodule directives replaced by the pinned single flat nautilus_trader.backtest automodule plus crates/backtest/ pointer
  closure-proof: grep -c 'automodule' skills/nt-backtest/references/api/backtest.md = 1

[NT-2026-09-04-48] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-data api/cache.md documents removed Python nautilus_trader.cache package, unlabelled
  file: skills/nt-data/references/api/cache.md:1
  evidence: python/nautilus_trader/cache/ absent; cache is crates/common/src/cache/mod.rs exposed as nautilus_trader.common.Cache/CacheConfig (pyi:17,75,284); pinned docs/api_reference/cache.md targets nautilus_trader.common
  fix: rewrite to pinned form (nautilus_trader.common, members Cache/CacheConfig) + Rust cache pointer
  acceptance-test: file matches pinned doc form
  closure: cache.md rewritten to pinned form: automodule nautilus_trader.common members Cache,CacheConfig plus crates/common/src/cache/ pointer
  closure-proof: grep -c 'nautilus_trader.cache' skills/nt-data/references/api/cache.md = 0

[NT-2026-09-04-49] [P1] [CLOSED 2026-09-04] V2 compliance: nt-backtest SKILL.md/guide use nonexistent 'stubs' cargo feature (pin: test-support) and pin crate versions 0.62 (pin workspace 0.63.0)
  file: skills/nt-backtest/SKILL.md:139
  evidence: crates/model/Cargo.toml:34 test-support = ["rstest"]; pinned guide uses features = ["test-support"]; workspace Cargo.toml:52 version = "0.63.0"
  fix: rename feature to test-support; bump versions to 0.63
  acceptance-test: grep '"stubs"' in skill returns 0; versions say 0.63
  closure: feature renamed to test-support in dependency block and feature table; versions bumped to 0.63
  closure-proof: grep '"stubs"' and '"0.62"' in skills = 0; pin Cargo.toml:34,52
  correction: 2026-09-04 - EVIDENCE CORRECTED during closure: the pinned quickstart (docs/how_to/run_rust_live_trading.md:18) pins nautilus-common = "0.62" while the workspace Cargo.toml says 0.63.0; repository policy (tests/test_v2_inventory_pins_versions.py) aligns dependency examples to the quickstart, so the 0.62 dependency pins were intentional. The test-support feature rename stands; the version bump portion of this finding was invalid and the examples were reverted to 0.62.

[NT-2026-09-04-50] [P1] [CLOSED 2026-09-04] V2 compliance: nt-backtest SKILL.md calls write_to_parquet by value; signature takes &[T]
  file: skills/nt-backtest/SKILL.md:230
  evidence: crates/persistence/src/backend/catalog.rs:580-586 write_to_parquet(&self, data: &[T], ...); pinned example node_ema_cross.rs:115 uses &quotes
  fix: catalog.write_to_parquet(&quotes, None, None, None)?
  acceptance-test: example passes reference
  closure: write_to_parquet(&quotes, ...) reference-passing everywhere
  closure-proof: catalog.rs:580-586 signature cited

[NT-2026-09-04-51] [P1] [CLOSED 2026-09-04] V2 compliance: nt-backtest SKILL.md BacktestNode example omits run-config id then looks it up — always fails at pin
  file: skills/nt-backtest/SKILL.md:245
  evidence: BacktestRunConfig.id defaults to random UUID4 (config.rs:1052-1054); get_engine_mut is a plain map lookup (node.rs:117-119); pinned example sets .id(RUN_ID.to_string())
  fix: add .id("ema-cross-run".to_string()) to the builder chain
  acceptance-test: example sets id before lookup
  closure: run config sets .id("ema-cross-run") before get_engine_mut; build() calls carry ? (builders return ConfigResult)
  closure-proof: config.rs:1052,548,836,1084; node.rs:117

[NT-2026-09-04-52] [P1] [CLOSED 2026-09-04] V2 compliance: nt-backtest SKILL.md scope line names nonexistent Python submodules (backtest/models, execution/matching_core)
  file: skills/nt-backtest/SKILL.md:70
  evidence: both packages flat at pin; matching_core is Rust-only crates/execution/src/matching_core.rs
  fix: flat backtest/ + move matching_core to Rust-crates line
  acceptance-test: scope line matches pinned layout
  closure: scope line uses flat backtest package; matching_core moved to the Rust-crates line
  closure-proof: python/nautilus_trader/backtest/ flat at pin

[NT-2026-09-04-53] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data SKILL.md cites stale type CustomDataBatch
  file: skills/nt-data/SKILL.md:121
  evidence: 0 hits at pin; write path is ParquetDataCatalog::write_custom_data_batch(Vec<CustomData>) and PyO3 write_custom_data; CustomData exists
  fix: drop CustomDataBatch; document CustomData + write_custom_data_batch/write_custom_data
  acceptance-test: grep CustomDataBatch returns 0
  closure: CustomDataBatch dropped; CustomData + write_custom_data_batch/write_custom_data documented
  closure-proof: catalog.rs:697; persistence pyi:218

[NT-2026-09-04-54] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data SKILL.md wrangler conventions teach removed v1 DataFrame API as current
  file: skills/nt-data/SKILL.md:150
  evidence: pinned wranglers: __init__(instrument_id, price_precision, size_precision) + process_record_batch_bytes(data: bytes) (persistence pyi:366-373); own serialization_patterns.md documents this correctly
  fix: rewrite section to bytes-based API; link serialization_patterns.md for legacy framing
  acceptance-test: conventions match pinned wrangler signature
  closure: wrangler conventions rewritten to the bytes-based API (instrument_id/price_precision/size_precision + process_record_batch_bytes)
  closure-proof: persistence pyi:366-373

[NT-2026-09-04-55] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data api/data.md automodules dead v1 submodules (aggregation, client, engine, messages)
  file: skills/nt-data/references/api/data.md:1
  evidence: python data/ flat at pin; engine Rust crates/data/src/engine/; pinned doc = single flat automodule
  fix: single flat automodule + Rust pointer
  acceptance-test: file matches pinned doc form
  closure: data.md regenerated to pinned flat automodule plus crates/data/ pointer
  closure-proof: grep 'automodule' skills/nt-data/references/api/data.md shows nautilus_trader.data only

[NT-2026-09-04-56] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data api/persistence.md automodules dead catalog/wranglers/writer submodules
  file: skills/nt-data/references/api/persistence.md:1
  evidence: persistence/ flat + loaders.py at pin; pinned doc = single flat automodule
  fix: single flat automodule + Rust backend pointer
  acceptance-test: file matches pinned doc form
  closure: persistence.md regenerated to pinned flat automodule plus crates/persistence/ pointer
  closure-proof: check-directives.sh DEAD: none

[NT-2026-09-04-57] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data api/serialization.md automodules dead serializer/base submodules
  file: skills/nt-data/references/api/serialization.md:1
  evidence: serialization/ flat at pin; own guide states no public serialization.arrow
  fix: single flat automodule
  acceptance-test: file matches pinned doc form
  closure: serialization.md regenerated to pinned flat automodule
  closure-proof: check-directives.sh DEAD: none

[NT-2026-09-04-58] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data cache_operations.md uses removed cache module paths and ghost types CacheDatabaseFacade/CachePostgresAdapter
  file: skills/nt-data/references/guides/cache_operations.md:7
  evidence: nautilus_trader.cache absent; v2 surface PostgresCacheConfig (infrastructure pyi:19) + crates/infrastructure/src/sql/pg.rs + redis/
  fix: update to nautilus_trader.common (Cache/CacheConfig) + pinned infrastructure backing story
  acceptance-test: no cache.* module paths or ghost types remain
  closure: module paths corrected to nautilus_trader.common; ghost cache types replaced by infrastructure backing stores
  closure-proof: common pyi Cache/CacheConfig; infrastructure pyi:19

[NT-2026-09-04-59] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data cache_operations.md uses v1 accessor names (quote_tick/quote_ticks/counts, index params on mark_price etc., prices(), instruments(underlying=))
  file: skills/nt-data/references/guides/cache_operations.md:76
  evidence: pinned Cache API: quote/quotes/quote_count, trade/trades/trade_count (common pyi:295-344); mark_price/index_price/funding_rate take no index; instruments(venue) has no underlying param
  fix: rename accessors to v2 forms; drop removed params; update CacheConfig example (no database kwarg; save_market_data exists)
  acceptance-test: accessor examples match pinned pyi
  closure: accessors renamed to v2 forms (quote/quotes/quote_count, trade/trades/trade_count); index params dropped; CacheConfig kwargs match pyi
  closure-proof: common pyi:295-344,75-90

[NT-2026-09-04-60] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data tardis.md teaches removed TardisCSVDataLoader class and inverted precision rule
  file: skills/nt-data/references/guides/tardis.md:11
  evidence: TardisCSVDataLoader 0 hits at pin; pinned surface load_tardis_*/stream_tardis_* functions; pinned doc states precisions inferred from CSV when omitted
  fix: replace loader examples with load_tardis_*/stream_tardis_*; correct precision statement
  acceptance-test: grep TardisCSVDataLoader in skill returns 0
  closure: load_tardis_*/stream_tardis_* functions documented; precision-inference corrected (inferred when omitted)
  closure-proof: tardis pyi exports; pinned doc :494-517

[NT-2026-09-04-61] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data test_datasets.md uses wrong fixture paths (tests/test_data/ vs top-level test_data/)
  file: skills/nt-data/references/guides/test_datasets.md:11
  evidence: pinned repo has top-level test_data/ (test_data/large/checksums.json); no tests/test_data/
  fix: replace tests/test_data/ with test_data/
  acceptance-test: grep 'tests/test_data' returns 0
  closure: paths corrected to top-level test_data/
  closure-proof: tests/test_data grep = 0; pin has test_data/large/checksums.json

[NT-2026-09-04-62] [P1] [CLOSED 2026-09-04] V2 compliance: nt-data SKILL.md scope line lists cache/ as a Python module
  file: skills/nt-data/SKILL.md:54
  evidence: python cache/ absent; cache is nautilus_trader.common.Cache
  fix: list data/, persistence/, serialization/, common/ (cache)
  acceptance-test: scope line matches pinned layout
  closure: scope line lists common/ for cache and flat packages
  closure-proof: python cache/ absent at pin

[NT-2026-09-04-63] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: five nt-backtest/nt-data api reference files carry v1-only automodule markers with no legacy label
  file: skills/nt-backtest/references/api/backtest.md:1
  evidence: every directive targets a module absent from the pinned python tree; no label in the files (other .md files in both skills carry banners)
  fix: apply the flat v2 module fixes above (preferred), after which no labelling is needed
  acceptance-test: files regenerated; check_legacy_labelling.py green
  closure: closed by regeneration of all five nt-backtest/nt-data api pages; no labelling needed
  closure-proof: check_legacy_labelling.py green

[NT-2026-09-04-64] [P2] [CLOSED 2026-09-04] Improvement opportunities: simulation modules (FXRolloverInterestModule, CfdSwapModule, SimulationModule trait) uncovered in nt-backtest
  file: skills/nt-backtest/SKILL.md:66
  evidence: crates/backtest/src/modules/: SimulationModule(:262), FXRolloverInterestModule, CfdSwapModule, PythonSimulationModule; PyO3 exports them
  fix: add simulation-modules subsection to SKILL.md Rust Usage (venue config modules field, config.rs:307)
  acceptance-test: subsection present
  closure: simulation-modules subsection added (trait, FX rollover, CFD swap, venue config modules field, Python exposure)
  closure-proof: crates/backtest/src/modules/ cited

[NT-2026-09-04-65] [P2] [CLOSED 2026-09-04] Improvement opportunities: benchmarking guidance predates pinned doc rewrite (CodSpeed, flamegraph, iai correction); benchmarking_review.md is a byte-duplicate
  file: skills/nt-backtest/references/guides/benchmarking.md:3
  evidence: pinned docs/developer_guide/benchmarking.md adds CodSpeed+flamegraph, corrects iai as Cachegrind-based; skill claims hardware counters
  fix: re-snapshot both files from pinned doc; delete or genuinely differentiate benchmarking_review.md
  acceptance-test: guide matches pinned content; duplicate resolved
  closure: guide re-snapshotted byte-identical to the pinned doc; duplicate benchmarking_review.md deleted with no dangling references
  closure-proof: diff clean vs pinned docs/developer_guide/benchmarking.md (366 lines)

[NT-2026-09-04-66] [P2] [CLOSED 2026-09-04] Improvement opportunities: streaming Feather writer with rotation uncovered in nt-data
  file: skills/nt-data/SKILL.md:93
  evidence: StreamingFeatherWriter + StreamingConfig (rotation_mode, max_file_size, ...) in crates/persistence/src/backend/feather.rs:194 + Python pyi:336,377
  fix: add streaming-writer/rotation subsection
  acceptance-test: subsection present
  closure: StreamingFeatherWriter/rotation subsection added with verified rotation ints
  closure-proof: pyi:336-377; python/feather.rs:83,176

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-67] [P2] [CLOSED 2026-09-04] Improvement opportunities: v2 Redis/Postgres cache backing stores uncovered (only stale v1 adapter described)
  file: skills/nt-data/SKILL.md:86
  evidence: nautilus_trader.infrastructure exports PostgresCacheConfig, RedisMessageBusBacking etc. (pyi:19-60); Rust crates/infrastructure/src/{redis,sql}
  fix: add pinned v2 backing-store configuration to cache invariants section
  acceptance-test: section covers infrastructure backing stores
  closure: v2 backing-store configuration documented (infrastructure module + Rust redis/sql)
  closure-proof: infrastructure pyi:19-60; crates/infrastructure/src/{redis,sql}

[NT-2026-09-04-68] [P2] [CLOSED 2026-09-04] Improvement opportunities: user-fetched test-dataset model uncovered; guide predates pinned rewrite
  file: skills/nt-data/references/guides/test_datasets.md:5
  evidence: pinned docs/developer_guide/test_datasets.md:16-39 adds user-fetched model + tightened metadata.json requirements
  fix: re-snapshot guide from pinned doc (also fixes path drift)
  acceptance-test: guide matches pinned doc
  closure: guide re-snapshotted from the pinned doc incl. user-fetched model
  closure-proof: byte-identical to pinned doc (mod banner); doc:16-39

[NT-2026-09-04-69] [P2] [CLOSED 2026-09-04] Improvement opportunities: DeFi backtest feature (cargo defi, Data::Defi handling) uncovered
  file: skills/nt-backtest/SKILL.md:150
  evidence: crates/backtest/Cargo.toml:28 defi feature; engine.rs:443-447 add_data special-cases Data::Defi
  fix: add defi row to feature table + add_data note
  acceptance-test: feature table includes defi
  closure: defi feature row added; add_data guidance notes Data::Defi handling
  closure-proof: crates/backtest/Cargo.toml:28; engine.rs:431-468

[NT-2026-09-04-70] [P2] [CLOSED 2026-09-04] Improvement opportunities: nt-backtest migration_reference dangling internal pointer (templates/legacy_migration/fill_model.py)
  file: skills/nt-backtest/migration_reference/python/python-extension.md:29
  evidence: file actually lives at migration_reference/python/templates/fill_model.py
  fix: correct the pointer
  acceptance-test: pointer resolves
  closure: pointer corrected to migration_reference/python/templates/fill_model.py
  closure-proof: target file exists

[NT-2026-09-04-71] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-architect AGENTS.md teaches adapters as hybrid Rust-core + Python-integration split; adapters are end-to-end Rust crates at pin
  file: skills/nt-architect/AGENTS.md:70
  evidence: crates/adapters/okx/src/: data.rs, execution.rs, factories.rs, providers — full Rust clients; factories implement DataClientFactory/ExecutionClientFactory (crates/common/src/factories/client.rs:57,85); registered via LiveNodeBuilder::add_data_client/add_exec_client (builder.rs:444,485); no Python adapter layer in v2
  fix: rewrite constraint: entire adapter is a Rust crate under crates/adapters/<venue>/; Python only optional bounded PyO3 control-plane projection
  acceptance-test: AGENTS.md no longer claims a Python integration layer for new adapters
  closure: adapter constraint rewritten: entire adapter is an end-to-end Rust crate under crates/adapters/<venue>/; Python at most an optional bounded PyO3 control-plane projection
  closure-proof: pin crates/adapters/okx/src/ full Rust clients; no Python adapter layer at v2

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-72] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-strategy-builder dos_and_donts.md live DO teaches removed Python TradingNodeConfig timeouts
  file: skills/nt-strategy-builder/rules/dos_and_donts.md:115
  evidence: TradingNodeConfig 0 matches in pinned python; same four timeout fields exist in Rust LiveNodeConfig (crates/live/src/node/config.rs:775-784)
  fix: replace with Rust LiveNodeConfig timeout fields; keep v1 snippet only in migration_reference
  acceptance-test: grep TradingNodeConfig in rules/ returns 0 unlabelled
  closure: timeout DO now uses Rust LiveNodeConfig Duration fields; v1 snippet preserved labelled in migration_reference
  closure-proof: grep TradingNodeConfig in rules/ = 0; config.rs:775-784 cited

[NT-2026-09-04-73] [P1] [CLOSED 2026-09-04] V2 compliance: market_exit(instrument_id) signature wrong; v2 market_exit() takes no argument
  file: skills/nt-implement/AGENTS.md:36
  evidence: trading pyi:491 def market_exit(self); Rust crates/trading/src/strategy/mod.rs:1724 fn market_exit(&mut self) (config-driven TIF/reduce-only)
  fix: market_exit() everywhere; drop instrument_id
  acceptance-test: grep 'market_exit(instrument_id)' returns 0
  closure: market_exit() no-arg form everywhere (nt-implement AGENTS, nt-strategy-builder SKILL, templates note)
  closure-proof: grep 'market_exit(instrument_id)' = 0; trading pyi:491

[NT-2026-09-04-74] [P1] [CLOSED 2026-09-04] V2 compliance: nt-implement AGENTS.md teaches InstrumentProvider with v1-only async method names (load_all_async, load_ids_async, load_async)
  file: skills/nt-implement/AGENTS.md:47
  evidence: zero _async-suffixed provider methods at pin; Rust trait InstrumentProvider crates/common/src/providers.rs:130 with load_all(:144)/load_ids(:154); Python InstrumentProvider class gone
  fix: replace rows with the Rust trait methods; move v1 wording to labelled migration material
  acceptance-test: grep load_all_async in nt-implement returns 0 unlabelled
  closure: Required Rust traits replace v1 Python interface list: InstrumentProvider load_all(filters)/load_ids/load; async-suffixed names only inside labelled changelog table
  closure-proof: crates/common/src/providers.rs:144,154 cited

[NT-2026-09-04-75] [P1] [CLOSED 2026-09-04] V2 compliance: nt-implement AGENTS.md cites OrderBook.get_target_px_for_quantity() — nonexistent at pin
  file: skills/nt-implement/AGENTS.md:51
  evidence: grep target_px over pin = only unrelated proptest locals; no such method on OrderBook
  fix: delete row / stop citing as current API
  acceptance-test: grep get_target_px_for_quantity returns 0 unlabelled
  closure: get_target_px_for_quantity row deleted from current tables (historical mention only in labelled legacy_migration)
  closure-proof: zero target_px method matches at pin

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-76] [P1] [CLOSED 2026-09-04] V2 compliance: nt-implement AGENTS.md teaches WS connect() needs loop_=self._loop (v1 Python-adapter-only guidance)
  file: skills/nt-implement/AGENTS.md:50
  evidence: no loop_ param anywhere in pinned pyi; v2 WebSocket clients are Rust
  fix: remove row or mark 'v1 Python adapters only (removed in v2)'
  acceptance-test: no unlabelled loop_ guidance remains
  closure: loop_= row deleted
  closure-proof: no loop_ param in pinned pyi

[NT-2026-09-04-77] [P1] [CLOSED 2026-09-04] V2 compliance: nt-architect AGENTS.md uses self.cache.quote_tick(); v2 cache exposes quote()/quotes()
  file: skills/nt-architect/AGENTS.md:43
  evidence: common pyi:296 def quote(...), :303 def quotes(...)
  fix: update state-management table
  acceptance-test: accessor names match pinned pyi
  closure: state-management table uses cache.quote()/quotes()/bar()
  closure-proof: common pyi:296,303

[NT-2026-09-04-78] [P1] [CLOSED 2026-09-04] V2 compliance: nt-architect AGENTS.md cites v1 Python client class families InstrumentProvider/LiveDataClient/LiveExecutionClient as adapter contract
  file: skills/nt-architect/AGENTS.md:71
  evidence: pinned live pyi exports DataClientConfig/ExecutionClientConfig; v2 contracts are Rust traits InstrumentProvider/DataClient/ExecutionClient
  fix: rename method families to the Rust traits (+ factories)
  acceptance-test: contract cites pinned Rust traits
  closure: adapter contract cites Rust traits InstrumentProvider/DataClient/ExecutionClient + factories via LiveNodeBuilder; v1 class families marked legacy
  closure-proof: crates/common/src/clients/*.rs and factories/client.rs:57-93 cited

[NT-2026-09-04-79] [P1] [CLOSED 2026-09-04] V2 compliance: nt-strategy-builder SKILL.md factory create(loop, name, config, msgbus, cache, clock) is the v1 Python signature
  file: skills/nt-strategy-builder/SKILL.md:141
  evidence: crates/common/src/factories/client.rs:57-64 DataClientFactory::create(name, config, cache: CacheView, clock); :85-93 exec factory create(trader_id, name, config, cache); registered via LiveNodeBuilder
  fix: state v2 trait-object factory contract; keep v1 form only as labelled migration note
  acceptance-test: factory signature matches pinned traits
  closure: factory bullet states v2 trait-object contract with pinned signatures; v1 create(loop,...) only as labelled migration note
  closure-proof: factories/client.rs:57-64,85-93 cited

[NT-2026-09-04-80] [P1] [CLOSED 2026-09-04] V2 compliance: nt-strategy-builder rules cite LiveExecEngineConfig; v2 exports LiveExecutionEngineConfig
  file: skills/nt-strategy-builder/rules/dos_and_donts.md:105
  evidence: live pyi:124 class LiveExecutionEngineConfig; LiveExecEngineConfig 0 hits at pin
  fix: rename class in snippet (import from nautilus_trader.live)
  acceptance-test: grep LiveExecEngineConfig returns 0
  closure: snippet renamed LiveExecutionEngineConfig with verified kwargs
  closure-proof: live pyi:124 + constructor params

[NT-2026-09-04-81] [P1] [CLOSED 2026-09-04] V2 compliance: nt-strategy-builder rules/AGENTS teach FillModel constructor kwargs; base FillModel takes none at pin
  file: skills/nt-strategy-builder/rules/dos_and_donts.md:167
  evidence: execution pyi:152-157 class FillModel def __init__(self); kwargs constructors are DefaultFillModel(:75)/BestPriceFillModel(:35)/ProbabilisticFillModel(:228)
  fix: use DefaultFillModel(...)/variants; note fill models import from nautilus_trader.execution
  acceptance-test: examples use concrete fill model classes
  closure: fill-model examples use DefaultFillModel(prob_fill_on_limit, prob_slippage, ...) from nautilus_trader.execution; base FillModel documented as taking no constructor args
  closure-proof: execution pyi:75,152

[NT-2026-09-04-82] [P1] [CLOSED 2026-09-04] V2 compliance: nt-strategy-builder DEX DON'T subclasses removed LiveExecClientConfig and uses pydantic SecretStr typing
  file: skills/nt-strategy-builder/rules/dos_and_donts.md:285
  evidence: live pyi exports ExecutionClientConfig; zero SecretStr in pinned pyi (adapter configs take plain str | None)
  fix: rename base to ExecutionClientConfig; drop pydantic/SecretStr from v2 snippet (keep don't-log-keys intent)
  acceptance-test: snippet uses pinned config base
  closure: DEX DON'T no longer subclasses LiveExecClientConfig/pydantic SecretStr; v2 = plain-str env-sourced fields on frozen ExecutionClientConfig with Rust-boundary redaction
  closure-proof: live pyi:49 frozen ExecutionClientConfig; zero SecretStr at pin

[NT-2026-09-04-83] [P1] [CLOSED 2026-09-04] V2 compliance: nt-implement custom-simulation recipe imports nautilus_trader.backtest.models and passes fill_model to BacktestEngineConfig
  file: skills/nt-implement/legacy_migration/custom-simulation-models.md:14
  evidence: backtest pyi __all__ has neither FillModel nor MarginModel; BacktestEngineConfig has no fill_model param (:141-175); models attach per-venue via BacktestVenueConfig.fill_model/.margin_model (:331,374); MarginModel only as Rust account types
  fix: correct recipe: import fill models from nautilus_trader.execution, attach via BacktestVenueConfig; mark MarginModelConfig subclassing removed (v2 custom simulation via Rust SimulationModule)
  acceptance-test: recipe compiles against pinned API conceptually; no dead imports
  closure: fill models import from nautilus_trader.execution; DefaultFillModel attached via BacktestVenueConfig(fill_model=...); MarginModelConfig/Python MarginModel subclassing marked removed at v2
  closure-proof: backtest pyi __new__ takes fill_model/margin_model on venue config only

[NT-2026-09-04-84] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-architect AGENTS.md presents removed @customdataclass decorator in production knowledge base with no label within 5 lines
  file: skills/nt-architect/AGENTS.md:34
  evidence: customdataclass 0 matches in pinned python tree; v2 structured data is CustomData (crates/common/src/custom.rs:34) via publish_data
  fix: label row legacy or replace with v2 pattern (CustomData + publish_data)
  acceptance-test: no unlabelled @customdataclass remains
  closure: @customdataclass row replaced with publish_data() + DataType/CustomData payload pattern; decorator marked legacy-only
  closure-proof: trading pyi:495 publish_data; crates/common/src/custom.rs:34

[NT-2026-09-04-85] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-implement AGENTS.md v1.223/v1.224 changelog tables presented as current API knowledge with no adjacent label
  file: skills/nt-implement/AGENTS.md:32
  evidence: block contains markers verified absent at pin (load_all_async family, loop_=, get_target_px_for_quantity); only note is at file line 1
  fix: add legacy/migration note directly above the tables; correct/remove rows absent at pin
  acceptance-test: tables labelled or corrected
  closure: legacy/migration note added directly above the v1.223/v1.224 tables; pin-absent rows deleted
  closure-proof: label within 5 lines of every retained v1 marker

[NT-2026-09-04-86] [P2] [CLOSED 2026-09-04] Improvement opportunities: v2 custom-simulation extension point SimulationModule/SimulationModuleContext not covered
  file: skills/nt-implement/SKILL.md:56
  evidence: crates/backtest/src/modules/mod.rs:262 pub trait SimulationModule; Python exposure crates/backtest/src/python/modules.rs; exports CfdSwapModule/FXRolloverInterestModule/SimulationModule(Context)
  fix: add Rust SimulationModule guidance; note it supersedes v1 FillModel/MarginModel subclassing
  acceptance-test: current custom-simulation path documented
  closure: new current-v2 extension-point paragraph: SimulationModule/SimulationModuleContext (pre_process/process/acknowledge) attached via BacktestVenueConfig(modules=[...]), built-ins CfdSwapModule/FXRolloverInterestModule, supersedes v1 subclassing
  closure-proof: crates/backtest/src/modules/mod.rs:262 + backtest pyi subclassable bases

[NT-2026-09-04-87] [P2] [CLOSED 2026-09-04] Improvement opportunities: LiveNodeBuilder::add_simulated_exec_client paper/sandbox wiring uncovered
  file: skills/nt-strategy-builder-rust/SKILL.md:224
  evidence: crates/live/src/node/builder.rs:527 add_simulated_exec_client; sandbox adapter crates/adapters/sandbox/
  fix: document paper-mode wiring alongside add_strategy
  acceptance-test: paper-mode wiring documented
  closure: paper/sandbox wiring documented: LiveNodeBuilder::add_simulated_exec_client(name, factory, config) alongside add_strategy; strategy-builder paper-mode row names the mechanism
  closure-proof: builder.rs:527 + sandbox example databento_cme.rs:134

[NT-2026-09-04-88] [P2] [CLOSED 2026-09-04] Improvement opportunities: Live node lifecycle control (NodeState, LiveNodeHandle) uncovered
  file: skills/nt-strategy-builder-rust/SKILL.md:224
  evidence: live pyi exports NodeState and LiveNodeHandle; state machine crates/live/src/node/state.rs
  fix: add short paragraph on NodeState transitions + LiveNodeHandle usage
  acceptance-test: lifecycle control documented
  closure: lifecycle bullet documents LiveNode::handle()/LiveNodeHandle (state/is_running/is_stopping/stop) and NodeState transitions Idle->Starting->Running->ShuttingDown->Stopped; poll instead of sleep
  closure-proof: live pyi:377,445,483 + crates/live/src/node/state.rs:44-51

[NT-2026-09-04-89] [P2] [CLOSED 2026-09-04] Improvement opportunities: canonical reference-adapter list drifts from pinned developer guide
  file: skills/nt-implement/SKILL.md:72
  evidence: pinned references/developer_guide/adapters.md:31-38 lists Bybit, OKX, Binance, Kraken, Lighter, Derive — not BitMEX
  fix: align list with pinned guide table
  acceptance-test: list matches pinned guide
  closure: reference-adapter list aligned to pinned guide: Bybit, OKX, Binance, Kraken, Lighter, Derive (BitMEX removed)
  closure-proof: pinned docs/developer_guide/adapters.md reference table

[NT-2026-09-04-90] [P2] [CLOSED 2026-09-04] Improvement opportunities: adapter phase numbering contradicts pinned guide (1-10 vs Phase 0-9) and AGENTS files teach 7-phase
  file: skills/nt-implement/SKILL.md:81
  evidence: pinned guide defines Phase 0 'Define scope' through Phase 9; SKILL.md numbers 1-10; both AGENTS.md teach older 7-phase
  fix: renumber SKILL.md to Phase 0-9; update AGENTS files to same sequence
  acceptance-test: phase numbering consistent with pinned guide
  closure: phase numbering aligned to pinned Phase 0-9 across nt-implement SKILL/AGENTS and nt-architect AGENTS; adjacent 1-4 mentions updated to 0-4
  closure-proof: pinned guide headers Phase 0..Phase 9

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-91] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-live concepts/live.md teaches v1 TradingNodeConfig as the main live config class with no v2 section
  file: skills/nt-adapters/references/concepts/live.md:67
  evidence: TradingNodeConfig 0 matches in pinned python + docs; v2 surface LiveNodeConfig (crates/live/src/node/config.rs:750; live pyi:20)
  fix: replace section with LiveNodeConfig (Rust + builder wiring); move TradingNodeConfig content to migration_reference
  acceptance-test: concepts/live.md config section is LiveNodeConfig-based
  closure: LiveNodeConfig section with builder wiring replaces TradingNodeConfig as the main config story; v1 content labelled
  closure-proof: crates/live/src/node/config.rs:750+ cited

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-92] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-live concepts/cache.md live-cache example keeps TradingNodeConfig; pinned upstream doc for same section uses LiveNodeConfig
  file: skills/nt-live/references/concepts/cache.md:83
  evidence: pinned docs/concepts/cache.md:70-92 uses LiveNodeConfig(cache=CacheConfig(...)); Rust LiveNodeConfig.cache ~config.rs:797
  fix: update example to pinned form
  acceptance-test: example matches pinned doc
  closure: live-cache example updated to LiveNodeConfig(cache=CacheConfig(...)) matching pinned docs/concepts/cache.md:70-92
  closure-proof: example matches pinned doc form; no TradingNodeConfig in current guidance

[NT-2026-09-04-93] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-live teaches cache/msgbus persistence via v1 CacheConfig(database=DatabaseConfig)/MessageBusConfig(database=...); no such fields at pin
  file: skills/nt-adapters/references/concepts/live.md:114
  evidence: crates/common/src/cache/config.rs:36-73 CacheConfig has no database field; DatabaseConfig 0 matches in pinned python; v2 wiring LiveNodeBuilder::with_cache_database_factory (builder.rs:322) + with_external_msgbus_* (builder.rs:404-433)
  fix: rewrite around with_cache_database_factory and MessageBusConfig.external_streams/msgbus factory wiring
  acceptance-test: no DatabaseConfig-based wiring remains as current guidance
  closure: database wiring rewritten to with_cache_database_factory + with_external_msgbus_*; DatabaseConfig blocks labelled
  closure-proof: builder.rs:322,404-433

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-94] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-live capability matrix steers Interactive Brokers users to v1 legacy; pin ships a v2 Rust IB adapter with runnable examples
  file: skills/nt-live/references/concepts/rust.md:73
  evidence: crates/adapters/interactive_brokers/examples/{node_exec_tester,node_data_tester}.rs run with --features examples; full Rust data/execution/gateway modules
  fix: mark IB v2 Rust available; remove IB from v1-only choosing-a-path list
  acceptance-test: matrix + guidance reflect pinned IB crate
  closure: IB matrix row v2 Rust/PyO3 set to available (full pinned crate + runnable examples); IB removed from the v1-only choosing-a-path list
  closure-proof: crates/adapters/interactive_brokers/ exists at pin with examples

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-95] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-live's only deployment guide documents v1 Python TradingNode internals; no LiveNode deployment guidance exists
  file: skills/nt-live/references/guides/deployment_patterns.md:1
  evidence: v1 internals cited are 0-match ghosts (live/cancellation.py, cancel_tasks_with_timeout, RetryManagerPool, add_stream_processor, check_disconnected, _is_built/TradingNodeBuilder); pinned surface LiveNode run/run_async/stop/dispose (live pyi:366-398)
  fix: rewrite around pinned LiveNode lifecycle (run modes, stop/dispose, LiveNodeHandle, TaskGroup cancellation); move v1 internals to migration_reference
  acceptance-test: deployment guide teaches LiveNode lifecycle
  closure: deployment guide rewritten around pinned LiveNode lifecycle (run/run_async/run_with_mode, LiveNodeHandle stop, stop->delay_post_stop->finalize, dispose, TaskGroup cancellation, pinned timeouts, backing wiring); v1 internals moved to new fully-labelled migration_reference/python/deployment-v1-tradingnode.md
  closure-proof: guide cites live pyi:366-398 and node/mod.rs:965-1000; grep unlabelled v1 internals = 0

[NT-2026-09-04-96] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live SKILL.md/guide show OKXExecutionClientConfig with nonexistent trader_id field (deny_unknown_fields makes it fail)
  file: skills/nt-live/SKILL.md:196
  evidence: crates/adapters/okx/src/config.rs:247-296 field list has no trader_id (grep = 0); deny_unknown_fields at :238; pinned example builds exec client without trader_id (trader_id goes to LiveNode::builder)
  fix: delete trader_id field/builder call from both examples
  acceptance-test: examples match pinned config fields
  closure: trader_id dropped from OKXExecutionClientConfig example in SKILL.md and run_rust_live_trading.md
  closure-proof: okx/src/config.rs:247-296 has no trader_id (deny_unknown_fields); example matches node_exec_tester.rs:77-85

[NT-2026-09-04-97] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live cargo dependency examples pin 0.62; pinned workspace is 0.63.0
  file: skills/nt-live/SKILL.md:160
  evidence: pinned Cargo.toml:52 version = "0.63.0"
  fix: bump nautilus-* requirements to 0.63
  acceptance-test: grep '"0.62"' in nt-live returns 0
  closure: all nautilus-* dependency examples bumped to 0.63
  closure-proof: grep '"0.62"' skills/nt-live = 0; pin Cargo.toml:52 = 0.63.0
  correction: 2026-09-04 - EVIDENCE CORRECTED during closure: same quickstart-vs-workspace conflict as NT-2026-09-04-49; nt-live dependency examples reverted to the quickstart-pinned 0.62.

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-98] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live references/api/*.md automodule stubs point at v1 submodule paths (common.actor, core.fsm, live.node, config.*, system.kernel)
  file: skills/nt-live/references/api/common.md:1
  evidence: pinned packages flat; nautilus_trader.system and nautilus_trader.cache do not exist at all; pinned docs use single flat automodules
  fix: regenerate stubs against pinned flat modules or link pinned stubs; drop/redirect api/system.md to kernel types re-exported from live/backtest
  acceptance-test: no dead automodule paths remain
  closure: common/core/config regenerated from pinned pages; system.md became a pointer page (kernel is Rust crates/system/src/kernel.rs surfaced via LiveNode/BacktestNode); live.md target regenerated from pinned live.md
  closure-proof: check-directives.sh DEAD: none

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-99] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live concepts/cache.md imports from dead v1 path nautilus_trader.core.rust.model
  file: skills/nt-live/references/concepts/cache.md:257
  evidence: core/ has only datetime.py; pinned docs/concepts/cache.md:279,291 use from nautilus_trader.model import PriceType/AggregationSource
  fix: change to flat nautilus_trader.model imports
  acceptance-test: grep 'core.rust' in nt-live returns 0 unlabelled
  closure: imports corrected to flat nautilus_trader.model
  closure-proof: grep 'core.rust' in nt-live unlabelled = 0

[NT-2026-09-04-100] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live concepts/logging.md teaches v1 LoggingConfig with log_level/log_colors params; pinned name is LoggerConfig (stdout_level/fileout_level/component_levels/is_colored)
  file: skills/nt-live/references/concepts/logging.md:118
  evidence: common pyi:183-218 class LoggerConfig; LoggingConfig 0 matches at pin; use_tracing exists only on the Rust struct (config.rs:106)
  fix: rename class + params throughout; keep use_tracing guidance Rust-only
  acceptance-test: grep LoggingConfig in nt-live returns 0 unlabelled
  closure: LoggerConfig with stdout_level/fileout_level/component_levels/is_colored + FileWriterConfig fields documented; use_tracing marked Rust-only
  closure-proof: common pyi:183-218 and logging/config.rs:106 cited

[NT-2026-09-04-101] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live logging.md 'using a logger directly' snippet uses wrong module (common.component) and wrong empty init_logging signature
  file: skills/nt-live/references/concepts/logging.md:306
  evidence: init_logging exported from nautilus_trader.common (pyi:50-51) requiring trader_id, instance_id, level_stdout (pyi:1768-1784); pinned doc shows exact call
  fix: replace with pinned snippet (from nautilus_trader.common import init_logging, Logger)
  acceptance-test: snippet matches pinned signature
  closure: direct-logger snippet replaced with pinned init_logging(trader_id, instance_id, level_stdout, ...) form
  closure-proof: common pyi:1768-1784 signature matches

[NT-2026-09-04-102] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live logging.md teaches engine.get_log_guard(); 0 matches at pin
  file: skills/nt-live/references/concepts/logging.md:371
  evidence: pinned logging docs obtain guard from init_logging(...) return value
  fix: replace with log_guard = init_logging(...) pattern
  acceptance-test: grep get_log_guard returns 0
  closure: get_log_guard guidance removed; guards owned internally, standalone via init_logging
  closure-proof: grep get_log_guard in nt-live = 0

[NT-2026-09-04-103] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live teaches graceful_shutdown_on_exception as an exec-engine setting; removed at pin in favor of node-level shutdown_on_error
  file: skills/nt-adapters/references/concepts/live.md:349
  evidence: pinned docs/concepts/live.md:396 'per-engine graceful_shutdown_on_error option has been removed'; LiveNodeConfig.shutdown_on_error (config.rs:765-767)
  fix: delete option from both tables; document LiveNodeConfig.shutdown_on_error
  acceptance-test: guidance points at shutdown_on_error
  closure: graceful_shutdown_on_exception removed with removed-note; shutdown_on_error documented; leftover LiveExecEngineConfig renames in kraken/coinbase docs fixed
  closure-proof: LiveNodeConfig.shutdown_on_error config.rs:765-767

[NT-2026-09-04-104] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live uses stale v1 names LiveExecEngineConfig, LiveExecClientConfig, LiveDataClientConfig
  file: skills/nt-adapters/references/concepts/live.md:86
  evidence: live pyi:16-21 exports LiveExecutionEngineConfig, DataClientConfig, ExecutionClientConfig; v1 names 0 matches
  fix: rename all occurrences to pinned names
  acceptance-test: grep v1 names in nt-live returns 0
  closure: v1 LiveExec* names eliminated across live.md and venue docs
  closure-proof: grep LiveExecEngineConfig/LiveExecClientConfig/LiveDataClientConfig unlabelled = 0

[NT-2026-09-04-105] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live timeout table stale vs pinned LiveNodeConfig defaults + stale field timeout_post_stop (pin: delay_post_stop)
  file: skills/nt-adapters/references/concepts/live.md:104
  evidence: config.rs:775-796: timeout_connection 60s default, timeout_reconciliation 30s, delay_post_stop 10s; builder exposes with_delay_post_stop_secs
  fix: update defaults/names to pinned values
  acceptance-test: table matches pinned config
  closure: timeout table matches pinned defaults (60/30/10/10/10/5s) with delay_post_stop naming; timeout_post_stop explicitly noted absent
  closure-proof: config.rs:767-796 and pyi:253-261

[NT-2026-09-04-106] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live SKILL.md teaches v1 component lifecycle INITIALIZED→RUNNING→STOPPED→DISPOSED; pinned v2 has no INITIALIZED state
  file: skills/nt-live/SKILL.md:121
  evidence: crates/common/src/enums.rs:58-74 ComponentState starts PreInitialized/Ready; pinned architecture docs document PRE_INITIALIZED/READY; skill's own architecture.md:277-332 is correct
  fix: use pinned state machine (PRE_INITIALIZED → READY → RUNNING → STOPPED → DISPOSED, with DEGRADED/FAULTED)
  acceptance-test: SKILL.md lifecycle matches enums.rs
  closure: lifecycle corrected to PRE_INITIALIZED -> READY -> RUNNING -> STOPPED -> DISPOSED (+DEGRADED/FAULTED)
  closure-proof: matches crates/common/src/enums.rs:58-74

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-107] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live environment_setup build instructions reference .pyx/.pxd sources and build.py — none exist at pin
  file: skills/nt-live/references/guides/environment_setup.md:276
  evidence: 0 .pyx/.pxd in pinned repo; 0 build.py; Makefile:320-326 build/build-debug run maturin develop in python/
  fix: replace with pinned flow (make build / make build-debug after .rs/Python changes)
  acceptance-test: no .pyx/build.py references remain unlabelled
  closure: build flow now make build / make build-debug (maturin develop in python/); .pyx/build.py references removed except labelled legacy note
  closure-proof: pin Makefile:320-326

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-108] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live migration reference asserts Python examples may still use nautilus_trader.live.node.TradingNode; module absent at pin
  file: skills/nt-live/migration_reference/python/live-runtime-contract.md:14
  evidence: live/ contains only __init__.py/.pyi; TradingNode 0 matches in pinned python tree
  fix: reword to v1-historical; migrate to LiveNode
  acceptance-test: text no longer presents live.node.TradingNode as usable at pin
  closure: live.node.TradingNode wording corrected to v1-historical (module absent at pinned baseline; migrate to LiveNode)
  closure-proof: pinned live/ ships only __init__.py/.pyi

[NT-2026-09-04-109] [P1] [CLOSED 2026-09-04] V2 compliance: nt-live guide cites pinned baseline d2b62d35a7; the mission pin is 4692bac
  file: skills/nt-live/references/guides/run_rust_live_trading.md:154
  evidence: SKILL.md:37 names pin 4692bac; d2b62d35a7 is an older reviewed tip
  fix: update pin reference to 4692bac
  acceptance-test: guide cites current pin
  closure: pin citation updated to 4692bac35bb11a25eeebb8d7af4d51c55afe53ec
  closure-proof: grep d2b62d35a7 in skill tree = 0

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-110] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-live concepts/cache.md v1-only markers (DatabaseConfig wiring, core.rust.model imports, core.Data inheritance) with no label within 5 lines
  file: skills/nt-live/references/concepts/cache.md:117
  evidence: DatabaseConfig/core.rust.model/core.Data all 0 matches at pin; custom data is common.CustomData
  fix: label blocks or rewrite to pinned equivalents
  acceptance-test: no unlabelled v1 markers remain
  closure: all cache.md v1 markers resolved: DatabaseConfig wiring -> builder-factory wiring, core.rust.model -> flat model, core.Data -> CustomData
  closure-proof: greps for the three marker classes in cache.md unlabelled = 0

[NT-2026-09-04-111] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-live concepts/live.md database-config block unlabelled (DatabaseConfig wiring, types_filter=[QuoteTick, TradeTick])
  file: skills/nt-adapters/references/concepts/live.md:114
  evidence: pinned MessageBusConfig.types_filter is Sequence[str]; no database param
  fix: label or rewrite per pin
  acceptance-test: block labelled or rewritten
  closure: database-config block uses string types_filter per pinned Sequence[str]; v1 blocks labelled
  closure-proof: pinned MessageBusConfig types_filter typing

[NT-2026-09-04-112] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-live concepts/logging.md v1-only markers (log_level, LoggingConfig blocks, common.component import, get_log_guard, use_tracing on Python config) far from labels
  file: skills/nt-live/references/concepts/logging.md:247
  evidence: all names 0 matches at pin (see v2 findings)
  fix: migrate to pinned v2 API (preferred) or add adjacent legacy labels
  acceptance-test: no unlabelled v1 markers remain
  closure: logging v1 markers migrated to pinned names; only one labelled legacy mention remains
  closure-proof: sweep grep LoggingConfig/log_level unlabelled = 0

[NT-2026-09-04-113] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-live deployment_patterns.md v1 internals presented as current guidance (run() internals, cancellation.py, RetryManagerPool, check_disconnected, LiveExecEngineConfig production block)
  file: skills/nt-live/references/guides/deployment_patterns.md:42
  evidence: all symbols 0 matches at pin; production block presents nonexistent config type
  fix: covered by the deployment-guide rewrite (label v1 or replace with LiveNode surface)
  acceptance-test: guide rewritten; no unlabelled v1 internals
  closure: covered by the full deployment-guide rewrite; zero unlabelled v1 internals remain
  closure-proof: grep RetryManagerPool/cancel_tasks_with_timeout/check_disconnected unlabelled = 0

[NT-2026-09-04-114] [P2] [CLOSED 2026-09-04] Improvement opportunities: zero coverage of pinned live task lifecycle API (TaskGroup/TaskSpawner/TaskSlot) in nt-live
  file: skills/nt-live/SKILL.md:21
  evidence: crates/live/src/task.rs: TaskGroup(:104, spawner() :132, begin_shutdown() :159, abort() :164), TaskSpawner(:276), TaskSlot(:442), SharedTaskSlot(:564); grep TaskGroup in nt-live = 0
  fix: add task-lifecycle section (groups, spawners, shutdown generations, abort semantics)
  acceptance-test: section present citing task.rs
  closure: new Live task lifecycle section documents TaskGroup (spawner/begin_shutdown/abort/drain/start_generation), TaskSpawner, TaskSlot/SharedTaskSlot, TaskGroupGuard, timeout_shutdown bound
  closure-proof: task.rs:104-564 cited

[NT-2026-09-04-115] [P2] [CLOSED 2026-09-04] Improvement opportunities: node-level LiveNodeConfig.shutdown_on_error not documented in nt-live
  file: skills/nt-live/SKILL.md:389
  evidence: config.rs:765-767; pinned docs/concepts/live.md:378-396 (trigger cleared/re-armed per run; observes Rust log records)
  fix: cover shutdown_on_error in production-readiness guidance
  acceptance-test: option documented
  closure: shutdown_on_error documented in Production Readiness + deployment guide (normal stop path, cleared/re-armed per run, Rust log records only)
  closure-proof: config.rs:765-767 and docs/concepts/live.md:376-396 cited

[NT-2026-09-04-116] [P2] [CLOSED 2026-09-04] Improvement opportunities: adapter example/capability tables omit four shipped v2 Rust adapters (blockchain, coinbase, derive, lighter)
  file: skills/nt-live/SKILL.md:316
  evidence: examples exist for all four at pin
  fix: add the four adapters to both tables
  acceptance-test: tables list them
  closure: SKILL.md examples table + rust.md matrix list blockchain/coinbase/derive/lighter (+IB in SKILL.md) with pinned example-coverage note; matrix now lists all 19 pinned adapters
  closure-proof: crates/adapters/*/examples/ listings cited

[NT-2026-09-04-117] [P2] [CLOSED 2026-09-04] Improvement opportunities: LiveNodeBuilder wiring surface beyond clients/logging/reconciliation undocumented (engine configs, state persistence, run-mode)
  file: skills/nt-live/SKILL.md:215
  evidence: builder.rs: with_data_engine_config :359, with_risk_engine_config :369, with_exec_engine_config :379, with_msgbus_config :332, with_cache_config :312, with_streaming_config :349; Python with_load_state/with_save_state/with_instance_id; run_with_mode(NodeRunMode) node/mod.rs:977
  fix: extend builder guide with these methods + NodeRunMode note
  acceptance-test: builder surface documented
  closure: new Builder wiring surface section: with_cache_config/with_cache_database_factory/with_msgbus_config/with_streaming_config/with_{data,risk,exec}_engine_config/add_simulated_exec_client, Python builder options, run_with_mode(NodeRunMode)
  closure-proof: builder.rs:312-434, node/mod.rs:977, live pyi:402-439 cited

[NT-2026-09-04-118] [P0] [CLOSED 2026-09-04] Rust conversion gaps: concepts/risk.md teaches a Python RiskEngine runtime API that no longer exists in Python (engine is Rust-only at pin)
  file: references/concepts/risk.md:37
  evidence: crates/risk/src/engine/mod.rs:456 set_max_notional_per_order(instrument_id, Decimal) Rust-only; python risk pyi exposes only FixedRiskSizer/PositionSizer/RiskEngineConfig — no RiskEngine class
  fix: replace Python example with Rust engine call or RiskEngineConfig(max_notional_per_order=...) (pyi:59); add legacy label for retained v1 form
  acceptance-test: page documents pinned surface; file carries v2 banner
  closure: Python risk-engine runtime example replaced with the v2 surface: RiskEngineConfig(max_notional_per_order=...) Python config + Rust engine set_max_notional_per_order(instrument_id, Decimal); v1 form retained only under a Legacy v1 label
  closure-proof: risk pyi:50-67 and crates/risk/src/engine/mod.rs:456 cited

[NT-2026-09-04-119] [P0] [CLOSED 2026-09-04] Rust conversion gaps: entire api_reference is a v1 Python submodule snapshot for Rust-owned subsystems; no Rust/v2 API reference exists
  file: references/api_reference/system.md:1
  evidence: nautilus_trader.system does not exist at pin (kernel is Rust crates/system); trading/ and indicators/ flat; pinned docs/api_reference documents current surfaces
  fix: regenerate pages against pinned v2 flat modules with per-page owning-crate pointers; retain v1 snapshot only as clearly secondary historical reference
  acceptance-test: api_reference targets only modules that exist at pin (or are labelled historical)
  closure: full api_reference sweep: all root, model, and venue pages regenerated from the pin with owning-crate pointers; machine check over all directives reports zero dead targets
  closure-proof: bash /tmp/check-directives.sh -> total_directives=36 DEAD: none

[NT-2026-09-04-120] [P0] [CLOSED 2026-09-04] Rust conversion gaps: concepts guides for actors/strategies teach only v1 handler/subscription names; Rust how-to guides exist upstream but are not surfaced
  file: references/concepts/strategies.md:117
  evidence: pinned docs/concepts/strategies.md:132 on_quote + :271 subscribe_quotes; pinned docs/how_to/write_rust_strategy.md and write_rust_actor.md exist; skill concepts use on_quote_tick/subscribe_quote_ticks (also actors.md:152-153, adapters.md:156,161, backtesting.md:394,421, instruments.md:473)
  fix: update names to pinned v2; add Rust concept sections referencing the pinned how-to guides
  acceptance-test: concept files use v2 names and cite Rust how-tos
  closure: handler lists/tables use v2 names across strategies.md/actors.md; each file gained a Rust strategies/actors section citing the pinned how-to guides
  closure-proof: trading pyi:616-618; docs/how_to/write_rust_{strategy,actor}.md exist at pin

[NT-2026-09-04-121] [P1] [CLOSED 2026-09-04] V2 compliance: nt-learn curriculum dependency versions pinned to 0.62; pinned workspace is 0.63.0
  file: skills/nt-learn/curriculum/09-full-rust-trading.md:28
  evidence: pinned Cargo.toml:52 version = "0.63.0"
  fix: bump version pins to 0.63
  acceptance-test: curriculum Cargo.toml example says 0.63
  closure: all nine crate versions bumped to 0.63
  closure-proof: pin Cargo.toml version = 0.63.0; grep '"0.62"' in nt-learn = 0
  correction: 2026-09-04 - EVIDENCE CORRECTED during closure: same quickstart-vs-workspace conflict as NT-2026-09-04-49; nt-learn curriculum dependency pins reverted to 0.62.

[NT-2026-09-04-122] [P1] [CLOSED 2026-09-04] V2 compliance: nt-learn curriculum teaches nonexistent stubs cargo feature on nautilus-model
  file: skills/nt-learn/curriculum/09-full-rust-trading.md:32
  evidence: crates/model/src/lib.rs:138 pub mod stubs unconditional; Cargo.toml features have test-support, not stubs
  fix: remove features=["stubs"] and the stubs row; stubs available without a flag
  acceptance-test: grep '"stubs"' in nt-learn returns 0
  closure: features=["stubs"] removed from dependency line and feature table; note added that stubs live under test-support gating
  closure-proof: crates/model/src/lib.rs:137-138; grep '"stubs"' in nt-learn = 0

[NT-2026-09-04-123] [P1] [CLOSED 2026-09-04] V2 compliance: nt-learn teaches BacktestEngine::add_venue with legacy multi-arg signature; pinned Rust API takes a single SimulatedVenueConfig
  file: skills/nt-learn/curriculum/09-full-rust-trading.md:217
  evidence: crates/backtest/src/engine.rs:274 add_venue(&mut self, config: SimulatedVenueConfig)
  fix: replace with engine.add_venue(SimulatedVenueConfig {...})?
  acceptance-test: example uses pinned signature
  closure: add_venue example replaced with the single-arg SimulatedVenueConfig::builder() form
  closure-proof: crates/backtest/src/engine.rs:274 + engine_ema_cross.rs:105-113

[NT-2026-09-04-124] [P1] [CLOSED 2026-09-04] V2 compliance: nt-learn misattributes actor framework ownership to nautilus_trading; DataActor lives in nautilus_common at pin
  file: skills/nt-learn/curriculum/03-foundations.md:18
  evidence: crates/common/src/actor/mod.rs:36 re-exports DataActor/DataActorCore from crates/common/src/actor/data_actor.rs; crates/trading has no actor module (re-export only)
  fix: state nautilus_common owns the actor framework; correct both stages
  acceptance-test: both stages state pinned ownership
  closure: both stages state nautilus_common owns the actor framework (crates/common/src/actor) with nautilus_trading owning strategies/exec-algorithms and re-exporting
  closure-proof: crates/common/src/actor/mod.rs vs crates/trading/src/lib.rs:104

[NT-2026-09-04-125] [P1] [CLOSED 2026-09-04] V2 compliance: concepts/strategies.md teaches v1 handler names on_quote_tick/on_trade_tick and subscribe_quote_ticks
  file: references/concepts/strategies.md:117
  evidence: trading pyi:616-618 on_quote/on_trade/on_bar; :715,721 subscribe_quotes/subscribe_trades; on_quote_tick 0 hits in pinned python+docs
  fix: rename handlers/subscriptions to v2 names
  acceptance-test: grep on_quote_tick in concepts returns 0 unlabelled
  closure: on_quote_tick/on_trade_tick/subscribe_quote_ticks replaced with on_quote/on_trade/subscribe_quotes; handler block aligned to the pinned handler list
  closure-proof: grep v1 handler names in references/concepts/ unlabelled = 0; pyi:616-618,715

[NT-2026-09-04-126] [P1] [CLOSED 2026-09-04] V2 compliance: concepts/actors.md subscription table maps v1 names to v1 handlers
  file: references/concepts/actors.md:152
  evidence: pinned docs/concepts/actors.md:386 uses subscribe_quotes() → on_quote()
  fix: update table and prose to v2 names
  acceptance-test: table matches pinned doc
  closure: subscription/request table replaced with the pinned table (subscribe_quotes->on_quote, subscribe_book_depth10->on_book_depth, request_quotes->on_historical_quotes, etc.)
  closure-proof: pinned docs/concepts/actors.md:374-402

[NT-2026-09-04-127] [P1] [CLOSED 2026-09-04] V2 compliance: v1 subscription/handler names in adapters.md, backtesting.md, instruments.md concept files
  file: references/concepts/adapters.md:156
  evidence: same pinned evidence as above
  fix: replace with pinned v2 names
  acceptance-test: grep returns 0 unlabelled v1 names
  closure: v1 subscription/handler names fixed in adapters.md, backtesting.md, instruments.md
  closure-proof: pyi:715,721; grep sweep clean

[NT-2026-09-04-128] [P1] [CLOSED 2026-09-04] V2 compliance: api_reference/model/tick_scheme.md documents removed module layout
  file: references/api_reference/model/tick_scheme.md:1
  evidence: model/ flat at pin; only a tick_scheme config field survives (pyi:296,350); pinned api_reference/model has reports.md instead
  fix: drop page (or reduce to surviving field + Rust pointer); add model/reports.md per pin
  acceptance-test: page matches pinned api_reference set
  closure: tick_scheme pages reduced to the surviving tick_scheme field/property surface plus crates/model/src/instruments/tick_scheme.rs pointer; model/reports.md added per pinned index
  closure-proof: grep -c 'tick_scheme.implementations' references/api_reference/model/tick_scheme.md = 0

[NT-2026-09-04-129] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: concepts/risk.md contains v1-only Python API markers with no legacy/migration label anywhere
  file: references/concepts/risk.md:1
  evidence: zero legacy/migration/NT v2 strings in file; presented as current authored content
  fix: add standard NT v2 compatibility banner; mark Python risk-engine runtime example legacy (covered by the P0 fix)
  acceptance-test: file carries banner and pinned surface
  closure: file now carries the standard NT v2 compatibility banner worded for the Rust-only risk engine
  closure-proof: banner present; risk pyi exposes no RiskEngine class

[NT-2026-09-04-130] [P2] [CLOSED 2026-09-04] Improvement opportunities: concepts/ lacks coverage for 15+ pinned concept topics (orders/, events/, instruments/, data/, backtesting/ subdirs; reconciliation, custom_data, order_book, synthetics, value_types, rust, configuration)
  file: references/concepts/index.md:1
  evidence: pinned docs/concepts/ contains accounting, configuration, continuous_futures, custom_data, dst, event_sourcing, greeks, networking, options, order_book, reconciliation, rust, synthetics, value_types, python + 5 subdirectories
  fix: add concept pages or pointers for high-value pinned topics; index the subdirectories
  acceptance-test: index covers pinned subdirectories or documents the pointer policy
  closure: new pinned-upstream concept topics section indexes the five subdirectories and seven high-value pages with pinned paths and a do-not-paraphrase policy
  closure-proof: pinned docs/concepts/ tree listing cited

[NT-2026-09-04-131] [P2] [CLOSED 2026-09-04] Improvement opportunities: api_reference/adapters missing 6 venue pages present at pin (architect_ax, bitmex, deribit, hyperliquid, kraken, sandbox)
  file: references/api_reference/adapters/index.md:1
  evidence: pinned docs/api_reference/adapters/ has 15 venues; skill has 10
  fix: add the six pages or pointers to pinned pages/owning crates
  acceptance-test: adapter api_reference set matches pin or documents policy
  closure: six venue pages (architect_ax, bitmex, deribit, hyperliquid, kraken, sandbox) added as faithful pinned copies; adapters index toctree matches the pinned 15 venues
  closure-proof: ls references/api_reference/adapters/ = 16 files incl. index.md

[NT-2026-09-04-132] [P2] [CLOSED 2026-09-04] Improvement opportunities: Stage 09 handler table omits many pinned DataActor handlers (on_data/on_signal, on_instrument_close, on_block, DeFi on_pool_*, on_historical_*)
  file: skills/nt-learn/curriculum/09-full-rust-trading.md:277
  evidence: crates/common/src/actor/data_actor.rs: on_data :393, on_signal :403, on_book_depth :453, on_instrument_close :563, on_block :574, on_pool_* :585-629, on_historical_* :652-725
  fix: extend handler table with these families
  acceptance-test: table covers the families
  closure: Stage 09 handler table extended with on_data/on_signal, on_book_depth, on_instrument_close, on_block, five DeFi on_pool_* handlers, eight on_historical_* handlers with feature note
  closure-proof: crates/common/src/actor/data_actor.rs:393-725

[NT-2026-09-04-133] [P2] [CLOSED 2026-09-04] Improvement opportunities: curriculum never cites the pinned Rust how-to guides (write_rust_strategy, write_rust_actor, run_rust_backtest, get_started_lighter)
  file: skills/nt-learn/curriculum/07-live-trading.md:62
  evidence: pinned docs/how_to/ contains all four; grep shows no nt-learn reference
  fix: link write_rust_strategy from Stage 04, write_rust_actor from Stage 06, run_rust_backtest from Stage 05/09
  acceptance-test: checkpoints cite the pinned how-tos
  closure: curriculum now cites write_rust_strategy (Stage 04), run_rust_backtest (Stage 05/09), write_rust_actor (Stage 06)
  closure-proof: all four how-to files exist under pinned docs/how_to/

[NT-2026-09-04-134] [P2] [CLOSED 2026-09-04] Improvement opportunities: migration material never cites pinned upstream MIGRATION_V2.md
  file: skills/nt-learn/migration_reference/python/curriculum/01-setup.md:5
  evidence: MIGRATION_V2.md (796 lines) is the canonical v1→v2 migration guide; grep MIGRATION_V2 in scope = 0
  fix: add MIGRATION_V2.md as authoritative pointer in migration headers and legacy banners
  acceptance-test: MIGRATION_V2.md cited
  closure: all ten migration_reference curriculum headers cite MIGRATION_V2.md at the pinned root as the authoritative migration guide
  closure-proof: 10 MIGRATION_V2 citations; file exists at pinned root

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-135] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations betfair.md routing story inverted: calls pinned upstream Betfair doc 'v1 wiring' though at pin it IS the current Rust-adapter/LiveNode guide
  file: references/integrations/betfair.md:14
  evidence: pinned docs/integrations/betfair.md:7 'implemented in Rust and exposed at nautilus_trader.adapters.betfair'; :20-21 BetfairDataClientFactory/BetfairExecutionClientFactory; :25 LiveNode.builder example
  fix: replace inverted framing: upstream doc is authoritative v2 guidance; sync primary guide to it (or make betfair_v2.md a delta page); delete wrong-commit citations
  acceptance-test: betfair pages no longer dismiss the pinned upstream doc as v1
  closure: framing corrected: pinned upstream Betfair doc (4692bac) is authoritative v2 guidance; wrong-commit citations replaced (8ecab1ce9 for terminal-order-identity)
  closure-proof: betfair.md:5-13 and betfair_v2.md:5-10 cite the pin; pinned docs/integrations/betfair.md:7,20-21 confirm Rust adapter + factories

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-136] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations binance.md overview presents v1 Python component surface as the adapter surface
  file: references/integrations/binance.md:29
  evidence: pinned binance doc:13-14 'implemented in Rust...same public configurations, factories, and data types'; BinanceLiveDataClientFactory/BinanceLiveExecClientFactory 0 hits at pin
  fix: rewrite overview to pinned v2 surface (flat configs/factories/loaders/decoders)
  acceptance-test: overview lists pinned components
  closure: overview lists pinned components (configs/factories/loaders/decoders); v1 factory names 0 hits
  closure-proof: pin binance pyi __all__

[NT-2026-09-04-137] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations architect_ax.md overview omits pinned Rust/PyO3 statement and teaches v1 factory names
  file: references/integrations/architect_ax.md:29
  evidence: pinned doc:12 'implemented in Rust...PyO3 bindings'; :19-20 AxDataClientFactory/AxExecutionClientFactory; v1 names 0 hits
  fix: adopt pinned overview or label list v1
  acceptance-test: overview matches pinned doc
  closure: overview carries the Rust/PyO3 statement and pinned Ax factories
  closure-proof: pin architect_ax pyi:16-20

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-138] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations bitmex.md example sections teach v1 import paths as current (adapters.bitmex.config, core.nautilus_pyo3)
  file: references/integrations/bitmex.md:582
  evidence: pinned doc:595,854-856 use flat from nautilus_trader.adapters.bitmex import BitmexExecutionClientConfig; .config submodule and core.nautilus_pyo3 absent at pin
  fix: flatten imports per pinned doc or add adjacent legacy labels
  acceptance-test: no unlabelled dead import paths remain
  closure: example sections use flat adapters.bitmex imports
  closure-proof: pin bitmex pyi:15-19

[NT-2026-09-04-139] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations coinbase.md teaches config construction via dead PyO3 module core.nautilus_pyo3 as the current method
  file: references/integrations/coinbase.md:705
  evidence: pinned doc:781-783 imports from flat nautilus_trader.adapters.coinbase; core.nautilus_pyo3 0 hits at pin
  fix: replace imports with flat adapter module; correct :46 module-path claim
  acceptance-test: no core.nautilus_pyo3 references remain unlabelled
  closure: core.nautilus_pyo3 replaced by flat adapter imports
  closure-proof: nautilus_pyo3 grep = 0 across the tree

[NT-2026-09-04-140] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations hyperliquid.md teaches removed core.nautilus_pyo3 client surface in current-framed sample
  file: references/integrations/hyperliquid.md:399
  evidence: pinned hyperliquid pyi exports HyperliquidEnvironment flat; core.nautilus_pyo3 absent
  fix: import from nautilus_trader.adapters.hyperliquid or label legacy
  acceptance-test: no unlabelled pyo3-path imports remain
  closure: flat adapters.hyperliquid imports
  closure-proof: pin exports HyperliquidEnvironment flat

[NT-2026-09-04-141] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations lighter.md teaches revoke_lighter_integrator/LighterEnvironment via dead pyo3 path
  file: references/integrations/lighter.md:148
  evidence: pinned doc:256 from nautilus_trader.adapters.lighter import revoke_lighter_integrator
  fix: use flat adapter imports
  acceptance-test: imports match pinned doc
  closure: flat revoke_lighter_integrator/LighterEnvironment imports
  closure-proof: pin lighter pyi:23,147-153

[NT-2026-09-04-142] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations tardis.md teaches removed TardisCSVDataLoader as THE way to load Tardis CSVs, unlabelled
  file: references/integrations/tardis.md:357
  evidence: TardisCSVDataLoader 0 hits in pinned python/crates/docs; pinned surface load_tardis_*/stream_tardis_*/convert_tardis_options_chain_csv (adapters/tardis pyi __all__)
  fix: replace sections with pinned loader/stream API or label legacy v1
  acceptance-test: no unlabelled TardisCSVDataLoader guidance remains
  closure: TardisCSVDataLoader replaced by the pinned load_*/stream_*/convert family
  closure-proof: pin tardis pyi:15-31; TardisCSVDataLoader grep = 0

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-143] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations polymarket.md complete backtest example is unlabelled pure-v1 Python pointing at a nonexistent example file
  file: references/integrations/polymarket.md:1165
  evidence: examples/backtest/polymarket_simple_quoter.py absent at pin; nautilus_trader.examples package absent; EMACrossLongOnly/get_polymarket_instrument_id/model.currencies.pUSD 0 hits; pinned fee path SimulatedVenueConfig::builder().fee_model(...)
  fix: rewrite to pinned v2 or label legacy v1
  acceptance-test: example uses pinned surface or is labelled
  closure: backtest example rewritten with pinned names (PolymarketDataLoader.from_market_slug, PolymarketFeeModel, venue-config fee wiring)
  closure-proof: pin polymarket pyi:370-376 and backtest add_venue fee_model :462

[NT-2026-09-04-144] [P0] [CLOSED 2026-09-04] Rust conversion gaps: root integrations ib.md teaches v1 HistoricInteractiveBrokersClient and Strategy-from-submodule workflows as current
  file: references/integrations/ib.md:633
  evidence: pinned exports HistoricalInteractiveBrokersClient (spelling) flat from nautilus_trader.adapters.interactive_brokers; Strategy flat in nautilus_trader.trading; .historical.client and trading.strategy submodules absent
  fix: use pinned names/imports or label sections legacy v1
  acceptance-test: no unlabelled v1 IB client guidance remains
  closure: HistoricalInteractiveBrokersClient flat import; Strategy from flat nautilus_trader.trading
  closure-proof: pin trading pyi:26; historical section uses pinned-flat imports

[NT-2026-09-04-145] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations overviews teach v1 factory names (*LiveDataClientFactory/*LiveExecClientFactory) across 9 venue files
  file: references/integrations/bybit.md:25
  evidence: every pinned adapter pyi exports {Venue}DataClientFactory/{Venue}ExecutionClientFactory; grep Live*Factory over pin = 0
  fix: rename to pinned factory names in every overview and prose repetition
  acceptance-test: grep LiveExecClientFactory/LiveDataClientFactory in references/integrations returns 0 unlabelled
  closure: v1 factory names eliminated across all venue overviews (ib.md residue completed)
  closure-proof: grep LiveDataClientFactory/LiveExecClientFactory across references/integrations/ = 0

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-146] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations bitmex.md dead v1 module paths (adapters.bitmex.config, core.nautilus_pyo3, model.identifiers, model.enums)
  file: references/integrations/bitmex.md:838
  evidence: pinned doc:152,245,275 flat model imports; no .config submodule or pyo3 path at pin
  fix: flatten all imports
  acceptance-test: imports resolve against pinned tree
  closure: all imports flattened to nautilus_trader.adapters.bitmex / nautilus_trader.model
  closure-proof: classes verified in pin model pyi

[NT-2026-09-04-147] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations databento.md data-loading guidance uses v1 submodule paths (adapters.databento.loaders, model.enums/identifiers/data, persistence.catalog)
  file: references/integrations/databento.md:702
  evidence: pinned DatabentoDataLoader flat from nautilus_trader.adapters.databento; ParquetDataCatalog flat from persistence; model types flat
  fix: flatten imports
  acceptance-test: imports resolve against pinned tree
  closure: DatabentoDataLoader flat import; ParquetDataCatalog from flat persistence
  closure-proof: pin pyi:14,18

[NT-2026-09-04-148] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations deribit.md current samples use adapters.deribit.data, model.data, model.identifiers, core.nautilus_pyo3
  file: references/integrations/deribit.md:355
  evidence: pinned deribit pyi exports DeribitVolatilityIndex/DeribitEnvironment/DeribitProductType flat; no .data submodule
  fix: flatten imports
  acceptance-test: imports resolve against pinned tree
  closure: flat model imports; DeribitVolatilityIndex flat
  closure-proof: pin deribit pyi:23

[NT-2026-09-04-149] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations hyperliquid.md teaches HyperliquidInstrumentProvider as a Python class and .providers/.enums/.constants/.data submodules
  file: references/integrations/hyperliquid.md:244
  evidence: HyperliquidInstrumentProvider 0 hits in pinned pyi and pinned doc; pinned exports HyperliquidProductType/HYPERLIQUID flat
  fix: drop Python provider usage (Rust-internal at pin); flatten imports
  acceptance-test: no phantom provider class remains
  closure: phantom HyperliquidInstrumentProvider removed
  closure-proof: 0 hits; absent from pin pyi

[NT-2026-09-04-150] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations ib.md teaches v1-only symbols (IBMarketDataTypeEnum, IBContract class, IBOrderTags import, new_generic_spread_id, .config/.common/.gateway submodules)
  file: references/integrations/ib.md:1007
  evidence: pinned doc:43 MarketDataType flat; :176-186 load_contracts=[dicts]; IBOrderTags is a string tag prefix; new_generic_spread_id 0 hits; submodules absent
  fix: convert to pinned forms; remove or legacy-label new_generic_spread_id
  acceptance-test: no v1-only symbols remain unlabelled
  closure: IBMarketDataTypeEnum -> MarketDataType; ibg_* kwargs -> host/port/client_id; JSON load_contracts; SIMPLIFIED variant; new_generic_spread_id gone
  closure-proof: pin IB pyi:771-775,100-115,148-161

[NT-2026-09-04-151] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations architect_ax.md teaches AxExecClientConfig — exists in neither v1 nor v2 (pin: AxExecutionClientConfig)
  file: references/integrations/architect_ax.md:347
  evidence: architect_ax pyi:16-20 AxExecutionClientConfig; AxExecClientConfig 0 hits at pin
  fix: rename to AxExecutionClientConfig
  acceptance-test: grep AxExecClientConfig returns 0
  closure: AxExecClientConfig renamed to AxExecutionClientConfig everywhere
  closure-proof: grep AxExecClientConfig = 0; pin ax pyi:19

[NT-2026-09-04-152] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations binance.md teaches from nautilus_trader.core import Data for on_data handler
  file: references/integrations/binance.md:490
  evidence: pinned core __all__ has only helpers — no Data; pinned doc:687-690 uses from nautilus_trader.model import DataType + subscribe_data
  fix: drop Data import; type handler against concrete class per pinned doc
  acceptance-test: no core-Data import remains
  closure: core-Data import dropped; DataType from flat model + subscribe_data per pinned doc
  closure-proof: pin core __all__ has no Data; model pyi:1676

[NT-2026-09-04-153] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations polymarket.md backtest imports model.currencies.pUSD as a currency object
  file: references/integrations/polymarket.md:1177
  evidence: pUSD 0 hits in pinned pyi (Rust-side + doc concept only); model.currencies submodule absent
  fix: remove pUSD import; use instrument currency from loader
  acceptance-test: no pUSD import remains
  closure: model.currencies.pUSD import removed; currency taken from loader.instrument
  closure-proof: pin pyi:388

[NT-2026-09-04-154] [P1] [CLOSED 2026-09-04] V2 compliance: root integrations betfair pages cite wrong baseline commit 8e51f957c (actual terminal-order-identity commit: 8ecab1ce9; repo pin 4692bac)
  file: references/integrations/betfair.md:11
  evidence: git log -1 8e51f957c = 'Restore persistence config re-exports'; grep 'Retain Betfair terminal order identity' = 8ecab1ce9
  fix: re-cite actual pin 4692bac (and 8ecab1ce9 where that landing is meant)
  acceptance-test: citations name correct commits
  closure: citations corrected to pin 4692bac and 8ecab1ce9
  closure-proof: 8e51f957c grep = 0; betfair.md:9,12-13 cite correct commits
  correction: 2026-09-04 - PARTIAL: 8e51f957c is the legitimate reviewed-tip citation for the 2026-08-28 transition (references/upstream-delta-review.json), not a misattributed landing commit; betfair_v2.md retains it as the reviewed-through baseline while feature landings cite 8ecab1ce9 and the pin cites 4692bac. The landing-attribution half of the finding stands corrected.

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-155] [P1] [CLOSED 2026-09-04] V2 compliance: references/AGENTS.md WHERE-TO-LOOK routes live trading under v1 symbol TradingNode
  file: references/AGENTS.md:40
  evidence: pinned docs have 0 TradingNode mentions, 167 LiveNode; docs/concepts/live.md documents LiveNode::run()
  fix: change row key to LiveNode; keep TradingNode only as labelled legacy alias
  acceptance-test: routing key is LiveNode
  closure: WHERE-TO-LOOK routes live trading under LiveNode; TradingNode kept only as an explicitly labelled legacy alias row; structure-tree comment updated
  closure-proof: pinned docs/concepts/live.md has zero TradingNode mentions

[NT-2026-09-04-156] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations architect_ax.md v1 factories + model.identifiers unlabelled
  file: references/integrations/architect_ax.md:29
  evidence: v1 names 0 hits at pin; no note within 5 lines
  fix: label or update to v2 names
  acceptance-test: no unlabelled v1 markers
  closure: closed by the pinned-factory/flat-import sweep; retained v1 blocks labelled within 5 lines
  closure-proof: segment-wide v1-marker grep = 0 unlabelled

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-157] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations binance.md v1 factory names + dead core Data import unlabelled
  file: references/integrations/binance.md:34
  evidence: v1 names 0 hits at pin
  fix: label or rename per pin
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

[NT-2026-09-04-158] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations bitmex.md 9 unlabelled v1-marker clusters
  file: references/integrations/bitmex.md:30
  evidence: dead paths absent from pinned python tree
  fix: label each block or flatten imports
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

[NT-2026-09-04-159] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations bybit.md overview v1 factories + model.data import unlabelled
  file: references/integrations/bybit.md:25
  evidence: DataType flat in model pyi:1676; v1 factory names 0 hits
  fix: label or update
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-160] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations coinbase.md dead core.nautilus_pyo3 path claims unlabelled
  file: references/integrations/coinbase.md:46
  evidence: module absent at pin
  fix: label or correct module path
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

[NT-2026-09-04-161] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations databento.md v1 submodule samples unlabelled
  file: references/integrations/databento.md:170
  evidence: dead submodules absent at pin
  fix: label or flatten
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

[NT-2026-09-04-162] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations deribit.md v1 samples unlabelled
  file: references/integrations/deribit.md:27
  evidence: dead paths absent at pin
  fix: label or flatten
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

[NT-2026-09-04-163] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations dydx.md overview v1 factories unlabelled
  file: references/integrations/dydx.md:94
  evidence: pinned DydxDataClientFactory/DydxExecutionClientFactory
  fix: rename or label
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

[NT-2026-09-04-164] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations hyperliquid.md 5 unlabelled v1 clusters
  file: references/integrations/hyperliquid.md:22
  evidence: dead paths (core.nautilus_pyo3, .providers, .constants, .data, model.data) absent at pin
  fix: label or flatten
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

[NT-2026-09-04-165] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations ib.md ~20 unlabelled v1 clusters
  file: references/integrations/ib.md:66
  evidence: pinned flat surface in adapters/interactive_brokers pyi; Historic*/new_generic_spread_id 0 hits
  fix: label v1 blocks or convert to pinned flat API
  acceptance-test: no unlabelled v1 markers
  closure: whole wiring tail converted to pinned-flat IB imports, pinned factories, host/port/client_id kwargs, TradingMode, LiveNode.builder(...) mirroring pinned examples/live/interactive_brokers/_common.py:415-441
  closure-proof: residual-marker grep = 0

[NT-2026-09-04-166] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations kraken.md overview v1 factories unlabelled
  file: references/integrations/kraken.md:27
  evidence: pinned KrakenDataClientFactory/KrakenExecutionClientFactory
  fix: rename or label
  acceptance-test: no unlabelled v1 markers
  closure: overview factories renamed; leftover adapters.kraken.config import flattened
  closure-proof: pin kraken pyi:15

[NT-2026-09-04-167] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations lighter.md dead pyo3 path unlabelled
  file: references/integrations/lighter.md:148
  evidence: pinned flat import at doc:256
  fix: flatten or label
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

[NT-2026-09-04-168] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations okx.md overview v1 factories unlabelled (file's only cluster)
  file: references/integrations/okx.md:53
  evidence: pinned OKXDataClientFactory/OKXExecutionClientFactory
  fix: rename or label
  acceptance-test: no unlabelled v1 markers
  closure: closed by the same sweep
  closure-proof: same sweep

[NT-2026-09-04-169] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations polymarket.md overview factories, v1 backtest block, helper block unlabelled
  file: references/integrations/polymarket.md:71
  evidence: v1 names + examples package 0 hits at pin
  fix: label or rewrite to pinned surface
  acceptance-test: no unlabelled v1 markers
  closure: component list rewritten to pinned pyi exports; stale pre-V2 banner replaced; v1 config tables legacy-labelled
  closure-proof: pinned polymarket pyi exports verified

[NT-2026-09-04-170] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: root integrations tardis.md TardisCSVDataLoader blocks unlabelled
  file: references/integrations/tardis.md:357
  evidence: TardisCSVDataLoader 0 hits at pin
  fix: label as v1 or replace with pinned loader functions
  acceptance-test: no unlabelled v1 markers
  closure: closed with NT-2026-09-04-142
  closure-proof: same as 142

[NT-2026-09-04-171] [P2] [CLOSED 2026-09-04] Improvement opportunities: root integrations binance.md missing pinned discovery/loading utilities (load_binance_instruments, load_binance_order_book_deltas, get_binance_arrow_schema_map)
  file: references/integrations/binance.md:27
  evidence: all three in pinned binance pyi __all__ and doc overview :27-40
  fix: add section covering standalone discovery and depth-CSV loading
  acceptance-test: utilities documented
  closure: load_binance_instruments/load_binance_order_book_deltas/get_binance_arrow_schema_map covered
  closure-proof: pin binance pyi:42-44

[NT-2026-09-04-172] [P2] [CLOSED 2026-09-04] Improvement opportunities: root integrations tardis.md missing the pinned load_tardis_*/stream_tardis_*/convert_tardis_options_chain_csv family
  file: references/integrations/tardis.md:350
  evidence: pinned adapters/tardis pyi __all__; upstream doc :463-639 documents each
  fix: document current loader/stream API
  acceptance-test: family documented
  closure: full load_*/stream_*/convert coverage with pinned signatures
  closure-proof: convert call kwargs match pin sig :194-203

[NT-2026-09-04-173] [P2] [CLOSED 2026-09-04] Improvement opportunities: root integrations polymarket.md missing pinned Rtds custom data types and PolymarketUpDownEventSlugConfig
  file: references/integrations/polymarket.md:952
  evidence: pinned doc :963-967 (Rtds + DataType subscription) and :1495
  fix: add RTDS subscription and UpDown event-slug sections
  acceptance-test: sections present
  closure: Rtds types and PolymarketUpDownEventSlugConfig covered
  closure-proof: pin polymarket pyi:23-26

[NT-2026-09-04-174] [P2] [CLOSED 2026-09-04] Improvement opportunities: only derive.md shows the v2 LiveNode.builder registration API; every other integration page resolves to v1 wiring
  file: references/integrations/index.md:7
  evidence: pinned LiveNodeBuilder.add_data_client(name, factory, config, routing)/add_exec_client; derive.md:481-486 is the only correct in-repo example
  fix: add shared LiveNode.builder wiring pattern (or per-adapter examples) mirroring derive.md
  acceptance-test: wiring pattern available from the index
  closure: shared LiveNode.builder wiring pattern documented matching pin builder signature; LIGHTER_ROBINHOOD + Blockchain index rows added
  closure-proof: live pyi:425-435; derive.md:481-486 model

[NT-2026-09-04-175] [P2] [CLOSED 2026-09-04] Improvement opportunities: root integrations ib.md missing pinned TradingMode export (gateway trading-mode selection)
  file: references/integrations/ib.md:1550
  evidence: pinned doc:78 from nautilus_trader.adapters.interactive_brokers import TradingMode
  fix: document TradingMode in gateway section
  acceptance-test: TradingMode documented
  closure: TradingMode documented in the gateway section
  closure-proof: pin IB pyi:783-785; pinned doc:78

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-176] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-dev ffi_memory.md teaches legacy *_API Box-wrapper pattern; pinned Rust uses *mut T + Box::into_raw
  file: skills/nt-dev/references/guides/ffi_memory.md:104
  evidence: crates/model/src/ffi/orderbook/book.rs:35-40 orderbook_new -> *mut OrderBook via Box::into_raw; orderbook_drop(book: *mut OrderBook) :51; grep _API( crates/ = 0; pinned docs/developer_guide/ffi.md documents *mut pattern
  fix: replace section + SKILL.md rule 6 with pinned pattern; label OrderBook_API example legacy v1
  acceptance-test: grep '_API' in ffi guidance returns 0 unlabelled
  closure: opaque owning-pointer pattern (*mut T via Box::into_raw, orderbook_new/orderbook_drop) replaces the *_API wrapper section; v1 example retained only inside the labelled Legacy pattern block; SKILL.md rule 6 teaches the pointer pattern
  closure-proof: crates/model/src/ffi/orderbook/book.rs:35-51 cited; zero *_API tokens outside the labelled block

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-177] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-dev/nt-testing testing.md test-layer matrix routes through legacy Cython backtest client
  file: skills/nt-testing/references/guides/testing.md:406
  evidence: crates/backtest/src/data_client.rs is Rust BacktestDataClient; pinned python backtest/ has no .pyx; upstream testing doc drops the layer and contains zero .pyx references
  fix: point layer at crates/backtest/src/data_client.rs or delete row/step as upstream did; update SKILL.md layer list
  acceptance-test: no .pyx backtest-client layer remains
  closure: test-layer matrix rows cite pinned Rust/python test locations; zero .pyx tokens in current guidance
  closure-proof: cited paths exist at pin (crates/data/tests/engine.rs, crates/common/src/actor/tests.rs, python/tests/unit/common/test_actor.py)

[NT-2026-09-04-178] [P1] [CLOSED 2026-09-04] V2 compliance: nt-testing/nt-dev testing.md describes make pytest as v1 root-suite runner; at pin it runs python/tests and root tests/ does not exist
  file: skills/nt-testing/references/guides/testing.md:158
  evidence: Makefile:1304-1308 pytest: build-debug runs cd python && uv run --no-sync pytest tests/; no root tests/ dir
  fix: rewrite section (single suite via make pytest); delete v1 uv invocation
  acceptance-test: guidance matches pinned Makefile
  closure: make pytest framed as the single-suite runner (python/tests via uv, debug extension via build-debug); v1 root-tests framing and uv --new-first invocation deleted
  closure-proof: pin Makefile:1304-1308

[NT-2026-09-04-179] [P1] [CLOSED 2026-09-04] V2 compliance: skills teach nonexistent Make targets (pytest-v2, build-debug-v2, test-performance, test, lint)
  file: skills/nt-testing/references/guides/testing.md:181
  evidence: grep Makefile for those targets = 0; real: pytest(:1304), build-debug(:325), cargo-ci-benches(:1223), check-code, clippy, pre-commit
  fix: replace with real targets; drop make test/make lint block
  acceptance-test: all cited make targets exist in pinned Makefile
  closure: phantom targets deleted; every cited replacement target exists at pin (pytest:1304, build-debug:325, cargo-ci-benches:1223, check-code:433, clippy:503, format:422, pre-commit:427)
  closure-proof: grep pytest-v2/build-debug-v2/test-performance across skills = 0

[NT-2026-09-04-180] [P1] [CLOSED 2026-09-04] V2 compliance: stale Python test path tests/unit_tests/common/test_actor.py
  file: skills/nt-testing/references/guides/testing.md:404
  evidence: pinned path is python/tests/unit/common/test_actor.py; no unit_tests dir
  fix: update all occurrences
  acceptance-test: grep unit_tests returns 0
  closure: test path corrected to python/tests/unit/common/test_actor.py
  closure-proof: grep unit_tests in skills = 0

[NT-2026-09-04-181] [P1] [CLOSED 2026-09-04] V2 compliance: wait_until_async mislabelled 'legacy helper'; it is the current public helper upstream recommends
  file: skills/nt-testing/references/guides/testing.md:286
  evidence: crates/common/src/testing.rs:106 pub async fn wait_until_async; pinned doc:303-306 prefers it
  fix: present as current recommendation
  acceptance-test: framing corrected
  closure: wait_until_async presented as the current recommended helper
  closure-proof: crates/common/src/testing.rs:106 cited

[NT-2026-09-04-182] [P1] [CLOSED 2026-09-04] V2 compliance: nt-dev SKILL.md teaches await eventually(...) — symbol absent at pin
  file: skills/nt-dev/SKILL.md:381
  evidence: grep eventually over pin = 0; only wait_until_async exists
  fix: remove eventually
  acceptance-test: grep 'eventually(' in nt-dev returns 0
  closure: await eventually(...) deleted; wait_until_async alone
  closure-proof: grep 'eventually(' in nt-dev = 0

[NT-2026-09-04-183] [P1] [CLOSED 2026-09-04] V2 compliance: aligned-features table omits arrow and streaming from pinned standard set
  file: skills/nt-dev/references/guides/rust_conventions.md:52
  evidence: Makefile:182 BASE_FEATURES := arrow,ffi,python,high-precision,streaming,defi; scripts/clippy-changed.sh:9 same
  fix: update table and snippets
  acceptance-test: feature sets match pinned Makefile
  closure: feature set updated to arrow,ffi,python,high-precision,streaming,defi in both files
  closure-proof: matches Makefile:182 BASE_FEATURES

[NT-2026-09-04-184] [P1] [CLOSED 2026-09-04] V2 compliance: nt-dev rust_conventions names cargo feature stubs; pin gates stubs/specs behind test-support
  file: skills/nt-dev/references/guides/rust_conventions.md:40
  evidence: crates/model/Cargo.toml:34 test-support; cfg(any(test, feature="test-support")) in events/order/mod.rs:57,59; upstream rust.md:656
  fix: rename both occurrences; drop stubs from feature list
  acceptance-test: grep 'feature = "stubs"' in skills returns 0
  closure: both occurrences renamed to test-support including the cfg gate example
  closure-proof: feature = "stubs" = 0; matches pin convention

[NT-2026-09-04-185] [P1] [CLOSED 2026-09-04] V2 compliance: nt-dev environment_setup references root pyproject.toml/uv.lock and root uv sync; at pin only python/pyproject.toml exists
  file: skills/nt-dev/references/guides/environment_setup.md:61
  evidence: no root pyproject/uv.lock at pin; python/pyproject.toml (2.0.0rc4) and python/uv.lock exist; make sync runs uv sync in python/
  fix: replace with python/ paths or make sync
  acceptance-test: manifest paths match pin
  closure: manifest references corrected to python/pyproject.toml, python/uv.lock, make sync
  closure-proof: no root-manifest references remain

[NT-2026-09-04-186] [P1] [CLOSED 2026-09-04] V2 compliance: exclude-newer cooldown stated as 3 days; pin uses 7 days
  file: skills/nt-dev/references/guides/environment_setup.md:228
  evidence: python/pyproject.toml:69 exclude-newer = "7 days"
  fix: correct to 7 days
  acceptance-test: value matches pin
  closure: cooldown corrected to 7 days
  closure-proof: python/pyproject.toml:69

[NT-2026-09-04-187] [P1] [CLOSED 2026-09-04] V2 compliance: make install-tools list misattributes shared Cargo CLIs to workspace.metadata.tools
  file: skills/nt-dev/references/guides/environment_setup.md:103
  evidence: Cargo.toml:405-412 metadata.tools has cargo-codspeed/fuzz/hawk/machete/cbindgen/flamegraph/lychee; cargo-audit/deny/edit/llvm-cov/nextest/vet + uv pinned in .nautilus-engineering/tools.toml:61-79
  fix: split shared vs local CLI lists with paths
  acceptance-test: attribution matches pin
  closure: attribution split matches pin: shared CLIs from .nautilus-engineering/tools.toml, NautilusTrader CLIs from workspace.metadata.tools
  closure-proof: Cargo.toml:405-412 and tools.toml:61-79 cited

[NT-2026-09-04-188] [P1] [CLOSED 2026-09-04] V2 compliance: releases guidance points at root pyproject.toml; version lives only in python/pyproject.toml
  file: skills/nt-dev/references/guides/releases.md:15
  evidence: grep ^version pyproject.toml python/pyproject.toml = only python/ (2.0.0rc4)
  fix: update all references
  acceptance-test: paths match pin
  closure: all four references corrected to python/pyproject.toml with version 2.0.0rc4 example
  closure-proof: pin python/pyproject.toml:3

[NT-2026-09-04-189] [P1] [CLOSED 2026-09-04] V2 compliance: coding_standards teaches Gitlint which does not exist at pin; commit messages enforced by in-repo script
  file: skills/nt-dev/references/guides/coding_standards.md:116
  evidence: grep gitlint over pin = 0; no .gitlint; .pre-commit-config.yaml:135-144 commit-msg hook runs scripts/ci/check_commit_message.py
  fix: replace with pinned commit-message gate + upstream conventions
  acceptance-test: no gitlint guidance remains
  closure: gitlint section replaced with pinned commit-message conventions and the check_commit_message.py commit-msg gate
  closure-proof: .pre-commit-config.yaml:135-144; content mirrors pinned coding_standards.md:142-203

[NT-2026-09-04-190] [P1] [CLOSED 2026-09-04] V2 compliance: python_conventions teaches TypeVar/Generic[T]; pin requires Python >=3.12 and upstream mandates PEP 695 syntax
  file: skills/nt-dev/references/guides/python_conventions.md:46
  evidence: python/pyproject.toml:25 requires-python >=3.12,<3.15; TypeVar 0 hits in pinned python/; upstream python.md:44 mandates PEP 695
  fix: replace example with PEP 695 syntax
  acceptance-test: no TypeVar-based generic guidance
  closure: PEP 695 type-parameter syntax section replaces TypeVar example
  closure-proof: TypeVar = 0; requires-python >=3.12,<3.15

[NT-2026-09-04-191] [P1] [CLOSED 2026-09-04] V2 compliance: nt-testing api/data_tester_config.md import path nautilus_trader.test_kit.strategies.tester_data does not exist
  file: skills/nt-testing/references/api/data_tester_config.md:5
  evidence: pinned package is testkit/ (no test_kit, no strategies/); testkit pyi exports only DataTesterConfig; DataTester is Rust (crates/testkit/src/testers/data/actor.rs:50)
  fix: Python: from nautilus_trader.testkit import DataTesterConfig; state DataTester is Rust-only, registered via node.add_builtin_actor
  acceptance-test: import paths match pin
  closure: flat testkit import; DataTester stated Rust-only; add_builtin_actor registration documented; instrument_ids documented as defaulting empty
  closure-proof: testkit pyi __all__; crates/testkit/src/testers/data/actor.rs:50; config.rs:51-54

[NT-2026-09-04-192] [P1] [CLOSED 2026-09-04] V2 compliance: nt-testing SKILL.md prohibition cites nonexistent compat root nautilus_trader.core.nautilus_pyo3
  file: skills/nt-testing/SKILL.md:113
  evidence: nautilus_pyo3 0 hits; compiled root at pin is nautilus_trader._libnautilus
  fix: point rule at _libnautilus or drop named path
  acceptance-test: rule names the real root
  closure: prohibition names nautilus_trader._libnautilus as the private compiled root
  closure-proof: live/__init__.py imports _libnautilus at pin

[NT-2026-09-04-193] [P1] [CLOSED 2026-09-04] V2 compliance: rust_conventions makes anyhow::Result the primary pattern; upstream mandates typed Result at library/domain boundaries
  file: skills/nt-dev/references/guides/rust_conventions.md:202
  evidence: docs/developer_guide/rust.md:242-250 error-boundary table; enforced by .pre-commit-hooks/check_anyhow_usage.sh
  fix: replace with boundary table (typed Result for reusable/domain APIs; anyhow for app/adapter orchestration) + import rule
  acceptance-test: guidance matches pinned boundary policy
  closure: error-boundary table matches pinned policy (typed Result library/domain, anyhow app/adapter, CorrectnessResult validation) with the check_anyhow_usage.sh import rule
  closure-proof: mirrors pin docs/developer_guide/rust.md:242-250

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-194] [P1] [CLOSED 2026-09-04] V2 compliance: docs_style example uses stale type TradingNodeConfig
  file: skills/nt-dev/references/guides/docs_style.md:50
  evidence: TradingNodeConfig 0 hits at pin; upstream docs.md:49 uses LiveNodeConfig
  fix: change example type
  acceptance-test: example uses LiveNodeConfig
  closure: example type changed to LiveNodeConfig
  closure-proof: TradingNodeConfig = 0 in docs_style

[NT-2026-09-04-195] [P1] [CLOSED 2026-09-04] V2 compliance: nt-dev SKILL.md core FFI rule cites nonexistent DataFfiCVec example
  file: skills/nt-dev/SKILL.md:431
  evidence: grep DataFfiCVec = 0; only CVec (crates/core/src/ffi/cvec.rs:49)
  fix: drop named example or substitute real pinned wrapper
  acceptance-test: example exists at pin
  closure: DataFfiCVec dropped; CVec is the real pinned type
  closure-proof: crates/core/src/ffi/cvec.rs:49

[NT-2026-09-04-196] [P1] [CLOSED 2026-09-04] V2 compliance: test-dataset paths use tests/test_data/...; pinned data lives in root test_data/ and cited curation suite does not exist
  file: skills/nt-testing/references/guides/test_datasets.md:11
  evidence: pinned root has test_data/ + test_data/large/checksums.json; no tests/ dir; no test_data_curation suite (curation uses scripts/curate-dataset.sh)
  fix: replace paths; delete the nonexistent suite command
  acceptance-test: grep 'tests/test_data' in skills returns 0
  closure: root test_data/ layout, checksums.json, curate-dataset.sh, ensure_test_data_exists; tests/test_data and test_data_curation references gone
  closure-proof: pinned paths verified to exist

[NT-2026-09-04-197] [P1] [CLOSED 2026-09-04] V2 compliance: benchmarking guide says opt into CI benches by editing the cargo-ci-benches recipe; pin uses CI_BENCH_CRATES/CODSPEED_BENCH_TARGETS variables
  file: skills/nt-dev/references/guides/benchmarking.md:59
  evidence: Makefile:1198 CI_BENCH_CRATES, :1203 CODSPEED_BENCH_TARGETS, :1224 recipe iterates the variables; upstream benchmarking.md:54-59
  fix: point at the variables (+ CodSpeed exclusion rules)
  acceptance-test: guidance matches pinned Makefile
  closure: CI bench registration points at CI_BENCH_CRATES/CODSPEED_BENCH_TARGETS variables
  closure-proof: Makefile:1198,1203

[NT-2026-09-04-198] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: testing.md mixed-debugging section teaches v1-only test_kit.debug_helpers.setup_debugging unlabelled
  file: skills/nt-testing/references/guides/testing.md:337
  evidence: setup_debugging/debug_helpers 0 hits at pin; no make build-debug-pyo3 target; upstream uses uv run --no-sync maturin develop --profile debug-pyo3 in python/
  fix: replace with pinned maturin debug-pyo3 workflow or label legacy
  acceptance-test: section matches pinned workflow
  closure: mixed-debugging uses the pinned maturin debug-pyo3 workflow in python/; setup_debugging/debug_helpers gone
  closure-proof: pin docs/developer_guide/testing.md:308-319 pattern

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-199] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: testing.md .pyx token in test-layer matrix outside the 5-line label window
  file: skills/nt-testing/references/guides/testing.md:406
  evidence: nearest note 11 lines above; row target does not exist at pin
  fix: covered by the P0 matrix fix
  acceptance-test: no unlabelled .pyx remains
  closure: closed with NT-2026-09-04-177 (matrix regeneration removed the row)
  closure-proof: zero unlabelled .pyx tokens

[NT-2026-09-04-200] [P2] [CLOSED 2026-09-04] Improvement opportunities: per-adapter fuzz harness (scripts/fuzz-adapter.sh, adapter fuzz features) not covered
  file: skills/nt-dev/references/guides/testing.md:100
  evidence: pinned docs/developer_guide/testing.md:122-127 documents scripts/fuzz-adapter.sh + adapter fuzz features
  fix: add fuzz-adapter.sh invocation and registration pattern
  acceptance-test: fuzz harness documented
  closure: scripts/fuzz-adapter.sh documented with adapter fuzz-feature registration
  closure-proof: script exists at pin; derive fuzz feature verified

[NT-2026-09-04-201] [P2] [CLOSED 2026-09-04] Improvement opportunities: benchmark registration and v1-vs-v2 comparison harness (scripts/benchmark-backtest-versions.py) not covered
  file: skills/nt-dev/references/guides/benchmarking.md:140
  evidence: pinned benchmarking.md:184-240; script exists at pin; CODSPEED_BENCH_TARGETS exclusions documented
  fix: document registration + comparison workflow
  acceptance-test: coverage present
  closure: benchmark-backtest-versions.py comparison workflow covered in guide and SKILL.md
  closure-proof: script exists at pin; covered at guide:217-253

[NT-2026-09-04-202] [P2] [CLOSED 2026-09-04] Improvement opportunities: markdown lint toolchain and shared style baseline not covered
  file: skills/nt-dev/references/guides/docs_style.md:44
  evidence: pinned .markdownlint.jsonc exists; make check-markdown (Makefile:643); docs/developer_guide/markdown_style.md is the shared baseline
  fix: reference markdown_style.md, .markdownlint.jsonc, make check-markdown
  acceptance-test: toolchain referenced
  closure: markdown toolchain referenced: markdown_style.md baseline, make check-markdown, .markdownlint.jsonc
  closure-proof: Makefile:643; files exist at pin

[NT-2026-09-04-203] [P2] [CLOSED 2026-09-04] Improvement opportunities: pinned Rust-guide sections missing (Error boundaries/Panic policy, Runtime ownership, Domain numeric types, check-cbindgen-abi, exclude-newer-package)
  file: skills/nt-dev/references/guides/rust_conventions.md:198
  evidence: docs/developer_guide/rust.md:242-292,341-366,417-430,707-723; make check-cbindgen-abi (Makefile:770); python/pyproject.toml:71
  fix: fold pinned sections into the guides
  acceptance-test: sections present
  closure: all five pinned Rust-guide sections present (panic policy, runtime ownership, domain numeric types, FFI ABI/check-cbindgen-abi, exclude-newer-package)
  closure-proof: Makefile:770; python/pyproject.toml:71; sections cited

[NT-2026-09-04-204] [P2] [CLOSED 2026-09-04] Improvement opportunities: current commit-message conventions and their automated gate not covered (gitlint section stale)
  file: skills/nt-dev/references/guides/coding_standards.md:102
  evidence: docs/developer_guide/coding_standards.md:140-203; enforced by scripts/ci/check_commit_message.py via commit-msg hook
  fix: replace gitlint section with rules + gate
  acceptance-test: covered by the P1 gitlint fix
  closure: closed with NT-2026-09-04-189 (gitlint replacement covers current conventions + gate)
  closure-proof: same as 189

[NT-2026-09-04-205] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-adapters official_adapter_spec task-management section teaches hand-rolled spawn_task()/JoinHandle pattern replaced by TaskGroup/TaskSpawner/TaskSlot
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:1657
  evidence: crates/live/src/task.rs:104,132,151,159,174,276,442; pinned docs/developer_guide/adapters.md:1489-1554 mandates TaskGroup; skill's own SKILL.md:505-548 already teaches the correct model
  fix: rewrite section to ownership table + TaskGroup admission + begin_shutdown/finish_shutdown + TaskSlot for singular loops; delete spawn_task/JoinHandle example
  acceptance-test: spec matches pinned doc and SKILL.md
  closure: task-management section reproduces the pinned ownership table and TaskGroup/begin_shutdown/finish_shutdown/TaskSlot model; hand-rolled spawn_task guidance removed
  closure-proof: spec section mirrors pinned docs/developer_guide/adapters.md:1489-1554

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-206] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-adapters SKILL.md Python Layer Structure teaches v1 per-module Python adapter layout as the build path
  file: skills/nt-adapters/SKILL.md:202
  evidence: every pinned adapters/<venue>/ has only __init__.py (+binance instruments.py); no config.py/factories.py/providers.py anywhere; adapters/_template/ absent; pinned adapters.md:12-14,205-216 states out-of-tree Python adapters are not a defined surface
  fix: replace tree with pinned v2 wiring (crate src/python bindings + PyO3 registry + __init__.py re-export projection); label v1 layout migration-only; drop _template claim
  acceptance-test: SKILL.md layout matches pinned tree
  closure: Python Layer Structure replaced by the pinned v2 wiring (crate src/python bindings + PyO3 registry + flat __init__.py projection; out-of-tree Python adapters not a defined surface)
  closure-proof: pinned adapters/<venue>/ dirs contain only flat __init__ files

[NT-2026-09-04-207] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-adapters spec teaches Pydantic config subclassing in Python for a Rust-owned #[pyclass] config surface
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:2556
  evidence: nautilus_trader.config.DataClientConfig re-exports a frozen PyO3 pyclass (config pyi:18 → live pyi:34), not subclassable; all 18 venue configs are Rust structs with bon::Builder
  fix: replace with Rust config struct + #[pyclass(from_py_object)] + impl_pyo3_config_getters! pattern, or move under v1-labelled lane
  acceptance-test: no Python config subclassing taught as current
  closure: config-subclass section replaced by Rust struct + #[pyclass(from_py_object)] + impl_pyo3_config_getters! pattern; Pydantic block moved under v1-lane note
  closure-proof: macro at crates/core/src/python/mod.rs:36

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-208] [P0] [CLOSED 2026-09-04] Rust conversion gaps: nt-adapters references/api/ tree documents retired v1 Python adapter module surface with no labels
  file: skills/nt-adapters/references/api/adapters/binance.md:1
  evidence: pinned adapters/<venue>/ dirs contain only __init__.py/.pyi; live/ only __init__.py; grep legacy/migration in references/api/ = 0
  fix: regenerate stubs against pinned projections (automodule on nautilus_trader.adapters.<venue> + nautilus_trader.live only) or quarantine with migration-only banner
  acceptance-test: api tree matches pinned projections or is labelled
  closure: all references/api pages byte-identical to pinned docs/api_reference counterparts; automodules target only flat modules
  closure-proof: diff empty vs pin; check-directives.sh DEAD: none

[NT-2026-09-04-209] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters SKILL.md factory trait example uses async_trait/create(name: String) and omits cache/clock/trader_id — drift vs pinned trait
  file: skills/nt-adapters/SKILL.md:370
  evidence: crates/common/src/factories/client.rs:48-60 sync create(name:&str, config, cache: CacheView, clock: Rc<RefCell<dyn Clock>>); :76-91 exec create(trader_id, name, config, cache); reference impl bybit factories.rs:84-107
  fix: rewrite to sync trait with pinned signatures + name()/config_type()
  acceptance-test: example matches pinned traits
  closure: factory example rewritten to the pinned sync trait signatures with name()/config_type()
  closure-proof: crates/common/src/factories/client.rs:48-91

[NT-2026-09-04-210] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters SKILL.md builder call wrong arity/order: add_data_client(data_config, Box::new(factory))
  file: skills/nt-adapters/SKILL.md:397
  evidence: builder.rs:444-448 add_data_client(name: Option<String>, factory: Box<dyn DataClientFactory>, config: Box<dyn ClientConfig>) -> Result<Self>
  fix: add_data_client(None, Box::new(Factory), Box::new(cfg))? (matches SKILL.md:42-45)
  acceptance-test: calls match pinned builder
  closure: builder calls use .add_data_client(None, Box::new(F), Box::new(cfg))?
  closure-proof: builder.rs:444 signature

[NT-2026-09-04-211] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters naming convention {Venue}ExecClientConfig contradicts every pinned venue ({Venue}ExecutionClientConfig)
  file: skills/nt-adapters/SKILL.md:567
  evidence: 17 of 18 pinned adapters use ExecutionClientConfig; grep struct ExecClientConfig = 0
  fix: change convention to {Venue}ExecutionClientConfig
  acceptance-test: convention matches pin
  closure: naming convention corrected to {Venue}ExecutionClientConfig
  closure-proof: grep ExecClientConfig over skill = 0

[NT-2026-09-04-212] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters integrations stale {Venue}ExecClientConfig names in okx/architect_ax/hyperliquid docs
  file: skills/nt-adapters/references/integrations/okx.md:664
  evidence: pinned exports OKXExecutionClientConfig/AxExecutionClientConfig/HyperliquidExecutionClientConfig
  fix: rename each site
  acceptance-test: grep 'ExecClientConfig' returns 0 in nt-adapters integrations
  closure: all stale ExecClientConfig names renamed
  closure-proof: 0 hits in integrations

[NT-2026-09-04-213] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters integrations teach v1 factory names in 11 venue Overview sections (50 mentions)
  file: skills/nt-adapters/references/integrations/binance.md:34
  evidence: grep LiveDataClientFactory/LiveExecClientFactory over pin = 0; pinned names in every projection pyi
  fix: global rename to pinned factory names + LiveNode builder wiring
  acceptance-test: grep v1 factory names in nt-adapters returns 0 unlabelled
  closure: every factory/config symbol in all 17 venue docs verified present in pinned pyi __all__; v1 factory names 0 unlabelled
  closure-proof: per-venue pyi verification

[NT-2026-09-04-214] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters binance.md config tables/examples teach removed v1 fields (key_type, account_type, update_instruments_interval_mins, use_agg_trade_ticks, BinanceAccountType)
  file: skills/nt-adapters/references/integrations/binance.md:671
  evidence: pinned BinanceDataClientConfig fields (crates/adapters/binance/src/config.rs:173-200): product_type, spot_market_data_mode, instrument_refresh_interval_secs, transport_backend...; BinanceAccountType absent (BinanceProductType only)
  fix: replace tables/sections with pinned fields (Product type section)
  acceptance-test: config fields match pinned struct
  closure: config tables match pinned BinanceDataClientConfig fields
  closure-proof: crates/adapters/binance/src/config.rs:160-235

[NT-2026-09-04-215] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters kraken.md config tables teach nonexistent URL/heartbeat fields and plural product_types
  file: skills/nt-adapters/references/integrations/kraken.md:673
  evidence: pinned KrakenDataClientConfig (crates/adapters/kraken/src/config.rs:41-120): product_type singular, base_url, ws_public_url, ws_private_url, ws_l3_url, heartbeat_interval_secs, ws_idle_timeout_ms, timeout_secs, validate_l3_checksum; no .config submodule
  fix: rewrite tables against pinned struct; flat imports
  acceptance-test: fields match pinned struct
  closure: tables match pinned KrakenDataClientConfig
  closure-proof: crates/adapters/kraken/src/config.rs:41-125

[NT-2026-09-04-216] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters okx.md config rows base_url_ws/use_fills_channel/use_spot_cash_position_reports are not pinned fields
  file: skills/nt-adapters/references/integrations/okx.md:901
  evidence: pinned okx configs: base_url_ws_public/business/private; no use_fills_channel/use_spot_cash_position_reports in crate; current rows load_spreads/region/book_stale_* exist
  fix: replace rows with pinned fields
  acceptance-test: fields match pinned structs
  closure: rows match pinned fields (region/load_spreads/book_stale_*); use_fills_channel/use_spot_cash_position_reports gone
  closure-proof: okx config.rs:61,78,99-107

[NT-2026-09-04-217] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters dydx.md base_url_grpc field and environment= kwarg do not exist at pin
  file: skills/nt-adapters/references/integrations/dydx.md:500
  evidence: pinned dydx config.rs:50-59 fields grpc_url/grpc_urls; :269-273 network: DydxNetwork (no environment field)
  fix: use grpc_url/grpc_urls and network=DydxNetwork.Testnet
  acceptance-test: fields match pinned struct
  closure: grpc_url(s)/network=DydxNetwork replace base_url_grpc/environment
  closure-proof: dydx config.rs:52-59,346-350

[NT-2026-09-04-218] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters hyperliquid.md data config passes product_types= — not a pinned field
  file: skills/nt-adapters/references/integrations/hyperliquid.md:267
  evidence: pinned HyperliquidDataClientConfig (config.rs:47-97): private_key, URLs, environment, timeouts, stale_stream_*, transport_backend — no product_types
  fix: remove product_types from examples
  acceptance-test: examples match pinned struct
  closure: product_types occurrences all labelled not-a-pinned-field
  closure-proof: hyperliquid config.rs:47-97 has no product_types

[NT-2026-09-04-219] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters lighter.md exec config lists/builder-uses trader_id and active_markets — not config fields
  file: skills/nt-adapters/references/integrations/lighter.md:582
  evidence: pinned LighterExecutionClientConfig (config.rs:240-288): environment, deployment, venue, account_id, account_index, api_key_index, private_key, URLs, timeouts, slippage/quota fields; trader_id arrives via factory create()
  fix: drop trader_id/active_markets; add pinned fields
  acceptance-test: config matches pinned struct
  closure: trader_id/active_markets labelled migration-only; factory create(trader_id,...) noted
  closure-proof: client.rs:82-87; lighter config.rs:240-288

[NT-2026-09-04-220] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters ib.md connection guidance uses v1 kwargs/paths (ibg_host/ibg_port/ibg_client_id, .config/.gateway imports, request_timeout_secs, IBMarketDataTypeEnum, superseded dockerized_gateway flow)
  file: skills/nt-adapters/references/integrations/ib.md:63
  evidence: pinned InteractiveBrokersDataClientConfig kwargs (pyi:96-112): host, port, client_id, use_regular_trading_hours, market_data_type: MarketDataType, connection_timeout, request_timeout, handle_revised_bars, batch_quotes, instrument_provider, dockerized_gateway; pinned doc: passing non-None dockerized_gateway raises
  fix: rename kwargs to pinned names; package-root imports; document pinned DockerizedIBGateway flow
  acceptance-test: kwargs match pinned pyi
  closure: host/port/client_id kwargs, DockerizedIBGateway flow documented
  closure-proof: pinned IB pyi ctor

[NT-2026-09-04-221] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters ib.md SymbologyMethod.IB_SIMPLIFIED variant and IBContract class (46 uses) do not exist at pin
  file: skills/nt-adapters/references/integrations/ib.md:293
  evidence: pinned variants SIMPLIFIED/RAW (pyi:778-780); IBContract 0 hits; provider loads contracts as JSON Vec<serde_json::Value> (config.rs:231)
  fix: rename variant; replace IBContract examples with load_contracts JSON format
  acceptance-test: no IB_SIMPLIFIED/IBContract remains unlabelled
  closure: IB_SIMPLIFIED gone (SIMPLIFIED/RAW only); IBContract blocks labelled; leftover IB_RAW fixed
  closure-proof: pyi:778-780 variants

[NT-2026-09-04-222] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters databento.md configuration teaches v1 keys (http_gateway, live_gateway, instrument_ids, parent_symbols, timeout_initial_load, mbo_subscriptions_delay)
  file: skills/nt-adapters/references/integrations/databento.md:880
  evidence: pinned DatabentoDataClientConfig (crates/adapters/databento/src/data.rs:105-113): publishers_filepath, venue_dataset_map, use_exchange_as_venue, bars_timestamp_on_close, reconnect_timeout_mins
  fix: regenerate table from pinned struct
  acceptance-test: fields match pinned struct
  closure: tables match pinned DatabentoDataClientConfig keys with verified defaults
  closure-proof: crates/adapters/databento/src/data.rs:105-117,156

[NT-2026-09-04-223] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters polymarket.md config tables list options not on any pinned config (venue, trader_id, ack_timeout_secs, ws_connection_delay_secs, generate_order_history_from_trades, log_raw_ws_messages)
  file: skills/nt-adapters/references/integrations/polymarket.md:226
  evidence: pinned PolymarketExecutionClientConfig (pyi + config.rs): account_id, funder, signature_type, URLs, timeouts, max_retries, heartbeat_enabled, transport_backend, instrument_config; ghost keys 0 hits; no .providers submodule
  fix: regenerate both tables from pinned struct/pyi; flat imports
  acceptance-test: fields match pinned struct
  closure: tables match pinned struct/pyi; ghost keys labelled
  closure-proof: polymarket config pyi verification

[NT-2026-09-04-224] [P1] [CLOSED 2026-09-04] V2 compliance: nt-adapters bybit.md exec rows use_ws_execution_fast/use_http_batch_api/repay_queue_interval_secs/ws_trade_timeout_secs/ws_auth_timeout_secs not pinned; plus Tardis loader/nautilus_pyo3/venu-passphrase drifts
  file: skills/nt-adapters/references/integrations/bybit.md:799
  evidence: pinned bybit configs (config.rs:40-90,210-245) lack the five keys; TardisCSVDataLoader/TardisHttpClient absent; nautilus_pyo3 absent; bybit has no passphrase (okx api_passphrase only)
  fix: drop the five bybit rows (keep auth_timeout_secs/heartbeat_interval_secs/recv_window_ms); replace tardis loaders with functions; flatten all nautilus_pyo3 imports; SKILL.md passphrase note OKX-only
  acceptance-test: grep phantom keys + nautilus_pyo3 in nt-adapters returns 0 unlabelled
  closure: five bybit ghost keys labelled; OKX-only passphrase note in SKILL.md; tardis loader names corrected to load_tardis_depth10_from_snapshot25/5
  closure-proof: bybit config.rs field list; tardis pyi:211-218

[NT-2026-09-04-225] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters venue Overview sections list v1 factory names as current components with no note within 5 lines
  file: skills/nt-adapters/references/integrations/binance.md:34
  evidence: symbols absent from pinned tree; file-top banners >5 lines away
  fix: rename to pinned factories (preferred) or add local notes
  acceptance-test: no unlabelled v1 factory names
  closure: overview sections use pinned factory names
  closure-proof: v1 names 0 unlabelled

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-226] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters nautilus_trader.core.nautilus_pyo3 imports in current-guidance sections
  file: skills/nt-adapters/references/integrations/coinbase.md:46
  evidence: module absent at pin
  fix: rewrite to pinned projection imports; label retained v1 snippets
  acceptance-test: no unlabelled pyo3-path imports
  closure: zero unlabelled nautilus_pyo3 imports
  closure-proof: grep sweep = 0

[NT-2026-09-04-227] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters binance.md Environments examples use nonexistent BinanceAccountType, unlabelled
  file: skills/nt-adapters/references/integrations/binance.md:866
  evidence: no BinanceAccountType in pinned crate/pyi (__all__ has BinanceProductType only)
  fix: replace with BinanceProductType examples or label v1
  acceptance-test: no unlabelled BinanceAccountType
  closure: BinanceAccountType mentions labelled migration-only; tables use BinanceProductType
  closure-proof: pin has BinanceProductType only

[NT-2026-09-04-228] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters kraken.md Configuration tables present v1 fields as current, unlabelled
  file: skills/nt-adapters/references/integrations/kraken.md:673
  evidence: fields absent from pinned config.rs; no note in section
  fix: regenerate table from pinned config (preferred)
  acceptance-test: tables match pinned struct
  closure: tables match pinned struct
  closure-proof: kraken config.rs:41-125

[NT-2026-09-04-229] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters databento.md configuration-parameter rows are v1 keys, unlabelled
  file: skills/nt-adapters/references/integrations/databento.md:921
  evidence: keys absent from pinned data.rs:105-113; nearest label >15 lines above
  fix: prune to pinned keys or add local note
  acceptance-test: tables match pinned struct
  closure: v1 keys pruned/labelled
  closure-proof: pinned keys verified

[NT-2026-09-04-230] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters ib.md v1 kwargs/submodules/IBContract blocks unlabelled
  file: skills/nt-adapters/references/integrations/ib.md:66
  evidence: pinned kwargs host/port/client_id; IBContract absent; first body note at :941 far below
  fix: add local migration notes or convert to pinned guidance
  acceptance-test: no unlabelled v1 blocks
  closure: v1 blocks carry local migration notes
  closure-proof: notes within 5 lines of each block

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-231] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters okx.md TradingNode block imports dead .factories submodule and nautilus_trader.live.node
  file: skills/nt-adapters/references/integrations/okx.md:953
  evidence: okx python pkg flat; live/ exports via __init__ only; notes exist at :948,961 but lines 955-958,995-997 outside window
  fix: add inline notes inside the code block or convert to LiveNode wiring
  acceptance-test: no unlabelled dead imports
  closure: inline notes + LiveNode.builder wiring with pinned factories
  closure-proof: okx wiring matches pin

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-232] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters concepts/adapters.md instrument-discovery example uses v1-only symbols unlabelled
  file: skills/nt-adapters/references/concepts/adapters.md:66
  evidence: binance.common.enums/.futures.providers, get_cached_binance_http_client, BinanceAccountType.USDT_FUTURES, common.component.LiveClock, load_all_async — all 0 hits/mismatched at pin; pinned flat example load_binance_instruments (binance __init__.py:29-31)
  fix: replace with pinned example or label v1
  acceptance-test: example matches pinned surface
  closure: flat load_binance_instruments example
  closure-proof: pinned binance/__init__.py:29-31

[NT-2026-09-04-233] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters official_adapter_spec.md v1 markers outside labelled lanes (load_all_async milestone, nautilus_pyo3 prose, Pydantic config block)
  file: skills/nt-adapters/references/guides/official_adapter_spec.md:130
  evidence: trait is load_all; nautilus_pyo3 absent; DataClientConfig is frozen PyO3; nearest v1-lane note >100 lines above 2556
  fix: add NT v2 notes within 5 lines of each site
  acceptance-test: no unlabelled v1 markers
  closure: NT v2 notes within 5 lines of load_all milestone, nautilus_pyo3 prose, and config pattern
  closure-proof: notes at spec :129,:173,:1999,:2593

[NT-2026-09-04-234] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters SKILL.md scope/layout claims unlabelled (adapters/_template/, config.py/factories.py/providers.py layout, ExecClientConfig naming)
  file: skills/nt-adapters/SKILL.md:85
  evidence: _template and per-module files absent at pin; 17/18 venues use ExecutionClientConfig
  fix: covered by the P0 layout fix + naming fix
  acceptance-test: SKILL.md layout matches pinned tree
  closure: subsumed by the layout/naming fixes; _template and per-module claims gone
  closure-proof: SKILL.md layout matches pinned tree

NT v2 compatibility note: quoted legacy v1/Cython/`TradingNode` tokens are historical finding evidence (migration reference only).
[NT-2026-09-04-235] [P1] [CLOSED 2026-09-04] Legacy unlabelled content: nt-adapters bybit options README documents a v1-only example script as a current runnable path, whole file unlabelled
  file: skills/nt-adapters/references/examples/bybit/README_options_data_collector.md:35
  evidence: no bybit_options_data_collector.py or BybitOptionsDataCollectorConfig at pin; pinned Rust options examples exist (node_option_chain.rs, node_greeks.rs)
  fix: add migration-only banner pointing at pinned Rust options examples or replace README
  acceptance-test: README labelled or replaced
  closure: migration banner points at pinned Rust options examples
  closure-proof: crates/adapters/bybit/examples/ contains node_option_chain.rs + node_greeks.rs

[NT-2026-09-04-236] [P2] [CLOSED 2026-09-04] Improvement opportunities: nt-adapters sandbox adapter has zero coverage although the skill ships its example
  file: skills/nt-adapters/references/integrations/index.md:9
  evidence: crates/adapters/sandbox/ (SandboxExecutionClientConfig config.rs:45) with examples/databento_cme.rs; skill ships references/examples/rust_adapters/sandbox/databento_cme.rs undocumented
  fix: add short sandbox.md integration guide + index/venue-list rows
  acceptance-test: sandbox documented
  closure: sandbox.md guide added matching pinned SandboxExecutionClientConfig; index + SKILL.md rows
  closure-proof: config.rs:45-135

[NT-2026-09-04-237] [P2] [CLOSED 2026-09-04] Improvement opportunities: Lighter-on-Robinhood deployment absent from lighter guide and index
  file: skills/nt-adapters/references/integrations/lighter.md:1
  evidence: pinned LighterDeployment::{Lighter,Robinhood} (common/enums.rs:60-66); pinned index.md:24,32 LIGHTER_ROBINHOOD with registration caveat
  fix: document deployment/venue fields + Robinhood caveat; add index row
  acceptance-test: deployment documented
  closure: deployment/venue rows + index LIGHTER_ROBINHOOD row + registration caveat + LiveNode.builder wiring
  closure-proof: LighterDeployment pyi:142-144

[NT-2026-09-04-238] [P2] [CLOSED 2026-09-04] Improvement opportunities: nt-adapters integration index and SKILL.md venue lists omit Blockchain (and sandbox)
  file: skills/nt-adapters/references/integrations/index.md:9
  evidence: pinned index lists Blockchain; skill's own blockchain.md exists
  fix: add rows
  acceptance-test: index lists blockchain
  closure: Blockchain + Sandbox index rows and SKILL.md venue-list entries
  closure-proof: pinned index lists Blockchain

[NT-2026-09-04-239] [P2] [CLOSED 2026-09-04] Improvement opportunities: current pinned config fields absent from nt-adapters venue docs (binance transport_backend, okx region/load_spreads/book_stale_*, polymarket resolve_poll_*/RTDS, kraken ws_idle_timeout_ms)
  file: skills/nt-adapters/references/integrations/binance.md:671
  evidence: greps of the four files for the pinned fields all empty; fields exist in pinned config structs
  fix: add the pinned fields to the tables
  acceptance-test: tables include pinned fields
  closure: missing pinned fields added (binance transport_backend, okx region/load_spreads/book_stale_*, polymarket resolve_poll_*/base_url_rtds, kraken ws_idle_timeout_ms)
  closure-proof: fields verified in pinned structs/pyi

[NT-2026-09-04-240] [P2] [CLOSED 2026-09-04] Improvement opportunities: derive.md-style LiveNode.builder wiring absent from nt-adapters venue docs (only derive.md correct, in root integrations)
  file: skills/nt-adapters/references/integrations/derive.md:1
  evidence: pinned per-adapter docs show LiveNode wiring; derive.md:481-486 is the model
  fix: adopt the shared LiveNode.builder pattern in venue wiring sections
  acceptance-test: wiring sections use LiveNode.builder
  closure: verified LiveNode.builder wiring added across venue docs + Rust LiveNode::builder in betfair_v2 citing pinned node_data_tester example
  closure-proof: every factory/config/enum checked against pyi

[NT-2026-09-04-241] [P1] [CLOSED 2026-09-04] V2 compliance: instrument_types.md teaches phantom instrument-class set constants and marks lot_size as required
  file: skills/nt-model/references/guides/instrument_types.md:359
  evidence: EXPIRING_INSTRUMENT_CLASSES/ENGINE_EXPIRING_INSTRUMENT_CLASSES/NEGATIVE_PRICE_INSTRUMENT_CLASSES have 0 hits in the pinned python/ and crates/ trees; pinned lot_size property returns Quantity | None (model/__init__.pyi:304) so it is optional
  fix: replace the Expiring Instruments section with the pinned activation_ns/expiration_ns story and the Rust instruments module pointer; mark lot_size optional with the pyi citation
  acceptance-test: grep EXPIRING_INSTRUMENT_CLASSES in the guide returns 0
  closure: discovered and corrected during the NT-2026-09-04-08/11 segment verification
  closure-proof: grep -c 'EXPIRING_INSTRUMENT_CLASSES' skills/nt-model/references/guides/instrument_types.md = 0; lot_size documented as optional citing pyi:304
## Current audit result

[NT-2026-08-30-02] [P1] [CLOSED 2026-08-30] G2 evidence health: refreshing the reviewed upstream delta changed owned-content hashes through shared reference symlinks, leaving durable evidence stale for `nt-architect`, `nt-implement`, and `nt-review`.
  file: references/upstream-delta-review.json:5; references/g2-evidence/nt-architect.json:2; references/g2-evidence/nt-implement.json:2; references/g2-evidence/nt-review.json:2
  evidence: Phase 2 re-executed all three affected G2 harnesses against a disposable writable checkout of pinned commit `81eedc7cea29a52c0568f0bfbafd190c2bebe74f`; every repository and Cargo step returned 0.
  fix: refreshed the three durable JSON evidence files with current owned-content hashes and fresh successful execution metadata.
  acceptance-test: `python3 tools/check_skill_g2_harnesses.py --check-cards` exits 0; `python3 -m pytest -q tests/test_skill_g2_harnesses.py tests/test_progressive_gate_cards.py` reports 57 passed.
  closure: validated Phase 2 receipt `docs/tracking/receipts/harden-nt-v2-20260830/phase-2-g2-evidence-refreshed.json`; the disposable upstream worktree is clean at the pinned commit.

NT v2 compatibility note: the 2026-09-02 source audit reviewed 61 new develop commits and the full in-scope skill tree; all Cython and v1 mentions below describe migration/reference-only content:

- P0 Rust conversion gaps: 0
- P1 V2 API, symbol, and import violations: 5 (NT-2026-09-02-01, -02, -03, -04, -05)
- P1 unlabelled migration/reference-only Cython or v1 content: 2 (NT-2026-09-02-11, -12)
- P2 current-upstream coverage opportunities requiring a repository change: 3 (NT-2026-09-02-06, -07, -08)

Mission-infrastructure findings outside the four audit categories: NT-2026-09-02-09 (G2 evidence health, P1) and NT-2026-09-02-10 (pinned-baseline currency, P2).

## Open findings

[NT-2026-09-02-01] [P1] [CLOSED 2026-09-02] V2 compliance: nt-live guidance states Python can register only bundled Rust examples; develop `5d5c21e24` adds `LiveNode.add_actor` registration for constructed Python actor instances.
  file: skills/nt-live/references/concepts/rust.md:224
  evidence: pinned `81eedc7c` `crates/live/src/python/node.rs` lacks instance registration; develop `5d5c21e24abb5bf321b35835a43a3091c9195f88` adds `add_actor`, exposed in `python/nautilus_trader/live/__init__.pyi`; the obsolete restriction repeats at `skills/nt-live/references/concepts/rust.md:245` and `:260`.
  fix: replace the restriction with guidance distinguishing constructed Python actor instances via `node.add_actor(actor)` from feature-gated built-ins via `add_builtin_actor(type_name, config)`; retain the bundled-examples limitation only for the built-in methods.
  acceptance-test: `grep -nE "add_actor|add_builtin_actor" skills/nt-live/references/concepts/rust.md` shows instance registration distinguished from built-in registration with no obsolete restriction remaining.
  closure: grep for "Python can register only" and "only bundled examples" in `skills/nt-live/references/concepts/rust.md` returns zero hits; the phrase "not a first-class extension API" intentionally remains exactly once, correctly scoped to the bundled `add_builtin_*` methods at `skills/nt-live/references/concepts/rust.md:264`; the revised text documents `LiveNode.add_actor` consistent with the pinned `python/nautilus_trader/live/__init__.pyi`.
  closure-proof: grep for the obsolete restriction in `skills/nt-live/references/concepts/rust.md` returns zero hits while `add_actor` appears six times; `python3 tools/check_legacy_labelling.py` and `python3 tools/check_dev_guide_sync.py` pass.
  correction: 2026-09-02 — [content] — MODIFIED: nt-live Python registration guidance now documents the LiveNode instance/config registration surface and scopes the bundled-examples limitation to `add_builtin_*` — files: skills/nt-live/references/concepts/rust.md

[NT-2026-09-02-02] [P1] [CLOSED 2026-09-02] V2 compliance: nt-adapters teaches standalone `CancellationToken` task management without the standardized generation-safe `TaskGroup`/`TaskSpawner`/`TaskSlot` lifecycle introduced by develop `4c1869127`.
  file: skills/nt-adapters/SKILL.md:500
  evidence: develop `crates/live/src/task.rs` at `4692bac35` documents `TaskGroup`, `TaskSpawner`, `TaskGroupGuard`, and `TaskSlot` ownership with bounded observable shutdown; 159 adapter files were migrated and `docs/developer_guide/adapters.md` updated; `references/upstream-delta-review.json` records the standardization as affecting adapter guidance.
  fix: augment the task-management section with the upstream task-group pattern (admission closure, generation-bound child spawning, bounded shutdown, task ownership), retaining `CancellationToken` only as the cancellation signal inside that lifecycle.
  acceptance-test: `grep -nE "TaskGroup|TaskSpawner|TaskGroupGuard|TaskSlot" skills/nt-adapters/SKILL.md` returns the standardized lifecycle guidance.
  closure: grep for `TaskGroup|TaskSpawner|TaskGroupGuard|TaskSlot` in `skills/nt-adapters/SKILL.md` returns standardized lifecycle guidance whose example matches the pinned `docs/developer_guide/adapters.md` task-management requirements after the pin move.
  closure-proof: grep for `TaskGroup|TaskSpawner|TaskGroupGuard|TaskSlot` in `skills/nt-adapters/SKILL.md` returns seven hits including the signature-accurate lifecycle example verified against pinned `crates/live/src/task.rs`; legacy labelling and dev-guide sync pass.
  correction: 2026-09-02 — [content] — MODIFIED: nt-adapters task management teaches the standardized ownership-classified TaskGroup lifecycle with bounded finish_shutdown — files: skills/nt-adapters/SKILL.md

[NT-2026-09-02-03] [P1] [CLOSED 2026-09-02] V2 compliance: nt-dex-adapter forbids production `tokio::spawn` and requires `get_runtime().spawn` but omits the standardized Nautilus task-ownership and bounded-shutdown APIs.
  file: skills/nt-dex-adapter/SKILL.md:224
  evidence: develop `crates/live/src/task.rs` at `4692bac35` introduces the standardized task lifecycle consumed by all adapter crates; `references/upstream-delta-review.json` lists `skills/nt-dex-adapter/SKILL.md` as affected.
  fix: add DEX-specific task-ownership guidance using `TaskGroup`/`TaskSpawner`/`TaskSlot` for WebSocket, receipt-monitoring, reconciliation, and shutdown tasks, including generation-safe restart and bounded drain behavior.
  acceptance-test: `grep -nE "TaskGroup|TaskSpawner|TaskGroupGuard|TaskSlot" skills/nt-dex-adapter/SKILL.md` returns the standardized lifecycle guidance.
  closure: grep for `TaskGroup|TaskSpawner|TaskGroupGuard|TaskSlot` in `skills/nt-dex-adapter/SKILL.md` returns lifecycle guidance tied to the pinned upstream task module after the pin move.
  closure-proof: grep for `TaskGroup|TaskSpawner|TaskGroupGuard|TaskSlot` in `skills/nt-dex-adapter/SKILL.md` returns four hits tying DEX WebSocket/receipt/reconciliation work to the standardized lifecycle; legacy labelling passes.
  correction: 2026-09-02 — [content] — MODIFIED: nt-dex-adapter gains the DEX task-ownership subsection referencing the standardized lifecycle — files: skills/nt-dex-adapter/SKILL.md

[NT-2026-09-02-04] [P1] [CLOSED 2026-09-02] V2 compliance: curated Polymarket integration copy presents two implementations, an official Python CLOB V2 client dependency, and a `polymarket` installation extra; the pinned upstream document already describes one Rust implementation exposed to Python with no adapter-specific extra.
  file: references/integrations/polymarket.md:11
  evidence: pinned `81eedc7c` `docs/integrations/polymarket.md` states the adapter is implemented in Rust, exposed at `nautilus_trader.adapters.polymarket`, installs with `uv pip install --pre nautilus_trader`, and requires no adapter-specific extra; the curated copy's false claims span `references/integrations/polymarket.md:11-38`.
  fix: replace the two-implementation comparison and `nautilus_trader[polymarket]` installation instructions with the current Rust-native implementation and package installation guidance; update the examples section to current Rust examples and Rust-native Python testers.
  acceptance-test: `grep -nE "CLOB V2 client|nautilus_trader\[polymarket\]|two Polymarket implementations" references/integrations/polymarket.md` returns no false claims.
  closure: `references/integrations/polymarket.md` contains no claim that the official Python CLOB client is the active implementation or that a `polymarket` extra is required, verified against the pinned upstream document after the pin move.
  closure-proof: grep for `nautilus_trader[polymarket]`, `two Polymarket implementations`, and unlabelled CLOB-client claims in `references/integrations/polymarket.md` returns zero active hits (remaining mentions sit in legacy-labelled lines); `python3 -m pytest -q tests/test_nt_v2_adapter_overlays.py tests/test_quality_gates.py` pass with the curated fee-model sections retained.
  correction: 2026-09-02 — [content] — MODIFIED: Polymarket curated copy corrected to the single Rust implementation, no-adapter-extra install, crates examples path, with legacy labels on v1 comparison/history — files: references/integrations/polymarket.md

[NT-2026-09-02-05] [P1] [CLOSED 2026-09-02] V2 compliance: nt-testing states the pinned baseline matches the reviewed `origin/develop` head, verified 2026-08-25; develop has since moved to `4692bac35` and the claim is false.
  file: skills/nt-testing/SKILL.md:17
  evidence: `references/upstream-delta-review.json` records `reviewed_commit` `4692bac35bb11a25eeebb8d7af4d51c55afe53ec` while the pinned baseline at audit time remained `81eedc7cea29a52c0568f0bfbafd190c2bebe74f`.
  fix: replace the equality claim with explicit pinned-baseline and current-develop commit values plus the delta-review pointer; the claim becomes accurate again automatically once the pin moves to the reviewed tip.
  acceptance-test: `grep -n "matches the reviewed" skills/nt-testing/SKILL.md` returns either no equality claim or an accurate one naming the current reviewed commit.
  closure: `skills/nt-testing/SKILL.md:17-19` names both distinct commits and the delta-review evidence, or names a single commit after the pin move makes them equal again.
  closure-proof: `skills/nt-testing/SKILL.md:18` reads `verified 2026-09-02 via tools/upstream_freshness.py` and the equality is true again at the moved pin; `python3 tools/check_upstream_freshness.py --format json` exits 0.
  correction: 2026-09-02 — [content] — MODIFIED: nt-testing baseline claim re-verified at the moved pin with a delta-review pointer — files: skills/nt-testing/SKILL.md

[NT-2026-09-02-06] [P2] [CLOSED 2026-09-02] Improvement opportunity: nt-testing's charter covers memory-leak tests but the guide does not teach the upstream `python/memray_tests/` infrastructure or its nightly workflow added by develop `92dce1859`.
  file: skills/nt-testing/references/guides/testing.md:15
  evidence: develop `92dce1859` adds `python/memray_tests/` (backtest, components, live_node, model, persistence suites), a `nightly-tests.yml` workflow, and Makefile wiring; the guide lists "Memory leak tests" as a category without memray guidance.
  fix: add a scoped memory-leak section covering `python/memray_tests/`, its invocation and prerequisites, and the associated nightly CI workflow, distinguished from ordinary Rust/Python test runs.
  acceptance-test: `grep -ni "memray" skills/nt-testing/references/guides/testing.md` returns the memory-leak testing section.
  closure: `skills/nt-testing/references/guides/testing.md` contains `memray`, `python/memray_tests/`, and the nightly workflow command or link, verified against the pinned upstream tree after the pin move.
  closure-proof: grep -c memray in `skills/nt-testing/references/guides/testing.md` returns eight hits covering `python/memray_tests/`, `make pytest-memray`, prerequisites, and the nightly workflow; legacy labelling passes.
  correction: 2026-09-02 — [coverage] — MODIFIED: nt-testing guide teaches the upstream memray memory-leak lane — files: skills/nt-testing/references/guides/testing.md

[NT-2026-09-02-07] [P2] [CLOSED 2026-09-02] Improvement opportunity: nt-dev documents generic Clippy usage but not the strict Clippy audit surface added by develop `177a802d5`.
  file: skills/nt-dev/references/guides/rust_conventions.md:52
  evidence: develop `177a802d5` adds `scripts/clippy-strict-audit.py`, `scripts/test-clippy-strict-audit.bash`, and a Makefile target reporting the configured strict lint set separately from the normal Clippy gate.
  fix: add the strict-audit command and Make target, explain it reports the strict lint set separately from the normal Clippy gate, and state when contributors must run it.
  acceptance-test: `grep -n "clippy-strict-audit" skills/nt-dev/references/guides/rust_conventions.md` returns the strict-audit guidance.
  closure: `skills/nt-dev/references/guides/rust_conventions.md` names `clippy-strict-audit.py`, its Make target, and the expected successful result, verified against the pinned upstream tree after the pin move.
  closure-proof: grep -c clippy-strict-audit in `skills/nt-dev/references/guides/rust_conventions.md` returns two hits naming the Make target, the strict lint set, and its non-failing report semantics; legacy labelling passes.
  correction: 2026-09-02 — [coverage] — MODIFIED: nt-dev conventions document the strict Clippy audit lane — files: skills/nt-dev/references/guides/rust_conventions.md

[NT-2026-09-02-08] [P2] [CLOSED 2026-09-02] Improvement opportunity: nt-learn curriculum pin maintenance lacks an auditable inventory of which files cite the pinned baseline.
  file: skills/nt-learn/curriculum/07-live-trading.md:60
  evidence: only `07-live-trading.md:60` cites the full pinned commit; generic pinned references occur in `01-setup.md`, `02-run-examples.md`, `04-first-strategy.md`, `05-backtesting.md`, `10-building-nt.md`, `11-testing-quality.md`, and `12-adapter-development.md`.
  fix: enumerate every curriculum file whose source-pinned examples must be refreshed when the baseline moves, or centralize the pin reference so the refresh set is explicit.
  acceptance-test: `grep -rn "pinned" skills/nt-learn/curriculum/*.md` resolves to an explicit refresh inventory.
  closure: the curriculum contains an auditable inventory listing every file with pinned-baseline references, refreshed for the new pin.
  closure-proof: `skills/nt-learn/SKILL.md` carries the pinned-baseline refresh inventory enumerating the nine pin-bound curriculum files; `skills/nt-learn/curriculum/07-live-trading.md` cites the moved pin.
  correction: 2026-09-02 — [content] — MODIFIED: nt-learn gains the auditable curriculum pin-refresh inventory — files: skills/nt-learn/SKILL.md, skills/nt-learn/curriculum/07-live-trading.md

[NT-2026-09-02-09] [P1] [CLOSED 2026-09-02] G2 evidence health: refreshing the reviewed upstream delta changed owned-content hashes through shared reference links, leaving durable evidence stale for `nt-architect`, `nt-implement`, and `nt-review`.
  file: references/upstream-delta-review.json:5; references/g2-evidence/nt-architect.json:2; references/g2-evidence/nt-implement.json:2; references/g2-evidence/nt-review.json:2
  evidence: `python3 tools/check_skill_g2_harnesses.py --check-cards` exits 1 reporting durable-evidence mismatch for the three skills; `python3 -m pytest -q tests/test_skill_g2_harnesses.py::test_current_readiness_evidence_matches_owned_content` fails.
  fix: re-execute the three affected G2 harnesses against a disposable writable checkout of the pinned commit (or of the moved pin, executed together with NT-2026-09-02-10) and refresh the durable JSON evidence files.
  acceptance-test: `python3 tools/check_skill_g2_harnesses.py --check-cards` exits 0.
  closure: `python3 tools/check_skill_g2_harnesses.py --check-cards` exits 0 and the focused pytest passes with refreshed evidence recorded via a phase-2 receipt.
  closure-proof: `python3 tools/check_skill_g2_harnesses.py --execute --upstream-root <disposable-4692bac35-worktree>` completed all 17 skills PASS (nt through nt-trading; the four Python-runtime-dependent skills re-run after preparing `make sync && make build-debug` at the pin); `python3 tools/check_skill_g2_harnesses.py --check-cards` exit 0; `python3 tools/check_skill_g2_harnesses.py --check-card-declarations` exit 0; `python3 -m pytest -q` reports 531 passed / 3 skipped.
  correction: 2026-09-02 — [evidence] — MODIFIED: re-executed every G2 harness against the moved pin and refreshed all 17 durable evidence files — files: references/g2-evidence/*.json (17)

[NT-2026-09-02-10] [P2] [CLOSED 2026-09-02] Pinned-baseline currency: develop has moved 87 commits ahead of the pinned G2 baseline; the master prompt requires moving the pin and refreshing every pin-citing layer.
  file: tools/upstream_baseline.py:4
  evidence: `python3 tools/check_upstream_freshness.py --format json` records `pinned_commit` `81eedc7cea29a52c0568f0bfbafd190c2bebe74f`, resolved develop tip `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`, ahead count 87, delta reviewed 2026-09-02 through the fifth manifest transition.
  fix: update `UPSTREAM_COMMIT` to the reviewed tip `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`; re-sync every drifted `references/developer_guide/*.md` snapshot and the curated Polymarket copy; refresh the README pinned-baseline line and the nt-learn curriculum pin references per NT-2026-09-02-08; re-execute all affected `references/g2-evidence/*.json` harnesses in a disposable writable worktree of the new pin; `python3 tools/check_skill_g2_harnesses.py --check-cards --check-card-declarations` must pass afterwards.
  acceptance-test: `python3 tools/check_upstream_freshness.py --format json` exits 0 with pinned_commit equal to the reviewed tip.
  closure: `python3 tools/check_upstream_freshness.py --format json` exits 0 with the new pin; `python3 tools/check_dev_guide_snapshot_sync.py` exits 0 against the new pin; `python3 tools/check_skill_g2_harnesses.py --check-cards --check-card-declarations` exits 0; evidence recorded via phase-2 receipts.
  closure-proof: `python3 tools/check_upstream_freshness.py --format json` exits 0 with pinned_commit 4692bac35; `python3 tools/check_dev_guide_snapshot_sync.py` exits 0 against the new pin; `python3 tools/check_skill_g2_harnesses.py --check-cards --check-card-declarations` exit 0; README pinned-baseline pointer unchanged (cites tools/upstream_baseline.py); nt-learn curriculum refreshed per NT-2026-09-02-08.
  correction: 2026-09-02 — [baseline] — MODIFIED: moved UPSTREAM_COMMIT to 4692bac35, re-synced six drifted developer-guide snapshots, refreshed mirrors, stamps, manifest, and all pin citations — files: tools/upstream_baseline.py, references/upstream-delta-review.json, references/developer_guide/*.md, skills mirrors and pin citations

[NT-2026-09-02-11] [P1] [CLOSED 2026-09-02] Legacy unlabelled content: the `references/api_reference/` tree presents a v1-era Python module layout as the current API ("built from the latest NautilusTrader source code"), citing 186 automodule paths that do not exist in the pinned V2 Python package, with no legacy labelling and no charter entry.
  file: references/api_reference/execution.md:4
  evidence: pinned `python/nautilus_trader/` exposes flat PyO3 re-export shims (`execution/`, `backtest/`, `live/` contain only `__init__.py`/`__init__.pyi`); automated resolution of every automodule citation in `references/api_reference/**` against the pinned package finds 26 valid and 186 invalid paths (e.g. `nautilus_trader.execution.algorithm`, `nautilus_trader.backtest.auction`, `nautilus_trader.live.node_builder`); `references/api_reference/index.md` claims the reference is built from the latest source; no `legacy:` or migration label appears in the tree and no `docs/tracking/` charter mentions it.
  fix: label every retained v1-era page `legacy: migration/reference-only` with the NT v2 compatibility note, correct `index.md` to stop presenting the tree as current, and remove or rewrite pages whose content is better served by the Rust/PyO3 crate documentation; record the tree's disposition in `docs/tracking/Structure.md`.
  acceptance-test: `python3 - <<EOF` automodule resolution over references/api_reference reports zero unlabelled invalid-path pages.
  closure: every page under `references/api_reference/` either carries an explicit legacy label or cites only module paths that resolve in the pinned V2 Python package, verified by automated automodule resolution over the tree; Structure.md records the tree's role.
  closure-proof: grep -rLn "NT v2 compatibility" over `references/api_reference/**/*.md` returns zero files (37 labelled pages plus the rewritten index); `docs/tracking/Structure.md` evidence layers record the tree's legacy disposition; legacy labelling and dev-guide sync pass.
  correction: 2026-09-02 — [content] — MODIFIED: api_reference tree labelled legacy v1 snapshot on every page, index rewritten to stop claiming currency, Structure.md records the disposition — files: references/api_reference/** (37 files), docs/tracking/Structure.md

[NT-2026-09-02-12] [P1] [CLOSED 2026-09-02] Legacy unlabelled content: the nt-review live-trading checklist carries v1.223.0 items as active checklist entries with only a distant conditional section note.
  file: skills/nt-review/AGENTS.md:136
  evidence: `skills/nt-review/AGENTS.md:133-139` lists `- [ ] v1.223.0:` entries inside the active LIVE TRADING CHECKLIST; the section-level NT v2 note at `:127` is six lines away and conditional; `skills/**/AGENTS.md` files are outside the `check_legacy_labelling.py` scan scope, so the lint cannot catch this.
  fix: move the versioned v1 items into an explicitly labelled `legacy:` migration/reference subsection with their current V2 replacements, out of the active checklist.
  acceptance-test: `grep -n "v1.223.0" skills/nt-review/AGENTS.md` shows every hit inside an explicitly labelled legacy subsection.
  closure: `skills/nt-review/AGENTS.md` active checklist contains no `v1.223.0` entries and the historical items sit in a labelled subsection with replacement guidance.
  closure-proof: the v1.223.0/v1.224.0 material in `skills/nt-review/AGENTS.md` sits under explicit NT v2 compatibility notes and `legacy: migration/reference-only` labels; `python3 tools/check_legacy_labelling.py` passes (AGENTS.md files are outside its scan scope, verified manually).
  correction: 2026-09-02 — [content] — MODIFIED: nt-review checklist v1 items moved to labelled legacy history with V2 replacements; v1.223.0/v1.224.0 change sections labelled — files: skills/nt-review/AGENTS.md

[NT-2026-09-02-13] [P1] [CLOSED 2026-09-02] V2 compliance: two active-content citations still referenced the superseded pin `81eedc7c` because the refresh matched only the 10-character prefix `81eedc7cea`.
  file: skills/nt/SKILL.md:37
  evidence: the Phase 5 independent reconciliation review found the nt router G2 evidence row citing `81eedc7ce` and the test comment at `tests/test_current_develop_guidance.py:111` citing `(81eedc7ce)`; repo-wide sweep confirmed these were the only active-content occurrences outside receipts, manifest transition history, and this ledger.
  fix: repoint both citations to `4692bac35` and re-execute the `nt` G2 harness so its durable evidence matches the changed owned content.
  acceptance-test: repo-wide grep for `81eedc7c` excluding receipts, manifest transition history, and this ledger returns zero active-content hits; `python3 tools/check_skill_g2_harnesses.py --check-cards` exits 0.
  closure: `python3 tools/check_skill_g2_harnesses.py --execute --skill nt` PASS with refreshed evidence; `--check-cards` exit 0; `python3 -m pytest -q tests/test_current_develop_guidance.py` 7 passed.
  closure-proof: stale active-content citation count after fix: 0; nt harness re-executed PASS at 4692bac35 with evidence refreshed.
  correction: 2026-09-02 — [content] — MODIFIED: repointed the two missed old-pin citations and refreshed nt G2 evidence — files: skills/nt/SKILL.md, tests/test_current_develop_guidance.py, references/g2-evidence/nt.json


[NT-2026-08-30-01] [P1] [CLOSED 2026-08-30] Prompt governance audit: the master prompt coupled impact priority to evidence state, prescribed free-form `.txt` evidence receipts with no secret-safety contract, and defined no spec-delta or verifier-owned legacy-receipt protocol.
  file: docs/prompts/master-prompt.md:95; docs/prompts/master-prompt.md:212; docs/prompts/master-prompt.md:255
  evidence: the cross-repository governance audit (reference improvements shipped as Nautilus-Daedalus `ebc8971f`) found the prompt lowering finding priority when evidence was missing, accepting unversioned `.txt` receipts that could commit raw credentials, and requiring no deterministic `spec-deltas` on implementation manifests; all five baseline pressure scenarios (no-impact spec delta, legacy receipts, unverified P0, secret-bearing output, machine-checkable contract) failed against the pre-change prompt.
  fix: separate impact priority (P0/P1/P2) from evidence state (verified/verified-manual/unverified) with the rule that missing evidence never lowers impact; replace `.txt` receipts with schema-version-1 secret-safe JSON receipts under `docs/tracking/receipts/` validated by `python3 tools/check_governance_receipts.py`; define verifier-owned Phase 3 receipts for legacy implementations; bootstrap `docs/specs/` subordinate to executable truth and require deterministic `spec-deltas` including `spec-deltas: []`; align `AGENTS.md`.
  acceptance-test: `python3 -m pytest -q tests/test_master_prompt_governance.py tests/test_governance_receipts.py`; `python3 tools/check_governance_receipts.py`; `python3 tools/check_findings_schema.py`.
  closure: full suite 531 passed / 3 skipped with Ruff and Pyright clean; both representative receipts validate; the same five pressure scenarios now pass 5/5.

[NT-2026-08-28-13] [P1] [CLOSED 2026-08-28] Post-ship review: eight guidance and evidence surfaces cited the invalid pin abbreviation `81eedc7cec`.
  file: docs/end_to_end_guide.md:8; skills/nt-dev/SKILL.md:20; skills/nt-testing/SKILL.md:82; skills/nt-adapters/SKILL.md:20; skills/nt-adapters/references/integrations/betfair.md:11; skills/nt-adapters/references/integrations/betfair_v2.md:8
  evidence: the independent code-quality review found `81eedc7cec` — not a prefix of the pinned commit `4692bac35bb11a25eeebb8d7af4d51c55afe53ec` — in eight user-facing surfaces, making the cited baseline unresolvable.
  fix: replace every `81eedc7cec` occurrence with the valid 10-character prefix `4692bac35`, add a regression test asserting the resolvable abbreviation across user-facing guidance, and re-execute G2 evidence for the six skills whose owned content changed.
  acceptance-test: `python3 -m pytest -q tests/test_current_develop_guidance.py` includes the baseline-abbreviation regression and passes; `python3 tools/check_skill_g2_harnesses.py --check-cards` is green with refreshed evidence.
  closure: commit `01ab00c` corrected all eight citations, added `test_current_baseline_abbreviation_is_consistent`, and re-executed the six affected G2 evidence files at the pin; guidance tests 7 passed, freshness tests 17 passed, `--check-cards` green, full suite 522 passed / 3 skipped; independent code-quality re-review returned PASS.

[NT-2026-08-28-14] [P2] [CLOSED 2026-08-28] Post-ship review: the delta-review rationale for benchmark commit `8bdb040118` misdescribed the re-pin, and the pinned read-only checkout carried build artifacts.
  file: references/upstream-delta-review.json:2103; pinned cache `nautilus_trader-pinned` (not a repository path, see evidence)
  evidence: the independent security review found the manifest claiming the benchmark refinement "flows in at the next re-pin" with no repository change required, although that commit was itself included in this re-pin and its content was refreshed into `references/developer_guide/benchmarking.md`; the same review measured a 21 GB `target/` inside the pinned checkout, violating the master-prompt rule that the pinned cache is never built into.
  fix: rewrite the rationale to state the snapshot was refreshed by this re-pin, regenerate G2 evidence through the writable evidence checkout `nautilus_trader-evidence-81eedc7ce`, and delete `target/` from the pinned cache.
  acceptance-test: `python3 -m json.tool references/upstream-delta-review.json` parses; `python3 tools/check_upstream_freshness.py --format json` reports the manifest reviewed at the pin; the pinned cache has no `target/` and a clean git status.
  closure: commit `01ab00c` corrected the rationale; the pinned cache ended git-clean with `target/` absent and 63-64 GB disk free; independent security re-review returned PASS on both remediations.

[NT-2026-08-28-12] [P1] [CLOSED 2026-08-28] Upstream currency: the reproducible pin and reviewed delta stopped 3 commits before current `origin/develop`.
  file: tools/upstream_baseline.py:4; references/upstream-delta-review.json:1
  evidence: post-preflight freshness reported pin/review at `19df7796fcce341ca6c1f6a503fca2c7bf300e6c` with resolved develop `4692bac35bb11a25eeebb8d7af4d51c55afe53ec` (3 commits, 15 changed paths: strategy-managed contingent orders, benchmark refinements, pre-commit tooling wrappers); the suite's freshness tests require pin, review, and resolved develop to agree at ship.
  fix: advance `UPSTREAM_COMMIT` to `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`, checkout the pinned cache at the new commit, refresh all pin-derived snapshots and citations, re-label former develop-only overlays as develop-line content now at-pin, re-execute durable G2 evidence, and record the third reviewed transition.
  acceptance-test: `python3 tools/check_upstream_freshness.py --format json` exits 0 with pin, review, and `origin/develop` equal to `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`; `python3 -m pytest -q tests/test_upstream_freshness.py` passes; `python3 tools/check_dev_guide_snapshot_sync.py` matches the new pin.
  closure: advanced `UPSTREAM_COMMIT` to `81eedc7ce`, refreshed every pin-derived layer, and re-executed durable G2 evidence; fresh gates — `check_upstream_freshness.py --format json` exits 0 with `pinned_commit` = resolved develop = `4692bac35bb11a25eeebb8d7af4d51c55afe53ec` (status `current`, `commits_ahead` 0), `tests/test_upstream_freshness.py` 17 passed, `check_dev_guide_snapshot_sync.py` exits 0, G2 evidence 17/17 re-executed at the new pin with `--check-cards` green, full suite 521 passed / 3 skipped.

[NT-2026-08-28-11] [P1] [CLOSED 2026-08-28] Strategy-managed contingent order semantics are missing or stale in skills after upstream `81eedc7ce`.
  file: skills/nt-adapters/references/concepts/live.md:374; skills/nt-trading/references/concepts/orders.md:550; skills/nt-strategy-builder-rust/SKILL.md:3
  evidence: upstream `4692bac35bb11a25eeebb8d7af4d51c55afe53ec` rewrites the `StrategyConfig.manage_contingent_orders` description to "Manage open, non-active-local OTO, OCO, and OUO relationships" with `OrderEmulator` retaining active-local orders (docs/how_to/configure_live_trading.md, docs/concepts/orders/advanced.md "Strategy-managed contingencies"); `live.md:374` still carries the superseded "automatically manages" wording, `orders.md` contingency sections omit the strategy-managed path (OTO child quantity propagation and cancel rules, OCO sibling cancellation, OUO update scope), and the production Rust strategy skill never mentions the flag.
  fix: correct the `live.md` row to the upstream scope wording; add a develop-only overlay section to `nt-trading/references/concepts/orders.md` (house style per nt-model "Develop-only order metadata validation") documenting the strategy-managed contingency semantics with the `81eedc7ce` citation; add the flag to `nt-strategy-builder-rust` configuration guidance with the pinned-baseline version boundary.
  acceptance-test: a new deterministic policy test asserts the three skills cite `manage_contingent_orders` with the develop commit and non-active-local scope wording, and `nt-adapters` live config rows match the upstream `81eedc7ce` description; `python3 tools/check_upstream_freshness.py --format json` stays green with reviewed tip `81eedc7ce`.
  closure: all three files updated with `81eedc7ce` citations and upstream wording (OTO/OCO/OUO non-active-local relationships, OrderEmulator active-local retention); `tests/test_current_develop_guidance.py` 6/6 green including the new `test_contingent_order_guidance_covers_strategy_managed_semantics`; full suite 521 passed / 3 skipped.

[NT-2026-08-28-07] [P1] [CLOSED 2026-08-28] Upstream currency: the reproducible pin and reviewed delta stopped 10 commits before current `origin/develop`.
  file: tools/upstream_baseline.py:4; references/upstream-delta-review.json:1843
  evidence: pre-fix freshness reported pin/review at `8e51f957c6e31b28de14fbe244b3c048e291ddd7`, resolved develop `19df7796fcce341ca6c1f6a503fca2c7bf300e6c`, 10 commits and 45 changed paths, and a stale manifest; the new transition records all 10 commits and 45 paths.
  fix: advanced `UPSTREAM_COMMIT`, refreshed all pin-derived snapshots and citations, preserved the reviewed transition, and re-executed durable G2 evidence.
  closure: `python3 tools/check_upstream_freshness.py --format json` exits 0 with pin, review, and `origin/develop` equal to `19df7796fcce341ca6c1f6a503fca2c7bf300e6c`.

[NT-2026-08-28-08] [P1] [CLOSED 2026-08-28] Rust adapter correctness: local guidance omitted the current field-contract rule for decimal precision.
  file: references/developer_guide/adapters.md:474; skills/nt-adapters/SKILL.md:36
  evidence: upstream commit `91163e6e106bb3685b0beae5aeaea69bc0e726e6` adds `Price::from_decimal`, `Quantity::from_decimal`, `Decimal::normalize`, explicit instrument/currency precision, and a warning not to infer scale from incidental payload formatting.
  fix: refreshed the pinned adapter guide and taught adapter authors, reviewers, and tests to choose precision from the field contract with trailing-zero variant coverage.
  closure: `python3 tools/check_dev_guide_snapshot_sync.py` matches the current upstream body; `python3 tools/check_static_quality.py` is green and manual skill-surface QA confirms the field-contract decision tree.

[NT-2026-08-28-09] [P1] [CLOSED 2026-08-28] Rust live correctness: production guidance omitted current builder re-entry and reconciliation regression contracts.
  file: skills/nt-live/SKILL.md:19; skills/nt-strategy-builder-rust/SKILL.md:36
  evidence: upstream commits `f4a6e629c20d9c77f76e819d1766aadf6b9d1d18`, `be369b4b303dc2be3a2f4363c28e0c51c369bb75`, and `57ce1a80263fd014f1f5e3a7a7f7de82bb869322` respectively reject Python factory re-entry through `LiveNodeBuilder`, apply same-position fill reports, and restore side-aware quantity-free close-all quantities.
  fix: added bounded PyO3 builder-state guidance plus Rust live/reviewer/test requirements for same-position fill and quantity-free close-all reconciliation.
  closure: `python3 tools/check_static_quality.py` is green and manual skill-surface QA confirms the builder re-entry, same-position fill, and quantity-free close-all contracts across live, strategy, testing, and review guidance.

[NT-2026-08-28-10] [P2] [CLOSED 2026-08-28] Rust execution testing: review guidance could encourage brittle transient event-count assertions.
  file: skills/nt-review/SKILL.md:42; skills/nt-testing/SKILL.md:69
  evidence: upstream commit `af0e5d1d341c49be7d446176b84866d4118b7caa` optimizes `ExecutionEngine` position updates, including same-fill open/close handling where transient position-open events are not emitted.
  fix: required lifecycle-semantics assertions and rejected event-count assumptions unless event cardinality itself is the contract.
  closure: `python3 tools/check_static_quality.py` is green and manual skill-surface QA confirms explicit final-state, ordering, and duplicate-side-effect guidance.

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

[NT-2026-08-26-01] [P1] [CLOSED 2026-08-26] Upstream drift: develop tip advanced 5 commits past the pin (`73d4dd5b3` → `8ecab1ce9`), touching taught Rust surfaces (betfair execution identity, polymarket REST reconciliation, shared execution reconciliation core).
  file: tools/upstream_baseline.py:4; references/upstream-delta-review.json
  evidence: `python3 tools/check_upstream_freshness.py --format json` at the refreshed cache reports develop tip `8ecab1ce90d9790b1e18e162842decbae4d9de57`, 5 commits ahead of pin `8ecab1ce90d9790b1e18e162842decbae4d9de57`; per-commit delta review recorded in `references/upstream-delta-review.json` (5 commits, 37 paths; no Rust `examples/` paths changed).
  fix: move `UPSTREAM_COMMIT` to the reviewed tip, sync the two changed integration mirrors (`betfair.md` 62 lines, `polymarket.md` 11 lines, both layers), refresh pin citations, re-execute G2 evidence at the new pin.
  closure: `python3 tools/check_upstream_freshness.py --format json` exits 0 at the new pin with all sync checkers and the full suite green.
  closure-proof 2026-08-26: `python3 tools/check_upstream_freshness.py` exit 0 at pin `8ecab1ce9` (pinned == reviewed tip); `check_dev_guide_sync.py`, `check_dev_guide_snapshot_sync.py`, `check_rust_trading_reference_sync.py`, `check_legacy_labelling.py` all exit 0; all 17 G2 harnesses re-executed PASS at `8ecab1ce9` with `--check-cards` and `--check-card-declarations` exit 0 (evidence regenerated in `references/g2-evidence/*.json`, `upstream_commit=8ecab1ce90d9790b1e18e162842decbae4d9de57`); delta-review JSON collapsed to the new pin (deltas=[]). Pin-move commits: 506517b, cdf4ad8, 234556c; mirror/finding follow-ups in NT-02/-03/-04.

[NT-2026-08-26-02] [P1] [CLOSED 2026-08-26] The Betfair v2 Rust-surface tracker (`betfair_v2.md`) is stale against `8e51f957c`, which landed exactly the behaviors the tracker exists to track.
  file: references/integrations/betfair_v2.md:24-27,71-87,125; skills/nt-adapters/references/integrations/betfair_v2.md (mirror)
  evidence: upstream `8e51f957c` "Retain Betfair terminal order identity" routes late fills/voids through retained local order identity, restores closed order identity from cache across reconnects, bounds correlation/customer-refs/dedup/replaced-IDs, resolves replace state across REST/OCM/reconciliation, and reconciles terminal replace/reduction reports without duplicates; `crates/execution/src/reconciliation/orders.rs` changed in the same delta (shared core). The tracker's "Current Rust status" rows (reconciliation scope, post-reconnect halt, external order filtering) and the OCM/reconciliation section describe pre-`8e51f957c` behavior and carry no row for terminal order identity retention.
  fix: re-verify each tracker row against `8e51f957c` sources (`crates/adapters/betfair/src/execution.rs`, `stream/ocm.rs`, `crates/execution/src/reconciliation/orders.rs`), update stale rows, add the identity-retention behavior, and refresh both file copies.
  closure: every tracker row cites verified `8e51f957c` behavior; `python3 tools/check_dev_guide_sync.py` and `python3 tools/check_legacy_labelling.py` stay green.
  closure-proof 2026-08-26: terminal-order-identity row added citing `crates/adapters/betfair/src/execution.rs` (`OcmState::DEDUP_RETENTION`, most-recent 10,000 closed cached orders seeded into OCM state); reconciliation-scope and post-reconnect rows marked resolved/cutover-done against the upstream `8e51f957c` doc; customerOrderRef section carries the tracked-order collision wording. Gates: `check_dev_guide_sync.py`, `check_legacy_labelling.py` exit 0; `tests/test_v2_current_develop_overlays.py` green (cutover commit 990b5a5).
  2026-08-26 — P1 — MODIFIED: tracker refreshed at 8e51f957c and made the primary guide — files: references/integrations/betfair_v2.md, skills/nt-adapters/references/integrations/betfair_v2.md

[NT-2026-08-26-03] [P1] [CLOSED 2026-08-26] Rust-first routing gap: the Betfair v2 guide is unreachable from active guidance — every route lands on the v1 guide.
  file: references/integrations/index.md:10; skills/nt-adapters/SKILL.md
  evidence: `references/integrations/index.md:10` (byte-sync-enforced mirror, uneditable) routes Betfair → `betfair.md` (v1 Python-adapter guide, migration/reference-only once the cutover lands); no `skills/**/SKILL.md` references `betfair_v2.md` (`grep -rln betfair_v2 skills/` → empty; only `docs/tracking/Findings.md` and `tests/test_v2_current_develop_overlays.py` mention it). An agent following nt-adapters guidance therefore reads v1 wiring with no pointer to the Rust surface, violating the Rust-first default (master-prompt constraints; `docs/tracking/Handguard.md` invariant #5 spirit).
  decision (user, 2026-08-26): full cutover — v2 over v1. `betfair_v2.md` becomes the primary Betfair guide; v1 is cleared from active routing and demoted to labelled migration/reference-only. `betfair_v2.md`'s header pre-plans this ("can replace `betfair.md` with small edits instead of a full rewrite").
  fix: execute the cutover — update `betfair_v2.md` tracker rows against the new pin, stamp `betfair.md` (both layers) with a supersession label routing Rust v2 work to the v2 guide, flip every editable active route (SKILL.md guidance, cross-links) to `betfair_v2.md`; the byte-synced index row stays as-is (sync-enforced) but every skill-layer route that chooses a guide names v2 first.
  NT v2 compatibility note: v1 routing below is migration audit context; the cutover demotes it to migration/reference-only.
  closure: every active route reaches `betfair_v2.md` first; `betfair.md` carries the supersession/migration-reference label; `python3 tools/check_legacy_labelling.py`, `python3 tools/check_dev_guide_sync.py`, and routing tests stay green.
  closure-proof 2026-08-26 (cutover commit 990b5a5): index.md (both layers) Betfair row links `betfair_v2.md` as Guide with the v1 stub kept as the legacy link to `betfair.md`; `check_dev_guide_sync.py` CURRENT_INTEGRATION_GUIDES now enforces the v2 guide link (betfair_v2.md replaces betfair.md — the enforcement contract, not the mirror, changed); `skills/nt-adapters/SKILL.md` routes Betfair work to `betfair_v2.md` first; v1 files cleared to labelled supersession stubs. `tests/test_v2_current_develop_overlays.py::test_betfair_v2_is_primary_and_v1_cleared` and `::test_nt_adapters_routes_betfair_v2_first` green.
  2026-08-26 — P1 — MODIFIED: executed the user-directed cutover (v2 primary, v1 cleared to labelled stubs) — files: references/integrations/betfair.md, skills/nt-adapters/references/integrations/betfair.md, references/integrations/index.md, skills/nt-adapters/references/integrations/index.md, skills/nt-adapters/SKILL.md

[NT-2026-08-26-04] [P2] [CLOSED 2026-08-26] The polymarket mirror is stale against `0541a2189`/`ccc80cdb2`; upstream's guide is already Rust-first, so this is pure mirror drift with no v2 overlay needed.
  file: references/integrations/polymarket.md; skills/nt-adapters/references/integrations/polymarket.md
  evidence: upstream `docs/integrations/polymarket.md` states "The adapter is implemented in Rust and exposed to Python" (line 9) and "direct WebSocket, provider, data client, and execution client types are Rust-only" (line 84) — no `polymarket_v2.md` split is warranted; the delta changed 11 lines (order-recovery clarification, REST report binding to account/instrument).
  fix: fold the mirror refresh into the NT-2026-08-26-01 pin-move segment (byte-sync both layers).
  closure: `python3 tools/check_dev_guide_sync.py` exits 0 with both mirrors matching the reviewed tip.
  closure-proof 2026-08-26: both layers carry the upstream `8e51f957c` order-recovery wording (base-denominated `LIMIT` validation, "no known client association" fallback) and the authoritative Fees section; `python3 tools/check_dev_guide_sync.py` exits 0. Also fixed pre-existing layer divergence: the skills layer taught `Crypto 0.072` where upstream says `0.07`.
  2026-08-26 — P2 — MODIFIED: refreshed both polymarket mirrors to the reviewed tip and aligned the Fees section across layers — files: references/integrations/polymarket.md, skills/nt-adapters/references/integrations/polymarket.md

## Follow-up TODO

- [x] [NT-2026-08-21-07] Move the G2 pin to the reviewed develop tip and re-execute all 17 harnesses. Closed 2026-08-28: the pin, review, and `origin/develop` all equal `19df7796fcce341ca6c1f6a503fca2c7bf300e6c`; all 17 harnesses re-executed and `python3 tools/check_skill_g2_harnesses.py --check-cards` is green. Next scheduled re-run: 2026-09-28.

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

[NT-2026-08-28-01] [P0] [CLOSED 2026-08-28] Official develop advanced 63 commits and 543 unique paths beyond the reproducible pin.
  file: tools/upstream_baseline.py:4; references/upstream-delta-review.json:5; references/developer_guide/adapters.md:1
  evidence: after `git fetch origin develop`, `python3 tools/check_upstream_freshness.py --format json` reported `19df7796fcce341ca6c1f6a503fca2c7bf300e6c`, 63 commits ahead of `8ecab1ce90d9790b1e18e162842decbae4d9de57`, with the reviewed manifest stale; the independent upstream reviewer classified all 63 commits and aggregate 543 paths.
  fix: preserve the complete 63-commit transition classification, advance the pin to the reviewed tip, refresh changed developer-guide and Rust reference mirrors, synchronize pin metadata, and regenerate all G2 evidence against the new baseline.
  closure: `references/upstream-delta-review.json` retains all 63 reviewed commits and 543 net changed paths; `python3 tools/check_upstream_freshness.py --format json` validates that history and reports `status: current`, zero current changed commits/paths, and `manifest_reviewed: true`; `python3 tools/check_dev_guide_snapshot_sync.py` passes.

[NT-2026-08-28-02] [P1] [CLOSED 2026-08-28] NT v2 compatibility note: the mission prompt's migration/reference-only taxonomy violated the canonical legacy-labelling contract.
  file: docs/prompts/master-prompt.md:17,92-95,120,150-152,230,313
  evidence: `python3 tools/check_dev_guide_sync.py` failed on Python live `TradingNode` and legacy/Cython/v1 detection-only terms in the prompt that mandates the same check remain green.
  fix: mark detection-only taxonomy blocks with canonical NT v2 compatibility and migration/reference-only labels, then include active docs in the dedicated lint scope.
  closure: `python3 tools/check_dev_guide_sync.py` and `python3 tools/check_legacy_labelling.py` pass; focused legacy regression tests cover the prompt and active-doc surfaces.

[NT-2026-08-28-03] [P1] [CLOSED 2026-08-28] Skill gate commands used a non-portable pytest console-script invocation.
  file: skills/nt-review/SKILL.md:19; skills/nt-testing/SKILL.md:79; tests/test_command_portability.py:1
  evidence: the representative `uv run pytest -q ...` command failed collection with `ModuleNotFoundError: No module named 'tools'`; `uv run python -m pytest -q ...` passed 50 tests.
  fix: replace all bare `uv run pytest` guidance in the 17 top-level skill cards with module-safe `uv run python -m pytest` and add a repository regression guard scoped to those cards.
  closure: `tests/test_command_portability.py` passes and a representative four-file command passes exactly as documented.

[NT-2026-08-28-04] [P1] [CLOSED 2026-08-28] Current findings accepted malformed or incomplete entries without a schema gate.
  file: tools/check_findings_schema.py:8; tests/test_findings_schema.py:1; docs/tracking/Findings.md:15
  evidence: the 54-entry ledger had no parser or validator; historical entries used five field variants and no command rejected invalid IDs, priorities, statuses, duplicates, or incomplete current entries.
  fix: add a deterministic schema validator with explicit historical compatibility, strict 2026-08-28+ rules, fixture tests, and static-quality integration.
  closure: `python3 tools/check_findings_schema.py` and `tests/test_findings_schema.py` pass; malformed IDs, duplicate IDs, missing open acceptance tests, and missing current closure proof fail.

[NT-2026-08-28-05] [P2] [CLOSED 2026-08-28] Legacy terminology lint omitted active root and docs guidance.
  file: tools/check_legacy_labelling.py:14-21
  evidence: a temporary `docs/active.md` containing unlabelled `cdef` exited zero because scanning covered only `skills`, `references`, and `templates`.
  fix: scan `README.md` and `docs/**/*.md`, exclude `docs/tracking` history intentionally, and avoid treating hyphenated semantic metadata such as `regime-v1` as legacy API guidance.
  closure: focused fixtures prove unlabelled active docs fail, labelled migration text passes, and tracking history remains excluded; the full-tree lint passes.

[NT-2026-08-28-06] [P1] [CLOSED 2026-08-28] Progressive cutover decisions lacked one complete standard gate-card contract.
  file: docs/tracking/CutoverGateTemplate.md:1; docs/end_to_end_guide.md:16; skills/nt-review/SKILL.md:19
  evidence: all 17 skills exposed compact G0-G7 readiness rows, but no artifact covered the required 11 cross-cutting architecture-through-continuous-improvement gates with objective, applicability, evidence, status, owner, verification date, next action, and blocker fields.
  fix: add the standard template, wire every skill and the end-to-end guide to it, index it in Components, and enforce coverage by tests.
  closure: `tests/test_progressive_gate_cards.py` passes and `python3 tools/check_skill_g2_harnesses.py --check-card-declarations` confirms all 17 existing G0-G7 cards remain valid.

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
2026-08-28 — P1 — MODIFIED: corrected eight invalid `81eedc7cec` pin abbreviations to the resolvable prefix `4692bac35`, locked the abbreviation with a regression test, and re-executed the six affected G2 evidence files — files: docs/end_to_end_guide.md, skills/nt-dev/SKILL.md, skills/nt-testing/SKILL.md, skills/nt-adapters/SKILL.md, skills/nt-adapters/references/integrations/betfair.md, skills/nt-adapters/references/integrations/betfair_v2.md, tests/test_current_develop_guidance.py, references/g2-evidence/
2026-08-28 — P2 — MODIFIED: corrected the benchmark-commit re-pin rationale in the delta manifest and scrubbed build artifacts from the pinned read-only cache, with evidence regeneration moved to the writable evidence checkout — files: references/upstream-delta-review.json
2026-08-28 — P0 — MODIFIED: advanced the reproducible pin to reviewed develop `81eedc7ce` with the 3-commit/15-path transition classified in the delta review and every pin-derived layer refreshed (19 developer-guide snapshots, 28 pin-citation files across skills, manifest pinned=reviewed=`81eedc7ce`, all 17 G2 evidence files re-executed at the new baseline) — files: tools/upstream_baseline.py, references/upstream-delta-review.json, references/developer_guide/, references/g2-evidence/, skills/**, tests/test_upstream_freshness.py, tests/test_exec_spec_current_overlay.py
2026-08-28 — P1 — MODIFIED: strategy-managed contingent-order guidance aligned to upstream `81eedc7ce` (OTO/OCO/OUO non-active-local semantics, OrderEmulator active-local retention) in nt-trading orders.md, nt-adapters live.md config rows, and nt-strategy-builder-rust SKILL.md, with a deterministic regression test — files: skills/nt-trading/references/concepts/orders.md, skills/nt-adapters/references/concepts/live.md, skills/nt-strategy-builder-rust/SKILL.md, tests/test_current_develop_guidance.py
2026-08-28 — P0 — MODIFIED: advanced the reproducible pin to reviewed develop `8e51f957c` with the complete 63-commit/543-path transition classification preserved in the delta manifest and every pin-derived layer refreshed (developer-guide snapshots, adapter integration mirrors, curriculum pins, rust_trading example mirror, crates-lane guidance, and all 17 G2 evidence files re-executed at the new baseline) — files: tools/upstream_baseline.py, tools/check_upstream_freshness.py, tools/check_dev_guide_sync.py, tests/test_upstream_freshness.py, references/upstream-delta-review.json, references/developer_guide/, references/g2-evidence/, references/integrations/, skills/**, README.md, docs/end_to_end_guide.md, tests/test_active_doc_examples.py, tests/test_exec_spec_current_overlay.py, tests/test_nt_v2_adapter_overlays.py, tests/test_v2_current_develop_overlays.py
2026-08-28 — P1 — MODIFIED: NT v2 compatibility note: labelled the master prompt's detection-only Cython/v1 taxonomy as migration/reference-only and aligned the prompt with the canonical legacy-labelling contract its own mandates enforce — files: docs/prompts/master-prompt.md
2026-08-28 — P1 — MODIFIED: replaced every non-portable `uv run pytest` gate command with module-safe `uv run python -m pytest` across all 17 skill cards and added a repository portability guard — files: skills/*/SKILL.md, tests/test_command_portability.py
2026-08-28 — P1 — MODIFIED: added the deterministic Findings schema validator (strict 2026-08-28+ entry rules with historical compatibility) and the canonical static-quality orchestrator wiring schema, labelling, lane, template-classification, and card checks — files: tools/check_findings_schema.py, tools/check_static_quality.py, tests/test_findings_schema.py, tests/test_quality_gates.py, AGENTS.md, tools/check_skill_g2_harnesses.py, tests/test_skill_g2_harnesses.py
2026-08-28 — P2 — MODIFIED: widened the legacy-terminology lint to README and active docs (docs/tracking history intentionally excluded) without flagging hyphenated semantic metadata — files: tools/check_legacy_labelling.py, tests/test_legacy_labelling.py
2026-08-28 — P1 — MODIFIED: standardized the progressive cutover decision record with one complete gate-card template and end-to-end promotion guidance — files: docs/tracking/CutoverGateTemplate.md, tests/test_progressive_gate_cards.py, docs/end_to_end_guide.md
2026-08-28 — P1 — MODIFIED: resolved the independent post-fix review (3 P1 + 1 P2): schema candidate detection no longer pre-filters on `] [P` so malformed IDs/priorities/statuses are rejected, current entries reject duplicate/unknown/malformed fields, empty ledgers fail, current `file:` fields must cite at least one resolvable repository path:line (existence + line-range checked), the static-quality orchestrator now binds rust_trading_reference_sync and upstream_freshness with structural test coverage of the declared validator set, and all 2026-08-28 finding citations were narrowed to concrete path:line references (P2: portability-guard claim scoped to the 17 top-level skill cards) — files: tools/check_findings_schema.py, tools/check_static_quality.py, tests/test_findings_schema.py, tests/test_quality_gates.py, docs/tracking/Findings.md
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
