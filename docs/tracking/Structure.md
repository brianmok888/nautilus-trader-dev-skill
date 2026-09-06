# Structure — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Current structural wiring, skill inventory, evidence layers, and validation surfaces. -->
<!-- Updated when: skill inventory, repository boundaries, or validation wiring changes. -->
<!-- Does NOT contain: plans, historical attestations, or session state. -->

Review date: 2026-09-04

## Repository shape

- **Mission:** reusable NautilusTrader development skills only
- **Skills:** 17 `nt*` skills, routed by `skills/nt/SKILL.md`
- **Content:** Markdown guidance and references, Rust examples/contracts, Python repository validators and migration references
- **Upstream:** pinned reproducible checkout at `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d` plus preserved reviewed transition history; read-only evidence
- **Validation:** pytest, deterministic sync/freshness checks, legacy labelling, Findings schema, static-quality orchestration, progressive cutover gates, and per-skill G2 harness cards
- **Excluded:** downstream application skills, session state, handoffs, completed plans, and external attestations

## Skill inventory

| Skill | Role | Default status |
| --- | --- | --- |
| `nt` | Entry router and scope boundary | Current |
| `nt-architect` | Component and data-flow architecture | Current |
| `nt-implement` | Rust-first implementation workflow | Current |
| `nt-strategy-builder-rust` | Production Rust strategy and LiveNode path | Current |
| `nt-strategy-builder` | Python strategy migration/reference | Migration-only |
| `nt-review` | Architecture and code review | Current |
| `nt-adapters` | CeFi adapter contracts | Current |
| `nt-dex-adapter` | Custom DEX adapter contracts | Current |
| `nt-backtest` | Backtest configuration and execution | Current |
| `nt-data` | Data engine, catalogs, subscriptions | Current |
| `nt-dev` | Core contribution and toolchain guidance | Current |
| `nt-learn` | Structured learning curriculum | Current |
| `nt-live` | LiveNode, reconciliation, operations | Current |
| `nt-model` | Domain model contracts | Current |
| `nt-signals` | Indicators, order books, signal pipelines | Current |
| `nt-testing` | Testkit and environment guidance | Current |
| `nt-trading` | Orders, positions, portfolio, execution | Current |

## Evidence layers

1. `tools/upstream_baseline.py` defines the reproducible pin.
2. `references/upstream-delta-review.json` records reviewed post-pin changes.
3. `references/developer_guide/contracts/` holds canonical local contracts; the adapter snapshot carries field-contract precision rules and the Rust skills carry LiveNode reconciliation/lifecycle acceptance criteria.
4. `references/g2-evidence/` records per-skill executable evidence and owned-content hashes.
5. `references/api_reference/` (45 pages incl. `model/` and `adapters/`) mirrors the pinned upstream `docs/api_reference/` v2 surfaces: flat `nautilus_trader.<pkg>` automodules with per-page owning-crate pointers, last fully regenerated against pin `4692bac` (NT-2026-09-04-119/128/131); drift against the `ac22d5cf` pin is tracked by the 2026-09-05 audit. Legacy v1 snapshots survive only in sanctioned migration zones.
6. `docs/tracking/` records current invariants, structure, components, and findings.

## Validation surfaces

| Surface | Purpose |
| --- | --- |
| `tools/check_dev_guide_sync.py` | Skill/reference consistency |
| `tools/check_dev_guide_snapshot_sync.py` | Pinned snapshot integrity |
| `tools/check_upstream_freshness.py` | Reviewed current-develop freshness |
| `tools/check_rust_trading_reference_sync.py` | Rust trading contract alignment |
| `tools/check_legacy_labelling.py` | Migration-only labelling across active guidance |
| `tools/check_findings_schema.py` | Current Findings ID, status, field, and closure schema |
| `tools/check_static_quality.py` | Canonical deterministic static-quality orchestration |
| `docs/tracking/CutoverGateTemplate.md` | Standard progressive cutover evidence contract |
| `tools/check_skill_g2_harnesses.py` | G2 declaration, execution, and evidence validation |
| `tools/template_classification.py` | Shipped Python classification policy |
| `tests/test_repository_scope_cleanup.py` | NT-only repository boundary |
