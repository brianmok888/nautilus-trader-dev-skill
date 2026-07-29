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

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as 6e59fd74eaacacbb7410936f1766bd89fcce6f59. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed block-scoped legacy/Cython/v1 and TradingNode enforcement; `tests/test_dev_guide_sync.py` covers leakage and exemption boundaries. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | 2026-07-28: `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-strategy-builder` passed against pinned upstream commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; machine-checked scope and execution provenance are recorded in `references/g2-evidence/nt-strategy-builder.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py tests/test_dev_guide_sync.py` passed PyO3 registration, live-runner callback, Rust ownership, and V2 boundary regressions. |
| G4 Lane and API shape | Classify migration-only Python, active AI/advisory Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template inventory and V2 API regressions; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 308 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 113 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | All 18 targeted G2 harnesses passed and `uv run python tools/check_skill_g2_harnesses.py --check-cards` validated their durable evidence; no readiness row is Pending or Blocked. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Migration gate: upstream NT V2 still supports Python strategies, but this repository applies a stricter Rust cutover policy. This skill and its executable templates are migration/reference-only; route all new strategy, research/config, backtest, paper, live, production, and performance implementation to `nt-strategy-builder-rust`. The AI/advisory lane stays Python through `nt-evomap-integration`, remains non-authoritative, and stays off execution-critical paths.

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
│           ├─ Single venue  → templates/backtest_node.py
│           ├─ DEX venue     → templates/dex_venue_input.py
│           └─ Multi-venue   → templates/multi_venue_strategy.py
│
└─ YES ──► Runtime boundary
            ├─ Python live/integration-specific migration/reference → TradingNode templates
            └─ Rust v2 / Rust-backed path       → LiveNode references
```

## Venue Data Input Types

### 1. Standard CeFi Adapters (Built-in)

NautilusTrader ships adapters for Binance, Bybit, OKX, Coinbase (Rust/v2 `LiveNode` path), dYdX, Interactive Brokers, Databento, Tardis, and more.

NT v2 compatibility note: dYdX v3 legacy adapter text below is migration/reference-only; use the renamed current `nautilus_trader.adapters.dydx` path for new work.


> **v1.223.0**: dYdX v3 (legacy) adapter removed. Use `nautilus_trader.adapters.dydx` (module renamed from `dydx_v4`). Class prefix is now `Dydx` (e.g., `DydxDataClientConfig`, `DydxLiveDataClientFactory`). The dydx optional install extra is no longer needed.

> **v1.223.0 Binance**: `listen_key_ping_max_failures` removed from `BinanceExecClientConfig`. Binance now authenticates via WebSocket API (Ed25519/HMAC auto-detected from `api_secret` format). Credentials from `BINANCE_API_KEY`/`BINANCE_API_SECRET` env vars.

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

```python
from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory
from nautilus_trader.config import TradingNodeConfig, LiveDataEngineConfig

# NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

config = TradingNodeConfig(
    data_clients={
        "BINANCE": BinanceDataClientConfig(
            api_key=os.environ["BINANCE_API_KEY"],
            api_secret=os.environ["BINANCE_API_SECRET"],
            testnet=False,
        ),
    },
)
```

### 2. Custom DEX Adapter (nt-dex-adapter)

After building a DEX adapter with the `nt-dex-adapter` skill, wire it in exactly like a CeFi adapter:

```python
from my_dex_adapter.factory import MyDEXLiveDataClientFactory, MyDEXLiveExecClientFactory

# NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

config = TradingNodeConfig(
    data_clients={"MYDEX": MyDEXDataClientConfig(rpc_url="https://...", wallet_address="0x...")},
    exec_clients={"MYDEX": MyDEXExecClientConfig(rpc_url="https://...", private_key=SecretStr(...))},
    data_client_factories={"MYDEX": MyDEXLiveDataClientFactory},
    exec_client_factories={"MYDEX": MyDEXLiveExecClientFactory},
)
```

See `templates/dex_venue_input.py` for a complete wiring example.

### 3. Catalog Data (Backtest / Replay)

Use `ParquetDataCatalog` for any historical data — CeFi, DEX, or custom:

```python
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.config import BacktestDataConfig

catalog = ParquetDataCatalog("/path/to/catalog")

data_config = BacktestDataConfig(
    catalog_path=str(catalog.path),
    data_cls="nautilus_trader.model.data:Bar",
    instrument_id="WETH-USDC.UNISWAP_V3",
    start_time="2024-01-01",
    end_time="2024-12-31",
)
```

### 4. Multi-Venue (Mixed CeFi + DEX)

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

Wire multiple venues into a single `TradingNode` or `BacktestEngine`. Each venue gets its own:
- `data_client` entry
- `exec_client` entry (if trading)
- `BacktestVenueConfig` (backtest) / `LiveDataEngineConfig` (live)

See `templates/multi_venue_strategy.py`.

## Template Quick Reference

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

| Template | When to use |
|---|---|
| `backtest_node.py` | Full backtest with catalog data, custom FillModel/MarginModel |
| `live_node.py` | Production TradingNode with reconciliation, timeouts, persistence |
| `paper_node.py` | Paper-trading: real market data, simulated execution |
| `dex_venue_input.py` | Wire a custom DEX adapter as venue (backtest or live) |
| `multi_venue_strategy.py` | Strategy consuming data from 2+ venues simultaneously |

## Modern Tooling Standards
- **Project Management**: Use `uv` for lightning-fast dependency resolution and environment management (see `docs/uv_guide.md`).
- **Serialization**: Prefer `msgspec.Struct` for custom data types over standard dataclasses for 10-100x speedups (see `docs/serialization.md`).
- **Visualization (migration/reference-only)**: Use `TearsheetConfig` with `create_tearsheet` from `nautilus_trader.analysis` and install the `visualization` extra (see `docs/visualization.md`).

## Implementation Workflow

1. **Design** components with `nt-architect`
2. **Implement** Strategy/Actor/Indicator with `nt-implement`
3. **Migration/reference only:** inspect these templates only when converting an existing Python system. For all new strategy, research/config, backtest, paper, live, production, and performance work, use Rust `LiveNode` via `nt-strategy-builder-rust` + `nt-live`. AI/advisory work belongs to `nt-evomap-integration`, not this skill:
   a. Choose backtest / paper / live mode
   b. Configure venues (CeFi builtin or DEX via `nt-dex-adapter`)
   c. Configure data sources (catalog or live feeds)
4. **Configure simulation models** (FillModel, MarginModel) for backtest realism
5. **Integrate optional EvoMap sidecar** (advisory only):
   a. Export bounded strategy/actor artifacts via sidecar client
   b. Fetch suggestions on timer boundaries (not in hot handlers)
   c. Require explicit approval gate before strategy behavior changes
6. **Review** with `nt-review` before live deployment

## EvoMap Sidecar Wiring (Optional)

Use EvoMap, LangChain, or LangGraph as external refinement sources while preserving local trading determinism:

- Keep EvoMap Proxy mailbox calls, LangChain model/tool calls, and LangGraph execution off execution-critical paths (`on_bar`, `on_quote_tick`, `on_order_book_deltas`).
- Publish only necessary fields (avoid full account or secret context leakage).
- Use periodic sync (`on_timer`) and bounded queues to prevent memory growth.
- Record suggestion provenance (asset id, suggestion hash, LangGraph checkpoint id, decision reason) for post-trade audit.
- If EvoMap, LangChain, or LangGraph orchestration is unavailable, continue with local strategy logic and emit degraded-mode telemetry.

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

### FillModel — Backtest Realism

> **v1.223.0**: `prob_fill_on_stop` is deprecated. Use `prob_slippage` for market/stop order slippage probability.

```python
from nautilus_trader.backtest.models import FillModel

# DEX-realistic: high slippage, lower limit fill probability
dex_fill_model = FillModel(
    prob_fill_on_limit=0.3,   # DEX: limit orders rarely at exact price
    prob_slippage=0.7,        # DEX: high slippage probability
    random_seed=42,
)

# CeFi realistic
cefi_fill_model = FillModel(
    prob_fill_on_limit=0.5,
    prob_slippage=0.2,
    random_seed=42,
)
```

### BacktestVenueConfig — Account Types

```python
from nautilus_trader.backtest.config import BacktestVenueConfig

# Crypto spot
venue_config = BacktestVenueConfig(
    name="BINANCE",
    oms_type="NETTING",
    account_type="CASH",
    base_currency="USDT",
    starting_balances=["10_000 USDT", "1 BTC"],
    fill_model=fill_model,
)

# DEX (treat as CASH, no margin)
dex_venue_config = BacktestVenueConfig(
    name="UNISWAP_V3",
    oms_type="NETTING",
    account_type="CASH",
    base_currency="USDT",
    starting_balances=["10_000 USDT"],
    fill_model=dex_fill_model,
)

# Futures / perps
perp_venue_config = BacktestVenueConfig(
    name="BYBIT",
    oms_type="NETTING",
    account_type="MARGIN",
    base_currency="USDT",
    starting_balances=["10_000 USDT"],
    default_leverage=Decimal("10"),
    fill_model=fill_model,
)
```

## DO and DON'Ts

See `rules/dos_and_donts.md` for the full curated ruleset with rationale.

### Critical DON'Ts (red flags)

- ❌ Never block in `on_bar` / handlers (no HTTP, no file I/O, no `time.sleep()`)
- ❌ Never assume `self.cache.instrument()` is non-None
- ❌ Never use raw `float` for Price/Quantity on instrument
- ❌ Never set `reconciliation=False` for live trading without documented justification
- ❌ Never auto-apply EvoMap suggestions directly to live execution behavior
- ❌ Never put ML inference inside Strategy (use Actor)
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
uv run pytest skills/nt-strategy-builder/tests/ -v
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
