# Findings — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Issue tracker + closure evidence + delta log. -->
<!-- Read when: checking issue status, finding closure evidence, reading recent deltas to understand what changed. -->
<!-- Updated when: ALWAYS on plan closure (delta entry) + on issue open/close. -->
<!-- Does NOT contain: architecture descriptions, invariants, component reviews. -->
<!-- Write-target rule: this file is the default write-target. Other files are write-targets only when their scope changed. -->

Review date: 2026-07-30

## Open issues

No P0/P1 NT V2 Rust cutover finding remains open. Maintenance follow-ups are
tracked in `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md`.

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
**Closure evidence:** `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md` closes the post-fix audit; `uv run python tools/check_dev_guide_sync.py` passes.

### NTDS-003 — G2 gate status unverified per skill
**Status:** closed
**Severity:** medium
**Description:** Per Handguard invariant #7, each skill claiming V2 compliance must have passing G2 evidence (`tools/check_skill_g2_harnesses.py`). Current per-skill G2 status is not documented in a readiness card. Phase 3 of the mission prompt asks for a cutover readiness card per skill.
**Closure evidence:** all 18 `skills/nt*/SKILL.md` cards contain G0-G7 Pass rows; `uv run python tools/check_skill_g2_harnesses.py --check-cards` passes and `references/g2-evidence/*.json` stores G2 evidence.

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
2026-07-30 — [C] — MODIFIED: reconciled the tracking scaffold with the completed NT V2 Rust cutover, labelled audit-only legacy terminology, recorded 144 passing skill gates, and aligned structural/freshness contracts with the pinned baseline — files: AGENTS.md, docs/prompts/master-prompt.md, docs/tracking/Components.md, docs/tracking/Findings.md, docs/tracking/Handguard.md, docs/tracking/Structure.md
2026-07-30 — [C] — ADDED: standalone legacy-labelling compatibility gate over the canonical detector with clean-tree, unlabelled-fixture, and nearby-migration-note regression coverage — files: tools/check_legacy_labelling.py, tests/test_legacy_labelling.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: formatted and compile-gated the Criterion and iai Rust benchmark templates and removed prohibited banner comments — files: references/dev_templates/criterion_template.rs, references/dev_templates/iai_template.rs, tests/test_rust_benchmark_templates.py, docs/tracking/Findings.md
2026-07-30 — [C] — ADDED: version-scoped develop/nightly guidance for PyO3 custom-data injection and Rust actor/strategy state persistence without widening Python execution authority — files: skills/nt-backtest/SKILL.md, skills/nt-live/SKILL.md, skills/nt-trading/SKILL.md, tests/test_nt_v2_state_and_custom_data.py, docs/tracking/Findings.md
2026-07-30 — [C] — MODIFIED: aligned adapter delivery with the official ten-phase workflow and corrected current Polymarket fee and Lighter restart identity guidance — files: skills/nt-adapters/SKILL.md, skills/nt-implement/SKILL.md, skills/nt-review/AGENTS.md, references/integrations/polymarket.md, references/integrations/lighter.md, tests/test_nt_v2_adapter_overlays.py, docs/tracking/Findings.md
