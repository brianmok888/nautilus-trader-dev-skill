# nt-architect Knowledge Base

**Purpose:** Translate research outputs (trained ML models + signal logic) into NautilusTrader component architecture before writing any code.

**Entry Point:** `SKILL.md` (347 lines)

## DESIGN PROCESS (5 Phases)

1. **Intake** — Categorize research outputs: trained models (→ Actor), signal logic (→ Strategy/Indicator), data requirements (bars, ticks, timeframes)
2. **Decomposition** — Assign components using decision tree (see below)
3. **Data Flow** — Design message bus connections between components
4. **State Management** — Decide where state lives (Cache vs Actor attributes)
5. **Lifecycle Planning** — Document initialization order, warmup, dependency graph

## COMPONENT DECOMPOSITION DECISION TREE

```
Research Element
    ├─► Does it TRADE (submit orders)?     → STRATEGY
    ├─► Stateless computation on data?      → INDICATOR
    ├─► Stateful computation or ML?         → ACTOR
    └─► Custom data through message bus?    → CUSTOM DATA TYPE
```

**Rule:** Actors for ML inference. Strategies for orders. Never put model inference in Strategy.

## DATA FLOW PATTERNS

### Signal vs Custom Data

| Mechanism | When | API |
|-----------|------|-----|
| `publish_signal()` | Primitive values (str, float, int, bool, bytes) | Lightweight, no class needed |
| `publish_data()` | Structured complex values with `@customdataclass` | Auto-generated constructor |
| Manual `Data` subclass | Full control over `ts_event`/`ts_init` | Explicit property implementation |

### Common Topologies

- **ML → Signal → Strategy:** `[Market Data] → FeatureActor → RegimeActor → publish_signal → Strategy`
- **Multi-TF Aggregation:** Multiple BarType subscriptions aggregated in Actor, published as Custom Data
- **Ensemble:** Multiple model Actors publish signals → EnsembleActor → final_signal → Strategy

### Actor Subscriptions

Actors monitor trading activity through current message-bus order-event handlers:
- `OrderFilled` messages → `on_order_filled(event)`
- `OrderCanceled` messages → `on_order_canceled(event)`

## STATE MANAGEMENT

| State Type | Location | Access |
|------------|----------|--------|
| Orders, Positions, Instruments, Accounts | Cache | `self.cache.*` |
| Market Data | Cache | `self.cache.quote_tick()`, `self.cache.bar()` |
| Model State (weights, params) | Actor attribute | `self.model` loaded in `on_start` |
| Regime/Signal State | Actor attribute | `self.current_regime` |
| Strategy-specific State | Strategy attribute | `self.is_position_open` |

## LIFECYCLE RULES

1. **Init order:** CustomDataTypes → Indicators → Actors → Strategies
2. **Warmup:** Always `request_bars()` before `subscribe_bars()` in `on_start`
3. **Instrument load:** `self.cache.instrument(id)` with null check in `on_start`
4. **Model load:** Prefer `msgspec.msgpack.decode()` for serialization in `on_start`
5. **Single thread:** No async model inference in hot path

## ADAPTER CONSTRAINTS (if architecture includes adapter)

- Preserve 7-phase dependency order in design doc
- Rust core owns networking/parsing; Python layer owns Nautilus integration
- Include explicit method families: InstrumentProvider, LiveDataClient, LiveExecutionClient
- Record runtime rules: `get_runtime().spawn()`, no blocking hot handlers, direct `PyObject`/`Py<T>` for ordinary callbacks; justify and cycle-audit any `Arc<Py<T>>`
- Map phases to concrete test artifacts per milestone

## OUTPUT FORMAT

Design doc must include: Research Summary → Component Breakdown → Data Flow Diagram → Implementation Sequence → Warmup Requirements

## REFERENCES (symlinked)

- `references/concepts/` — architecture.md, strategies.md, actors.md, message_bus.md, data.md
- `references/developer_guide/` — python.md, adapters.md, coding_standards.md

## NEXT STEP

After architecture is defined → **nt-implement** skill for component implementation.
