---
name: nt-architect
description: "Use when translating research outputs, models, signals, or adapter requirements into NautilusTrader component architecture before implementation."
---

# NautilusTrader Architecture Design

## NT V2 Rust readiness gates

Use these gates as the architecture acceptance card. A gate is `Pass` only when its evidence is recorded; otherwise mark it `Pending` or `Blocked`.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Pin the developer-guide snapshot and APIs before design. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` verifies the immutable developer-guide snapshot. |
| G1 Legacy label | Keep migration/reference labels on legacy/Cython/v1 guidance outside production design. | Pass | `uv run python tools/check_dev_guide_sync.py` enforces migration labels for legacy/Cython/v1 guidance. |
| G2 V2 example validation | Compile representative Rust API shapes against the pinned baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-architect` passed against `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; evidence: `references/g2-evidence/nt-architect.json`. |
| G3 Rust bindings/PyO3 | Name crate ownership, binding registration, and callback routing. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` validates binding and callback boundaries. |
| G4 Lane and API shape | Quarantine non-AI Python and keep execution authority in Rust. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py` enforces Rust/PyO3/Python lane ownership. |
| G5 Test evidence | Map each component to unit, integration, and lifecycle evidence. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` runs the readiness-focused repository tests. |
| G6 Safety/compliance | Specify fail-closed risk, precision, async, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'` validates the safety boundaries. |
| G7 Completion report | Report changed paths, commands, evidence, and unresolved gates. | Pass | `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md` records findings, commands, gate results, and residual risk. |

Rust-oriented v2.0 readiness means producing a component ownership matrix before implementation. Rust owns strategy/configuration, adapters, networking, parsing, normalization, risk, execution-critical state, and live-node plumbing. Preserve message immutability across actor, strategy, adapter, cache, and message bus boundaries. AI/advisory lane remains Python and off execution-critical paths; all other Python content is migration/reference-only.

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
pub struct RegimeActor {
    current: Option<Regime>,
}

impl DataActor for RegimeActor {
    fn on_data(&mut self, data: &Data) -> anyhow::Result<()> {
        let next = self.classify(data)?;
        self.current = Some(next);
        self.publish(next.into())
    }
}
```

Execution-event architecture uses the current Rust callbacks
`on_order_filled(&OrderFilled)` and `on_order_canceled(&OrderCanceled)`; do not
reintroduce removed order-event subscription helpers.

The architecture handoff is complete only when it includes the ownership matrix, message flow, implementation order, warmup requirements, failure modes, and verification commands.

## PyO3 control-plane lane

PyO3 is a bounded control plane over Rust-owned behavior, not an alternate implementation lane. Design bindings for configuration construction, lifecycle invocation, read-only inspection, and non-execution callbacks. Rust remains authoritative for validation, state transitions, order submission, risk, adapter liveness, and reconciliation.

There are no active Python examples in this root skill. Specify the Rust `#[pyclass]`/`#[pymethods]` owner, module registration path, conversion/error contract, GIL boundary, and cleanup behavior. Prefer owned `Py<T>` handles; justify shared ownership, use weak references for back-references, and provide traversal/clear hooks where Python cycles are possible. Route callbacks from Tokio work through the supported live-runner/channel boundary rather than attaching Python on worker tasks.

AI/advisory integration is the sole active Python lane. It must be asynchronous, approval-gated, auditable, non-authoritative, and equipped with a deterministic Rust-owned fallback.

## Migration/reference lane

Legacy Python architecture prose and examples are physically quarantined at [`migration_reference/python/legacy-root-guidance.md`](migration_reference/python/legacy-root-guidance.md). Use them only for explicitly labelled migration/reference work; do not copy them into new production designs.

## Source-pinned upstream lane

Validate architecture decisions against the immutable developer-guide snapshot under [`references/developer_guide/`](../../references/developer_guide/), especially `rust.md`, `ffi.md`, `adapters.md`, and `contracts/design_principles.md`, pinned to commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59`. Treat newer upstream behavior as version-scoped until the repository pin advances.
