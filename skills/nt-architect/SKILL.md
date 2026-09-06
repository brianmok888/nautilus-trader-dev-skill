---
name: nt-architect
description: "Use when translating research outputs, models, signals, or adapter requirements into NautilusTrader component architecture before implementation."
---

# NautilusTrader Architecture Design

## NT V2 Rust readiness gates

Use these gates as the architecture acceptance card. A gate is `Pass` only when its evidence is recorded; otherwise mark it `Pending` or `Blocked`.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Pin the developer-guide snapshot and APIs before design. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` verifies the immutable developer-guide snapshot. |
| G1 Legacy labelling | legacy: Keep migration/reference labels on legacy/Cython/v1 guidance outside production design. | Pass | `uv run python tools/check_dev_guide_sync.py` enforces migration labels for legacy/Cython/v1 guidance. |
| G2 Pinned V2 examples | Compile representative Rust API shapes against the pinned baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-architect` passed against `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`; evidence: `references/g2-evidence/nt-architect.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run python -m pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` validates selected ownership and callback boundaries. |
| G4 Functional gates | Quarantine Python and keep execution authority in Rust. | Pass | `uv run python -m pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py` enforces Rust/PyO3/Python lane ownership. |
| G5 References and templates | Map each component to unit, integration, and lifecycle evidence. | Pass | `uv run python -m pytest -q --ignore=tests/test_quality_gates.py` runs the readiness-focused repository tests. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run python -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-architect.json`; repository closure is summarized in `docs/tracking/Findings.md`. |

Rust-oriented v2.0 readiness means producing a component ownership matrix before implementation. Rust owns strategy/configuration, adapters, networking, parsing, normalization, risk, execution-critical state, and live-node plumbing. Preserve message immutability across actor, strategy, adapter, cache, and message bus boundaries; Python content is limited to bounded PyO3 control-plane and migration/reference material.

## Rust production lane

Design new production systems as Rust crates and modules. Assign each research output to an execution role and an owner:

| Concern | Rust owner | Required design artifact |
| --- | --- | --- |
| Orders, positions, and risk | Strategy using `StrategyCore` | Commands/events, fail-closed checks, lifecycle transitions |
| Stateless calculations | Indicator | Inputs, warmup, initialization/reset invariants |
| Stateful inference or aggregation | `DataActor` or domain service | State ownership, deterministic update order, published data |
| Venue integration | `crates/adapters/<venue>/` | HTTP/WebSocket, parsing, normalization, provider/data/execution clients |
| Backtest and live wiring | Rust node configuration and `LiveNode` | Identical strategy ownership, reconciliation, shutdown path |

Use a component ownership matrix with crate/module, input messages, output messages, mutable state, failure behavior, and tests. Keep execution-critical state in Rust and pass immutable events or owned snapshots across boundaries. Request historical data before subscriptions, define warmup explicitly, and specify deterministic startup/reset/stop behavior.

For adapters, preserve dependency order: domain types and parsing, HTTP client, WebSocket client, instrument provider, live data client, live execution client, then factories/configuration. Runtime tasks use the project runtime rather than an isolated executor, hot handlers do not block, and every reconnect/reconciliation path has test evidence.

```rust
#[derive(Debug)]
pub struct RegimeActor {
    core: DataActorCore,
    current: Option<Regime>,
}

nautilus_actor!(RegimeActor);

impl DataActor for RegimeActor {
    fn on_data(&mut self, data: &CustomData) -> anyhow::Result<()> {
        let next = self.classify(data)?;
        self.current = Some(next);
        self.publish_signal(
            "regime",
            next.to_string(),
            self.clock().timestamp_ns(),
        );
        Ok(())
    }
}
```

The actor owns a `DataActorCore`, uses `nautilus_actor!` for the component
contract, receives `CustomData`, and publishes through the current
`publish_data`/`publish_signal` APIs. Treat this as a contract sketch: use the
pinned `crates/common/examples/greeks_actor_example.rs` for complete imports,
construction, registration, and subscription wiring.

Execution-event architecture uses the current Rust callbacks
`on_order_filled(&OrderFilled)` and `on_order_canceled(&OrderCanceled)`; do not
reintroduce removed order-event subscription helpers.

The architecture handoff is complete only when it includes the ownership matrix, message flow, implementation order, warmup requirements, failure modes, and verification commands.

## PyO3 control-plane lane

PyO3 is a bounded control plane over Rust-owned behavior, not an alternate implementation lane. Design bindings for configuration construction, lifecycle invocation, read-only inspection, and non-execution callbacks. Rust remains authoritative for validation, state transitions, order submission, risk, adapter liveness, and reconciliation.

There are no active Python examples in this root skill. Specify the Rust `#[pyclass]`/`#[pymethods]` owner, module registration path, conversion/error contract, GIL boundary, and cleanup behavior. Prefer owned `Py<T>` handles; justify shared ownership, use weak references for back-references, and provide traversal/clear hooks where Python cycles are possible. Route callbacks from Tokio work through the supported live-runner/channel boundary rather than attaching Python on worker tasks.


## Migration/reference lane

Legacy Python architecture prose and examples are physically quarantined at [`migration_reference/python/legacy-root-guidance.md`](migration_reference/python/legacy-root-guidance.md). Use them only for explicitly labelled migration/reference work; do not copy them into new production designs.

## Source-pinned upstream lane

Validate architecture decisions against the immutable developer-guide snapshot under [`references/developer_guide/`](../../references/developer_guide/), especially `rust.md`, `ffi.md`, `adapters.md`, and `contracts/design_principles.md`, pinned to commit `ac22d5cf4a7e55ba93b233bba5b04de4723b3d3d`. Treat newer upstream behavior as version-scoped until the repository pin advances.
