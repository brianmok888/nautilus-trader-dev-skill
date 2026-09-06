NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# NT-DEX-ADAPTER

NT v2 compatibility note: any legacy Python `TradingNode` factory mentioned
below is migration/reference-only; new production wiring uses Rust `LiveNode`.

Custom DEX adapter development for NautilusTrader.

## OVERVIEW

Build production-grade Rust DEX adapters with Rust clients and factories wired through `LiveNodeBuilder`; quarantined Python live templates are migration/reference-only.

## WHEN TO USE

| DEX Type | Approach |
|----------|----------|
| AMM (Uniswap, Curve) | Synthesize QuoteTick from reserves |
| On-chain CLOB (dYdX v4) | Use dYdX adapter as reference |
| Perp DEX (GMX) | CryptoPerpetual instrument |

## DEX vs CeFi

| Aspect | CeFi | DEX |
|--------|------|-----|
| Auth | API key | Wallet private key |
| Data | WebSocket | RPC polling/events |
| Orders | REST | Signed transaction |
| Fills | Exchange-reported | Tx output amount |

## 10-PHASE IMPLEMENTATION

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

1. **Define Scope**: Chains, products, environments, capabilities, protocol boundaries
2. **Build the Protocol Core**: Rust crate, RPC/WebSocket environments, wallet signing, shared types; apply the current-develop blockchain execution overlay (`nautilus-blockchain` crate)
3. **Implement Instruments**: Pool/market addresses → Nautilus instruments
4. **Implement Market Data**: QuoteTick synthesis, TradeTick from on-chain
5. **Implement Execution**: Build + sign + submit tx, receipt monitoring, reconciliation
6. **Add Optional Venue Capabilities**: Batch transactions, conditional orders, gas sponsorship, bridges
7. **Complete Factories and Projection**: Rust `LiveNodeBuilder` data/execution client factories; keep the Python factory template `legacy:` migration-only
8. **Prove Conformance**: Deterministic scenarios plus DataTester/ExecTester acceptance
9. **Measure Performance and Robustness**: Benchmarks, fuzz untrusted parsers
10. **Finish Documentation and Operations**: Capability matrix, ops runbook, safe recovery

## ADAPTER CANONICAL CONTRACT (2026)

- Keep phase order fixed: Rust infra -> instruments -> market data -> execution/reconciliation -> advanced -> config/factory -> tests/docs
- Implement complete provider/data/exec method contracts before marking adapter ready
- Use `get_runtime().spawn()` in adapter Rust runtime paths
- Prefer direct `PyObject`/`Py<T>` for ordinary PyO3 callbacks; justify and cycle-audit any `Arc<Py<T>>`; avoid blocking hot handlers
- Prefer real payload fixtures and condition-based async waits in tests

## ARCHITECTURE

```
crates/adapters/my_dex/     ← Rust core (client, signing, types)
nautilus_trader/adapters/   ← Optional PyO3 control/config exposure only
```

## TEMPLATES

| Template | Phase | Purpose |
|----------|-------|---------|
| `migration_reference/python/templates/dex_config.py` | 6 | Provider/data/exec configs |
| `migration_reference/python/templates/dex_instrument_provider.py` | 2 | Pool → Instrument |
| `migration_reference/python/templates/legacy_migration/dex_data_client.py` | 3 | Legacy Python live-client migration reference |
| `migration_reference/python/templates/legacy_migration/dex_exec_client.py` | 4-5 | Legacy Python live-client migration reference |
| `migration_reference/python/templates/legacy_migration/dex_factory.py` | 6 | Legacy: Python live-node migration reference; new factories are Rust `LiveNodeBuilder` factories |

## CRITICAL DON'Ts

- ❌ Poll chain in handlers — use polling Actor
- ❌ Store private keys as plain str — use SecretStr
- ❌ Skip `generate_order_status_report()`
- ❌ Use `tokio::spawn()` — use `get_runtime().spawn()`
- ❌ Use `Arc<PyObject>` as ordinary callback storage without a shared-ownership justification, cycle audit, weakrefs/cleanup, and PyO3 GC hooks when applicable

## TESTING

```bash
uv run pytest skills/nt-dex-adapter/tests/ -v
uv run pytest skills/nt-dex-adapter/tests/test_dex_compliance.py -v
```

## REFERENCE ADAPTERS

Study pinned examples: OKX, BitMEX, Bybit (built-in), dYdX v4, Hyperliquid (all under `crates/adapters/` at the pinned baseline; no `_template` adapter exists upstream)

## NEXT

- Wire adapter → `nt-strategy-builder-rust` with Rust `LiveNode` or backtest wiring
- Review code → `nt-review` (Rust/FFI checklist)
