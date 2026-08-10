# Findings — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Current evidence-backed findings and closure state. -->
<!-- Does NOT contain: session history, plans, or external attestations. -->

Review date: 2026-08-10

## Open findings

None.

## Closed in current working tree

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

- Removed the AI/EvoMap skill lane, sidecar, templates, tests, and G2 evidence.
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
