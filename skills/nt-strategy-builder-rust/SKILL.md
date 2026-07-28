---
name: nt-strategy-builder-rust
description: "Use when building a NautilusTrader strategy in Rust (native V2). Covers implementing the Rust `Strategy` trait, `StrategyConfig` builder, event handlers, order/portfolio APIs, PyO3 export, registration with LiveNode/BacktestEngine, and cargo testing. For Python strategies use nt-strategy-builder instead."
---

# Build NautilusTrader Strategies in Rust (V2 native)

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as 6e59fd74eaacacbb7410936f1766bd89fcce6f59. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed block-scoped legacy/Cython/v1 and TradingNode enforcement; `tests/test_dev_guide_sync.py` covers leakage and exemption boundaries. |
| G2 V2 example validation | Validate repository Rust examples against the pinned NT V2 develop/master baseline. | Pass | `python3 tools/check_rust_trading_reference_sync.py --compile` matched pinned upstream 6e59fd7 and `cargo check -p nautilus-trading --features examples,high-precision --lib` passed. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py tests/test_dev_guide_sync.py` passed PyO3 registration, live-runner callback, Rust ownership, and V2 boundary regressions. |
| G4 Lane and API shape | Classify supported Python V2, AI/advisory, config/control-plane, and Rust hot-path lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template inventory and V2 API regressions; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 270 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 110 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pending | Current cutover commits and independent post-fix review evidence will be recorded in the final reconciliation report. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Rust strategy gates: production/performance strategies must own `StrategyCore`, `StrategyConfig`, `DataActor` handlers, `nautilus_strategy!` registration, order submission shape, and FFI exposure if needed. Before `Pass`, run `cargo fmt --check`, `cargo nextest`, `cargo clippy`, `cargo deny`, targeted strategy/backtest tests, and document any Python research/config or AI/advisory boundary separately.

## What This Skill Covers

Authoritative Rust-native strategy development for NautilusTrader V2. Strategies
written in Rust implement the `Strategy` trait and run on the same Rust core as
the engines — no Python on the hot path. Use this when the strategy is
performance-critical (HFT, heavy per-tick computation, tight loops) or when you
are shipping a production strategy as part of a Rust adapter/workspace.

For Python strategies (user experimentation, config-heavy research strategies,
the AI/advisory lane) use `nt-strategy-builder` instead. Rust and Python
strategies both run on the same engines; the language choice is a
performance/packaging decision, not a capability one.

**Rust crate**: `nautilus-trading` → `crates/trading/src/strategy/`
**Trait**: `pub trait Strategy: DataActor`
**Runtime wiring**: store `StrategyCore`, invoke `nautilus_strategy!`, implement event handlers in `impl DataActor`
**Config**: `StrategyConfig` (`bon::Builder`, serde, `deny_unknown_fields`)
**Reference strategies** (official, in `crates/trading/src/examples/strategies/`):
`EmaCross`, `CompositeMarketMaker`, `GridMarketMaker`, `DeltaNeutralVol`,
`HurstVpinDirectional`.

## When To Use

- Writing a performance-critical or production strategy in Rust
- Extending a Rust adapter with a co-located strategy
- Porting a Python strategy to Rust for latency/throughput
- Registering a Rust strategy with `LiveNode` or `BacktestEngine` via PyO3

## When NOT To Use

- **Python strategies** → `nt-strategy-builder` (Python `Strategy` class)
- **Indicators / signal math** → `nt-signals` (Rust `Indicator` trait)
- **Actors / model hosting** → implement `Actor`; see `nt-architect`
- **Backtest engine config** → `nt-backtest` (works for both Rust and Python strategies)
- **Adapter networking/parsing** → `nt-adapters` (Rust adapter crate)

## Core API (authoritative, from `crates/trading/src/strategy/mod.rs`)

A Rust strategy implements the `Strategy` runtime contract through
`nautilus_strategy!`. `Strategy` extends `DataActor`, but normal event handlers
(`on_start`, `on_quote`, `on_bar`, `on_stop`) belong in `impl DataActor`, not in
an ad-hoc `impl Strategy` block. Store a `StrategyCore` field and call facade
methods on `self` for order and portfolio APIs.

```rust
pub trait Strategy: DataActor {
    fn external_order_claims(&self) -> Option<Vec<InstrumentId>> { None }
    fn strategy_id(&self) -> Option<StrategyId> where Self: StrategyNative { ... }
    fn order(&self) -> OrderApi<'_> where Self: StrategyNative { ... }
    fn portfolio(&self) -> PortfolioApi<'_> where Self: StrategyNative { ... }
    fn submit_order(
        &mut self,
        order: OrderAny,
        position_id: Option<PositionId>,
        client_id: Option<ClientId>,
        params: Option<Params>,
    ) -> anyhow::Result<()> where Self: StrategyNative { ... }
    fn submit_order_list(...) -> anyhow::Result<()> where Self: StrategyNative { ... }
    fn on_order_initialized(&mut self, event: OrderInitialized) {}
    fn on_order_event(&mut self, event: OrderEventAny) {}
    fn on_order_denied(&mut self, event: OrderDenied) {}
    fn on_order_submitted(&mut self, event: OrderSubmitted) {}
    fn on_order_rejected(&mut self, event: OrderRejected) {}
    fn on_order_accepted(&mut self, event: OrderAccepted) {}
    fn on_order_filled(&mut self, event: &OrderFilled) {}
    fn on_order_fill_voided(&mut self, event: &OrderFillVoided) {}
    fn on_order_canceled(&mut self, event: &OrderCanceled) {}
    // Lifecycle and market-data handlers belong to `impl DataActor`.
}
```

Key points:
- `on_start`/`on_stop` return `anyhow::Result<()>`; subscribe/unsubscribe there.
- `order()` returns the order-creation API (`order().market(...)`, `.limit(...)`, etc.).
- `portfolio()` returns the read-side portfolio API (positions, balances, PnL).
- `submit_order(order, position_id, client_id, params)` — pass `None` for defaults.
- Handlers receive **owned** events (except a few `&`-reference ones); never mutate
  after publication — publish state transitions, never edit in-flight events.

## Implementation Workflow (TDD)

1. **Scaffold the crate module** under your adapter or a strategies crate:
   ```
   crates/<your_crate>/src/strategies/your_strategy/
   ├── mod.rs        # re-exports Strategy + Config
   ├── config.rs     # YourStrategyConfig (StrategyConfig wrapper)
   ├── strategy.rs   # YourStrategy struct + impl Strategy
   └── tests.rs      # cargo tests (rstest fixtures)
   ```
2. **Write the config first** (derive a `bon::Builder` for the concrete config and embed the base `StrategyConfig`):
   ```rust
   use nautilus_trading::strategy::StrategyConfig;

   #[derive(Clone, Debug, serde::Deserialize, serde::Serialize, bon::Builder)]
   pub struct YourStrategyConfig {
       #[builder(default = StrategyConfig {
           strategy_id: Some(StrategyId::from("YOUR_STRATEGY-001")),
           order_id_tag: Some("001".to_string()),
           ..Default::default()
       })]
       pub base: StrategyConfig,
       pub instrument_id: InstrumentId,
       pub fast_period: usize,
       pub slow_period: usize,
       #[builder(default)]
       pub order_qty: Quantity,
   }
   ```
3. **Implement the runtime shape**, modelled on upstream Rust strategies:
   ```rust
   use nautilus_common::actor::DataActor;
   use nautilus_trading::{
       nautilus_strategy,
       strategy::{Strategy, StrategyConfig, StrategyCore},
   };

   pub struct YourStrategy {
       core: StrategyCore,
       instrument_id: InstrumentId,
       fast_period: usize,
       slow_period: usize,
       order_qty: Quantity,
       // mutable state (EMA accumulators, position tracking, etc.)
   }

   impl YourStrategy {
       pub fn new(config: YourStrategyConfig) -> Self {
           Self {
               core: StrategyCore::new(config.base),
               instrument_id: config.instrument_id,
               fast_period: config.fast_period,
               slow_period: config.slow_period,
               order_qty: config.order_qty,
               // ...
           }
       }

       pub fn from_config(config: YourStrategyConfig) -> anyhow::Result<Self> {
           Ok(Self::new(config))
       }
   }

   nautilus_strategy!(YourStrategy);

   impl DataActor for YourStrategy {
       fn on_start(&mut self) -> anyhow::Result<()> {
           self.subscribe_quotes(self.instrument_id, None, None);
           Ok(())
       }

       fn on_stop(&mut self) -> anyhow::Result<()> {
           self.unsubscribe_quotes(self.instrument_id, None, None);
           Ok(())
       }

       fn on_quote(&mut self, _quote: &QuoteTick) -> anyhow::Result<()> {
           // update EMA state, then on crossover:
           let order = self.order().market(
               self.instrument_id,
               order_side,
               self.order_qty,
               None, // time_in_force
               None, // reduce_only
               None, // quote_quantity
               None, // exec_algorithm_id
               None, // exec_algorithm_params
               None, // tags
               None, // client_order_id
           );
           self.submit_order(order, None, None, None)?;
           Ok(())
       }
   }
   ```
4. **Export via PyO3** (`#[pyclass]` + `#[pymethods]`) in the owning crate’s
   `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates the crate submodule.
   Register the strategy config as importable so node config can load it.
5. **Register with a node**:
   - `BacktestEngine` — `engine.add_strategy(your_strategy)?` (Rust API).
   - `LiveNode` — native Rust uses `node.add_strategy(your_strategy)?`. The upstream-only `add_builtin_strategy(...)` PyO3 helper is feature-gated to bundled example strategies and is not a general extension path. For custom production strategies, keep native Rust registration or expose a purpose-built owning-crate PyO3 registration surface. The legacy Python-live node is not a Rust-strategy target.
6. **Test in Rust** before wiring Python:
   ```bash
   cargo nextest run -p <your_crate> --features "python,ffi,high-precision,defi" \
       --cargo-profile nextest
   cargo clippy --workspace --all-targets --no-deps \
       --features "ffi,python,high-precision,defi" -- -D warnings
   ```
   Run precision-sensitive FFI work with `HIGH_PRECISION=true` to avoid regenerating
   committed bindings.

## V2 cutover: when to choose Rust vs Python for a strategy

NT v2 compatibility note: this whole file is Rust-native; the legacy Python-live
`TradingNode` is referenced only as the legacy contrast to `LiveNode`.

| Situation | Choose | Reason |
|---|---|---|
| HFT / sub-millisecond per-event, large tick volume | **Rust** (`Strategy` trait) | No Python GIL, zero-cost abstractions |
| Heavy per-tick math (order-book features, multi-TF) | **Rust** | Indicators/actors also Rust by default |
| Strategy shipped inside a Rust adapter crate | **Rust** | Co-locate with adapter networking/parsing |
| Research/experimentation, config-heavy, rapid iteration | **Python** (`nt-strategy-builder`) | Faster dev loop, PyO3 stubs |
| AI/advisory lane (model inference, signal aggregation) | **Python**, async, off hot path | Never execution-critical |
| Needs a Python-only library not available in Rust | **Python** | Bind rather than rewrite |

Rule of thumb: start in Python (`nt-strategy-builder`), port to Rust
(`nt-strategy-builder-rust`) when profiling shows the strategy on the hot path or
when the strategy ships as part of a production Rust adapter.

## Key Conventions

- **Message immutability**: publish new messages/state transitions; never mutate
  events, commands, requests, or responses after publication.
- **Ownership at async boundaries**: cache accessors may return scoped wrapper
  newtypes; request owned snapshots when values cross async/event boundaries.
- **No `get_runtime().block_on()` inside trait methods**: spawn work instead;
  `block_on` is only valid outside an ambient Tokio runtime (e.g. PyO3 entry).
- **Precision**: run FFI/precision-sensitive cargo commands with
  `HIGH_PRECISION=true`; do not hand-edit generated bindings.
- **Error handling**: `on_*` handlers return `anyhow::Result<()>`; propagate with `?`.

## References

- `crates/trading/src/strategy/mod.rs` — `Strategy` trait (source of truth)
- `crates/trading/src/strategy/config.rs` — `StrategyConfig`
- `crates/trading/src/examples/strategies/` — `EmaCross`, `CompositeMarketMaker`,
  `GridMarketMaker`, `DeltaNeutralVol`, `HurstVpinDirectional` (reference impls)
- `skills/nt-strategy-builder` — Python strategy surface
- `skills/nt-adapters` — Rust adapter crate layout (co-locate strategies here)
- `skills/nt-testing` — `nautilus_testkit` ExecTester for execution validation

## Next Step

Validate the Rust strategy with the ExecTester matrix (`nt-testing`) before
claiming production readiness; an adapter/strategy passing ExecTester groups 1–5
is baseline compliant.
