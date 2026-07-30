---
name: nt-learn
description: "Use when learning NautilusTrader from scratch or deepening understanding through a Rust-first V2 curriculum with bounded PyO3 and labelled migration references."
---

# Learn NautilusTrader

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; current-develop drift is version-scoped in `README.md`. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 25 tests. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-learn` passed the skill domain's scoped examples and owners against `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; schema-v2 provenance is recorded in `references/g2-evidence/nt-learn.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 tests. |
| G4 Lane and API shape | Classify migration-only Python, active AI/advisory Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'` passed 24 tests. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md` records the post-fix findings, validation commands, gate results, and residual risk. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Learning gates: the Rust-first curriculum is the default for production readiness, while Python labs are labelled Python research/config or AI/advisory and legacy/Python labelling is required before using older examples. Learners mark `Pending` until they can run the matching Rust build/test/check commands and explain each gate.

## Rust production lane

Teach the Rust architecture, model types, data flow, strategy lifecycle, backtest runtime, and `LiveNode` path as the default progression toward production readiness. A learner completes this lane by building and testing Rust components and explaining deterministic ordering, fixed-point precision, risk, and lifecycle boundaries.

## PyO3 control-plane lane

Teach PyO3 as the bounded interface for typed configuration, Rust component registration, node lifecycle control, and result inspection. Learners must be able to explain why Python does not own order execution, market-data handlers, risk decisions, adapter state, or live-node liveness.

## Migration/reference lane

Older non-AI Python and v1 curriculum material belongs under `migration_reference/` and is used only to understand or migrate an existing system. The only active Python lane is AI/advisory, which remains asynchronous and non-authoritative.

## Source-pinned upstream lane

Anchor lessons and API exercises to [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at immutable commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59`, and identify newer upstream examples as version-scoped before using them.

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
