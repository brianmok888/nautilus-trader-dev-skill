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
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as 6e59fd74eaacacbb7410936f1766bd89fcce6f59. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed block-scoped legacy/Cython/v1 and TradingNode enforcement; `tests/test_dev_guide_sync.py` covers leakage and exemption boundaries. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | 2026-07-28: `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt` passed against pinned upstream commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; machine-checked scope and execution provenance are recorded in `references/g2-evidence/nt.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py tests/test_dev_guide_sync.py` passed PyO3 registration, live-runner callback, Rust ownership, and V2 boundary regressions. |
| G4 Lane and API shape | Classify supported Python V2, AI/advisory, config/control-plane, and Rust hot-path lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template inventory and V2 API regressions; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 270 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 110 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | Cutover commits `9287019`, `6fc068b`, `44befad`, and `1707424` were pushed to `origin/main`; independent post-fix code review returned APPROVE and architecture review returned CLEAR, with no residual G2 Pending gates. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Router-specific gates: route production/performance work to Rust skills first (`nt-strategy-builder-rust`, `nt-adapters`, `nt-live`, `nt-trading`, `nt-dev`), keep `nt-strategy-builder` for supported NT V2 Python strategies including Python research/config use, and require the final router answer to include the gate status table before calling new NT work ready.

Python and Rust strategies are both supported NT V2 extension surfaces. This repository recommends Rust for hot paths and execution-critical ownership; that policy is a default, not a claim that current Python strategies are legacy or unsupported. The separate AI/advisory Python lane remains non-authoritative and off execution-critical paths.

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
- Python strategy ("build a strategy in Python") -> `nt-strategy-builder` ONLY.
- Rust strategy ("build a strategy in Rust", HFT/perf/ships with a Rust adapter) -> `nt-strategy-builder-rust` ONLY.
- Ambiguous ("build a strategy", no language stated) -> ask which language before loading either skill. Never mix the two skills in one strategy.


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
| Backtests, fill models, simulated venues, backtest configs | `nt-backtest` | `nt-strategy-builder`, `nt-testing` |
| Wire an idea into backtest, paper, or live execution (Python) | `nt-strategy-builder` | `nt-backtest`, `nt-live`, `nt-adapters` |
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

Default new work is Rust-first/PyO3/`LiveNode` oriented. Treat Python as the user strategy/configuration surface. The AI/advisory lane remains Python, asynchronous, and off execution-critical paths.

## Default workflows

### New trading system

Load in order:

1. `nt-architect` for component and data-flow design.
2. `nt-implement` for Strategy/Actor/Indicator templates.
3. Choose strategy language before builder selection:
   - Supported NT V2 Python strategy -> `nt-strategy-builder`.
   - Rust production/performance strategy -> `nt-strategy-builder-rust`.
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
Using nt as entry point. Routing to nt-strategy-builder with nt-backtest and
nt-testing because the task is backtest wiring plus validation.
```
