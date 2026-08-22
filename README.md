# NautilusTrader Development Skills for AI Agents

NT v2 compatibility note: legacy Cython/v1 and Python-live `TradingNode` material in this file is migration/release-history reference-only; prefer current Rust v2/PyO3 and `LiveNode` guidance for new Rust-backed work.

A collection of AI agent skills (Claude Code, Gemini CLI, Codex, Hermes) for developing trading systems with [NautilusTrader](https://github.com/nautechsystems/nautilus_trader) — a high-performance algorithmic trading platform written in Rust with Python bindings.

## Overview

NT v2 compatibility note: v1.x release/source labels in this baseline paragraph are release-history identifiers, not guidance to use legacy APIs.
These skills encode NautilusTrader best practices, correct patterns, and structured workflows for building production-quality trading systems. They are maintained against the official [NautilusTrader Developer Guide](https://nautilustrader.io/docs/latest/developer_guide/) and the GitHub `develop` source tree, with version-sensitive notes called out explicitly where they matter.

**Pinned reproducible baseline (verified 2026-08-22):** commit `98e6c39d8384c91dbf0102ea581aff5313ba9811`, workspace crates `0.63.0`, source label `v1.231.0`, and Python package `2.0.0rc4`; the repository toolchain is pinned to Rust 1.98.0. This is not a permanent MSRV promise; upstream generally follows the latest stable Rust release. Official Python support is Python 3.12-3.14. The v1.231.0 release remains the release-history baseline, while release notes identify `2.0.0rc1` as the first public candidate and use `2.0.0rcN` for the rolling candidate line.

**Current develop observation (reviewed 2026-08-08):** `origin/develop` is ahead of the reproducible pin. Develop-only guidance is labelled with its introducing commit and must not be assumed available at the pinned G2 baseline. Run `python3 tools/check_upstream_freshness.py --format json` for the current delta. Upstream is read-only ground truth for improving this skill repository.

## Skills Map

Start with `nt` when you want the skill suite to classify the task and route to the relevant NautilusTrader skills.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   DESIGN                 IMPLEMENT                 VALIDATE                  │
│                                                                              │
│  nt-architect  ──────► nt-implement  ──────────► nt-review                  │
│  Design component        Code components          Review conventions,       │
│  architecture            from templates           correctness, perf         │
│                              │                                              │
│                              ▼                                              │
│                  nt-strategy-builder-rust ◄── nt-dex-adapter              │
│                     Wire & run systems        Build on-chain                │
│                     (backtest, paper, live)   DEX venues                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                        DOMAIN KNOWLEDGE (7 skills)                           │
│                                                                              │
│   nt-trading      Orders, events, positions, portfolio                      │
│   nt-signals      Indicators, order books, data analysis                     │
│   nt-data         Market data types, subscriptions, catalogs                │
│   nt-backtest     BacktestEngine, venues, actors, fill models               │
│   nt-live         LiveNode/runtime boundary, adapters, reconciliation       │
│   nt-adapters     CeFi adapter spec (Binance, OKX, Bybit…), 10-phase build  │
│   nt-model        Core domain objects, identifiers, instruments             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

> **V2 boundary**: live/production skills route new Rust-backed work to `LiveNode`; the legacy Python-live `TradingNode` path is retained for migration/reference only (see each skill's "NT v2 compatibility note" for the labelled legacy surface).

┌──────────────────────────────────────────────────────────────────────────────┐
│                     DEVELOPER GUIDE & TESTING (2 skills)                     │
│                                                                              │
│   nt-dev          Coding standards, Rust/Python conventions, FFI,            │
│                   benchmarking, releases, environment setup                  │
│   nt-testing      Full testing pyramid, DataTesterConfig, ExecTesterConfig,  │
│                   property-based testing, fuzzing, test datasets             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                             LEARNING                                         │
│                                                                              │
│   nt-learn            12-stage structured curriculum                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Typical Workflows

| Goal | Skills to use |
|---|---|
| Design a new trading system | `nt` → `nt-architect` → `nt-implement` |
| Build a CeFi adapter (Binance, OKX…) | `nt-adapters` + `nt-dev` |
| Build a DEX adapter (on-chain) | `nt-dex-adapter` + `nt-implement` |
| Run a research/config backtest, including explicit Python requests | `nt-strategy-builder-rust` + `nt-backtest` |
| Deploy Rust/v2 live trading | `nt-strategy-builder-rust` + `nt-live` |
| Review code before merge | `nt-review` + `nt-testing` |
| Learn NautilusTrader | `nt` → `nt-learn` (12-stage curriculum) |
| Contribute to NautilusTrader core | `nt` → `nt-dev` + `nt-testing` |

## Skill Inventory (17 skills)

### Entry Point (1)
| Skill | Description | Key Content |
|---|---|---|
| `nt` | Start point/router for NautilusTrader tasks | Classifies intent, loads relevant `nt-*` skills |

### Workflow Pipeline (6)
| Skill | Description | Key Content |
|---|---|---|
| `nt-architect` | Research → component architecture decomposition | Design patterns, data flow planning |
| `nt-implement` | Templates for all NT component types | Strategy, Actor, Indicator, Adapter, FillModel, Rust+PyO3 |
| `nt-review` | Code review for NT conventions | Trading correctness, FFI safety, perf benchmarks |
| `nt-strategy-builder` | Migration/reference-only Python systems | Historical multi-venue wiring and migration examples |
| `nt-strategy-builder-rust` | Default production strategy path | Rust `Strategy`, backtest, and `LiveNode` wiring |
| `nt-dex-adapter` | Custom DEX adapter development | RPC nodes, wallet signing, pool discovery, test suite |

### Domain Knowledge (7)
| Skill | Description | Key Content |
|---|---|---|
| `nt-trading` | Trading domain: orders, events, positions | Order lifecycle, event-driven architecture |
| `nt-signals` | Indicators, order books, analysis | Technical indicators, book imbalance |
| `nt-data` | Market data types and pipelines | Subscriptions, catalogs, data model |
| `nt-backtest` | Backtesting engine and config | BacktestEngine, actors, fill models |
| `nt-live` | Live trading and production ops | Rust-backed `LiveNode` versus labelled Python-live runtime boundary, adapters, reconciliation |
| `nt-adapters` | CeFi adapter specification | Official 10-phase implementation and acceptance sequence |
| `nt-model` | Core domain objects | Instruments, identifiers, value objects |

### Developer Guide Skills (2)
| Skill | Description | Key Content |
|---|---|---|
| `nt-dev` | Official dev guide alignment | Coding standards, Rust/Python conventions, FFI memory, releases, release security |
| `nt-testing` | Testing pyramid and specs | DataTesterConfig, ExecTesterConfig, property-based, fuzzing |

### Learning (1)
| Skill | Description | Key Content |
|---|---|---|
| `nt-learn` | Structured 12-stage curriculum | From basics to adapter development |

## Official Developer Guide Coverage

Current developer-guide sync status is verified by `tools/check_dev_guide_sync.py`. Coverage includes `references/developer_guide/security.md` for trusted publishing, Sigstore, SLSA provenance, and cosign verification guidance.
Local references summarize official pages and include source metadata; skills use
canonical contracts under `references/developer_guide/contracts/` for
agent-actionable rules.

| Dev Guide Section | Skill | Status |
|---|---|---|
| Environment Setup | `nt-dev` | ✅ Reference + tooling contract |
| Coding Standards | `nt-dev` | ✅ Reference summary |
| Design Principles | `nt-architect` | ✅ Workflow skill |
| Rust | `nt-dev` | ✅ Reference summary |
| Python | `nt-dev` | ✅ Reference summary |
| Testing | `nt-testing` | ✅ Reference + policy contract |
| Spec Data Testing | `nt-testing` | ✅ Local summary + source metadata |
| Spec Exec Testing | `nt-testing` | ✅ Local summary + source metadata |
| Test Datasets | `nt-testing` | ✅ Local summary + source metadata |
| Docs Style | `nt-dev` | ✅ Reference summary |
| Releases | `nt-dev` | ✅ Reference summary |
| Adapters | `nt-adapters` + `nt-dex-adapter` | ✅ CeFi + DEX |
| Benchmarking | `nt-dev` | ✅ Reference summary |
| FFI | `nt-dev` | ✅ Memory contract spec |

## Reference Architecture

Skills use two reference patterns:

1. **Shared `references/` directory** — workflow skills (nt-architect, nt-implement, nt-review) symlink to the root `references/` directory containing API docs, concepts, developer guide, integrations, and dev templates.

2. **Per-skill `references/` directories** — domain skills (nt-trading, nt-signals, etc.) keep domain-specific references locally, with cross-skill deduplication via symlinks (e.g., nt-adapters → nt-dev for shared guides).

## Agent Compatibility

These skills work with:
- **Claude Code** (Anthropic) — via AGENTS.md per-skill
- **Gemini CLI** — via AGENTS.md
- **Codex** (OpenAI) — via AGENTS.md
- **Hermes Agent** — via SKILL.md + references/
- **OpenCode** — via SKILL.md + references/

## Developer Guide Sync Verification

Run the static drift checks after changing references, contracts, or skills:

```bash
uv run python tools/check_dev_guide_sync.py
uv run python tools/check_dev_guide_snapshot_sync.py
python3 tools/check_rust_trading_reference_sync.py
python3 tools/check_rust_trading_reference_sync.py --compile
uv run --with pytest pytest tests/test_dev_guide_sync.py -q
```

The checker validates required local developer-guide pages, source metadata,
stale reference paths, and high-risk NautilusTrader invariants used by the skill
suite. The snapshot and Rust-reference commands require a NautilusTrader checkout
at commit `98e6c39d8384c91dbf0102ea581aff5313ba9811`; pass its path with
`--upstream-root` when it is not available at the documented default under `/tmp`.

## Source of Truth

This skill repo is aligned to NautilusTrader itself, not to any downstream or prior skill repository.

- Official docs: [nautilustrader.io/docs/latest/developer_guide](https://nautilustrader.io/docs/latest/developer_guide/)
- NautilusTrader repo: [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader)

Prior or downstream skill repos such as [Martingale42/nautilus-dev](https://github.com/Martingale42/nautilus-dev) may be useful for comparison, but they are not alignment targets or sources of truth.
