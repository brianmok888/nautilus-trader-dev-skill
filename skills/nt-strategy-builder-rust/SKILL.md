---
name: nt-strategy-builder-rust
description: "Use when building a NautilusTrader strategy in Rust (native V2). Covers implementing the Rust `Strategy` trait, `StrategyConfig` builder, event handlers, order/portfolio APIs, PyO3 export, registration with LiveNode/BacktestEngine, and cargo testing. For Python strategies use nt-strategy-builder instead."
---

# Build NautilusTrader Strategies in Rust (V2 native)

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
    // event handlers (all default to no-op; override what you need):
    fn on_start(&mut self) -> anyhow::Result<()> { ... }
    fn on_stop(&mut self) -> anyhow::Result<()> { ... }
    fn on_time_event(&mut self, event: &TimeEvent) -> anyhow::Result<()> { ... }
    fn on_quote(&mut self, quote: &QuoteTick) -> anyhow::Result<()> { ... }
    fn on_bar(&mut self, bar: &Bar) -> anyhow::Result<()> { ... }
    fn on_order_initialized(&mut self, event: OrderInitialized) {}
    fn on_order_event(&mut self, event: OrderEventAny) {}
    fn on_order_denied(&mut self, event: OrderDenied) {}
    fn on_order_submitted(&mut self, event: OrderSubmitted) {}
    fn on_order_rejected(&mut self, event: OrderRejected) {}
    fn on_order_accepted(&mut self, event: OrderAccepted) {}
    fn on_order_filled(&mut self, event: OrderFilled) {}
    fn on_order_canceled(&mut self, event: &OrderCanceled) {}
    // ... modify/expire/trigger/reject handlers mirror the full order lifecycle
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
2. **Write the config first** (`StrategyConfig` is a `bon::Builder`):
   ```rust
   use nautilus_trading::strategy::StrategyConfig;

   #[derive(Clone, Debug, serde::Deserialize, serde::Serialize, bon::Builder)]
   #[builder(finish_fn(name = "build_inner", vis = ""))]
   #[serde(deny_unknown_fields)]
   pub struct YourStrategyConfig {
       pub strategy_id: Option<StrategyId>,
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
           let core_config = StrategyConfig {
               strategy_id: config.strategy_id,
               order_id_tag: Some("001".to_string()),
               ..Default::default()
           };
           Self {
               core: StrategyCore::new(core_config),
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
               TimeInForce::Gtc,
               None,
               None,
               false,
               false,
           )?;
           self.submit_order(order, None, None, None)?;
           Ok(())
       }
   }
   ```
4. **Export via PyO3** (`#[pyclass]` + `#[pymethods]`), registering new modules in
   `crates/pyo3/src/lib.rs`. Register the strategy config as importable so it can be
   loaded from a node config the same way Python strategies are.
5. **Register with a node**:
   - `BacktestEngine` — `engine.add_strategy(your_strategy, your_strategy_id)` (Rust API).
   - `LiveNode` — register the strategy config factory; `LiveNode` is the Rust-backed
     production default for new Rust strategies (the legacy Python-live node is not a
     Rust-strategy target).
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
