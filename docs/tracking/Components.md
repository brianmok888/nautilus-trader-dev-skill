# Components — nautilus-trader-dev-skill

NT v2 compatibility note: legacy Cython/v1 and Python `TradingNode` material in this file is migration/reference-only; prefer Rust V2/PyO3 and `LiveNode` for current work.

<!-- CHARTER -->
<!-- Role: Current per-skill behavior, ownership, and executable readiness. -->
<!-- Does NOT contain: plans, historical attestations, or removed lanes. -->

Review date: 2026-08-08
Reviewed upstream develop: `9ca072e2d98ae623f14ecaa5b336398f5d25de34`
Pinned G2 baseline: `6e59fd74eaacacbb7410936f1766bd89fcce6f59`

The repository contains 17 NautilusTrader-development skills. Each skill owns a measurable G0-G7 card and a G2 evidence file except `nt-strategy-builder`, which is migration/reference-only and has a Pending-by-design G2 card. Evidence is validated by `python3 tools/check_skill_g2_harnesses.py --check-cards`.

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
| `nt-strategy-builder` | Python strategy migration/reference | Pending by design |
| `nt-testing` | Testkit, execution specs, environment policy | Pass |
| `nt-trading` | Orders, positions, portfolio, execution | Pass |

## Shared boundaries

NT v2 compatibility note: legacy Python/Cython terms below describe migration/reference-only material.

- The `nt` router exposes only NT-development routes.
- Upstream is read-only evidence during skill-repository hardening.
- AI/advisory and downstream application work are out of scope.
- Rust V2/PyO3 is the production default; legacy Python/Cython is labelled migration/reference-only.
- G2 evidence must match the hash of each harness's declared owned content.
