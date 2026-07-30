# Findings — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Issue tracker + closure evidence + delta log. -->
<!-- Read when: checking issue status, finding closure evidence, reading recent deltas to understand what changed. -->
<!-- Updated when: ALWAYS on plan closure (delta entry) + on issue open/close. -->
<!-- Does NOT contain: architecture descriptions, invariants, component reviews. -->
<!-- Write-target rule: this file is the default write-target. Other files are write-targets only when their scope changed. -->

Review date: 2026-07-30

## Open issues

### NTDS-001 — ruff E402 lint debt in test_upstream_freshness.py
**Status:** open
**Severity:** low
**Description:** `tests/test_upstream_freshness.py:17` has 2 ruff E402 (module-level import not at top of file) errors. `uv run ruff check .` reports 2 errors. Does not block tests (320 passing) but blocks lint gate.
**Closure evidence:** _(pending)_

### NTDS-002 — Phase 1 Cython/legacy labelling audit not yet run
**Status:** open
**Severity:** high
**Description:** Every skill SKILL.md has between 2 and 9 Cython mentions and 4–18 legacy mentions. Per Handguard invariant #3, all Cython/v1/legacy content must be explicitly labelled. A Phase 1 deep review is required to confirm every instance is labelled `legacy:` or carries a migration note. Unlabelled instances are charter violations.
**Scope:** 18 skills × SKILL.md + reference files + templates.
**Closure evidence:** _(pending — requires Phase 1 review per mission prompt)_

### NTDS-003 — G2 gate status unverified per skill
**Status:** open
**Severity:** medium
**Description:** Per Handguard invariant #7, each skill claiming V2 compliance must have passing G2 evidence (`tools/check_skill_g2_harnesses.py`). Current per-skill G2 status is not documented in a readiness card. Phase 3 of the mission prompt asks for a cutover readiness card per skill.
**Closure evidence:** _(pending — requires Phase 3 gate checklist)_

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
