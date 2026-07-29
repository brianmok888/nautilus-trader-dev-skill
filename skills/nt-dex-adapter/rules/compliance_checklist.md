NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# DEX Adapter Compliance Checklist

Every custom DEX adapter must clear this checklist before use in backtesting or live trading.
Run the current Rust production contract gate first:

```bash
uv run pytest skills/nt-dex-adapter/tests/test_dex_compliance.py -v
```

The quarantined Python files have a separate non-production migration smoke:

```bash
uv run pytest skills/nt-dex-adapter/tests/test_nonproduction_migration_templates.py -v
```

This migration smoke covers all retained Python config, provider, client, and
factory templates. It does not gate production approval.

Then complete the manual checklist below.

---

## Quarantined Python Migration Layer

Python-only live adapters are migration/reference-only and cannot receive APPROVED FOR USE. Current production approval requires the Rust core, Rust clients/factories, and `LiveNodeBuilder` wiring below.

### InstrumentProvider

- [ ] `load_all_async()` implemented and fetches from chain/RPC
- [ ] `load_ids_async(instrument_ids)` implemented
- [ ] `get_all()` returns `dict[InstrumentId, Instrument]`
- [ ] `find(instrument_id)` returns `Instrument | None`
- [ ] Instrument IDs formatted as `{SYMBOL}.{VENUE}`
- [ ] Token fee tier mapped to `maker_fee` / `taker_fee` on instrument
- [ ] Minimum quantity set from pool/market minimum trade size
- [ ] `sandbox_mode` skips mainnet RPC calls during tests

### LiveMarketDataClient

- [ ] `_connect()` calls `load_all_async()` on instrument provider
- [ ] `_disconnect()` cancels polling tasks / closes WS connections
- [ ] `_subscribe_quote_ticks(instrument_id)` implemented
- [ ] `_subscribe_trade_ticks(instrument_id)` implemented
- [ ] `_subscribe_order_book_deltas(instrument_id)` implemented (or documented as N/A for AMM)
- [ ] `_unsubscribe_quote_ticks` / `_unsubscribe_trade_ticks` / `_unsubscribe_order_book_deltas` implemented
- [ ] `_handle_quote_tick()` called for each new pool state
- [ ] `_handle_trade_tick()` called for each confirmed on-chain swap
- [ ] No blocking RPC calls in any handler method
- [ ] Reconnection logic with exponential backoff

### LiveExecutionClient

- [ ] `_connect()` verifies wallet balance and establishes stream
- [ ] `_disconnect()` shuts down cleanly
- [ ] `_submit_order(order)` builds, signs, and broadcasts tx
- [ ] `_cancel_order(order)` supported or raises `NotImplementedError` with explanation
- [ ] `_cancel_all_orders(instrument_id)` supported or raises `NotImplementedError`
- [ ] `_query_order(client_order_id)` queries on-chain status
- [ ] `generate_account_state()` called after every balance-changing tx
- [ ] `generate_order_status_report()` implemented for reconciliation
- [ ] Transaction revert → `generate_order_rejected()` (NOT silent drop)
- [ ] Gas cost included as `commission` in `generate_order_filled()`
- [ ] Slippage tolerance applied to `min_amount_out` before submission

### Configuration

- [ ] Private key uses `SecretStr` (not plain `str`)
- [ ] RPC URL configurable via env var or config field (not hardcoded)
- [ ] `sandbox_mode: bool` flag present on exec client config
- [ ] `max_slippage_bps: int` configurable
- [ ] Gas limit configurable with safe default
- [ ] `InstrumentProviderConfig`, `DataClientConfig`, `ExecClientConfig` all defined

### Factory (Rust V2 default)

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

- [ ] Rust data and execution client factory implementations compile in the adapter crate
- [ ] Factories are registered through `LiveNode::builder(...)` / `LiveNodeBuilder`
- [ ] Factory names and routing are explicit; duplicate names fail closed
- [ ] Any Python `ClientFactory` is labelled legacy migration-only and is not used as the production default

---

## Rust Core (required for production approval)

- [ ] Copyright header on every source file (`2015-2026 Nautech Systems Pty Ltd`)
- [ ] Module-level `//!` documentation
- [ ] `new_checked()` + `new()` constructor pattern on all types
- [ ] `anyhow::bail!` for early error returns (not `Err(anyhow::anyhow!(...))`)
- [ ] `FAILED` constant used in `.expect()` calls
- [ ] `AHashMap`/`AHashSet` for price/instrument caches
- [ ] Standard `HashMap` for RPC client configuration
- [ ] `get_runtime().spawn()` for all async tasks (NOT `tokio::spawn()`)
- [ ] `abort_on_panic` wrapper on every `extern "C"` FFI function
- [ ] Matching `drop` function for every FFI constructor
- [ ] Type-specific CVec drop functions (if CVec used)
- [ ] PyO3 callbacks prefer direct `PyObject` / `Py<T>` plus `clone_py_object()`; any `Arc<Py<T>>` use is justified, cycle-audited, and paired with weakrefs/cleanup/GC hooks when needed
- [ ] `py_*` prefix on all Rust functions exposed via PyO3
- [ ] `SAFETY:` comment on every `unsafe` block
- [ ] `#[repr(C)]` on all FFI types
- [ ] `#![deny(unsafe_op_in_unsafe_fn)]` in crate root
- [ ] No `.unwrap()` in production code
- [ ] No `.clone()` in hot paths

---

## Testing

- [ ] **Unit: instrument parsing** — pool metadata → Nautilus instrument round-trip
- [ ] **Unit: quote synthesis** — pool reserves → `QuoteTick` correct mid-price
- [ ] **Unit: order book builder** — pool state → L2 order book levels
- [ ] **Unit: slippage model** — `amount_in` → `execution_price` follows AMM formula
- [ ] **Unit: signing interface** — tx builder produces deterministic output (mock key)
- [ ] **Integration: BacktestEngine** — adapter wired into engine with mock DEX data, runs without error
- [ ] **Rust production contract gate** — `test_dex_compliance.py` passes Rust client/factory, PyO3, and `LiveNodeBuilder` guidance checks
- [ ] **No live RPC required** — all tests run offline with mocks/fixtures

---

## Documentation

- [ ] README: supported pool/market types
- [ ] README: RPC endpoint requirements and rate limits
- [ ] README: gas configuration guidance
- [ ] README: testnet / local fork configuration
- [ ] README: known limitations (e.g., cancel not supported on AMM, no partial fills)
- [ ] CHANGELOG or version history if adapter is updated

---

## Sign-Off

| Item | Status | Notes |
|---|---|---|
| Quarantined Python migration references reviewed | ☐ / ✓ | Not a production approval gate |
| Rust core, clients, factories, and `LiveNodeBuilder` wiring complete | ☐ / ✓ | Required |
| All tests pass offline | ☐ / ✓ | |
| Rust production contract gate passes | ☐ / ✓ | `test_dex_compliance.py` |
| Documentation complete | ☐ / ✓ | |
| Reviewed with nt-review Rust/FFI checklist | ☐ / ✓ | |
| **APPROVED FOR USE** | ☐ / ✓ | |
