---
name: nt
description: "Entry-point/router skill for any NautilusTrader or nautilus_trader task. Use when the user asks for NautilusTrader help, says nt, asks which Nautilus skill to use, or gives a trading-system, strategy, adapter, data, backtest, live, testing, or core-contribution task without naming a more specific nt-* skill. Routes to and loads the relevant NautilusTrader skills instead of answering from memory alone."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# NautilusTrader Entry Skill

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
3. `nt-strategy-builder` for backtest, paper, or live wiring.
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
