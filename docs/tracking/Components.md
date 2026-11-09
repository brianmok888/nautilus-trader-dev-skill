# Components — nautilus-trader-dev-skill

NT v2 compatibility note: legacy Cython/v1 and Python `TradingNode` material in this file is migration/reference-only; prefer Rust V2/PyO3 and `LiveNode` for current work.

<!-- CHARTER -->
<!-- Role: Current per-skill behavior, ownership, and executable readiness. -->
<!-- Does NOT contain: plans, historical attestations, or removed lanes. -->

Review date: 2026-11-09
Reviewed upstream develop: `77d785c69205c4326e6aadb46d03fb45357a78f2`
Pinned G2 baseline: `77d785c69205c4326e6aadb46d03fb45357a78f2`
Latest published RC: `v2.0.0rc8` at `d53849b216e20f2c122ca01b4dd0da377638b186`

All 586 commits of the 2026-11-09 transition are reviewed exactly through `77d785c69205c4326e6aadb46d03fb45357a78f2` with per-commit evidence in
`references/upstream-delta-review.json`.

The repository contains 17 NautilusTrader-development skills. Each skill owns a measurable G0-G7 card and a G2 evidence file. `nt-strategy-builder` remains migration/reference-only; its G2 harness requires a separately prepared writable checkout with the pinned Python V2 PyO3 runtime. Evidence is validated by `python3 tools/check_skill_g2_harnesses.py --check-cards`.

All 17 skills carry current-pin G2 execution evidence (PASS) regenerated on
2026-11-09 under the signature-bound guarded environment; per-skill durable
evidence hashes match the final owned content.

| Skill | User-facing responsibility | Status |
| --- | --- | --- |
| `nt` | Scope classification and NT-only routing | Pass |
| `nt-adapters` | CeFi adapter contracts and integration patterns | Pass |
| `nt-architect` | Component and data-flow architecture | Pass |
| `nt-backtest` | Backtest engine and venue configuration | Pass |
| `nt-data` | Data engine, catalogs, subscriptions | Pass |
| `nt-dev` | Core contribution and toolchain guidance | Pass |
| `nt-dex-adapter` | DEX adapter standards and compliance | Pass |
| `nt-implement` | Rust-first component implementation | Pass |
| `nt-learn` | Rust-first V2 curriculum | Pass |
| `nt-live` | LiveNode and operational lifecycle | Pass |
| `nt-model` | Domain model contracts | Pass |
| `nt-review` | Correctness, safety, performance, and testability review | Pass |
| `nt-signals` | Indicators, order books, signals | Pass |
| `nt-strategy-builder-rust` | Production Rust strategies and LiveNode wiring | Pass |
| `nt-strategy-builder` | Python strategy migration/reference | Pass |
| `nt-testing` | Testkit, execution specs, environment policy | Pass |
| `nt-trading` | Orders, positions, portfolio, execution | Pass |

## Final readiness summary

- Upstream delta: Pass - reviewed exactly through `77d785c69205c4326e6aadb46d03fb45357a78f2`; published RC boundary `v2.0.0rc8`.
- Repository scope: Pass - 17 retained NautilusTrader-development skills; active removed-lane routes absent.
- Readiness cards: Pass - all 136 G0-G7 rows Pass with measured current-pin evidence; `python3 tools/check_skill_g2_harnesses.py --check-cards` exit 0.
- G2 execution: Pass - all 17 durable evidence files regenerated at `77d785c692` under the guarded environment (owned-content hashes match).
- Repository validation: Pass - final guarded review suite 493 passed, 10 skipped; documented validators and 499 governance receipts exit 0; independent review approved the evidence-write correction.
- Skill-pack readiness: Pass for repository guidance - current-cycle findings NT-2026-11-09-001/002/003 CLOSED with receipts.
- Shipping: Commit, integration, and push authorized; integration and push remain subject to the Phase 6 clean-primary-worktree gate. Release and publication are not authorized.
- Production strategy readiness: Not assessed - downstream strategies must run the ExecTester capability matrix and deployment acceptance gates; skill-pack evidence does not establish application readiness.

## Shared boundaries

NT v2 compatibility note: legacy Python/Cython terms below describe migration/reference-only material.

- The `nt` router exposes only NT-development routes.
- Upstream is read-only evidence during skill-repository hardening.
- Rust V2/PyO3 is the production default; legacy Python/Cython is labelled migration/reference-only.
- G2 evidence must match the hash of each harness's declared owned content.
