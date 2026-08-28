---
name: nt
description: "Entry-point router for NautilusTrader development only. Use for NautilusTrader architecture, implementation, adapters, data, backtests, live systems, testing, trading models, or core contributions; load the smallest relevant nt-* skill set instead of answering from memory."
---

# NautilusTrader Development Router

Entry-point/router skill for NautilusTrader development. Source of truth: pinned and reviewed upstream evidence from `https://github.com/nautechsystems/nautilus_trader` plus local canonical contracts.

NT v2 compatibility note: legacy, Cython/v1, Python `TradingNode`, and migration material in this whole file is migration/reference-only and never a production default.

This repository is the generic NT skill layer and covers **NautilusTrader development only**. It teaches agents to architect, implement, test, integrate, operate, and review NautilusTrader components. It is independent of downstream project-specific skills and companion repositories; this router never composes downstream consumers.

Upstream NautilusTrader source, developer guides, examples, and tests are **read-only ground truth**. Inspect them to verify APIs and standards. Do not modify the upstream repository, implement upstream features, prepare upstream commits, or treat upstream evidence as this repository's output.

Route all strategy implementation in this repository to Rust-first skills.

## Default direction

- Prefer Rust V2, PyO3, and `LiveNode` for new Rust-backed work; this is the repository's Rust-oriented v2.0 readiness path.
- NT v2 compatibility note: treat legacy Cython/v1 and Python `TradingNode` material as migration/reference-only guidance, never a production default.
- Verify version-sensitive guidance against the pinned baseline and the reviewed current-develop delta before copying an API.
- Never compose downstream consumer skills from this generic NT router.

## NT V2 Rust readiness gates

This card records current router readiness. Re-run cited evidence and use `Pending` or `Blocked` when proof is unavailable.

NT v2 compatibility note: legacy Cython/v1 and Python live TradingNode references in this table are migration/reference-only; prefer Rust V2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Pin and review upstream evidence without modifying upstream. | Pass | `tools/check_dev_guide_snapshot_sync.py` and `references/upstream-delta-review.json` distinguish the immutable baseline from reviewed current-develop overlays. |
| G1 Legacy labelling | Label retained Cython/v1 and Python live material as migration/reference-only. | Pass | `tools/check_legacy_labelling.py` enforces explicit labels and current alternatives. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt` passed the aggregate router harness at `19df7796`; `references/g2-evidence/nt.json` records provenance. Every retained child has current durable G2 evidence, including hybrid executable/static evidence for the migration-only `nt-strategy-builder` lane. |
| G3 Rust bindings/PyO3 | Validate selected Rust/PyO3 ownership for production implementation. | Pass | Domain skills and `nt-strategy-builder-rust` own version-scoped bindings guidance. |
| G4 Functional gates | Keep Rust production, bounded PyO3, migration, and source-pinned lanes explicit. | Pass | `tests/test_markdown_lane_contract.py` validates all four structural lanes. |
| G5 References and templates | Run repository and domain tests for routed work. | Pass | `python3 -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` validates router contracts; domain skills own executable checks. |
| G6 Operational and migration boundaries | Execute selected repository policy checks. | Pass | `nt-testing` and `nt-review` are required for production-facing, live, adapter, and cross-component work. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current evidence is recorded in `references/g2-evidence/nt.json`; repository closure is summarized in `docs/tracking/Findings.md`. |

## Routing

`nt-strategy-builder-rust` is the default for new Rust strategy implementation and `LiveNode` wiring. Ambiguous strategy requests default to Rust.

Production strategy or live-node work | `skills/nt-strategy-builder-rust/` Load only the skills required by the task.

Ambiguous ("build a strategy", no language stated) -> `nt-strategy-builder-rust`.
Python strategy ("build a strategy in Python") -> `nt-strategy-builder-rust` ONLY under this repository's Rust-first policy.

| User intent | Load |
| --- | --- |
| Design component boundaries or data flow | `nt-architect` plus relevant domain skills |
| Implement strategies, actors, indicators, or components | `nt-implement`; add `nt-strategy-builder-rust` for production strategy work |
| Backtests, fill models, simulated venues, backtest configs | `nt-backtest`, `nt-strategy-builder-rust`, `nt-testing` |
| Build live runtime configuration or reconciliation | `nt-live`, `nt-testing`, `nt-review` |
| Work with market data, catalogs, or subscriptions | `nt-data` |
| Work with orders, positions, portfolio, or execution models | `nt-trading`, `nt-model` |
| Build CeFi adapter integration | `nt-adapters`, `nt-live`, `nt-testing` |
| Build custom DEX adapter integration | `nt-dex-adapter`, `nt-data`, `nt-testing` |
| Build indicators, order-book signals, or signal pipelines | `nt-signals`, `nt-data` |
| Contribute to NautilusTrader core | `nt-dev`, `nt-testing`, and the owning domain skill |
| Learn NautilusTrader systematically | `nt-learn` |
| Review NT code or architecture | `nt-review` plus the owning implementation/domain skill |
| Maintain this skill repository | follow `docs/prompts/master-prompt.md`; upstream remains read-only |

## Operating sequence

1. Classify the request by NT subsystem and lifecycle stage; record the NT runtime version and implementation language when stated or detectable.
2. Load the smallest matching skill set from the table.
3. Confirm version-sensitive APIs from pinned and reviewed upstream evidence.
4. Implement in the user's target repository. Upstream contribution work uses a disposable writable clone or worktree; the pinned cache is evidence-only and is never an edit or build target.
5. Run the selected skill's G2 harness and task-level tests.
6. Finish with `nt-review` for production-facing, live, adapter, or cross-component changes.

Example: route backtest wiring plus validation to `nt-strategy-builder-rust`,
`nt-backtest`, and `nt-testing` together.

## Rust production lane

New production strategies, components, live wiring, adapters, and execution logic route to the owning Rust-first skills above.

## PyO3 control-plane lane

Use bounded public PyO3 projections only when a current upstream binding contract requires them; Python does not own execution authority.

## Migration/reference lane

NT v2 compatibility note: the legacy runtime material in this block is migration/reference-only.

Migration/reference-only legacy material is physically quarantined under each skill's `migration_reference/` or `legacy_migration/` directory. An explicitly labelled inline interoperability boundary may only point into that quarantined material; it is never a production default. Requests tied to a legacy runtime route to the owning skill's migration/reference lane; do not answer them with current V2 APIs as though the runtime were V2.

## Source-pinned upstream lane

The authoritative pinned upstream commit is `19df7796fcce341ca6c1f6a503fca2c7bf300e6c`; canonical guide contracts live under `references/developer_guide/`, and reviewed current-develop overlays are version-scoped in `references/upstream-delta-review.json`.

## Boundaries

- Do not invent upstream APIs or cite paths that were not inspected.
- Do not treat migration/reference-only examples as production defaults.
- Enforce no cross-contamination: do not expand a NautilusTrader task into AI or non-NT work.
- Do not develop NautilusTrader itself while executing this repository's master prompt; improve the skill artifacts instead.
