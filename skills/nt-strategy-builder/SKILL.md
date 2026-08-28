---
name: nt-strategy-builder
description: Use when migrating or referencing existing Python NautilusTrader backtest, paper-trading, or live-trading systems
---

NT v2 compatibility note: legacy/v1/Cython/TradingNode references in this file are labelled legacy/reference-only unless an adjacent paragraph explicitly says they are current Rust/PyO3/LiveNode guidance.

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.


NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Strategy Builder

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `81eedc7cea29a52c0568f0bfbafd190c2bebe74f`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run python -m pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Execute the supported `BacktestNode`/`BacktestRunConfig` contract against pinned V2 and statically verify that retained Python templates remain migration/reference-only. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-strategy-builder` passed against the writable pinned-V2 build selected through `NT_UPSTREAM_ROOT`; `tests/test_strategy_builder_v2_contract.py` provides executable V2 coverage plus static migration/reference checks, while pinned upstream backtest/live acceptance tests provide integration coverage; `references/g2-evidence/nt-strategy-builder.json` records provenance. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run python -m pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration-only Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run python -m pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run python -m pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels and Rust-first lane guidance. | Pass | `uv run python -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-strategy-builder.json`; repository closure is summarized in `docs/tracking/Findings.md`. |

Migration gate: upstream NT V2 still supports Python strategies, but this repository applies a stricter Rust cutover policy. This skill and its executable templates are migration/reference-only; route all new strategy, research/config, backtest, paper, live, production, and performance implementation to `nt-strategy-builder-rust`. Non-NautilusTrader development lanes are outside this repository.

## Rust production lane

Build new strategy systems in Rust through `nt-strategy-builder-rust`. Rust owns `StrategyCore`, event handlers, order submission, risk decisions, backtest execution, and `LiveNode` wiring. Keep prices and quantities in Nautilus fixed-precision domain types, make configuration deserialization fail closed, and verify both deterministic backtests and live reconciliation before deployment.

Use `BacktestEngine` for historical execution and Rust `LiveNode` for paper/live execution. A venue is ready only when its data and execution factories, provider lifecycle, report generation, and shutdown path have focused tests. Rust validates and authorizes every execution-critical transition.

## PyO3 control-plane lane

Use PyO3 only as a bounded configuration, inspection, and callback seam around Rust-owned strategy state. Convert Python inputs into validated Rust types at the boundary; return typed errors rather than silently substituting defaults. Store callback handles as `Py<T>`/`Py<PyAny>`, acquire the GIL only at the call boundary, and never expose order submission, risk mutation, or runtime ownership to Python.

The Python API may select a registered Rust strategy, provide serializable parameters, or receive non-authoritative telemetry. Rust retains `StrategyCore`, clock, cache, portfolio, order factory, and execution authority.

## Migration/reference lane

Historical Python prose and examples are pointer-only from this root. Read `migration_reference/python/venue-and-simulation-examples.md` and `templates/legacy_migration/` only when translating an existing Python system. New implementation routes to `nt-strategy-builder-rust`; non-NautilusTrader development is outside this repository.

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at `81eedc7cea29a52c0568f0bfbafd190c2bebe74f`. Treat this immutable snapshot as upstream evidence, not as an editable production template.

## Overview

This migration/reference-only skill documents existing Python systems from **idea → running system** for historical backtests, paper trading, and live-trading nodes. Route all new strategy implementation to `nt-strategy-builder-rust`; use this material only to understand or migrate existing Python systems. It covers standard CeFi adapters (Binance, Bybit, OKX, …), custom DEX adapters built with `nt-dex-adapter`, Databento/Tardis data feeds, and mixed multi-venue setups.

Complements the existing skills:
- **nt-architect** – use first to decide component decomposition (Actor/Indicator/Strategy split)
- **nt-implement** – use to write the individual Strategy/Actor components
- **nt-dex-adapter** – use to build a custom DEX adapter that plugs into this skill's venue wiring

## When to Use

NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.

| Scenario | Approach |
|---|---|
| Replay historical data, no live connection | `BacktestEngine` + `ParquetDataCatalog` |
| Test strategy on live data without real orders | Rust/v2 `LiveNode` paper mode; legacy Python-live `TradingNode` only for migration/reference |
| Deploy to production with CeFi exchange | Rust/v2 `LiveNode` + standard adapter (default); legacy Python-live `TradingNode` only for migration/reference |
| Deploy with custom DEX venue | Rust/v2 `LiveNode` + `nt-dex-adapter` factory (default); legacy Python-live `TradingNode` only for migration/reference |
| Multi-venue arb or signal aggregation | Rust/v2 `LiveNode` (default) or `BacktestEngine`; legacy Python-live `TradingNode` only for migration/reference |

## Decision Tree: Which Execution Mode?

### Live runtime selection

NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.

Use `LiveNode` for Rust v2 / Rust-backed live-node work. Python live
connectivity examples may still use `TradingNode`; label them as Python live or
integration-specific rather than universal defaults.

NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.

```
Are you using live market data?
│
├─ NO  ──► BacktestEngine
│           ├─ Single venue  → templates/legacy_migration/backtest_node.py
│           ├─ DEX venue     → templates/legacy_migration/dex_venue_input.py
│           └─ Multi-venue   → templates/legacy_migration/multi_venue_strategy.py
│
└─ YES ──► Runtime boundary
            ├─ Python live/integration-specific migration/reference → TradingNode templates
            └─ Rust v2 / Rust-backed path       → LiveNode references
```

## Venue Data Input Types

Use Rust adapter factories and `LiveNodeBuilder` for CeFi and custom DEX venues. Use `ParquetDataCatalog` inputs through the Rust backtest path for replay, and give each venue independent data/execution configuration plus deterministic reconciliation. Historical Python CeFi, DEX, catalog, and multi-venue wiring examples moved to `migration_reference/python/venue-and-simulation-examples.md`.

## Template Quick Reference

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

| Template | When to use |
|---|---|
| `legacy_migration/backtest_node.py` | Full backtest with catalog data, custom FillModel/MarginModel |
| `legacy_migration/live_node.py` | Legacy Python TradingNode migration reference; use `nt-strategy-builder-rust` and `nt-live` for current production wiring |
| `legacy_migration/paper_node.py` | Paper-trading: real market data, simulated execution |
| `legacy_migration/dex_venue_input.py` | Wire a custom DEX adapter as venue (backtest or live) |
| `legacy_migration/multi_venue_strategy.py` | Strategy consuming data from 2+ venues simultaneously |

## Modern Tooling Standards
- **Project Management**: Use `uv` for lightning-fast dependency resolution and environment management (see `docs/uv_guide.md`).
- **Serialization**: Use pinned NautilusTrader model and serialization APIs; verify custom-type schemas against the current registration contract (see `docs/serialization.md`).
- **Visualization (migration/reference-only)**: Use `TearsheetConfig` with `create_tearsheet` from `nautilus_trader.analysis` and install the `visualization` extra (see `docs/visualization.md`).

## Implementation Workflow

1. **Design** components with `nt-architect`
2. **Implement** Strategy/Actor/Indicator with `nt-implement`
3. **Migration/reference only:** inspect these templates only when converting an existing Python system. For all new strategy, research/config, backtest, paper, live, production, and performance work, use Rust `LiveNode` via `nt-strategy-builder-rust` + `nt-live`:
   a. Choose backtest / paper / live mode
   b. Configure venues (CeFi builtin or DEX via `nt-dex-adapter`)
   c. Configure data sources (catalog or live feeds)
4. **Configure simulation models** (FillModel, MarginModel) for backtest realism
5. **Review** with `nt-review` before live deployment

## Adapter Wiring Contract (2026 Guide Alignment)

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

When wiring any custom adapter into `TradingNode` or `BacktestEngine`, verify these invariants:

- Adapter implementation reached at least phases 1-4 before live order flow is enabled.
- Data and execution factories expose canonical static `create(loop, name, config, msgbus, cache, clock)` signatures.
- Provider + data + execution method contracts are complete (no placeholder methods).
- Reconciliation/report paths are enabled and validated before production mode.
- Adapter tests include provider/data/execution/factory integration coverage using realistic fixture payloads.

If any invariant fails, block deployment and return to `nt-dex-adapter` + `nt-review` loops.

## Simulation Model Patterns

Model fill probability, slippage, fees, latency, and account constraints in Rust-owned backtest configuration. Seed stochastic models for reproducibility, preserve fixed-point price/quantity boundaries, and test DEX cash and leveraged perp venues separately. The retired Python `FillModel` and `BacktestVenueConfig` examples moved to `migration_reference/python/venue-and-simulation-examples.md`.

## DO and DON'Ts

See `rules/dos_and_donts.md` for the full curated ruleset with rationale.

### Critical DON'Ts (red flags)

- ❌ Never block in `on_bar` / handlers (no HTTP, no file I/O, no `time.sleep()`)
- ❌ Never assume `self.cache.instrument()` is non-None
- ❌ Never use raw `float` for Price/Quantity on instrument
- ❌ Never set `reconciliation=False` for live trading without documented justification
- ❌ Never use `datetime.utcnow()` — use `self.clock.utc_now()`
- ❌ **v1.223.0**: Never use `from nautilus_trader.adapters.dydx_v4` — module renamed to `dydx`
- ❌ **v1.223.0**: Never assume `Quantity - Quantity` returns `Decimal` — it now returns `Quantity`; negative result raises `ValueError`
- ❌ **v1.223.0**: Never use `prob_fill_on_stop` in FillModel — deprecated; use `prob_slippage`

## New in v1.223.0 (2026-02-21)

Key additions that affect strategy and execution wiring:

| Feature | Description |
|---|---|
| `strategy.market_exit(instrument_id)` | New convenience method for full market exit with configurable `market_exit_time_in_force` and `market_exit_reduce_only` options |
| `StrategyConfig.manage_stop` | Automatically flattens position with market order on strategy stop |
| `PerpetualContract` instrument | New instrument type for asset-class-agnostic perpetual swaps (use instead of `CryptoPerpetual` where applicable) |
| `BacktestDataConfig.optimize_file_loading` | New parameter for optimized Parquet file loading in large backtests |
| `trade_execution` default → `True` | **Breaking**: previously defaulted to `False`; set `trade_execution=False` explicitly for bar-only matching |
| `oto_trigger_mode` venue config | Control OTO child order activation: `PARTIAL` (default) or `FULL` |
| `use_market_order_acks` venue config | Generate `OrderAccepted` events for market orders before filling (Binance-like behavior) |
| `request_funding_rates()` + `FundingRateUpdate` | New data type and request method for funding rate data |
| Nasdaq ITCH 5.0 parser | Built-in support for Nasdaq ITCH 5.0 market data format |
| Sandbox execution adapter (Rust) | Rust-native sandbox adapter for development/testing |


## Testing

New code built from these templates should pass the included test suite:

```bash
# From repo root
uv run python -m pytest skills/nt-strategy-builder/tests/ -v
```

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

Tests cover:
- `test_backtest_patterns.py` — venue config, fill model, catalog round-trip
- `test_live_node_config.py` — TradingNode config builds without error
- `test_dex_as_venue.py` — DEX adapter wired into BacktestEngine
- `test_multi_venue.py` — multi-venue data routing

## References

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

Load these for detailed API information (relative to nt-implement skill folder):
- `references/concepts/backtesting.md` — BacktestEngine, venue config, fill models
- `references/concepts/live.md` — TradingNode, reconciliation, timeouts
- `references/api_reference/backtest.md` — BacktestEngine, BacktestVenueConfig API
- `references/api_reference/live.md` — LiveDataClient, LiveExecutionClient API
- `references/developer_guide/adapters.md` — Adapter development guide

## Next Steps

- To build a custom DEX adapter: use **nt-dex-adapter**
- To implement Strategy/Actor components: use **nt-implement**
- To review before deployment: use **nt-review**
