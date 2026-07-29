---
name: nt
description: "Entry-point/router skill for any NautilusTrader or nautilus_trader task. Use when the user asks for NautilusTrader help, says nt, asks which Nautilus skill to use, or gives a trading-system, strategy, adapter, data, backtest, live, testing, or core-contribution task without naming a more specific nt-* skill. Routes to and loads the relevant NautilusTrader skills instead of answering from memory alone."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# NautilusTrader Entry Skill

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; current-develop drift is version-scoped in `README.md`. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 25 tests. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt` passed the skill domain's scoped examples and owners against `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; schema-v2 provenance is recorded in `references/g2-evidence/nt.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 tests. |
| G4 Lane and API shape | Classify migration-only Python, active AI/advisory Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'` passed 24 tests. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md` records the post-fix audit; `uv run python tools/check_skill_g2_harnesses.py --check-cards` validates all 18 cards and evidence artifacts. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Router-specific gates: route all non-AI strategy, configuration, backtest, paper, live, production, and performance work to Rust skills first (`nt-strategy-builder-rust`, `nt-adapters`, `nt-live`, `nt-trading`, `nt-dev`). Keep `nt-strategy-builder` migration/reference-only, route AI advisory work to `nt-evomap-integration`, and require the final router answer to include the gate status table before calling new NT work ready.

Upstream NT V2 supports Python strategies and documents them as a current extension surface; this repository applies a stricter cutover policy. New strategy, configuration, backtest, paper, live, and production guidance is Rust-oriented. The only active Python lane is AI/advisory through `nt-evomap-integration`, which remains non-authoritative and off execution-critical paths; existing Python strategy material is migration/reference-only.

Use this as the start point for NautilusTrader work. It does not replace the
specialized `nt-*` skills; it chooses which ones to load and how to sequence
them.

## Source of truth

Prioritize current NautilusTrader sources over downstream skill repos:

1. Local references in this repo that mirror or summarize official docs.
2. Official docs: <https://nautilustrader.io/docs/latest/>
3. Official repo: <https://github.com/nautechsystems/nautilus_trader>

If local guidance conflicts with official docs or the official repo, treat the
official source as authoritative and update/report the local drift.

## Routing protocol

1. Classify the user's goal.
2. Pick one **primary** skill and zero to three **supporting** skills from the
   table below.
3. Read the primary skill's `SKILL.md`. Read supporting `SKILL.md` files only
   when their scope affects the task.
4. Follow the loaded specialized skill instructions; do not duplicate all
   Nautilus guidance in this entry skill.
5. For implementation or review work, verify with the repo's relevant tests and
   `tools/check_dev_guide_sync.py` when docs/skill guidance changed.

## Skill router

NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.

**Strategy routing is language-gated (no cross-contamination):**
- Python strategy ("build a strategy in Python") -> `nt-strategy-builder-rust` ONLY. Explain this repository's stricter Rust cutover policy; use `nt-strategy-builder` only as explicitly labelled migration/reference material.
- Rust strategy ("build a strategy in Rust", HFT/perf/ships with a Rust adapter) -> `nt-strategy-builder-rust` ONLY.
- Ambiguous ("build a strategy", no language stated) -> `nt-strategy-builder-rust` ONLY. Rust is this repository's default; do not load `nt-strategy-builder` for new implementation work.
- AI/advisory request -> `nt-evomap-integration` ONLY. The AI lane stays Python but cannot own execution or block trading handlers.


NT v2 compatibility note: Python live/integration-specific TradingNode in the routing table is migration/reference-only; use LiveNode for Rust v2/Rust-backed work.

| User goal | Primary skill | Supporting skills |
|---|---|---|
| Unsure where to start / general NautilusTrader task | `nt` then route | Load only after classifying |
| Learn NautilusTrader from scratch | `nt-learn` | `nt-dev`, `nt-testing` |
| Design a trading system from research or requirements | `nt-architect` | `nt-model`, `nt-data`, `nt-trading` |
| Implement Strategy, Actor, Indicator, or component code | `nt-implement` | `nt-trading`, `nt-signals`, `nt-model` |
| Strategy logic, order lifecycle, positions, portfolio, risk | `nt-trading` | `nt-model`, `nt-testing` |
| Indicators, signals, order-book analytics, custom data signals | `nt-signals` | `nt-data`, `nt-model` |
| Market data, catalogs, persistence, serialization | `nt-data` | `nt-model`, `nt-testing` |
| Backtests, fill models, simulated venues, backtest configs | `nt-backtest` | `nt-strategy-builder-rust`, `nt-testing` |
| Wire an idea into backtest, paper, or live execution, including explicit Python requests | `nt-strategy-builder-rust` | `nt-backtest`, `nt-live`, `nt-adapters` |
| Build a performance-critical / production strategy in Rust | `nt-strategy-builder-rust` | `nt-trading`, `nt-testing`, `nt-live` |
| Live trading runtime, `LiveNode`/`TradingNode`, reconciliation | `nt-live` | `nt-adapters`, `nt-review` |
| Exchange/data-provider adapter work | `nt-adapters` | `nt-dev`, `nt-testing`, `nt-live` |
| Custom on-chain/DEX adapter | `nt-dex-adapter` | `nt-adapters`, `nt-implement`, `nt-testing` |
| Domain objects: instruments, identifiers, prices, quantities | `nt-model` | `nt-trading`, `nt-data` |
| Contributing to NautilusTrader core or aligning with dev guide | `nt-dev` | `nt-testing`, `nt-review` |
| Test strategy, adapter, data client, or core contribution | `nt-testing` | Domain skill for code under test |
| Review NautilusTrader code before merge/live use | `nt-review` | `nt-testing`, relevant domain skill |
| EvoMap advisory sidecar integration | `nt-evomap-integration` | `nt-architect`, `nt-review` |

## Rust-oriented v2.0 readiness

Default new work is Rust-first/PyO3/`LiveNode` oriented. Treat non-AI Python strategy/configuration material as migration/reference-only. The AI/advisory lane remains the sole active Python surface, asynchronous, and off execution-critical paths.

## Default workflows

### New trading system

Load in order:

1. `nt-architect` for component and data-flow design.
2. `nt-implement` for Strategy/Actor/Indicator templates.
3. Select the builder without cross-contamination:
   - Explicit Python, ambiguous, production, performance, backtest, paper, live, or explicit Rust strategy -> `nt-strategy-builder-rust`.
   - AI/advisory lane -> `nt-evomap-integration`; Python remains isolated from execution authority.
4. `nt-review` + `nt-testing` before live deployment or merge.

### Existing code review or bug investigation

Load in order:

1. Domain skill for the code area (`nt-trading`, `nt-data`, `nt-adapters`, etc.).
2. `nt-testing` for evidence requirements.
3. `nt-review` for pre-merge/live-readiness checks.

### Adapter development

Load in order:

1. `nt-adapters` for the official adapter contract and implementation phases.
2. `nt-dev` for Rust/Python/FFI/dev-guide rules.
3. `nt-testing` for DataTester/ExecTester/spec evidence.
4. `nt-live` if the adapter must run under a live runtime.

## Output expectations

When this entry skill routes a task, state the selected primary/supporting
skills briefly, then proceed with those skills. Example:

```text
Using nt as entry point. Routing to nt-strategy-builder-rust with nt-backtest and
nt-testing because the task is backtest wiring plus validation.
```
