# Handguard — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Non-negotiable invariants. "Must never" / "must always" rules. -->
<!-- Read when: checking if X is allowed, validating against constraints. -->
<!-- Updated when: a new invariant is introduced or an existing rule changes. -->
<!-- Does NOT contain: closures, architecture facts, component readiness, plans. -->
<!-- Write-target rule: only update this file if an invariant changed. -->

Review date: 2026-07-30
Purpose: non-negotiable rules for NT V2 Rust cutover skill work.

## 1. Rust-first authority

1. **All new skill content MUST default to Rust-first / NT V2.** Default strategy, LiveNode, and execution guidance routes through `skills/nt-strategy-builder-rust/`. The Python `skills/nt-strategy-builder/` is migration/reference-only and MUST NOT be offered as the default for new work.
2. **The AI/EvoMap lane is the ONLY permitted Python lane.** It is advisory-only and MUST NEVER be treated as execution authority. No other skill should introduce Python as a primary path.

## 2. Legacy labelling

NT v2 compatibility note: Cython, v1, and legacy terms in this section describe
migration/reference-only controls. They are prohibited as production defaults;
new non-AI guidance remains Rust-first and PyO3-oriented.

3. **All Cython, v1, or legacy content MUST be explicitly labelled.** Every instance of Cython syntax (`cdef`, `cpdef`, `.pyx`), v1-only API, or migration-history references MUST carry an explicit `legacy:` label or migration note. Unlabelled legacy content is a charter violation.
4. **Legacy content MUST NOT be promoted as current guidance.** Content labelled `legacy:` is reference/migration-history only and MUST NOT appear in "how to do X" sections without an active V2/Rust alternative alongside it.

## 3. Canonical contracts

5. **Skills MUST follow the developer-guide contracts in `references/developer_guide/contracts/`.** When a skill's guidance conflicts with a contract, the contract wins. Contracts are the agent-actionable extraction of NT official docs.
6. **Authority hierarchy MUST be respected when sources disagree:** NT source code > NT official docs > developer-guide contracts > skill SKILL.md files > other references.

## 4. G2 gate discipline

7. **Skill examples MUST validate against the immutable pinned NT V2 baseline.** The G2 evidence harness (`tools/check_skill_g2_harnesses.py`) is the gate. A skill claiming V2 compliance MUST have passing G2 evidence; status is `Pending` until evidence exists.
8. **Deterministic sync checkers MUST stay green, and freshness drift MUST be reviewed.** `check_dev_guide_sync.py` and `check_rust_trading_reference_sync.py` are deterministic gates. `check_upstream_freshness.py` is a moving-ref detector whose non-zero drift result requires deliberate review and baseline reconciliation, not suppression.

## 5. Upstream alignment

9. **Local references are summaries, not authority.** They summarize official NT pages with source metadata. When NT upstream changes, references MUST be updated via the sync checker workflow, not hand-edited to look current.
10. **Stale snapshots MUST NOT be presented as current.** The `Generated:` / `Commit:` / `NT alignment:` headers in AGENTS.md and reference files are the freshness markers. Editing them without an actual sync is fabrication.
