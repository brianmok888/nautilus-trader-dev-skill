NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# NT-STRATEGY-BUILDER

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

NT v2 compatibility note: the legacy Python `TradingNode` templates named below
are migration/reference-only; use Rust `LiveNode` for new production work.

Python strategy and live-node migration references for NautilusTrader. All new
implementation, including explicit Python requests, routes to
`nt-strategy-builder-rust`; non-NautilusTrader development is outside this repository.

## OVERVIEW

From idea → running system. Covers backtesting, paper trading, and live deployment with multi-venue support (CeFi + custom DEX adapters).

## TEMPLATES

| Template | Mode | Use When |
|----------|------|----------|
| `legacy_migration/backtest_node.py` | Python migration reference | Historical comparison |
| `legacy_migration/live_node.py` | Python migration reference | Move Python live wiring to Rust `LiveNode` |
| `legacy_migration/paper_node.py` | Python migration reference | Move paper wiring to Rust |
| `legacy_migration/dex_venue_input.py` | Python migration reference | Move DEX wiring to a Rust adapter factory |
| `legacy_migration/multi_venue_strategy.py` | Python migration reference | Move multi-venue wiring to Rust |

## DECISION TREE

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

```
Existing Python system being migrated?
├─ YES → nt-strategy-builder (migration/reference only)
└─ NO  → nt-strategy-builder-rust
         ├─ Backtest → Rust backtest engine example
         └─ Live     → Rust LiveNode example
```

## VENUE INPUTS

1. **CeFi Adapters** — Built-in (Binance, Bybit, OKX, etc.)
2. **DEX Adapter** — Built with nt-dex-adapter, wire via `legacy_migration/dex_venue_input.py`
3. **Catalog Data** — ParquetDataCatalog for backtests
4. **Multi-Venue** — Multiple data_clients + exec_clients

## ADAPTER WIRING CONTRACT (2026)

- Enable live order flow only after adapter Phases 0-4 are complete
- Require the v2 trait-object factory contract for data/exec wiring (registered via `LiveNodeBuilder`)
- Verify reconciliation/report generation paths before production mode
- Block deploy when provider/data/exec contracts are incomplete

## SIMULATION MODELS

```python
# Fill models import from nautilus_trader.execution; the base FillModel takes
# no constructor arguments at v2 - use the concrete model constructors.

# DEX-realistic
DefaultFillModel(prob_fill_on_limit=0.3, prob_slippage=0.7)

# CeFi-realistic
DefaultFillModel(prob_fill_on_limit=0.5, prob_slippage=0.2)
```

## CRITICAL DON'Ts

- ❌ Block in handlers (no HTTP, file I/O, `time.sleep()`)
- ❌ Assume `cache.instrument()` is non-None
- ❌ Use raw `float` for Price/Quantity
- ❌ Set `reconciliation=False` without justification
- ❌ Use `datetime.utcnow()` — use `self.clock.utc_now()`

## TESTING

```bash
uv run pytest skills/nt-strategy-builder/tests/ -v
```

## NEXT

- Build DEX adapter → `nt-dex-adapter`
- Review code → `nt-review`
