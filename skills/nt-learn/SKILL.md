---
name: nt-learn
description: "Use when learning NautilusTrader from scratch or deepening understanding. Provides a structured curriculum from installation to building custom NT components in Python and Rust."
---

# Learn NautilusTrader

## NT V2 Rust readiness gates

Use these gates for newly built or newly created work guided by this skill. Complete the status gate before coding and mark each gate `Pass`, `Pending`, `Blocked`, `N/A`, or `Waived`; `Pass` requires explicit docs, diff, or command evidence, and `Waived` names the owner and reason.

| Gate | Required check |
| --- | --- |
| G0 Upstream baseline | Verify latest official docs, GitHub `develop`, release tag, and local reference snapshot before copying APIs. |
| G1 Lane classification | Classify every component as Rust production/performance/live, Python research/config, AI/advisory, or labelled migration/reference work. |
| G2 Legacy label | NT v2 compatibility note: legacy Cython/v1/TradingNode template/reference guidance is reference-only; convert unlabelled guidance to Rust v2/PyO3/LiveNode before use. |
| G3 Rust ownership | Rust owns production, performance, live, networking, parsing, normalization, risk/execution state, and all execution-critical paths. |
| G4 NT V2 API shape | Use current NT V2 Rust/PyO3 APIs: `LiveNode`, builder APIs, `StrategyCore`/`DataActor` when relevant, and message bus boundaries. |
| G5 Test evidence | Capture targeted tests/checker output before readiness is `Pass`; Rust production gates usually include `cargo fmt --check`, `cargo nextest`, `cargo clippy`, `cargo deny`, and adapter/parser `scripts/fuzz-adapter.sh` or fuzz/property tests when relevant. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. |
| G7 Completion report | Reconcile all gates in the final report with status plus evidence path/command, leaving no silent `Pending` gate. |

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
