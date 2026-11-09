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
| G0 Scope and ownership | Pin the developer-guide snapshot and APIs before design. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `77d785c69205c4326e6aadb46d03fb45357a78f2`; `references/upstream-delta-review.json` records the complete 586-commit reviewed transition to this pin. |
| G1 Legacy labelling | legacy: Keep migration/reference labels on legacy/Cython/v1 guidance outside production design. | Pass | `python3 tools/check_legacy_labelling.py` and `python3 tools/check_dev_guide_sync.py` passed on the synchronized source tree. |
| G2 Pinned V2 examples | Compile representative Rust API shapes against the pinned baseline. | Pass | `python3 tools/check_skill_g2_harnesses.py --execute --skill nt-architect` is the current-pin harness; evidence is `references/g2-evidence/nt-architect.json`. Pass requires its actual successful execution against `77d785c69205c4326e6aadb46d03fb45357a78f2`. A G2 `cargo check` result is compilation only; it does not prove spec, testnet, resilience, fuzz, or operations acceptance. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `python3 -m pytest -q tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed as part of 158 repository checks; source audits checked current Rust/PyO3 ownership and callback signatures. Runtime execution is covered separately by G2. |
| G4 Functional gates | Quarantine Python and keep execution authority in Rust. | Pass | `python3 -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed 158 repository policy checks; this does not certify downstream application behavior. |
| G5 References and templates | Map each component to unit, integration, and lifecycle evidence. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` and `python3 tools/check_rust_trading_reference_sync.py` passed; exact source comparisons covered 22 shared guides, 33 trading source files, 81 analysis files, and 23 matching adapter examples. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `python3 tools/check_legacy_labelling.py` and the 158-test source-policy run passed for migration labels, language lanes, precision, callbacks, and fail-closed guidance; live venue acceptance remains change-specific. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | `references/g2-evidence/nt-architect.json` records current-pin G2 execution (status pass, owned-content hash match); mission closure receipts under `docs/tracking/receipts/nt-v2-rc-20261109/`; `python3 tools/check_governance_receipts.py` validated 497 receipts. |

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

Use a component ownership matrix with crate/module, input messages, output messages, mutable state, failure behavior, and tests. Keep execution-critical state in Rust and pass immutable events or owned snapshots across boundaries. Request historical data before subscriptions, define warmup explicitly, and specify deterministic startup/reset/stop behavior. On the deterministic simulation path, design for the DST seams: clocks, randomness, task spawning, and network access route through `nautilus_network::dst::{time, task, net}` (Madsim-selected under simulation); with the `simulation` feature, HTTP/1.1 and WebSocket transports run over simulated byte streams, while HTTPS/TLS, HTTP/2, proxies, and streaming responses stay outside the simulated transport (upstream `docs/concepts/dst.md` at the pinned baseline).

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

PyO3 is a bounded control plane over Rust-owned behavior, not an alternate implementation lane. Design bindings for configuration construction, lifecycle invocation, read-only inspection, and non-execution callbacks. Rust remains authoritative for validation, state transitions, order submission, risk, adapter liveness, and reconciliation. Python components coordinate in-process through the component messaging facade (`publish_message` / `subscribe_topic` / `unsubscribe_topic`); raw `MessageBus` access is Rust-only.

There are no active Python examples in this root skill. Specify the Rust `#[pyclass]`/`#[pymethods]` owner, module registration path, conversion/error contract, GIL boundary, and cleanup behavior. Prefer owned `Py<T>` handles; justify shared ownership, use weak references for back-references, and provide traversal/clear hooks where Python cycles are possible. Route callbacks from Tokio work through the supported live-runner/channel boundary rather than attaching Python on worker tasks.


## Migration/reference lane

Legacy Python architecture prose and examples are physically quarantined at [`migration_reference/python/legacy-root-guidance.md`](migration_reference/python/legacy-root-guidance.md). Use them only for explicitly labelled migration/reference work; do not copy them into new production designs.

## Source-pinned upstream lane


Current source pin: `77d785c69205c4326e6aadb46d03fb45357a78f2`. The latest
published RC is `v2.0.0rc8`; develop is an unreleased rc9 source boundary.
See `references/README.md`. Older commit-specific notes below are historical
review context; they do not establish current G2 execution or release availability.

Validate architecture decisions against the immutable developer-guide snapshot under [`references/developer_guide/`](../../references/developer_guide/), especially `rust.md`, `ffi.md`, `adapters.md`, and `contracts/design_principles.md`, pinned to commit `77d785c69205c4326e6aadb46d03fb45357a78f2`. Treat newer upstream behavior as version-scoped until the repository pin advances.
