---
name: nt-learn
description: "Use when learning NautilusTrader from scratch or deepening understanding through a Rust-first V2 curriculum with bounded PyO3 and labelled migration references."
---

# Learn NautilusTrader

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `77d785c69205c4326e6aadb46d03fb45357a78f2`; `references/upstream-delta-review.json` records the complete 586-commit reviewed transition to this pin. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `python3 tools/check_legacy_labelling.py` and `python3 tools/check_dev_guide_sync.py` passed on the synchronized source tree. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `python3 tools/check_skill_g2_harnesses.py --execute --skill nt-learn` is the current-pin harness; evidence is `references/g2-evidence/nt-learn.json`. Pass requires its actual successful execution against `77d785c69205c4326e6aadb46d03fb45357a78f2`. A G2 `cargo check` result is compilation only; it does not prove spec, testnet, resilience, fuzz, or operations acceptance. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `python3 -m pytest -q tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed as part of 158 repository checks; source audits checked current Rust/PyO3 ownership and callback signatures. Runtime execution is covered separately by G2. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `python3 -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed 158 repository policy checks; this does not certify downstream application behavior. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` and `python3 tools/check_rust_trading_reference_sync.py` passed; exact source comparisons covered 22 shared guides, 33 trading source files, 81 analysis files, and 23 matching adapter examples. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `python3 tools/check_legacy_labelling.py` and the 158-test source-policy run passed for migration labels, language lanes, precision, callbacks, and fail-closed guidance; live venue acceptance remains change-specific. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | `references/g2-evidence/nt-learn.json` records current-pin G2 execution (status pass, owned-content hash match); mission closure receipts under `docs/tracking/receipts/nt-v2-rc-20261109/`; `python3 tools/check_governance_receipts.py` validated 497 receipts. |


Learning gates: the active curriculum uses Rust for research, configuration, backtests, strategies, adapters, and live runtime work. Older Python labs are migration/reference-only; non-NautilusTrader development lanes are outside this repository. Learners mark `Pending` until they can run the matching Rust build/test/check commands and explain each gate.

This is the Rust-first curriculum. Its legacy/Python labelling points only to
physically quarantined migration material, not an active implementation lane.

## Rust production lane

Teach the Rust architecture, model types, data flow, strategy lifecycle, backtest runtime, and `LiveNode` path as the default progression toward production readiness. A learner completes this lane by building and testing Rust components and explaining deterministic ordering, fixed-point precision, risk, and lifecycle boundaries.

## PyO3 control-plane lane

Teach PyO3 as the bounded interface for typed configuration, Rust component registration, node lifecycle control, and result inspection. Learners must be able to explain why Python does not own order execution, market-data handlers, risk decisions, adapter state, or live-node liveness.

## Migration/reference lane

NT v2 compatibility note: older Python and v1 curriculum material belongs under `migration_reference/` and is used only to understand or migrate an existing system.

## Source-pinned upstream lane


Current source pin: `77d785c69205c4326e6aadb46d03fb45357a78f2`. The latest
published RC is `v2.0.0rc8`; develop is an unreleased rc9 source boundary.
See `references/README.md`. Older commit-specific notes below are historical
review context; they do not establish current G2 execution or release availability.

Anchor lessons and API exercises to [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at immutable commit `77d785c69205c4326e6aadb46d03fb45357a78f2`, and identify newer upstream examples as version-scoped before using them.

## Overview

A structured Rust-first pathway from installation and domain concepts through
Rust strategies, adapters, backtests, PyO3 control boundaries, and complete Rust
trading systems. Historical Python strategies are migration/reference-only.

## Workflow

1. Ask: "What's your current level with NautilusTrader?"
   - **Brand new** → Start at Stage 01
   - **Can run examples** → Start at Stage 03
   - **Can write strategies** → Start at Stage 05
   - **Want to learn Rust internals** → Start at Stage 08
   - **Want to write full Rust trading systems** → Start at Stage 09
   - **Want to build/extend NT** → Start at Stage 10
2. Work through stages sequentially from entry point
3. Each stage has concepts, exercises, and a checkpoint
4. Ask user for local NT path at first source exploration

## Curriculum

| Stage | Topic | Prerequisites | Key Skill |
|-------|-------|--------------|-----------|
| 01 | Setup & Installation | None | nt-dev |
| 02 | Running Examples | Stage 01 | — |
| 03 | Architecture Foundations | Stage 02 | nt-model |
| 04 | First Strategy | Stage 03 | nt-trading |
| 05 | Backtesting Deep Dive | Stage 04 | nt-backtest |
| 06 | Indicators & Actors | Stage 05 | nt-signals |
| 07 | Live Trading | Stage 06 | nt-live |
| 08 | Rust Internals | Stage 07 | nt-dev |
| 09 | Full Rust Trading | Stage 08 | nt-trading |
| 10 | Building NT | Stage 09 | nt-dev, nt-testing |
| 11 | Testing & Quality | Stage 10 | nt-testing |
| 12 | Adapter Development | Stage 11 | nt-adapters |

## Stage Files

Each stage is in `curriculum/NN-topic.md`. Load the appropriate stage file based on where the user is.

Pinned-baseline refresh inventory: when `tools/upstream_baseline.py` moves the pinned upstream commit, refresh the source-pinned example references in `curriculum/01-setup.md`, `curriculum/02-run-examples.md`, `curriculum/04-first-strategy.md`, `curriculum/05-backtesting.md`, `curriculum/06-indicators-actors.md`, `curriculum/07-live-trading.md` (it cites the concrete commit), `curriculum/09-full-rust-trading.md`, `curriculum/11-testing-quality.md`, and `curriculum/12-adapter-development.md`; the remaining stage files carry no pin-bound examples.
