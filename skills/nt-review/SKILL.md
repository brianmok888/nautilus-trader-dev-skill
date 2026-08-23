---
name: nt-review
description: "Use when reviewing NautilusTrader implementations for correctness, Rust and FFI safety, performance, testability, and live deployment readiness."
---

# NautilusTrader Implementation Review

## NT V2 Rust readiness gates

A review is not complete without command evidence. Mark a gate `Pass` only after reading fresh output; otherwise use `Pending` or `Blocked`.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | API claims match the pinned developer-guide snapshot. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` verifies the immutable developer-guide snapshot. |
| G1 Legacy labelling | NT v2 compatibility note: legacy/Cython/v1 guidance is migration/reference-only and does not enter production code. | Pass | `uv run python tools/check_dev_guide_sync.py` enforces migration labels for legacy/Cython/v1 guidance. |
| G2 Pinned V2 examples | Changed Rust examples compile or have scoped harness evidence. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-review` passed against `d2b62d35a74f7f9fc4d419c29b5b2b37a71e190c`; evidence: `references/g2-evidence/nt-review.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` validates selected ownership and callback boundaries. |
| G4 Functional gates | Python production guidance is quarantined; Rust retains execution authority. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py` enforces Rust/PyO3/Python lane ownership. |
| G5 References and templates | Targeted tests plus relevant lint/build commands are recorded. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` runs the readiness-focused repository tests. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1'` passed selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-review.json`; repository closure is summarized in `docs/tracking/Findings.md`. |

NT v2 compatibility note: Rust-oriented v2.0 readiness rejects unlabelled legacy/Cython/v1 guidance as migration/reference-only and requires Rust-owned production paths. Python live `TradingNode` material is reference-only; current Rust-backed live work uses `LiveNode`.

## Rust production lane

Review behavior before style. Classify findings as **Blocker** (unsafe or incorrect for merge), **Major** (material correctness/operability gap), or **Minor** (bounded maintainability issue), and cite a file/line plus the failing invariant.

**Correctness and lifecycle**
- Verify deterministic startup, warmup, reset, stop, and shutdown behavior.
- Confirm order rejection, cancellation, expiration, partial fill, reconciliation, position limits, and circuit-breaker paths.
- Ensure `DataActor`, strategy, adapter, cache, and message bus responsibilities are separated and messages remain immutable after publication.
- Check current V2 shapes: `TryFrom<OrderInitialized>`, owned cache snapshots at boundaries, `RecencyMap` behavior, v2 wranglers, and raw fixed-point overflow handling.

**Rust, async, and FFI safety**
- Require `#![deny(unsafe_op_in_unsafe_fn)]`, `// SAFETY:` justification, tests for unsafe paths, `#[repr(C)]`, panic containment, and matching allocation/drop contracts.
- Reject `.unwrap()` in production, accidental clones/allocations in hot paths, blocking handlers, and runtime spawning that bypasses the project runtime.
- Audit fixed-point precision, conversion bounds, deterministic ordering, secret handling, and error propagation.

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

Review PyO3 as a thin control plane over Rust-owned state. There are no active Python examples in this root skill. Confirm `#[pyclass]` and `#[pymethods]` registration, explicit conversions, stable exceptions, GIL-safe access, deterministic cleanup, and documentation of ownership.

Require subclassable PyO3 stubs to match actual Rust virtual/dispatch behavior. Prefer direct owned `Py<T>` handles; require rationale for `Arc<Py<T>>`, weak references for back-references, and traversal/clear support for traceable cycles. Reject Python callback attachment from Tokio worker tasks; use the supported live-runner/channel route. No binding may expose independent order, risk, reconciliation, or adapter-liveness authority.


## Migration/reference lane

Legacy Python review prose, checklists, and examples are physically quarantined at [`migration_reference/python/legacy-root-guidance.md`](migration_reference/python/legacy-root-guidance.md). Consult them only for explicitly labelled migration/reference reviews; they are not production defaults.

## Source-pinned upstream lane

Validate review claims against the immutable snapshot under [`references/developer_guide/`](../../references/developer_guide/), particularly `rust.md`, `ffi.md`, `testing.md`, `benchmarking.md`, `adapters.md`, and `coding_standards.md`, pinned to commit `d2b62d35a74f7f9fc4d419c29b5b2b37a71e190c`. Version-scope any newer upstream guidance until the pin advances.
