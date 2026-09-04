---
name: nt-dex-adapter
description: "Use when building a custom DEX adapter that fully complies with NautilusTrader's adapter standard. Covers DEX-specific instrument discovery, on-chain data normalisation, wallet-signed order execution, and the official ten-phase implementation sequence. Includes DO/DON'Ts rules, a compliance checklist, and a test suite."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Custom DEX Adapter

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No migration/reference-only Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run python -m pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-dex-adapter` passed the skill domain's scoped examples and owners against `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`; schema-v2 provenance is recorded in `references/g2-evidence/nt-dex-adapter.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run python -m pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run python -m pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run python -m pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run python -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-dex-adapter.json`; repository closure is summarized in `docs/tracking/Findings.md`. |


DEX adapter gates: Rust-first default applies to on-chain/off-chain clients, signing, precision, state reconciliation, and venue adapters; Python may configure or inspect only through PyO3/control-plane seams. Add `cargo nextest`, `cargo clippy`, `cargo deny`, fuzz/property tests, allowance/security checks, and dry-run reconciliation evidence before live order flow is `Pass`.

## Rust production lane

Implement the adapter under `crates/adapters/<venue>/`. Rust owns RPC/WebSocket transport, wallet signing, nonce and gas policy, instrument normalization, fixed-point AMM/CLOB math, execution state, and reconciliation. Use `nautilus_network::http::HttpClient`, `nautilus_network::websocket::WebSocketClient`, and the Nautilus runtime; never hold private-key material in Python.

Complete provider → data → execution phases in order. Fail closed on stale chain state, reorg ambiguity, precision overflow, unsupported cancellation, or an unknown transaction outcome. Register Rust data/execution factories through `LiveNodeBuilder`, then prove parser properties, deterministic event ordering, receipt reconciliation, and sandbox/mainnet configuration separation.

## PyO3 control-plane lane

Expose only validated configuration, startup/shutdown control, and read-only diagnostics through PyO3. Parse chain IDs, addresses, instruments, slippage bounds, and secret references into Rust types before constructing clients. Keep signing keys, transaction assembly, order commands, receipt monitoring, and reconciliation inside Rust.

For callbacks, prefer direct `Py<T>`/`Py<PyAny>` handles with explicit cleanup. Schedule Rust work with the Nautilus runtime, release the GIL around blocking boundary calls, and translate Rust failures into typed Python exceptions without granting Python execution authority.

## Migration/reference lane

NT v2 compatibility note: Python templates are quarantined at
`migration_reference/python/templates/`. They are migration/reference-only
material for earlier providers, synthetic order-book helpers, and legacy live
clients. Do not copy them into a new adapter. Active Python remains limited to

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`. Treat this immutable snapshot as upstream evidence, not as an editable production template.

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
- `InstrumentProvider.load_all(filters)` implemented, with targeted load methods
  `load_ids(instrument_ids, filters)` / `load(instrument_id, filters)`
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

## Adapter Implementation Sequence

This maps directly to the canonical adapter implementation pattern. Complete each phase fully before moving to the next.

### Phase 0: Define scope

Record chains, products, environments, account modes, data/order/report capabilities, protocol
boundaries, reorg/finality assumptions, unsupported operations, and the smallest end-to-end slice.

### Phase 1: Build the protocol core

Add the Rust crate; implement RPC/WebSocket environments, credentials, wallet signing, shared
types, deterministic parsers/serializers, retry classification, authentication, heartbeat, and
transport lifecycle. Use `nautilus_network::http::HttpClient` and
`nautilus_network::websocket::WebSocketClient`, not independent runtimes or direct production
`reqwest` clients.

### Current-develop blockchain execution overlay

The upstream EVM execution slice is a concrete contract, not a generic adapter shortcut. Model the
wallet as `WalletAccount`; validate chain ID, wallet identity, RPC network, balances, and allowances
before enabling execution. Keep private keys outside config/logs and perform local signing. Configure
custody through a Rust secret reference such as `signer_private_key_env`; never materialize the
private key in Python.

Reserve exact input quantities and fees with checked integer arithmetic. Serialize nonce ownership,
signed transaction identity, broadcast state, receipt status, replacements, and terminal outcomes so
the transaction lifecycle survives restart. Reconcile the persisted state before accepting new
orders. Unit tests use deterministic mocked RPC responses for reservation and state transitions;
fork tests are separate environment-gated evidence and never default CI.

Reuse the upstream `nautilus-blockchain` crate (`crates/adapters/blockchain/`)
rather than reimplementing EVM plumbing: it ships chain definitions (Ethereum, BSC,
Polygon, Arbitrum, Base) under `rpc/chains/`, Hypersync streaming under
`hypersync/`, contract ABIs under `contracts/`, and the execution client under
`execution/`. See `references/integrations/blockchain.md` for the DeFi model
primitives and configuration surface.

### Phase 2: Implement instruments

Implement pool/market discovery, bidirectional symbol identity, every supported instrument family,
token/currency mapping, complete precision and contract fields, cache boundaries, and definition
updates. Derive pool instrument identity from the pool contract address or protocol pool ID so
same-token pools and fee tiers remain distinct; token-pair-only IDs are valid only when the venue
guarantees uniqueness. Map the AMM swap fee tier to `taker_fee`; LP economics are not trader
`maker_fee`.

### Phase 3: Implement market data

Start with one public stream and instrument. Add AMM quote synthesis or CLOB deltas, trades,
historical requests, unsubscribe, malformed-input, reorg, reconnect, and event-ordering behavior.

### Phase 4: Implement execution

Establish wallet/account identity, private state, receipt monitoring, and reconciliation before
order flow. Then add submit/cancel/modify, unknown-transaction outcomes, fill deduplication, and
order/fill/position/mass-status reports.

### Phase 5: Add optional venue capabilities

Add batch transactions, conditional orders, gas sponsorship, bridges, product-specific data, or
split clients only after the base lifecycle is stable, with independent fixtures and limitations.

### Phase 6: Complete factories and projection

Finalize typed configs, secret redaction, Rust `InstrumentProvider`, data and execution client
factories, `CacheView` and clock inputs, and registration through `LiveNodeBuilder`. Add bounded
PyO3 projection only when supported.

### Phase 7: Prove conformance

Run deterministic functional/integration scenarios plus applicable DataTester and ExecTester
acceptance on a local fork, testnet, or controlled account. Exercise connection failure,
reconnect, shutdown, rate limits, reorgs, uncertain transactions, and recovery; document every
skipped case.

### Phase 8: Measure performance and robustness

Benchmark confirmed hot paths, then signing, hashing, authentication, and codecs. Fuzz every
untrusted parser, decoder, normalizer, signer, and encoder using realistic corpora and strong
invariants.

### Phase 9: Finish documentation and operations

Reconcile the capability matrix and document RPC requirements, credentials, gas/nonce policy,
limits, reconciliation, finality, environment differences, tester entry points, generated output,
known gaps, troubleshooting, and safe operational recovery.

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
- ❌ Never use `tokio::spawn()` for adapter production tasks — use `get_runtime().spawn()`; deterministic tests may use `tokio::spawn()` on their own runtime
- ❌ Do not use `Arc<PyObject>` for ordinary callbacks — prefer direct `PyObject`/`Py<T>` with `clone_py_object()`; justify any exception and audit cycles, weakrefs, cleanup, and PyO3 GC hooks when applicable
- ❌ Don't treat AMM spot price as fill price without modelling slippage

Runtime-spawn rule source (upstream `4692bac35bb11a25eeebb8d7af4d51c55afe53ec`): `.pre-commit-hooks/check_tokio_usage.sh` rejects `tokio::spawn` in adapter production code while skipping `/tests/` files and `#[cfg(test)]` regions, so deterministic tests may use `tokio::spawn()` on their own runtime.

### DEX task ownership (standardized lifecycle)

Own DEX background work with the standardized Nautilus task lifecycle (pinned
`4692bac35`, `crates/live/src/task.rs`; see `nt-adapters` "Task Management" for
the full ownership table): one session `TaskGroup` for the WebSocket stream,
keepalive, and receipt-monitoring loop; a separate command `TaskGroup` for
work spawned by execution commands so a disconnect never reclassifies an
accepted command's outcome; `TaskSlot`/`SharedTaskSlot` for an explicitly
singular transport loop or disconnect operation. Spawn children through
`TaskSpawner` so they stay in the same generation, use the group's
`CancellationToken` as the shutdown signal, and finish with bounded
`finish_shutdown(graceful_timeout, abort_timeout)` so reconciliation and
shutdown failures are observed, not dropped.

## Compliance Checklist

Every adapter must clear `rules/compliance_checklist.md` before use. Run the structural compliance test:

```bash
uv run python -m pytest skills/nt-dex-adapter/tests/test_dex_compliance.py -v
```

Required checks before claiming adapter readiness:

- [ ] 10 phases completed in order and each milestone satisfied
- [ ] Provider/data/exec method contracts implemented (no placeholder `pass`)
- [ ] `get_runtime().spawn()` used for production Rust async tasks (deterministic tests may use `tokio::spawn()` on their own runtime)
- [ ] PyO3 callback bindings prefer direct `PyObject`/`Py<T>`; any `Arc<Py<T>>` exception is justified and cycle-audited
- [ ] Credentials resolved via config/env without plain-text key leakage
- [ ] Fixture payloads sourced from real upstream docs/live captures
- [ ] Async tests avoid arbitrary sleep and use condition-based waiting

## Modern Tooling Standards
- **Dependencies**: Use `uv` for managing the adapter dev environment.
- **Serialization**: For internal data passing, `msgspec` structs are faster than standard classes.
- **Visualization (current V2 Python)**: Inspect recorded data with `TearsheetConfig` and `create_tearsheet` / `create_tearsheet_from_stats` from `nautilus_trader.analysis`; install the `visualization` extra.

## Testing Strategy

```bash
# All DEX adapter tests
uv run python -m pytest skills/nt-dex-adapter/tests/ -v

# Structural compliance only (fastest gate)
uv run python -m pytest skills/nt-dex-adapter/tests/test_dex_compliance.py -v
```

## References

Load these for detailed API information (relative to nt-implement skill folder):
- `references/developer_guide/adapters.md` — Rust-first adapter development guide
- `references/developer_guide/rust.md` — Rust conventions, async runtime patterns
- `references/developer_guide/ffi.md` — FFI memory contract, CVec, abort_on_panic
- `crates/common/src/clients/`: Current Rust `DataClient` / `ExecutionClient` trait bases for live clients
- `references/api_reference/live.md`: LiveMarketDataClient, LiveExecutionClient APIs (legacy v1 snapshot)
- `references/integrations/dydx.md` — On-chain CLOB reference adapter (v4)
- `references/integrations/hyperliquid.md` — DEX perp reference adapter
- `references/integrations/blockchain.md`: `nautilus-blockchain` crate (`crates/adapters/blockchain/`): DeFi primitives, chains, contracts, execution
- `crates/adapters/<adapter>/` — Canonical Rust adapter crate layout; follow the wiring checklist in `references/developer_guide/adapters.md` and expose only the required Python projection under `python/nautilus_trader/adapters/<adapter>/`

## Next Steps

- Wire your adapter: use **nt-strategy-builder-rust** for Rust `LiveNode` or backtest wiring
- Review code: use **nt-review** Rust/FFI checklist before deployment
