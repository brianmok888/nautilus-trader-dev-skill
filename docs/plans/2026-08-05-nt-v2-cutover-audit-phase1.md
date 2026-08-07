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

- Repository baseline SHA: `a496b58f4d32641c6775f45ac8dbb70b6527063a` (`main`, equal to
  `origin/main` before the current uncommitted audit corrections); this report
  was reconciled against the current working tree.
- Pinned NautilusTrader baseline: `6e59fd74eaacacbb7410936f1766bd89fcce6f59`.
- The freshness manifest records the reviewed current-develop overlay at
  `8742607995df2bd0650a04cd690353353b1206da`
  (`references/upstream-delta-review.json:4`).
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

### Rust conversion gaps (P0)

No P0 Rust-conversion finding was raised in the scoped audit. Active non-AI
guidance is routed through Rust-first skills, while retained Python material is
explicitly migration/reference-only or part of the AI/EvoMap advisory lane; the
post-fix reconciliation records the closed P0 findings.

### V2 compliance and freshness

[P1] V2 compliance violation: stale upstream freshness manifest.
  file: `references/upstream-delta-review.json:4`; `tools/check_upstream_freshness.py:47-65`
  fix: Update the reviewed-develop manifest and rerun the freshness checker.
  disposition: Closed. The manifest now records reviewed commit
  `8742607995df2bd0650a04cd690353353b1206da` and the freshness gate passes.

[P1] Verification gap: freshness gate failed against the stale manifest.
  file: `tests/test_upstream_freshness.py:25-29`
  fix: Refresh stale verification evidence and rerun the freshness gate.
  disposition: Closed. `uv run python tools/check_upstream_freshness.py` exits 0
  with the reconciled manifest.

[P2] Improvement opportunity: upstream drift needs an explicit review artifact.
  file: `references/upstream-delta-review.json:6`; `docs/superpowers/reports/2026-07-30-nt-v2-rust-cutover-reconciliation.md:1-8`
  fix: Record the reviewed upstream range and disposition its current-develop delta.
  disposition: Closed. The manifest and reconciliation report record the
  current-develop review range and its evidence boundary.

### Verification and ship evidence

[P1] Verification gap: stale audit evidence reported a failing full test suite and lint.
  file: `tests/test_upstream_freshness.py:25-29`; `tests/test_pytest_environment_split.py:13`
  fix: Rerun the full test and lint commands and replace stale failure evidence.
  disposition: Closed. Fresh runs report `507 passed, 1 skipped` and `All checks passed!`.

[P1] Ship evidence gap: exact-SHA attestation and independent post-fix review.
  file: `tools/check_cutover_attestation.py:1-20`
  fix: Obtain independent review artifacts, commit the reconciled tree, and run the exact-SHA attestation verifier.
  disposition: Pending external attestation. The verifier is available, but an
  attestation cannot truthfully be created by the authoring session without
  independent reviewer artifacts and a final committed SHA.

### Legacy unlabelled content (P1)

No new unlabelled legacy finding was raised in the scoped tree. The dedicated
migration/reference audit and its full-tree checker are documented below.

### Improvement opportunities (P2)

The upstream-drift improvement finding is recorded in the V2 compliance section
above; no additional untracked P2 finding was raised.

### Migration/reference-only legacy audit

NT v2 compatibility note: This whole section is migration/reference-only audit
prose. No new unlabelled legacy finding was observed in the scoped tree: the
fresh legacy gate passed with `Legacy labelling check passed.` Existing legacy
terms remain explicitly labelled under the repository handguard and are not
treated as current implementation guidance.

## Baseline evidence

- `uv run python tools/check_legacy_labelling.py`: **Pass** — `Legacy labelling check passed.`
- `uv run python tools/check_dev_guide_sync.py`: **Pass** — `Developer guide sync checks passed.`
- `uv run python tools/check_dev_guide_snapshot_sync.py`: **Pass** — snapshot bodies match pinned upstream.
- `uv run python tools/check_rust_trading_reference_sync.py`: **Pass** — references match pinned examples; this sync gate is included in the current verification and attestation command set.
- `uv run python tools/check_upstream_freshness.py`: **Pass** — reviewed overlay is current.
- Staged-toolchain `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-implement`: **Pass in the staged environment** — nt-implement's Cap'n Proto schema compiler and owning-crate checks ran against the pinned baseline; this result is environment-specific evidence, while a clean environment without Cap'n Proto remains Pending.
- `uv run python tools/check_skill_g2_harnesses.py --check-cards`: **Pass** — 18 cards validated; 143 G0-G7 rows are Pass and nt-implement G2 is Pending in the standard environment.
- `uv run pytest -q --ignore=tests/test_quality_gates.py`: **500 passed, 1 skipped**.
- `uv run pytest -q tests/test_quality_gates.py`: **7 passed**.
- `uv run pytest -q`: **507 passed, 1 skipped**.
- `uv run --with ruff ruff check .`: **Pass** — `All checks passed!`.
- `python3 -m compileall -q tools tests skills/nt-evomap-integration/python_sidecar/brainstorming_evomap`: **Pass**.
- `git diff --check`: **Pass**.

## Phase 1 disposition

The freshness, test, and lint findings are closed against the reconciled tree.
The staged-toolchain Cap'n Proto run provides local G2 evidence, but the durable
G2 state remains environment-dependent until the compiler is available in the
standard verification environment. Residuals are exact-SHA attestation,
independent review evidence, reproducible Cap'n Proto availability, the
historical red-before-green proof required for each Phase 2 segment, and the
methodology skills named by the mission that are not installed in this runtime.
The current green tests verify behavior, but cannot reconstruct that historical
TDD sequence without the unavailable workflow skill or session artifacts:
`$superpowers:code-review`, `$oh-my-codex:best-practice-research`,
`$superpowers:brainstorming`, `$superpowers:test-driven-development`,
`$superpowers:verification-before-completion`, and
`$superpowers:requesting-code-review`.
