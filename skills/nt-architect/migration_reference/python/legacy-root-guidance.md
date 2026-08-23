# Legacy Python Root Guidance

> **Migration/reference-only.** This is the pre-cutover root guidance preserved for Python migration and historical review. It is not an active production lane.

---
name: nt-architect
description: "Use when translating research outputs (models, signals) into nautilus_trader component architecture. Guides component decomposition, data flow design, and implementation planning."
---

# Nautilus Trader Architecture Design

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `f725e184dbd2f7432b5c7b9458b4ef6d1f85fd5f`; current-develop drift is version-scoped in `README.md`. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 25 tests. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-architect` passed the skill domain's scoped examples and owners against `f725e184dbd2f7432b5c7b9458b4ef6d1f85fd5f`; schema-v2 provenance is recorded in `references/g2-evidence/nt-architect.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 tests. |
| G4 Lane and API shape | Classify migration-only Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed 24 tests. |
| G7 Completion report | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current evidence is recorded in `references/g2-evidence/nt-architect.json`; repository closure is summarized in `docs/tracking/Findings.md`. |


Architecture gates: produce a component ownership matrix where Rust owns strategy, research/config, networking, parsing, normalization, and execution-critical state. All Python material is migration/reference-only. Designs are `Pending` until the handoff names the Rust crate/module, PyO3 boundary, message bus flow, and tests for each production component.

## Overview

Translate research outputs (trained ML models + signal generation logic) into a nautilus_trader component architecture before writing any code. This skill guides the decomposition of research into Nautilus components and produces an architecture document for implementation.

## When to Use

- After completing research/alpha discovery (e.g., HMM regime detection, meta-learners)
- Before implementing any Nautilus components
- When designing a new trading system from research

## Adapter-Aware Architecture Constraints (2026 Guide Alignment)

If the architecture includes a custom or modified adapter, enforce these constraints in the design doc:

- **Lifecycle ordering**: the architecture must preserve the adapter 7-phase dependency order.
- **Boundary clarity**:
  - Rust owns production adapter contracts and implementations: `InstrumentProvider`, data/execution clients, factory wiring, networking, parsing, normalization, and execution-critical state.
  - PyO3 exposes reviewed Rust capabilities only through bounded bindings. Under this repository's cutover policy, Python strategy, research, configuration, and orchestration material is migration/reference-only.
- **Contract completeness**: include explicit method families for provider/data/execution clients so implementation cannot skip required methods.
- **Runtime and safety assumptions**: record async/runtime rules (`get_runtime().spawn()` in adapter Rust paths, no blocking hot handlers, direct `PyObject`/`Py<T>` for ordinary callbacks; justify and cycle-audit any `Arc<Py<T>>` binding).
- **Validation plan by phase**: each architecture output should map phases to concrete milestone checks and test artifacts (fixtures, integration tests, reconciliation checks).

## Architecture Design Process

### Design principles invariant

Preserve message immutability across actor, strategy, adapter, cache, and
message-bus boundaries. Design components to publish new messages or state
transitions rather than mutating events, commands, requests, or responses after
publication. See `references/developer_guide/contracts/design_principles.md`.

### Phase 1: Intake Research Outputs

Identify and categorize what your research produced:

**Trained Models** (become Actor-hosted inference):
- Regime detection models (HMM, clustering)
- Signal prediction models (meta-learners, classifiers)
- Feature transformation models (PCA, autoencoders)

**Signal Logic** (becomes Strategy or Indicator logic):
- Entry/exit rules based on model outputs
- Position sizing formulas
- Risk thresholds and filters

**Data Requirements**:
- Input data types (bars, ticks, custom features)
- Timeframes and instruments
- Warmup periods for indicators/models

### Phase 2: Component Decomposition

Use this decision tree to assign research elements to Nautilus components:

```
Research Element
    │
    ├─► Does it TRADE (submit orders)?
    │       │
    │       YES ──► STRATEGY
    │       │       - Order management
    │       │       - Position tracking
    │       │       - Entry/exit execution
    │       │
    │       NO ──► Does it produce DATA for other components?
    │               │
    │               ├─► Stateless computation on market data?
    │               │       │
    │               │       YES ──► INDICATOR
    │               │               - Technical indicators
    │               │               - Feature calculations
    │               │               - Stateless transformations
    │               │
    │               ├─► Stateful computation or ML inference?
    │               │       │
    │               │       YES ──► ACTOR
    │               │               - Model hosting
    │               │               - Regime detection
    │               │               - Signal aggregation
    │               │               - Complex state management
    │               │
    │               └─► Custom data flowing through message bus?
    │                       │
    │                       YES ──► CUSTOM DATA TYPE
    │                               - Regime states
    │                               - Signal values
    │                               - Feature vectors
```

#### Language boundary: Rust core vs Python (V2 default)

V2 is Rust-core with Python bindings. After assigning each element to a
component above, assign its *language* using this boundary. The default for
new V2 work is Rust; Python is reserved for the boundaries listed below.

NT v2 compatibility note: this whole file references the legacy Python-live `TradingNode` only as reference-only context for migration; for Rust v2 / Rust-backed work use `LiveNode`.

| Concern | Default language | Notes |
|---|---|---|
| Networking clients (HTTP/WebSocket), request signing, rate limiting | **Rust** (`crates/adapters/<venue>/src/{http,websocket}`) | Performance-critical; mirror the official adapter crate layout |
| Venue parsing / data normalization | **Rust** (`crates/adapters/<venue>/src/common/parse.rs`) | Hot path |
| Core domain model, identifiers, value types, engine state | **Rust** (`crates/`) | Execution-critical state stays in Rust |
| Live node plumbing, execution engine | **Rust** (`LiveNode`, Rust-backed) | Prefer `LiveNode` for new production; legacy Python-live `TradingNode` is reference-only |
| User orchestration, config, and research strategy | **Rust** | Repository cutover policy; Python examples are migration/reference-only |
| Production/performance strategy logic | **Rust** (`crates/trading/`, `nautilus_strategy!`) | HFT, tight loops, or strategies shipped with Rust adapters |

Official Rust adapter crate layout (from the developer guide) to target when an
element belongs in Rust:

```
crates/adapters/your_adapter/
├── src/
│   ├── common/    # consts.rs credential.rs enums.rs error.rs models.rs parse.rs retry.rs urls.rs testing.rs
│   ├── http/      # client.rs error.rs models.rs parse.rs query.rs   (REST + auth + rate limit)
│   └── websocket/ # client.rs dispatch.rs handler.rs messages.rs parse.rs subscription.rs
```

Rule of thumb: if the element sits on the networking/parse/perf/state path it
goes in Rust; Python stays asynchronous and off the execution-
critical path.

### Phase 3: Data Flow Design

#### Message Bus Patterns

**Signals** (lightweight, primitive values — str, float, int, bool, or bytes):
```python
# Publisher (Actor)
self.publish_signal(name="regime_state", value="trending", ts_event=ts)

# Subscriber (Strategy)
self.subscribe_signal("regime_state")
def on_signal(self, signal):
    if signal.value == "trending":
        self.enable_trend_following()
```

**Custom Data with `@customdataclass`** (structured, complex values — auto-generated constructor):
```python
from nautilus_trader.model.custom import customdataclass
from nautilus_trader.core.data import Data
from nautilus_trader.model.identifiers import InstrumentId

@customdataclass
class RegimeData(Data):
    instrument_id: InstrumentId = InstrumentId.from_str("BTCUSDT-PERP.BINANCE")
    regime: str = "unknown"
    confidence: float = 0.0
    transition_prob: float = 0.0

# Publisher (Actor)
self.publish_data(
    DataType(RegimeData, metadata={"instrument_id": "BTCUSDT-PERP.BINANCE"}),
    data,
)

# Subscriber (Strategy)
self.subscribe_data(
    data_type=DataType(RegimeData, metadata={"instrument_id": "BTCUSDT-PERP.BINANCE"}),
)
def on_data(self, data: Data):
    if isinstance(data, RegimeData):
        self.handle_regime(data)
```

**Custom Data with manual `Data` subclass** (full control, explicit ts_event/ts_init):
```python
from nautilus_trader.core.data import Data

class RegimeData(Data):
    def __init__(self, regime: str, confidence: float, ts_event: int, ts_init: int) -> None:
        self.regime = regime
        self.confidence = confidence
        self._ts_event = ts_event
        self._ts_init = ts_init

    @property
    def ts_event(self) -> int:
        return self._ts_event

    @property
    def ts_init(self) -> int:
        return self._ts_init
```

**Order Fill/Cancel Handling** (keep execution lifecycle in a Rust strategy):
```rust
nautilus_strategy!(ExecutionStrategy, {
    fn on_order_filled(&mut self, event: &OrderFilled) {
        log::info!("Fill: {} {} @ {}", event.order_side, event.last_qty, event.last_px);
    }

    fn on_order_canceled(&mut self, event: &OrderCanceled) {
        log::info!("Cancel: {}", event.client_order_id);
    }
});
```

The strategy runtime dispatches `OrderEventAny` variants to these callbacks.
Use the lower-level message-bus `subscribe_order_events` only for an explicitly
external/custom observer, not ordinary strategy lifecycle handling.

#### Typical Data Flow Patterns

**Pattern: ML Model → Signal → Strategy**
```
[Market Data] → [FeatureActor] → [RegimeActor] → publish_signal → [Strategy]
                 (features)       (HMM inference)                  (trades)
```

**Pattern: Multi-Timeframe Aggregation**
```
[1-min bars] → [Indicator] → [AggregatorActor] → publish_data → [Strategy]
[5-min bars] → [Indicator] ↗
[1-hour bars] → [Indicator] ↗
```

**Pattern: Ensemble Signals**
```
[Model1Actor] → signal1 ↘
[Model2Actor] → signal2 → [EnsembleActor] → final_signal → [Strategy]
[Model3Actor] → signal3 ↗
```

### Phase 4: State Management

#### Where State Lives

| State Type | Location | Access Pattern |
|------------|----------|----------------|
| Orders, Positions | Cache | `self.cache.orders()`, `self.cache.positions()` |
| Instruments, Accounts | Cache | `self.cache.instrument()`, `self.cache.account()` |
| Market Data | Cache | `self.cache.quote_tick()`, `self.cache.bar()` |
| Model State (weights, params) | Actor attribute | `self.model`, loaded in `on_start` |
| Regime/Signal State | Actor attribute | `self.current_regime` |
| Strategy-specific State | Strategy attribute | `self.is_position_open` |

#### State Initialization in `on_start`

```python
def on_start(self) -> None:
    # 1. Load instrument from cache
    self.instrument = self.cache.instrument(self.config.instrument_id)

    # 2. Load models (msgspec preferred for serialization)
    self.model = load_model(self.config.model_path)

    # 3. Initialize indicators
    self.ema = ExponentialMovingAverage(self.config.ema_period)
    self.register_indicator_for_bars(self.config.bar_type, self.ema)

    # 4. Request historical data for warmup
    self.request_bars(self.config.bar_type)

    # 5. Subscribe to live data
    self.subscribe_bars(self.config.bar_type)
```

### Phase 5: Lifecycle Planning

#### Initialization Order

Components are initialized in dependency order:

1. **Custom Data Types** - Define data structures first
2. **Indicators** - Stateless computations
3. **Actors** - Model hosting, feature generation
4. **Strategies** - Trading logic (consumes outputs from above)

#### Warmup Requirements

Document warmup needs for each component:

| Component | Warmup Requirement | Method |
|-----------|-------------------|--------|
| EMA(20) | 20 bars minimum | `request_bars()` in `on_start` |
| HMM Regime | 100+ bars for stable regime | Historical inference in `on_historical_data` |
| Custom Features | Depends on lookback | Calculate on historical before live |

#### Dependency Graph Example

```
CustomDataTypes (RegimeData, FeatureData)
        │
        ▼
   Indicators (EMA, RSI, custom features)
        │
        ▼
   FeatureActor (aggregates features, publishes FeatureData)
        │
        ▼
   RegimeActor (runs HMM on features, publishes RegimeData)
        │
        ▼
   TradingStrategy (consumes RegimeData, executes trades)
```


After completing the design, produce a document with:

```markdown
# [System Name] Architecture

## Research Summary
- Models: [list trained models and their purpose]
- Signals: [list trading signals/rules]
- Data: [required market data]

## Component Breakdown

### Custom Data Types
- `RegimeData`: regime state with confidence
- `FeatureData`: computed features for models

### Indicators
- `FeatureIndicator`: computes [X] from bars

### Actors
- `RegimeActor`: hosts HMM model, publishes RegimeData

### Strategies
- `TrendStrategy`: trades based on regime signals

## Data Flow Diagram
[ASCII diagram or description]

## Implementation Sequence
1. Define RegimeData in custom_data.py
2. Implement FeatureIndicator
3. Implement RegimeActor
4. Implement TrendStrategy
5. Integration test with backtest

## Warmup Requirements
- FeatureIndicator: 50 bars
- HMM RegimeActor: 100 bars historical inference

## Key Principles

1. **Actors for ML, Strategies for Orders** - Never put model inference in Strategy
2. **Signals for Simple, Data for Complex** - Use `publish_signal` for primitives (str/float/int/bool/bytes), `publish_data` for structured data
3. **Cache for Framework State** - Orders, positions, instruments live in Cache
4. **Warmup Before Live** - Always `request_bars` before `subscribe_bars`
5. **Single Thread Model** - Nautilus runs on single thread; no async model inference in hot path
6. **Strategy Order Events** - Rust strategies handle fills and cancels through `on_order_filled(&OrderFilled)` and `on_order_canceled(&OrderCanceled)`; use `on_order_event(OrderEventAny)` for all lifecycle events
7. **@customdataclass for Quick Custom Data** - Use `@customdataclass` decorator for auto-generated constructors; use manual `Data` subclass for full control

## References

Load these for detailed API information (relative to this skill folder):
- `references/concepts/architecture.md`
- `references/concepts/strategies.md`
- `references/concepts/actors.md`
- `references/concepts/message_bus.md`
- `references/concepts/data.md`

For implementation patterns:
- `references/developer_guide/python.md` - Python conventions
- `references/developer_guide/adapters.md` - Adapter development guide
- `references/developer_guide/coding_standards.md` - Style guide

## Next Step

After architecture is defined, use **nt-implement** skill to implement components with templates.
