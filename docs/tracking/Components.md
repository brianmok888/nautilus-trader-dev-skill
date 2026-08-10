# Components — nautilus-trader-dev-skill

NT v2 compatibility note: legacy Cython/v1 and Python `TradingNode` material in this file is migration/reference-only; prefer Rust V2/PyO3 and `LiveNode` for current work.

<!-- CHARTER -->
<!-- Role: Current per-skill behavior, ownership, and executable readiness. -->
<!-- Does NOT contain: plans, historical attestations, or removed lanes. -->

Review date: 2026-08-10
Reviewed upstream develop: `90b3d71b0e2e5ec8fa4b366cbf68a8f04996b4c1`
Pinned G2 baseline: `6e59fd74eaacacbb7410936f1766bd89fcce6f59`

The repository contains 17 NautilusTrader-development skills. Each skill owns a measurable G0-G7 card and a G2 evidence file. `nt-strategy-builder` remains migration/reference-only; its pinned V2 Python harness now passes after building the exact upstream environment. Evidence is validated by `python3 tools/check_skill_g2_harnesses.py --check-cards`.

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

- Upstream delta: Pass — reviewed exactly through `90b3d71b0e2e5ec8fa4b366cbf68a8f04996b4c1`.
- Repository scope: Pass — 17 retained NautilusTrader-development skills; active removed-lane routes absent.
- Readiness cards: 136 Pass, 0 Blocked, 0 Pending across 136 G0-G7 gates.
- G2 execution: all 17 skill harnesses pass in the current environment; `nt-strategy-builder` passed 32 repository migration tests and 69 pinned-upstream V2 tests with 6 explicit post-cutover skips.
- Legacy labelling, guide snapshots, and Rust trading references: Pass.
- Release readiness: all 17 NT-development skill cards are green; AI/EvoMap remains excluded rather than assessed.

## Shared boundaries

NT v2 compatibility note: legacy Python/Cython terms below describe migration/reference-only material.

- The `nt` router exposes only NT-development routes.
- Upstream is read-only evidence during skill-repository hardening.
- AI/advisory and downstream application work are out of scope.
- Rust V2/PyO3 is the production default; legacy Python/Cython is labelled migration/reference-only.
- G2 evidence must match the hash of each harness's declared owned content.
