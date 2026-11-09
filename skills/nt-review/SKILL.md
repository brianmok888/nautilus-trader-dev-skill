---
name: nt-review
description: "Use when reviewing NautilusTrader implementations for correctness, Rust and FFI safety, performance, testability, and live deployment readiness."
---

# NautilusTrader Implementation Review

## NT V2 Rust readiness gates

A review is not complete without command evidence. Mark a gate `Pass` only after reading fresh output; otherwise use `Pending` or `Blocked`.

For delivery and cutover decisions, complete every applicable standard gate in `docs/tracking/CutoverGateTemplate.md`; `Pending` and `Blocked` remain non-pass states.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | API claims match the pinned developer-guide snapshot. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `77d785c69205c4326e6aadb46d03fb45357a78f2`; `references/upstream-delta-review.json` records the complete 586-commit reviewed transition to this pin. |
| G1 Legacy labelling | NT v2 compatibility note: legacy/Cython/v1 guidance is migration/reference-only and does not enter production code. | Pass | `python3 tools/check_legacy_labelling.py` and `python3 tools/check_dev_guide_sync.py` passed on the synchronized source tree. |
| G2 Pinned V2 examples | Changed Rust examples compile or have scoped harness evidence. | Pass | `python3 tools/check_skill_g2_harnesses.py --execute --skill nt-review` is the current-pin harness; evidence is `references/g2-evidence/nt-review.json`. Pass requires its actual successful execution against `77d785c69205c4326e6aadb46d03fb45357a78f2`. A G2 `cargo check` result is compilation only; it does not prove spec, testnet, resilience, fuzz, or operations acceptance. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `python3 -m pytest -q tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed as part of 158 repository checks; source audits checked current Rust/PyO3 ownership and callback signatures. Runtime execution is covered separately by G2. |
| G4 Functional gates | Python production guidance is quarantined; Rust retains execution authority. | Pass | `python3 -m pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_current_develop_guidance.py tests/test_nt_v2_state_and_custom_data.py` passed 158 repository policy checks; this does not certify downstream application behavior. |
| G5 References and templates | Targeted tests plus relevant lint/build commands are recorded. | Pass | `python3 tools/check_dev_guide_snapshot_sync.py` and `python3 tools/check_rust_trading_reference_sync.py` passed; exact source comparisons covered 22 shared guides, 33 trading source files, 81 analysis files, and 23 matching adapter examples. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `python3 tools/check_legacy_labelling.py` and the 158-test source-policy run passed for migration labels, language lanes, precision, callbacks, and fail-closed guidance; live venue acceptance remains change-specific. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | `references/g2-evidence/nt-review.json` records current-pin G2 execution (status pass, owned-content hash match); mission closure receipts under `docs/tracking/receipts/nt-v2-rc-20261109/`; `python3 tools/check_governance_receipts.py` validated 497 receipts. |

NT v2 compatibility note: Rust-oriented v2.0 readiness rejects unlabelled legacy/Cython/v1 guidance as migration/reference-only and requires Rust-owned production paths. Python live `TradingNode` material is reference-only; current Rust-backed live work uses `LiveNode`.

## Rust production lane

Review behavior before style. Classify findings as **Blocker** (unsafe or incorrect for merge), **Major** (material correctness/operability gap), or **Minor** (bounded maintainability issue), and cite a file/line plus the failing invariant.

**Correctness and lifecycle**
- Verify deterministic startup, warmup, reset, stop, and shutdown behavior.
- Confirm order rejection, cancellation, expiration, partial fill, reconciliation, position limits, and circuit-breaker paths.
- Verify adapter order-status-report filtering follows the shared rule at `crates/live/src/execution/reports.rs` (pinned `77d785c69205c4326e6aadb46d03fb45357a78f2`, upstream `9b7db823`): open-only venue report requests must retain both open and in-flight reports (`is_open() || is_inflight()`); only the documented Bybit and Polymarket reconciliation exceptions may deviate.
- Ensure `DataActor`, strategy, adapter, cache, and message bus responsibilities are separated and messages remain immutable after publication.
- Check current V2 shapes: `TryFrom<OrderInitialized>`, owned cache snapshots at boundaries, `RecencyMap` behavior, v2 wranglers, and raw fixed-point overflow handling.

**Rust, async, and FFI safety**
- Require `#![deny(unsafe_op_in_unsafe_fn)]`, `// SAFETY:` justification, tests for unsafe paths, `#[repr(C)]`, panic containment, and matching allocation/drop contracts.
- Reject `.unwrap()` in production, accidental clones/allocations in hot paths, blocking handlers, and runtime spawning that bypasses the project runtime.
- Audit fixed-point precision, conversion bounds, deterministic ordering, secret handling, and error propagation.
- For adapter discrete values, reject precision inferred from incidental payload formatting. Trace the field contract through `Decimal`, use `Decimal::normalize` only for documented non-semantic padding, and apply instrument or currency precision where authoritative; require trailing-zero parser variants.
- For live execution, require same-position fill and side-aware quantity-free close-all reconciliation coverage. Assert lifecycle semantics, final state, ordering, and duplicate-side-effect freedom rather than transient event counts.

**Performance and evidence**
- Require representative benchmarks for hot paths, setup outside timing loops, `black_box`, and before/after measurements for optimization claims.
- Run the smallest relevant package tests first, then record `cargo nextest`, `cargo clippy`, and `cargo deny` command evidence when applicable.
- Verify backtest/paper/live parity and fail-closed behavior rather than accepting configuration presence as proof.

```rust
#![deny(unsafe_op_in_unsafe_fn)]

pub fn checked_notional(price_raw: i64, quantity_raw: u64) -> anyhow::Result<i128> {
    i128::from(price_raw)
        .checked_mul(i128::from(quantity_raw))
        .ok_or_else(|| anyhow::anyhow!("raw fixed-point overflow"))
}
```

Also reject Python v2 config stub/readback drift, stale Generated Python artifacts, and missing `make py-stubs` evidence when binding surfaces change.

## PyO3 control-plane lane

Review PyO3 as a thin control plane over Rust-owned state. There are no active Python examples in this root skill. Confirm `#[pyclass]` and `#[pymethods]` registration, explicit conversions, stable exceptions, GIL-safe access, deterministic cleanup, and documentation of ownership. A Python factory must not re-enter the same active `LiveNodeBuilder`; verify the explicit re-entry error, active state, and builder restoration after callback errors.

Require subclassable PyO3 stubs to match actual Rust virtual/dispatch behavior. Prefer direct owned `Py<T>` handles; require rationale for `Arc<Py<T>>`, weak references for back-references, and traversal/clear support for traceable cycles. Reject Python callback attachment from Tokio worker tasks; use the supported live-runner/channel route. No binding may expose independent order, risk, reconciliation, or adapter-liveness authority.


## Migration/reference lane

Legacy Python review prose, checklists, and examples are physically quarantined at [`migration_reference/python/legacy-root-guidance.md`](migration_reference/python/legacy-root-guidance.md). Consult them only for explicitly labelled migration/reference reviews; they are not production defaults.

## Source-pinned upstream lane


Current source pin: `77d785c69205c4326e6aadb46d03fb45357a78f2`. The latest
published RC is `v2.0.0rc8`; develop is an unreleased rc9 source boundary.
See `references/README.md`. Older commit-specific notes below are historical
review context; they do not establish current G2 execution or release availability.

Validate review claims against the immutable snapshot under [`references/developer_guide/`](../../references/developer_guide/), particularly `rust.md`, `ffi.md`, `testing.md`, `benchmarking.md`, `adapters.md`, and `coding_standards.md`, pinned to commit `77d785c69205c4326e6aadb46d03fb45357a78f2`. Version-scope any newer upstream guidance until the pin advances.
