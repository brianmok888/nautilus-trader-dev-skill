# Findings — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Issue tracker + closure evidence + delta log. -->
<!-- Read when: checking issue status, finding closure evidence, reading recent deltas to understand what changed. -->
<!-- Updated when: ALWAYS on plan closure (delta entry) + on issue open/close. -->
<!-- Does NOT contain: architecture descriptions, invariants, component reviews. -->
<!-- Write-target rule: this file is the default write-target. Other files are write-targets only when their scope changed. -->

Review date: 2026-08-05

## Open issues

No P0/P1 NT V2 Rust cutover finding remains open. The 2026-08-05 audit's
freshness and lint findings were closed in this session. Cap'n Proto execution
and exact-SHA external attestation remain pending as documented in
`docs/superpowers/reports/2026-07-30-nt-v2-rust-cutover-reconciliation.md`.

## Closed issues

### NTDS-001 — ruff E402 lint debt in test_upstream_freshness.py
**Severity:** low
**Description:** `tests/test_upstream_freshness.py:17` has 2 ruff E402 (module-level import not at top of file) errors. `uv run ruff check .` reports 2 errors. Does not block tests (320 passing) but blocks lint gate.
**Status:** closed
**Closure evidence:** `uv run --with ruff ruff check .` passes on the merged tree.

### NTDS-002 — Phase 1 Cython/legacy labelling audit not yet run
NT v2 compatibility note: this issue records migration/reference-only Cython,
v1, and legacy audit terms; it does not authorize those paths for new work.
**Status:** closed
**Severity:** high
**Description:** Every skill SKILL.md has between 2 and 9 Cython mentions and 4–18 legacy mentions. Per Handguard invariant #3, all Cython/v1/legacy content must be explicitly labelled. A Phase 1 deep review is required to confirm every instance is labelled `legacy:` or carries a migration note. Unlabelled instances are charter violations.
**Scope:** 18 skills × SKILL.md + reference files + templates.
**Closure evidence:** `docs/superpowers/reports/2026-07-30-nt-v2-rust-cutover-reconciliation.md` closes the post-fix audit; `uv run python tools/check_legacy_labelling.py` and `uv run python tools/check_dev_guide_sync.py` pass.

### NTDS-003 — G2 gate status unverified per skill
**Status:** closed
**Severity:** medium
**Description:** Per Handguard invariant #7, each skill claiming V2 compliance must have passing G2 evidence (`tools/check_skill_g2_harnesses.py`). Current per-skill G2 status is not documented in a readiness card. Phase 3 of the mission prompt asks for a cutover readiness card per skill.
**Closure evidence:** all 18 `skills/nt*/SKILL.md` cards contain exactly one G0-G7 row; `uv run python tools/check_skill_g2_harnesses.py --check-cards` passes and `references/g2-evidence/*.json` stores G2 evidence. The aggregate is 143 Pass, 1 Pending, 0 Blocked because real Cap'n Proto generation could not run without `capnp`.

## Delta log

Append-only log of one-line deltas on every plan closure (all tiers A/B/C/D).
Format:
```
YYYY-MM-DD — [tier] — one-line description — files: a, b, c
```
For ADDED/MODIFIED/REMOVED requirement deltas, use:
```
YYYY-MM-DD — [tier] — ADDED: <what> — files: a, b, c
YYYY-MM-DD — [tier] — MODIFIED: <what changed> — files: a, b, c
YYYY-MM-DD — [tier] — REMOVED: <what removed, why> — files: a, b, c
```
Do not edit historical deltas.

2026-07-30 — [B] — ADDED: tracking system scaffold (4 charter-scoped trackers + handoffs dir + AGENTS.md charter section) populated from repo truth at commit 6260468 — files: docs/tracking/Handguard.md, docs/tracking/Structure.md, docs/tracking/Components.md, docs/tracking/Findings.md, docs/handoffs/README.md, AGENTS.md
2026-07-30 — [C] — MODIFIED: reconciled the tracking scaffold with the NT V2 Rust cutover, labelled audit-only legacy terminology, recorded 143 Pass and 1 Pending skill gates, and aligned structural/freshness contracts with the pinned baseline — files: AGENTS.md, docs/prompts/master-prompt.md, docs/tracking/Components.md, docs/tracking/Findings.md, docs/tracking/Handguard.md, docs/tracking/Structure.md
2026-07-30 — [C] — ADDED: standalone legacy-labelling compatibility gate over the canonical detector with clean-tree, unlabelled-fixture, and nearby-migration-note regression coverage — files: tools/check_legacy_labelling.py, tests/test_legacy_labelling.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: formatted and compile-gated the Criterion and iai Rust benchmark templates and removed prohibited banner comments — files: references/dev_templates/criterion_template.rs, references/dev_templates/iai_template.rs, tests/test_rust_benchmark_templates.py, docs/tracking/Findings.md
2026-07-30 — [C] — ADDED: version-scoped develop/nightly guidance for PyO3 custom-data injection and Rust actor/strategy state persistence without widening Python execution authority — files: skills/nt-backtest/SKILL.md, skills/nt-live/SKILL.md, skills/nt-trading/SKILL.md, tests/test_nt_v2_state_and_custom_data.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: aligned adapter delivery with the official ten-phase workflow and corrected current Polymarket fee and Lighter restart identity guidance — files: skills/nt-adapters/SKILL.md, skills/nt-implement/SKILL.md, skills/nt-review/AGENTS.md, references/integrations/polymarket.md, references/integrations/lighter.md, tests/test_nt_v2_adapter_overlays.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: replaced floating-point Cap'n Proto trading fields with fixed-point raw/precision values and wired schema validation into nt-implement G2; real capnp compilation remains environment-dependent — files: skills/nt-implement/templates/capnp_schema.capnp, tools/check_skill_g2_harnesses.py, tests/test_capnp_schema_precision.py, tests/test_skill_g2_harnesses.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: removed active non-AI Python authorization, converted the live curriculum to Rust LiveNode, quarantined copyable TradingNode snippets, and corrected the public V2 ExecTester projection — files: skills/nt-signals/SKILL.md, skills/nt-backtest/SKILL.md, skills/nt-dev/SKILL.md, skills/nt-testing/SKILL.md, skills/nt-learn/SKILL.md, skills/nt-strategy-builder-rust/SKILL.md, skills/nt-learn/curriculum/07-live-trading.md, references/concepts/live.md, references/integrations/okx.md, skills/nt-adapters/references/integrations/ib.md, tests/test_rust_lane_cutover.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: NT v2 compatibility note: closed reference Python classification and lint exclusion bypasses and required file-level source-pinned legacy/reference-only policy metadata without changing snapshot bodies — files: tools/template_classification.py, tests/test_template_classification.py, tests/test_quality_gates.py, ruff.toml, references/api_reference/conf.py, tools/check_dev_guide_sync.py, tests/test_dev_guide_sync.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: version-scoped current execution-spec drift for close_positions_qty_precision and constrained TC-E06/TC-E82 acceptance to the exact precision-derived residual with no open orders while preserving the immutable migration/reference snapshot — files: skills/nt-testing/SKILL.md, tests/test_exec_spec_current_overlay.py, docs/tracking/Findings.md
2026-07-30 — [C] — ADDED: exact-commit upstream delta review manifests and external exact-SHA cutover attestations so reviewed drift, verification commands, and independent verdicts cannot be inferred from stale evidence — files: references/upstream-delta-review.json, tools/check_upstream_freshness.py, tests/test_upstream_freshness.py, tools/check_cutover_attestation.py, tests/test_cutover_attestation.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: reconciled all 16 cutover findings, regenerated all 18 G0-G7 cards from fresh harness evidence, and retained real Cap'n Proto generation as one explicit Pending gate instead of overclaiming readiness — files: docs/plans/2026-07-30-nt-v2-cutover-audit-phase1.md, docs/superpowers/reports/2026-07-30-nt-v2-rust-cutover-reconciliation.md, docs/tracking/Components.md, docs/tracking/Structure.md, skills/nt*/SKILL.md, references/g2-evidence/*.json, tools/check_skill_g2_harnesses.py, tests/test_skill_g2_harnesses.py, tests/test_v2_guidance_hardening.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: extended the official ten-phase adapter workflow to the DEX skill, learner curriculum, and public inventory; bounded shared card evidence claims; encoded Cap'n Proto Pending provenance; and strengthened exact-SHA attestation inputs — files: README.md, skills/nt-dex-adapter/SKILL.md, skills/nt-dex-adapter/tests/test_dex_compliance.py, skills/nt-learn/curriculum/12-adapter-development.md, skills/nt*/SKILL.md, references/g2-evidence/*.json, tools/check_skill_g2_harnesses.py, tools/check_cutover_attestation.py, tools/upstream_baseline.py, tests/test_nt_v2_adapter_overlays.py, tests/test_skill_g2_harnesses.py, tests/test_cutover_attestation.py, tests/test_upstream_freshness.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: completed the active Rust-first learning curriculum, moved historical Python/Cython lessons into labelled migration references, made Cap'n Proto G2 output explicitly Pending, bound command and review artifacts by content hash, and validated upstream delta subjects and paths against Git — files: skills/nt-learn/curriculum/*.md, skills/nt-learn/migration_reference/python/curriculum/*.md, tools/check_skill_g2_harnesses.py, tools/check_cutover_attestation.py, tools/check_upstream_freshness.py, tests/test_rust_lane_cutover.py, tests/test_skill_g2_harnesses.py, tests/test_cutover_attestation.py, tests/test_upstream_freshness.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: required exact unique SHA and decision lines in cutover review artifacts — files: tools/check_cutover_attestation.py, tests/test_cutover_attestation.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: bound final cutover verification to a clean detached exact tree, complete committed-file inventory, and command artifact hashes — files: tools/check_cutover_attestation.py, tests/test_cutover_attestation.py, docs/tracking/Findings.md
2026-08-05 — [C] — MODIFIED: reconciled 140 upstream develop commits through 8742607995df, removed Ruff E402 test bootstrap debt, and produced exact-SHA attestation for f15fef28 — files: references/upstream-delta-review.json, tests/test_pytest_environment_split.py, tests/test_upstream_freshness.py, docs/plans/2026-08-05-nt-cutover-audit-phase1.md, docs/tracking/Findings.md
