NT v2 compatibility note: legacy/v1/Cython/TradingNode references in this file are labelled legacy/reference-only unless an adjacent paragraph explicitly says they are current Rust/PyO3/LiveNode guidance.

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-review Knowledge Base

**Purpose:** Validate NautilusTrader implementations against conventions, trading correctness, performance, and testability before deployment.

**Entry Point:** `SKILL.md` (72 lines)

## REVIEW DIMENSIONS (8)

1. **Nautilus Conventions** — Lifecycle methods, API usage, naming
2. **Trading Correctness** — Position sizing, order management, risk checks, edge cases
3. **Performance** — Blocking calls, memory management, efficient data handling
4. **Testability** — Backtest compatibility, isolation, logging
5. **Live Trading** — Reconciliation, network resilience, order state management, risk controls
6. **Rust/FFI** — Memory safety, style conventions, PyO3 bindings
7. **Benchmarking** — Criterion/iai structure, profiling
8. **Visualization** — Plotly tearsheet config (v1.221.0+)

## ASSURANCE-DRIVEN ENGINEATION (Core Philosophy)

- **Executable Invariants:** Critical paths (risk, execution) verified by unit tests, property tests, or fuzzers
- **Parity:** Strategy code identical and deterministic across backtest/paper/live
- **Soundness:** Rust code free of memory safety bugs (`#![deny(unsafe_op_in_unsafe_fn)]`)

## REVIEW SEVERITY

| Level | Meaning | Examples |
|-------|---------|---------|
| **Blocker** | Must fix before merge | Runtime/FFI violations, missing reconciliation, execution coupling, secret leakage |
| **Major** | Should fix before merge | Incomplete method contracts, missing fallback/provenance, missing test categories |
| **Minor** | Can fix later | Naming drift, doc gaps with otherwise correct behavior |

## LIFECYCLE METHOD CHECKS

| Method | Required | Red Flags |
|--------|----------|-----------|
| `__init__` | `super().__init__(config)` first | Using `clock`/`logger`/`cache` here (not yet available) |
| `on_start` | Load instrument, models, subscribe | Subscribing before requesting historical data |
| `on_stop` | Cancel orders, unsubscribe | No cleanup |
| `on_reset` | Reset state for reuse | No buffer/cache clearing |

## ADAPTER REVIEW GATE

Fail review if missing:
- Phase compliance with the official dependency structure:
  1. Phase 0: Define scope
  2. Phase 1: Build the protocol core
  3. Phase 2: Implement instruments
  4. Phase 3: Implement market data
  5. Phase 4: Implement execution
  6. Phase 5: Add optional venue capabilities
  7. Phase 6: Complete factories and projection
  8. Phase 7: Prove conformance
  9. Phase 8: Measure performance and robustness
  10. Phase 9: Finish documentation and operations
- Required interfaces: InstrumentProvider async loaders, LiveDataClient contract, LiveExecutionClient reconciliation
- Factory/config contract: `create(loop, name, config, msgbus, cache, clock)` with safe credential handling
- Runtime/FFI safety: no `tokio::spawn()` in adapters, direct `PyObject`/`Py<T>` for ordinary callbacks, justified/cycle-audited `Arc<Py<T>>` exceptions only, no blocking hot handlers
- Testing doctrine: real payload fixtures, no sleep-based timing, cover providers/data/execution/factories

G2 `cargo check` is compilation only. Never treat it as spec, testnet, resilience, fuzz, or
operations acceptance evidence; require separate Phase 8-10 evidence for those claims.

## QUICK CHECK (<5 min)

- [ ] All lifecycle methods call `super()`
- [ ] `on_start` fetches instrument from cache with null check
- [ ] `request_bars` before `subscribe_bars`
- [ ] `on_stop` cancels orders and unsubscribes
- [ ] Type hints on all methods
- [ ] No blocking calls in handlers
- [ ] External integrations advisory-only and non-blocking

## FULL REVIEW (15-30 min)

Quick check + Conventions + Trading Correctness + Performance + Testability + (if adapter) Adapter Gate + (if Rust) Rust/FFI Checklist.

## COMMON ISSUES BY COMPONENT

| Component | Typical Issues |
|-----------|---------------|
| **Strategy** | Missing rejection handling, no position limits, blocking in `on_bar`, not canceling on stop |
| **Actor** | Model loading in handler (not `on_start`), unbounded signal history, no warmup, missing `on_reset` |
| **Indicator** | Missing `initialized` property, missing `reset` method, wrong handler signature |
| **Adapter** | Blocking HTTP in data handlers, no reconnection, not Rust-first, `tokio::spawn()` misuse |
| **Data Catalog** | Not using `ParquetDataCatalog`, missing `BacktestDataConfig` for custom data, missing `metadata` |

## RUST/FFI CHECKLIST (16 items)

- [ ] Copyright header (2015-2026 Nautech Systems)
- [ ] Module documentation with feature flags
- [ ] `new_checked()` + `new()` constructor pattern
- [ ] `anyhow::bail!` for early returns (not `Err(anyhow::anyhow!(...))`)
- [ ] `FAILED` constant in `.expect()` calls
- [ ] `AHashMap`/`AHashSet` for non-security collections
- [ ] `abort_on_panic` on all FFI functions
- [ ] Matching drop for every constructor
- [ ] Type-specific CVec drops (never generic)
- [ ] PyO3 callbacks prefer direct `PyObject` / `Py<T>` plus `clone_py_object()`; any `Arc<Py<T>>` exception is justified, cycle-audited, and paired with weakrefs/cleanup/GC hooks when needed
- [ ] `py_*` prefix on Rust function names
- [ ] SAFETY comments on all unsafe blocks
- [ ] `#[repr(C)]` on FFI types
- [ ] `#![deny(unsafe_op_in_unsafe_fn)]` in crate root
- [ ] Unit tests covering unsafe code paths
- [ ] No `.clone()` in hot paths, no `.unwrap()` in production

### Rust Doc Mood
- **Indicative:** "Returns the client" ✅
- **Imperative:** "Return the client" ❌

NT v2 compatibility note: the v1.223.0 and v1.224.0 change sections below are
migration/reference-only history; verify current Rust V2 behavior against the pinned
upstream `crates/` sources before applying any item.

### v1.223.0 Rust Breaking Change (legacy: migration/reference-only)
`AddAssign`/`SubAssign` removed from `Price`/`Quantity`/`Money`. Use `x = x + y` not `x += y`.

### v1.224.0 Changes (legacy: migration/reference-only)
- `fill_limit_at_touch` → `fill_limit_inside_spread`; `BestPriceFillModel` fills inside spread by default
- Coinbase International adapter (`COINBASE_INTX`) fully removed
- `InstrumentProvider` only needs `load_all_async`; `load_ids_async`/`load_async` have defaults
- Binance Ed25519 Spot/Margin raises `ValueError`; Futures soft-deprecated
- Hyperliquid `builder_fee_refresh_mins` config removed
- WS `connect()` needs `loop_=self._loop` in adapter code


## LIVE TRADING CHECKLIST (9+ items)
NT v2 compatibility note: v1.x checklist items below are migration/reference-only where they mention legacy/v1 removals; prefer current Rust v2/PyO3 guidance for new work.


- [ ] Reconciliation enabled with appropriate lookback (≥60 min)
- [ ] Timeouts configured for all connection phases
- [ ] External order claims configured if resuming
- [ ] All order lifecycle events handled (reject, cancel, expire, partial fill)
- [ ] Reconnection logic in adapters with exponential backoff
- [ ] Position limits and circuit breaker configured

NT v2 compatibility note: the v1.223.0 checklist entries below are migration/reference-only history superseded by the current Rust V2 items above.

- legacy: migration/reference-only — v1.223.0 `trade_execution` default `True` / set `False` for bar-only — V2: execution behavior is configured through the Rust execution engine and venue configs, not a strategy-level `trade_execution` flag.
- legacy: migration/reference-only — v1.223.0 `Quantity - Quantity` returns `Quantity`; `ValueError` if < 0 — V2: quantity arithmetic is enforced by the Rust model types in `crates/model`.
- legacy: migration/reference-only — v1.223.0 dYdX v3 adapter removed; use `nautilus_trader.adapters.dydx` — V2: the maintained dYdX adapter is the Rust implementation under `crates/adapters/dydx` exposed at `nautilus_trader.adapters.dydx`.

## PERFORMANCE CHECKLIST

- [ ] Criterion for end-to-end scenarios (>100ns)
- [ ] iai for micro-benchmarks (instruction counts)
- [ ] Setup outside timing loops
- [ ] `black_box` on inputs/outputs
- [ ] `harness = false` in Cargo.toml
- [ ] Benchmarks in `benches/` directory
- [ ] Flamegraph for optimization work
- [ ] Before/after comparison documented

## REFERENCES (symlinked)

- `references/developer_guide/` — coding_standards.md, python.md, rust.md, ffi.md, testing.md, benchmarking.md, adapters.md
- `references/concepts/` — backtesting.md, live.md

## PREVIOUS STEP

Components implemented via **nt-implement** skill.

## V2 hardening checkpoints

- Reject stale ExecTester guidance: Python must use constructor keywords; Rust must use `ExecTesterConfig::builder()`.
- Reject `Python::attach` from Tokio worker tasks for Python callbacks; require live runner channels.
- Check `OrderFillVoided`/`VOIDED`, `use_mark_prices` default true, `carry_replay_events_on_reopen`, `RedisMessageBusBacking`, SQL/catalog migration, deferred V2 limits, shared adapter task tracking when supported, and `#![deny(unsafe_op_in_unsafe_fn)]`.
