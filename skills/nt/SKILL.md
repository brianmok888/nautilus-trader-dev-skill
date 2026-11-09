---
name: nt
description: "Entry-point router for NautilusTrader development only. Use for NautilusTrader architecture, implementation, adapters, data, backtests, live systems, testing, trading models, or core contributions; load the smallest relevant nt-* skill set instead of answering from memory."
---

# NautilusTrader Development Router

Entry-point/router skill for NautilusTrader development. Source of truth: pinned and reviewed upstream evidence from `https://github.com/nautechsystems/nautilus_trader` plus local canonical contracts.

NT v2 compatibility note: legacy, Cython/v1, Python `TradingNode`, and migration material in this whole file is migration/reference-only and never a production default.

This repository is the generic NT skill layer and covers **NautilusTrader development only**. It teaches agents to architect, implement, test, integrate, operate, and review NautilusTrader components. It is independent of downstream project-specific skills and companion repositories; this router never composes downstream consumers.

During maintenance of this skill repository, upstream NautilusTrader source, developer guides, examples, and tests are **read-only ground truth**. Do not modify the upstream evidence cache. Inspect it to verify APIs and standards; do not implement upstream features, prepare upstream commits, or treat upstream evidence as this repository's output. Separately authorized core contribution tasks use a disposable writable checkout as described below; the pinned evidence cache remains read-only.

Route all strategy implementation in this repository to Rust-first skills.

Before any artifact-producing build or native-test preparation, read and apply
the bounded-build/storage policy in
`../../references/developer_guide/contracts/environment_tooling.md`: two build
jobs, shared serialization, protected reserve plus explicit growth budget,
monitored admission and ownership-aware retention. This also applies when a
task starts through this router rather than `nt-implement`.

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
| G0 Scope and ownership | Pin and review upstream evidence without modifying upstream. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `77d785c69205c4326e6aadb46d03fb45357a78f2`; `references/upstream-delta-review.json` records the complete 586-commit reviewed transition to this pin. |
| G1 Legacy labelling | Label retained Cython/v1 and Python live material as migration/reference-only. | Pass | `python3 tools/check_legacy_labelling.py` and `python3 tools/check_dev_guide_sync.py` passed on the synchronized source tree. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `python3 tools/check_skill_g2_harnesses.py --execute --skill nt` is the current-pin harness; evidence is `references/g2-evidence/nt.json`. Pass requires its actual successful execution against `77d785c69205c4326e6aadb46d03fb45357a78f2`. A G2 `cargo check` result is compilation only; it does not prove spec, testnet, resilience, fuzz, or operations acceptance. |
| G3 Rust bindings/PyO3 | Validate selected Rust/PyO3 ownership for production implementation. | Pass | `python3 -m pytest -q tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed as part of 158 repository checks; source audits checked current Rust/PyO3 ownership and callback signatures. Runtime execution is covered separately by G2. |
| G4 Functional gates | Keep Rust production, bounded PyO3, migration, and source-pinned lanes explicit. | Pass | `python3 -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed 158 repository policy checks; this does not certify downstream application behavior. |
| G5 References and templates | Run repository and domain tests for routed work. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` and `python3 tools/check_rust_trading_reference_sync.py` passed; exact source comparisons covered 22 shared guides, 33 trading source files, 81 analysis files, and 23 matching adapter examples. |
| G6 Operational and migration boundaries | Execute selected repository policy checks. | Pass | `python3 tools/check_legacy_labelling.py` and the 158-test source-policy run passed for migration labels, language lanes, precision, callbacks, and fail-closed guidance; live venue acceptance remains change-specific. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | `references/g2-evidence/nt.json` records current-pin G2 execution (status pass, owned-content hash match); mission closure receipts under `docs/tracking/receipts/nt-v2-rc-20261109/`; `python3 tools/check_governance_receipts.py` validated 497 receipts. |

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
3. Before substantive work in the target repository, pull the latest dependency versions as a prerequisite: query the authoritative upstream registry live (PyPI for Python packages, crates.io for Rust crates), refresh the target repository's lockfile to the latest upstream versions for the affected surface, and run the target repository's validation gates for it. The local lock state is a fact about the repository, never the ceiling; a companion skill's pinned versions are evidence about upstream, not the target repository's dependency truth. Exact-version compatibility gates in the target repository are re-validated and updated as part of the same change, never weakened to pass.
4. Confirm version-sensitive APIs from pinned and reviewed upstream evidence.
5. Implement in the user's target repository. Upstream contribution work uses a disposable writable clone or worktree; the pinned cache is evidence-only and is never an edit or build target.
6. Run the selected skill's G2 harness and task-level tests.
7. Finish with `nt-review` for production-facing, live, adapter, or cross-component changes.

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


Current source pin: `77d785c69205c4326e6aadb46d03fb45357a78f2`. The latest
published RC is `v2.0.0rc8`; develop is an unreleased rc9 source boundary.
See `references/README.md`. Older commit-specific notes below are historical
review context; they do not establish current G2 execution or release availability.

The authoritative pinned upstream commit is `77d785c69205c4326e6aadb46d03fb45357a78f2`; canonical guide contracts live under `references/developer_guide/`, and reviewed current-develop overlays are version-scoped in `references/upstream-delta-review.json`.

## Boundaries

- Do not invent upstream APIs or cite paths that were not inspected.
- Do not treat migration/reference-only examples as production defaults.
- Enforce no cross-contamination: do not expand a NautilusTrader task into AI or non-NT work.
- Do not develop NautilusTrader itself while executing this repository's master prompt; improve the skill artifacts instead.
