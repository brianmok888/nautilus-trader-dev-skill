---
name: nt-dex-adapter
description: "Use when building a custom DEX adapter that fully complies with NautilusTrader's adapter standard. Covers DEX-specific instrument discovery, on-chain data normalisation, wallet-signed order execution, and the 7-phase implementation sequence. Includes DO/DON'Ts rules, a compliance checklist, and a test suite."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Custom DEX Adapter

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; current-develop drift is version-scoped in `README.md`. |
| G1 Legacy label | No migration/reference-only Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 25 tests. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-dex-adapter` passed the skill domain's scoped examples and owners against `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; schema-v2 provenance is recorded in `references/g2-evidence/nt-dex-adapter.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 tests. |
| G4 Lane and API shape | Classify migration-only Python, active AI/advisory Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'` passed 24 tests. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md` records the post-fix audit; `uv run python tools/check_skill_g2_harnesses.py --check-cards` validates all 18 cards and evidence artifacts. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

DEX adapter gates: Rust-first default applies to on-chain/off-chain clients, signing, precision, state reconciliation, and venue adapters; Python may configure or inspect only through PyO3/control-plane seams. Add `cargo nextest`, `cargo clippy`, `cargo deny`, fuzz/property tests, allowance/security checks, and dry-run reconciliation evidence before live order flow is `Pass`.

## Rust production lane

Implement the adapter under `crates/adapters/<venue>/`. Rust owns RPC/WebSocket transport, wallet signing, nonce and gas policy, instrument normalization, fixed-point AMM/CLOB math, execution state, and reconciliation. Use `nautilus_network::http::HttpClient`, `nautilus_network::websocket::WebSocketClient`, and the Nautilus runtime; never hold private-key material in Python.

Complete provider → data → execution phases in order. Fail closed on stale chain state, reorg ambiguity, precision overflow, unsupported cancellation, or an unknown transaction outcome. Register Rust data/execution factories through `LiveNodeBuilder`, then prove parser properties, deterministic event ordering, receipt reconciliation, and sandbox/mainnet configuration separation.

## PyO3 control-plane lane

Expose only validated configuration, startup/shutdown control, and read-only diagnostics through PyO3. Parse chain IDs, addresses, instruments, slippage bounds, and secret references into Rust types before constructing clients. Keep signing keys, transaction assembly, order commands, receipt monitoring, and reconciliation inside Rust.

For callbacks, prefer direct `Py<T>`/`Py<PyAny>` handles with explicit cleanup. Schedule Rust work with the Nautilus runtime, release the GIL around blocking boundary calls, and translate Rust failures into typed Python exceptions without granting Python execution authority.

## Migration/reference lane

NT v2 compatibility note: non-AI Python templates are quarantined at
`migration_reference/python/templates/`. They are migration/reference-only
material for earlier providers, synthetic order-book helpers, and legacy live
clients. Do not copy them into a new adapter. Active Python remains limited to
AI/advisory work in `nt-evomap-integration`, off execution-critical paths.

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at `6e59fd74eaacacbb7410936f1766bd89fcce6f59`. Treat this immutable snapshot as upstream evidence, not as an editable production template.

## Overview

Build a custom on-chain DEX adapter that plugs into NautilusTrader's adapter framework — identical in structure to the built-in OKX, Bybit, or BitMEX adapters, but with DEX-specific plumbing (RPC nodes, wallet signing, pool discovery) instead of REST/WebSocket API keys.

Once built, wire your adapter through `nt-strategy-builder-rust` using Rust `LiveNode` or backtest wiring. The Python `nt-strategy-builder` examples are migration/reference-only.

**Canonical CeFi reference adapters**: OKX, BitMEX, Bybit — study their Python layer and Rust core before customising.

## Adapter canonical contract

Read `references/developer_guide/contracts/adapter_contract.md` and
`references/developer_guide/contracts/testing_policy.md` before claiming a DEX
adapter is ready.

DEX adapter readiness requires:

- provider/data/execution methods aligned to current Nautilus command/request
  object signatures;
- `InstrumentProvider.load_all_async()` implemented, with targeted load methods
  overridden only for DEX-specific semantics or efficiency;
- data connect lifecycle: bootstrap instruments, cache instruments, emit
  instruments, prepare WebSocket cache, then connect subscriptions;
- execution connect lifecycle: initialize instruments, connect private stream,
  subscribe, refresh account state, wait for account registration, then mark
  connected;
- reconciliation coverage for order status reports, fill reports, position
  status reports, and mass status where supported by the venue;
- DataTester and ExecTester or equivalent acceptance evidence.

## When to Use

| DEX Type | Notes |
|---|---|
| AMM (Uniswap V2/V3, Curve) | No order book — synthesise `QuoteTick` from pool reserves |
| On-chain CLOB (dYdX v4, Hyperliquid) | Use existing dYdX/Hyperliquid adapters as starting points |
| Perp DEX (GMX, Synthetix) | Use current `PerpetualContract` for asset-class-agnostic perps; use `CryptoPerpetual` only when a crypto-specific perp type is required |
| Cross-chain DEX | Implement per-chain data client; share execution client logic |

## DEX vs CeFi Key Differences

| Aspect | CeFi Adapter | DEX Adapter |
|---|---|---|
| Authentication | API key + secret | Wallet private key + signature |
| Market data | WebSocket streams | RPC polling or event subscription |
| Order book | L2 snapshot + delta | Derived from pool state (AMM) or on-chain updates |
| Order execution | REST/WebSocket | Signed Ethereum/Solana/Cosmos transaction |
| Order lifecycle | Exchange-managed | On-chain confirmation + receipt |
| Account state | REST balance query | On-chain wallet balance |
| Reconciliation | Order status REST | On-chain transaction history |
| Fill price | Exchange-reported | Actual tx output amount |

## 7-Phase Implementation Sequence

This maps directly to the canonical adapter implementation pattern. Complete each phase fully before moving to the next.

### Phase 1: Rust Core Infrastructure
- HTTP JSON-RPC client in `crates/adapters/my_dex/` using **`nautilus_network::http::HttpClient`** (not `reqwest` directly — this provides built-in rate limiting, retry logic, and consistent error handling matching the canonical adapters)
- WebSocket event subscription client using `nautilus_network::websocket::WebSocketClient`
- Wallet signing utilities (ECDSA for EVM, ed25519 for Solana) — implement in Rust core, never in Python layer
- Types: config structs, RPC response models

### Phase 2: Instrument Discovery
- `InstrumentProvider.load_all_async()` → fetch pool/market addresses from chain
- Parse pool metadata → `CurrencyPair`, `CryptoPerpetual`, or current `PerpetualContract` for asset-class-agnostic perps
- Map on-chain tokens to Nautilus `Currency` objects
- Normalise instrument IDs to `{POOL_SYMBOL}.{VENUE}` format

### Phase 3: Market Data
- AMM: synthesise `QuoteTick` from pool reserves (`x*y=k` price)
- CLOB DEX: map order book events → `OrderBookDelta`
- On-chain trades → `TradeTick`
- Polling Actor pattern (if no event subscription available)

### Phase 4: Order Execution
- `_submit_order()` → build + sign tx → submit via RPC
- `_cancel_order()` → on-chain cancel (if supported)
- `_cancel_all_orders()` → batch cancel or position close
- Handle tx inclusion + revert vs success → emit correct Nautilus events

### Phase 5: Account & Position Events
- `generate_account_state()` after each balance-changing tx
- On-chain wallet balance → `AccountBalance`
- Position tracking (DEX perps: on-chain position query)
- `generate_order_status_report()` for reconciliation

### Phase 6: Configuration & Factory
- Rust `InstrumentProvider`, data client, and execution client configuration
- Rust data and execution client factories registered through `LiveNodeBuilder`
- `sandbox_mode: bool` flag for test networks / local fork

### Phase 7: Testing & Documentation
- Unit tests: instrument parsing, quote synthesis, tx building
- Integration test: BacktestEngine with mock DEX data
- Compliance checklist: `rules/compliance_checklist.md`
- README: RPC requirements, supported pool types, gas configuration

## Rust-First Architecture

```
crates/adapters/my_dex/           ← Rust core
  src/
    lib.rs
    client.rs        ← HTTP JSON-RPC client
    ws_client.rs     ← WebSocket event client (if available)
    signing.rs       ← Wallet key management + tx signing
    types.rs         ← RPC response structs, pool state types
    python/          ← PyO3 configuration/control bindings when required
```

## Migration/reference-only Python architecture

The historical provider, configuration, synthetic order-book, and live-client examples are physically quarantined under `migration_reference/python/templates/`. They are migration evidence only; new adapters use Rust clients and factories with optional bounded PyO3 control bindings.

## Template Quick Reference

| Migration reference | Historical phase | Use |
|---|---:|---|
| `migration_reference/python/templates/dex_config.py` | 6 | Translate old Python config fields into validated Rust config |
| `migration_reference/python/templates/dex_instrument_provider.py` | 2 | Compare historical pool-to-instrument normalization |
| `migration_reference/python/templates/dex_order_book_builder.py` | 3 | Compare historical AMM synthetic-book math |
| `migration_reference/python/templates/legacy_migration/dex_data_client.py` | 3 | Migration/reference-only legacy Python data-client behavior |
| `migration_reference/python/templates/legacy_migration/dex_exec_client.py` | 4–5 | Migration/reference-only legacy Python execution/reconciliation behavior |
| `migration_reference/python/templates/legacy_migration/dex_factory.py` | 6 | Migration/reference-only ClientFactory wiring to replace with Rust `LiveNodeBuilder` factories |

## DO and DON'Ts

See `rules/dos_and_donts.md` for the full ruleset.

### Critical DEX-Specific Rules (red flags)

- ❌ Never poll chain in `on_bar`/`on_quote_tick` handlers — use a polling Actor or timer
- ❌ Never store private keys as plain `str` — use `SecretStr` or env-var injection
- ❌ Never skip `generate_order_status_report()` — needed for reconciliation
- ❌ Never use `tokio::spawn()` in adapter Rust code — use `get_runtime().spawn()`
- ❌ Do not use `Arc<PyObject>` for ordinary callbacks — prefer direct `PyObject`/`Py<T>` with `clone_py_object()`; justify any exception and audit cycles, weakrefs, cleanup, and PyO3 GC hooks when applicable
- ❌ Don't treat AMM spot price as fill price without modelling slippage

## Compliance Checklist

Every adapter must clear `rules/compliance_checklist.md` before use. Run the structural compliance test:

```bash
uv run pytest skills/nt-dex-adapter/tests/test_dex_compliance.py -v
```

Required checks before claiming adapter readiness:

- [ ] 7 phases completed in order and each milestone satisfied
- [ ] Provider/data/exec method contracts implemented (no placeholder `pass`)
- [ ] `get_runtime().spawn()` used for Rust async tasks
- [ ] PyO3 callback bindings prefer direct `PyObject`/`Py<T>`; any `Arc<Py<T>>` exception is justified and cycle-audited
- [ ] Credentials resolved via config/env without plain-text key leakage
- [ ] Fixture payloads sourced from real upstream docs/live captures
- [ ] Async tests avoid arbitrary sleep and use condition-based waiting

## Modern Tooling Standards
- **Dependencies**: Use `uv` for managing the adapter dev environment.
- **Serialization**: For internal data passing, `msgspec` structs are faster than standard classes.
- **Visualization (migration/reference-only)**: Inspect recorded data with `TearsheetConfig` and `create_tearsheet`; install the `visualization` extra.

## Testing Strategy

```bash
# All DEX adapter tests
uv run pytest skills/nt-dex-adapter/tests/ -v

# Structural compliance only (fastest gate)
uv run pytest skills/nt-dex-adapter/tests/test_dex_compliance.py -v
```

## References

Load these for detailed API information (relative to nt-implement skill folder):
- `references/developer_guide/adapters.md` — Rust-first adapter development guide
- `references/developer_guide/rust.md` — Rust conventions, async runtime patterns
- `references/developer_guide/ffi.md` — FFI memory contract, CVec, abort_on_panic
- `references/api_reference/live.md` — LiveMarketDataClient, LiveExecutionClient APIs
- `references/integrations/dydx.md` — On-chain CLOB reference adapter (v4)
- `references/integrations/hyperliquid.md` — DEX perp reference adapter
- `nautilus_trader/adapters/_template/` — Canonical adapter skeleton

## Next Steps

- Wire your adapter: use **nt-strategy-builder-rust** for Rust `LiveNode` or backtest wiring
- Review code: use **nt-review** Rust/FFI checklist before deployment
