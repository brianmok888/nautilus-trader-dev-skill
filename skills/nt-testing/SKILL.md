---
name: nt-testing
description: "Use when writing or running tests for NautilusTrader, setting up test fixtures, using DataTesterConfig or ExecTesterConfig, managing test datasets, or configuring CI testing."
---


# nt-testing

## Execution specification freshness

The official current `spec_exec_testing.md` remains the measurable adapter
execution contract: implement the supported capability matrix, and treat groups 1–5
as the baseline-compliant subset. Both upstream Python and Rust `ExecTester`
surfaces are current; this skill repository still routes new production work to
Rust and keeps Python execution examples migration/reference-only.

The pinned baseline differs from current upstream. At develop commit
`45903fc8b925adae6323035fb0b4fb5b49b4f89b`, change commit
`184e231f192ea7410aeb7730d6118fedfdf2c4d7` introduced the precision-close
contract. The reviewed `origin/develop` head is
`9ca072e2d98ae623f14ecaa5b336398f5d25de34`; keep the immutable snapshot at
`6e59fd74eaacacbb7410936f1766bd89fcce6f59` and apply these version-scoped
overlays until the repository pin advances:

- `spec_exec_testing.md` retains `TC-E74` through `TC-E78` and exposes the Rust
  tester to Python as the built-in strategy `nautilus_trader.testkit.ExecTesterConfig`.
  New Rust work continues to use
  `nautilus_testkit::testers::ExecTesterConfig::builder()`.
- Current TC-E06 and TC-E82 include `close_positions_qty_precision`: a passing
  close leaves the position flat or only the exact sub-precision residual determined by
`close_positions_qty_precision`; the truncated close quantity must be venue-fillable,
  and no open orders may remain.
- `spec_data_testing.md` documents Rust `subscribe_book_depth(true)` support and
  the current request toggles (`request_book_snapshot`, `request_quotes`,
  `request_trades`, and `request_bars`). Do not repeat the pinned snapshot's
  obsolete claim that Rust book-depth subscription is unsupported.
- Repository-only static contract tests that do not import `nautilus_trader` may
  run with the invoking repository Python when the pinned upstream
  `python/.venv` is absent. Any test importing `nautilus_trader` still requires
  the pinned upstream interpreter; never substitute a host or stale environment
  for runtime API evidence.
Official mirrors: [latest](https://nautilustrader.io/docs/latest/developer_guide/spec_exec_testing/)
and [nightly](https://nautilustrader.io/docs/nightly/developer_guide/spec_exec_testing/).

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` material in this whole file is migration/reference-only; prefer current Rust v2/PyO3 and `LiveNode` guidance for new Rust-backed work.

## V2 nightly migration regression coverage

Add or require focused regression coverage for current nightly migration behavior before marking V2 readiness:

- `OrderFillVoided` and terminal `OrderStatus.VOIDED`: replay must have the referenced fill locally before reopening, must not update after `VOIDED`, and strategy/algorithm `on_order_fill_voided` callbacks must be covered when the venue can void fills.
- `PortfolioConfig.use_mark_prices` now defaults to `true`; tests that depend on last-price valuation must set `use_mark_prices=False` explicitly and document why.
- `ExecutionEngineConfig.carry_replay_events_on_reopen` must be tested for NETTING close/reopen replay behavior when external order claims or restart reconciliation are involved.
- `RedisMessageBusBacking` is the current Python V2 name; fail migration tests that still reference the old Redis backing class name.
- SQL/catalog migration: regenerate or migrate catalogs and SQL schemas before in-place upgrades, then smoke replay old persisted events and new V2 events together.
- deferred V2 limits: record unsupported order/TIF/callback paths as deferred V2 limits with explicit test gaps, not as passing coverage.
- shared adapter task tracking: if upstream adapter support exists, verify spawned submit/modify/cancel tasks are tracked, forgotten on terminal events, and aborted on stop/drop.
- Rust crates with unsafe code must enable `#![deny(unsafe_op_in_unsafe_fn)]`.

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-testing` passed the skill domain's scoped examples and owners against `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; schema-v2 provenance is recorded in `references/g2-evidence/nt-testing.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-testing.json`; repository closure is summarized in `docs/tracking/Findings.md`. |

AI and advisory work are outside this repository and must not be introduced into NautilusTrader production paths.

Testing gates: Rust tests are the default readiness evidence for research, configuration, production, performance, and live paths. Require `cargo nextest`, `cargo clippy`, `cargo deny`, `ExecTesterConfig::builder()`, `DataTesterConfig::builder()`, adapter baseline matrices, reconciliation matrices, and fuzz/property tests where parsing/execution outcomes vary. Python checks are limited to bounded public PyO3 projections; retained Python material is migration/reference-only.

## Rust production lane

Rust tests are the production readiness authority. Use deterministic unit and integration tests for invariants, `DataTesterConfig::builder()` and `ExecTesterConfig::builder()` for adapter compliance, `proptest` for broad input spaces, fuzz targets for untrusted parsers, and subprocess isolation for panic/abort-prone FFI boundaries. Unknown execution outcomes remain non-terminal until reconciliation proves the venue result. Execution coverage includes marketable limits via `limit_aggressive` and rejected modify behavior via `test_modify_rejected` when supported.

```rust
use nautilus_testkit::testers::ExecTesterConfig;
use nautilus_trading::strategy::StrategyConfig;

let config = ExecTesterConfig::builder()
    .base(StrategyConfig::default())
    .instrument_id(instrument_id)
    .client_id(client_id)
    .order_qty(order_qty)
    .build()?;
```

## PyO3 control-plane lane

PyO3 tests verify binding registration, configuration round trips, error translation, ownership, and callback routing. They may exercise Python-visible configuration and observation surfaces, but production behavior must be asserted against Rust-owned state and Rust test harnesses. Isolate interpreter-terminating paths and never treat importability or method presence as execution readiness.

The public V2 projection is `from nautilus_trader.testkit import ExecTesterConfig`;
do not import the compatibility root `nautilus_trader.core.nautilus_pyo3`.

Current-develop overlay (`949207b053b040feaff273dff9ad36b796a0e2a9ea`): every public PyO3
actor `subscribe_*` and `unsubscribe_*` entry point calls `ensure_registered()` before mutating
subscription state and returns `PyResult`. Test that a call fails before actor registration, leaves
no retained subscription, and succeeds after registration.

## Migration/reference lane

The previous Python `DataTesterConfig` and `ExecTesterConfig` examples are quarantined under `migration_reference/python/`. Use them only to migrate or compare legacy integrations; Python is not an active production testing lane; AI and advisory work is outside this repository.

## Source-pinned upstream lane

Use `references/developer_guide/testing.md`, `references/developer_guide/spec_data_testing.md`, `references/developer_guide/spec_exec_testing.md`, and `references/developer_guide/rust.md` as source-pinned upstream snapshots at commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59`. Keep the execution-spec freshness and nightly migration notes explicitly version-scoped.

## What This Skill Covers

The complete NautilusTrader testing framework:
- **Testing pyramid** — unit, integration, acceptance, performance, property-based, fuzzing, memory leak tests
- **Data testing spec** — DataTesterConfig API for validating adapter data flows
- **Execution testing spec** — ExecTesterConfig API for validating order lifecycle per venue
- **Test datasets** — curation, storage, metadata, and checksum management
- **CI patterns** — Makefile targets, GitHub Actions, pre-commit hooks

## When To Use

- Writing new Rust tests or bounded PyO3-boundary tests for NT components
- Setting up DataTesterConfig or ExecTesterConfig for adapter validation
- Creating or managing test datasets (Parquet, JSON fixtures)
- Configuring CI pipelines for NT contributions
- Writing property-based tests or fuzz targets
- Debugging test failures in CI

## When NOT To Use

- **nt-backtest** — for running backtest simulations (not testing)
- **nt-dev** — for environment setup, coding standards, or release process
- **nt-adapters** — for building adapter internals (testing specs live here, implementation lives there)

## Test Categories

## Current testing policy contract

Read `references/developer_guide/contracts/testing_policy.md` before designing
adapter, live-runtime, or PyO3 tests.

Current v2 testing deltas:

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

- Treat upstream **Python v2 controller subclassing**, **subclassable execution
  algorithms**, `FeeModel`, and `FillModel` tests as source-pinned or
  migration/reference evidence. This repository's active behavior tests
  target Rust ownership and bounded PyO3 configuration/error boundaries.

Required testing rules:

- Choose the smallest mechanism that proves the production behavior.
- Use DataTester evidence for compatible data adapter behavior.
- Use ExecTester evidence for compatible execution adapter behavior.
- Do not treat method presence as production readiness.
- Isolate PyO3 panic or abort paths in subprocess-style tests when the failure
  can terminate the interpreter.
- Keep unit tests deterministic and do not implicitly download datasets.
- Execution adapters must cover ambiguous outcome failures (`TC-E74` through
  `TC-E78`) with mock HTTP/WebSocket boundaries where live venues cannot
  produce transport, timeout, send, retry, parse, or whole-batch failures.

## DST readiness

Before promoting async/runtime modules to deterministic simulation testing (DST), verify:

- Time, task, runtime, and signal primitives route through deterministic seams
  rather than direct Tokio or OS calls.
- Wall-clock reads go through the project time seam, not direct
  `SystemTime::now()` at call sites.
- Ordering-sensitive maps use `IndexMap` / `IndexSet`.
- Control-plane `tokio::select!` blocks use `biased` when poll order affects
  behavior.
- `Instant::now()`, `SystemTime::now()`, `tokio::signal::ctrl_c`,
  `std::thread::spawn`, and `tokio::task::spawn_blocking` do not escape
  reviewed seams.
- Replay-sensitive IDs are pure functions of their inputs.

NautilusTrader's test suite covers seven categories:

| Category | Scope | Typical Location |
|----------|-------|------------------|
| **Unit tests** | Single functions, types, modules | Inline `#[cfg(test)]` (Rust), `tests/` (Python) |
| **Integration tests** | Multi-component interactions | `tests/` directory |
| **Acceptance tests** | End-to-end workflows | `tests/` with full node setup |
| **Performance tests** | Criterion/iai benchmarks | `benches/` per crate |
| **Property-based tests** | Invariant checking with random inputs | `proptest` strategies inline |
| **Fuzzing** | Malformed input resilience | `fuzz/` targets |
| **Memory leak tests** | Drop verification, ASAN | CI-specific configurations |

## Running Tests

### Primary commands

```bash
# v1 legacy Python tests
make pytest
# or
uv run --active --no-sync pytest --new-first --failed-first

# Rust-backed PyO3 Python tests
make pytest-v2

# Rust tests
make cargo-test
# or
cargo nextest run --workspace --features "python,ffi,high-precision,defi" --cargo-profile nextest

# Optional feature coverage
make cargo-test EXTRA_FEATURES="capnp"

# Performance tests
make test-performance
```

### Makefile targets

```bash
make test          # Full test suite
make pre-commit    # Format + lint + all checks
make format        # Auto-format (ruff, rustfmt)
make lint          # Lint only (no format changes)
make cargo-test    # Rust-only test suite
```

## Test Style

- **Naming**: `test_<what>_<condition>_<expected>` — descriptive, no abbreviations
- **Assertions**: Use specific assert methods (`assert_eq!`, `assert_ne!`) over boolean `assert!`
- **Fixtures**: Shared setup via `#[fixture]` (Rust) or `conftest.py` (Python)
- **Parameterization**: Use `pytest.mark.parametrize` or proptest `Strategy` combinators
- **Isolation**: Each test must be independent; no ordering dependencies

## Property-Based Testing

Property testing verifies logic holds for *all* valid inputs using `proptest` in Rust.

**Use cases**: Core domain types (`Price`, `Quantity`, `UnixNanos`), accounting engines, matching engines, state machines.

**Example invariants:**
- Round-trip: `parse(to_string(value)) == value`
- Inverse: `(A + B) - B == A`
- Transitivity: `if A < B and B < C, then A < C`

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_price_round_trip(value in any::<f64>().prop_filter("positive", |v| *v > 0.0)) {
        let price = Price::new(value, 8).unwrap();
        let parsed = Price::from_str(&price.to_string()).unwrap();
        assert_eq!(price, parsed);
    }
}
```

## Fuzzing

Fuzzing verifies the system fails gracefully with unstructured/malformed data.

**Use cases**: Network boundaries, exchange data parsers (JSON, FIX, WebSocket), state machines.

**Goal**: System returns `Result::Err` — never panics, hangs, or leaks memory.

```rust
// Fuzz target structure
fn fuzz_parse_trade(data: &[u8]) {
    let _ = parse_trade(data); // Must return Err, not panic
}
```

## Data Testing Spec

The DataTesterConfig API validates adapter data flows end-to-end. Each adapter has specific data test configurations. Baseline adapter data compliance means DataTester groups 1-4 pass for the venue-supported subscriptions and requests before claiming data readiness.

### DataTesterConfig API

Use the Rust `DataTesterConfig::builder()` API and verify current fields against the reviewed upstream `crates/testkit/src/testers/data/config.rs`. Legacy Python constructor examples moved to `migration_reference/python/data_tester_config.md`.


### Data Validation Flow

1. Configure `DataTesterConfig` with subscription type
2. Runner subscribes and collects data for a configurable duration
3. Validates received data against expected schema
4. Checks for gaps, stale data, or malformed messages
5. Reports pass/fail per subscription type

**Full spec**: See `references/developer_guide/spec_data_testing.md` for per-adapter test configurations.

## Execution Testing Spec

The ExecTesterConfig API validates order lifecycle per venue. Each adapter has specific execution test configs.

> **Rust-first / V2 default**: the primary execution-test path is the Rust
> `nautilus_testkit::testers::ExecTesterConfig` builder below. Quarantined Python examples
> are migration/reference-only and do not define an active production lane.

### ExecTesterConfig API

Use the Rust `ExecTesterConfig::builder()` API below and verify current fields against the reviewed upstream `crates/testkit/src/testers/exec/config.rs`. Legacy Python constructor examples moved to `migration_reference/python/exec_tester_config.md`.



### Current Rust ExecTesterConfig API

New Rust execution tester examples use `ExecTesterConfig::builder()` with a
`StrategyConfig` base and finish with `build()?`; NT v2 compatibility note: older legacy positional-constructor examples are migration/reference-only; do not copy them into new Rust adapter docs.

```rust
use nautilus_trading::strategy::StrategyConfig;
use nautilus_testkit::testers::ExecTesterConfig;

let tester_config = ExecTesterConfig::builder()
    .base(StrategyConfig {
        strategy_id: Some(strategy_id),
        ..Default::default()
    })
    .instrument_id(instrument_id)
    .client_id(client_id)
    .order_qty(order_qty)
    .build()?;
```

### Adapter baseline matrix

Baseline adapter execution compliance means the adapter passes ExecTester groups
1–5 after DataTester groups 1-4 connectivity and data-flow coverage are already verified. Record the venue
capability matrix in the adapter guide, including order types, TIFs, post-only
behavior, modify/cancel support, trigger-order behavior, and which testnet/demo
credentials and instruments were used. Do not claim baseline readiness from
unit tests or method-presence checks alone.

### Account reconciliation matrix

Execution adapters must document reconciliation coverage for balances, open
orders, fills/trade reports, positions, rejected/canceled orders, and startup
state recovery. Reconciliation tests should prove unknown outcomes stay
non-terminal until venue state, query results, or account snapshots resolve
them.

### Current execution-test deltas

- Cover `TC-E74` through `TC-E78` for ambiguous submit, cancel, modify, and
  batch outcomes. Unknown outcomes must remain in-flight until venue updates,
  query results, or reconciliation resolve them; emit terminal reject events
  only for explicit per-order venue rejections, except the upstream
  local prepare-failure carve-out: local cancel/modify prepare failures that
  prove the command was not sent may emit `OrderCancelRejected` or
  `OrderModifyRejected` when attributable to exactly one command.
- For post-only crossing rejects, assert `due_post_only=true` when the adapter
  emits `OrderRejected`, so strategy code can distinguish post-only failures
  from other venue rejects.
- For stop and conditional orders, include trigger-order reconciliation when a
  venue keeps open trigger orders in a separate endpoint. Long-lived trigger
  signatures must use the trigger-order signing expiry window, not the normal
  order expiry.
- If a venue supports limit-order modify but not native trigger-order replace,
  skip native stop modify and cover the cancel-replace path instead.

### Execution Validation Flow

1. Configure `ExecTesterConfig` with order parameters
2. Runner submits orders via the adapter
3. Monitors order state transitions (SUBMITTED → ACCEPTED → FILLED, etc.)
4. Validates fills, rejects, and cancellations against expected behavior
5. Reports pass/fail per order type

**Full spec**: See `references/developer_guide/spec_exec_testing.md` for per-adapter execution test configurations.

## Test Datasets

### Categories

| Category | Size | Storage | Access |
|----------|------|---------|--------|
| **Small data** | < 1 MB | `tests/test_data/<source>/` | Always available |
| **Large data** | > 1 MB | R2 bucket (Parquet) | Downloaded on first use |
| **User-fetched** | Any | Local only | Requires vendor account |

### Required Metadata

Every dataset has a `metadata.json`:

```json
{
  "file": "binance_btcusdt_2024-01-01_trade_ticks.parquet",
  "sha256": "abc123...",
  "size_bytes": 1048576,
  "original_url": "https://example.com/source",
  "licence": "exchange terms",
  "added_at": "2026-05-03T00:00:00Z"
}
```

User-fetched datasets must also document distribution, fetch method/reference,
auth requirements, transform version, redistribution terms, and public mirror
status. Commit manifests and metadata only when redistribution is restricted;
tests must skip cleanly when local user-fetched data is absent.

### Large Data: Checksums

`tests/test_data/large/checksums.json` records SHA-256 for each file. The `ensure_test_data_exists()` helper:
1. Checks if file exists locally
2. Downloads from R2 if missing
3. Verifies SHA-256 checksum
4. Raises on integrity failure

### Regenerating Datasets

When schema changes invalidate Parquet files:

```bash
# Regenerate from source
uv run --active --no-sync pytest tests/test_data_curation/ -v

# Verify new checksums
sha256sum /tmp/<output_file>
# Update checksums.json
```

## Memory Leak Testing

- **Valgrind**: Run under valgrind to detect leaks
- **ASAN**: Address Sanitizer for Rust builds (`RUSTFLAGS="-Z sanitizer=address"`)
- **Drop verification**: Ensure `Drop` implementations free all resources

## CI Patterns

### GitHub Actions

- Tests run on every PR and push
- Rust tests use `make cargo-test` / `cargo nextest ... --cargo-profile nextest`
- Python tests use `pytest tests/ -n auto`
- Pre-commit hooks run: `ruff format`, `ruff check`, `rustfmt`, `clippy`

### Local CI Parity

```bash
# Before pushing, run locally:
make format && make pre-commit
```

## Key Conventions

- Tests are executable specifications — they document intended behavior
- Each test must be independent and deterministic
- Use `proptest` for invariant checking, not just example-based tests
- Adapter tests use DataTesterConfig/ExecTesterConfig specs, not custom harnesses
- Large test data is never checked into git — use R2 + checksums
- Test dataset metadata must be complete and accurate
- CI must pass before merge — fix locally first with `make pre-commit`

## References

- `references/developer_guide/testing.md` — Full testing guide
- `references/developer_guide/spec_data_testing.md` — Data testing spec per adapter
- `references/developer_guide/spec_exec_testing.md` — Execution testing spec per adapter
- `references/developer_guide/test_datasets.md` — Dataset curation standards
- `references/developer_guide/contracts/testing_policy.md` — Current testing policy contract
