---
name: nt-learn
description: "Use when learning NautilusTrader from scratch or deepening understanding. Provides a structured curriculum from installation to building custom NT components in Python and Rust."
---

# Learn NautilusTrader

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as f20f8af36e0f488779d3f543a217b2d19ea2db81. |
| G1 Lane classification | Classify the work as Rust execution-critical/performance, supported Python V2 strategy/config, Python AI/advisory, or legacy. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template lane inventory and Python/Rust V2 strategy boundary tests. |
| G2 Legacy label | Label legacy Cython/v1 and Python live TradingNode guidance as migration/reference-only. | Pass | Compatibility note in this file names legacy Cython/v1 and Python live `TradingNode` as migration/reference-only. |
| G3 Rust ownership | Rust owns runtime, adapter networking/parsing, normalization, risk/execution state, and performance-sensitive paths; Python and Rust strategies remain supported V2 surfaces. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the ownership-boundary regression tests; `references/developer_guide/python.md:12-14` records upstream Python strategy support. |
| G4 NT V2 API shape | Use current NT V2/PyO3 API shapes and crate/module boundaries instead of retired APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` byte-compared all 18 guide bodies to pinned upstream f20f8af; `uv run pytest -q tests/test_v2_guidance_hardening.py` passed current API-shape regressions. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 253 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 106 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | Cutover commits `8a7d985..4f044f5` were pushed to `origin/main`; independent code review returned APPROVE and architecture review returned CLEAR. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Learning gates: the Rust-first curriculum is the default for production readiness, while Python labs are labelled Python research/config or AI/advisory and legacy/Python labelling is required before using older examples. Learners mark `Pending` until they can run the matching Rust build/test/check commands and explain each gate.

## Overview

A structured learning pathway from beginner to NT developer. Walks through installation, examples, concepts, and progressively deeper implementation — from Python strategies to Rust internals to full Rust trading systems.

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
