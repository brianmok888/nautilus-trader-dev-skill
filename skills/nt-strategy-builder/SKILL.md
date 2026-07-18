---
name: nt-strategy-builder
description: Use when building NautilusTrader backtesting, paper-trading, or live-trading systems
---

NT v2 compatibility note: legacy/v1/Cython/TradingNode references in this file are labelled legacy/reference-only unless an adjacent paragraph explicitly says they are current Rust/PyO3/LiveNode guidance.

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.


NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Strategy Builder

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

Python strategy gates: this skill is for Python research/config, paper exploration, and AI/advisory orchestration only. Route production/performance to nt-strategy-builder-rust, keep live-default wiring on `LiveNode`, and mark `Pass` only when the completion report proves no execution-critical Rust path depends on Python advisory logic.

## Overview

This skill guides you from **idea → running system** — whether you are running a historical backtest, paper-trading on live market data, or deploying a live-trading node. It handles all supported venue data inputs: standard CeFi adapters (Binance, Bybit, OKX, …), custom DEX adapters built with `nt-dex-adapter`, Databento/Tardis data feeds, and mixed multi-venue setups.

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
- **Visualization**: Use the new `BacktestVisualizer` (Plotly-based) for interactive tearsheets instead of static matplotlib plots (see `docs/visualization.md`).

## Implementation Workflow

1. **Design** components with `nt-architect`
2. **Implement** Strategy/Actor/Indicator with `nt-implement`
3. **Wire venue(s)** using templates in this skill:
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
