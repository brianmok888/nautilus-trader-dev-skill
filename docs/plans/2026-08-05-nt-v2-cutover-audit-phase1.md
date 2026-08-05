---
date: 2026-08-05
status: draft
tier: C
write-targets: [docs/tracking/Findings.md, docs/tracking/Components.md]
---

# NT V2 Rust Cutover Audit: Phase 1 Findings

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode`
references in this report are migration/reference-only audit evidence. Prefer
current Rust v2/PyO3 guidance and `LiveNode` for new work.

## Review basis

- Repository SHA: `8b7ca069de6799a29ab6a4cb002aaa2754e98a21` (`main`, clean and
  equal to `origin/main`).
- Pinned NautilusTrader baseline: `6e59fd74eaacacbb7410936f1766bd89fcce6f59`.
- Resolved `origin/develop`: `8742607995df2bd0650a04cd690353353b1206da`.
- The local pinned checkout was restored at
  `/home/mok/.cache/nautilus-trader-dev-skill/nautilus_trader` and verifies the
  pinned SHA. Current upstream is 140 commits ahead of the pinned baseline.
- Official current guidance consulted: NautilusTrader Rust concept and
  developer-guide pages (`https://nautilustrader.io/docs/latest/concepts/rust/`
  and `https://nautilustrader.io/docs/latest/developer_guide/rust/`).
- Scope inventory: 18 skills and 306 Markdown files under `skills/` and
  `references/`; `templates/` does not exist at repository root, while skill
  templates are covered by the existing inventory checker.

## Findings

### V2 compliance and freshness

[P1] V2 compliance violation: the upstream freshness manifest is stale against
  the resolved authoritative `origin/develop` ref and therefore cannot certify
  current upstream review.
  file: `references/upstream-delta-review.json:4`; `tools/check_upstream_freshness.py:47-65`
  fix: Review and disposition all 100 commits between recorded reviewed commit
  `45903fc8b925adae6323035fb0b4fb5b49b4f89b` and current `origin/develop`, then
  update `reviewed_commit`, `reviewed_on`, and every delta entry with verified
  subjects, paths, and affected files or an explicit no-impact rationale.

[P1] Verification gap: the mandated freshness gate fails despite the pinned
  checkout and nightly ancestry being valid because the manifest reviewed SHA
  no longer matches the resolved develop ref.
  file: `tests/test_upstream_freshness.py:25-29`
  fix: Make the freshness gate green only after the manifest is genuinely
  reconciled; do not weaken the test or substitute the pinned SHA for moving
  `origin/develop` review evidence.

[P2] Improvement opportunity: current upstream changes include guidance-facing
  Rust/live/backtest and Python-v2 migration surfaces after the recorded review,
  but the repository has no current audit artifact classifying this drift.
  file: `docs/superpowers/reports/2026-07-30-nt-v2-rust-cutover-reconciliation.md:10-12`
  fix: Add a post-review reconciliation report that explicitly records the new
  upstream range, guidance-relevant paths, and residual skill impact.

### Verification and ship evidence

[P1] Verification gap: the full repository test suite is not green on the
  current checkout because the freshness test fails with the stale manifest.
  file: `tests/test_upstream_freshness.py:29`
  fix: Reconcile the manifest and rerun the complete `uv run pytest -q` suite.

[P1] Verification gap: repository lint is not green because three test imports
  violate Ruff E402 after `sys.path` bootstrap statements.
  file: `tests/test_pytest_environment_split.py:13`; `tests/test_upstream_freshness.py:12,18`
  fix: Replace import-path mutation with package-safe imports or add a narrowly
  scoped, justified lint configuration; add regression coverage if import
  behavior changes, then run `uv run ruff check .`.

[P1] Ship evidence gap: the mission requires an exact-SHA external attestation
  and independent post-fix review, but no attestation file is present in the
  repository or discoverable local evidence, and the committed reconciliation
  report explicitly leaves this requirement pending.
  file: `docs/superpowers/reports/2026-07-30-nt-v2-rust-cutover-reconciliation.md:25-26`; `tools/check_cutover_attestation.py:1-20`
  fix: Produce the required external attestation and independent review
  artifacts for the final exact repository SHA, then run the attestation
  verifier against those artifacts.

### Migration/reference-only legacy audit

NT v2 compatibility note: This whole section is migration/reference-only audit
prose. No new unlabelled legacy finding was observed in the scoped tree: the
fresh legacy gate passed with `Legacy labelling check passed.` Existing legacy
terms remain explicitly labelled under the repository handguard and are not
treated as current implementation guidance.

## Baseline evidence

- `uv run python tools/check_legacy_labelling.py`: **Pass**.
- `uv run python tools/check_dev_guide_sync.py`: **Pass**.
- `uv run python tools/check_dev_guide_snapshot_sync.py`: **Pass**.
- `uv run python tools/check_rust_trading_reference_sync.py`: **Pass**.
- `uv run python tools/check_skill_g2_harnesses.py --check-cards`: **Pass**.
- `uv run pytest -q`: **1 failed, 506 passed, 1 skipped**; failure is
  `test_required_develop_ref_contains_current_nightly_history` due to the stale
  upstream review manifest.
- `uv run ruff check .`: **Fail**, three E402 findings listed above.
- `uv run python tools/check_upstream_freshness.py`: **Fail** with
  `review manifest reviewed_commit does not match the resolved develop ref`.
- `git diff --check`: **Pass**.

## Phase 1 disposition

This is a read-only audit artifact. Phase 2 must address the P1 freshness and
lint findings before any readiness card is claimed fully green. Cap'n Proto
execution remains a separate pending G2 gate already documented in the prior
reconciliation report, and exact-SHA external attestation remains pending until
final ship evidence exists.
