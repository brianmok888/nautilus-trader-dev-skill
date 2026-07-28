---
name: nt-testing
description: "Use when writing or running tests for NautilusTrader, setting up test fixtures, using DataTesterConfig or ExecTesterConfig, managing test datasets, or configuring CI testing."
---


# nt-testing

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
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as 6e59fd74eaacacbb7410936f1766bd89fcce6f59. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed block-scoped legacy/Cython/v1 and TradingNode enforcement; `tests/test_dev_guide_sync.py` covers leakage and exemption boundaries. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | 2026-07-28: `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-testing` passed against pinned upstream commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; machine-checked scope and execution provenance are recorded in `references/g2-evidence/nt-testing.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py tests/test_dev_guide_sync.py` passed PyO3 registration, live-runner callback, Rust ownership, and V2 boundary regressions. |
| G4 Lane and API shape | Classify migration-only Python, active AI/advisory Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template inventory and V2 API regressions; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 308 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 113 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | All 18 targeted G2 harnesses passed and `uv run python tools/check_skill_g2_harnesses.py --check-cards` validated their durable evidence; no readiness row is Pending or Blocked. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Testing gates: Rust tests are the default readiness evidence for production/performance/live paths. Require `cargo nextest`, `cargo clippy`, `cargo deny`, `ExecTesterConfig::builder()`, `DataTesterConfig::builder()`, adapter baseline matrices, reconciliation matrices, fuzz/property tests where parsing/execution outcomes vary, and Python tests only for research/config or AI/advisory lane code.

## What This Skill Covers

The complete NautilusTrader testing framework:
- **Testing pyramid** — unit, integration, acceptance, performance, property-based, fuzzing, memory leak tests
- **Data testing spec** — DataTesterConfig API for validating adapter data flows
- **Execution testing spec** — ExecTesterConfig API for validating order lifecycle per venue
- **Test datasets** — curation, storage, metadata, and checksum management
- **CI patterns** — Makefile targets, GitHub Actions, pre-commit hooks

## When To Use

- Writing new tests for NT components (Python or Rust)
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

- Cover Python v2 controller subclassing and importable controller configs with
  backtest/live config round-trip tests when orchestration code changes.
- Cover subclassable execution algorithms for routed-order behavior.
- Cover custom Python v2 `FeeModel` and `FillModel` subclasses in backtest
  scenarios without relying on legacy Cython extension hooks.

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

```python
from nautilus_trader.test_kit.strategies.tester_data import DataTesterConfig

# Basic config
config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
)

# Constructor-keyword scenarios
config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_quotes=True,
)

config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_trades=True,
)

config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    bar_types=[bar_type],
    subscribe_bars=True,
)

# Order book variants
config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_book_deltas=True,
    book_type=BookType.L2_MBP,
)

config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_book_depth=True,
    book_type=BookType.L2_MBP,
    book_depth=10,
)

# Instrument discovery
config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    request_instruments=True,
)

config = DataTesterConfig(
    client_id=ClientId("BINANCE"),
    instrument_ids=[instrument_id],
    subscribe_instrument=True,
)
```

### Data Validation Flow

1. Configure `DataTesterConfig` with subscription type
2. Runner subscribes and collects data for a configurable duration
3. Validates received data against expected schema
4. Checks for gaps, stale data, or malformed messages
5. Reports pass/fail per subscription type

**Full spec**: See `references/developer_guide/spec_data_testing.md` for per-adapter test configurations.

## Execution Testing Spec

The ExecTesterConfig API validates order lifecycle per venue. Each adapter has specific execution test configs.

> **Rust-first / V2 default**: for Rust-backed adapters, the primary execution-test path is the
> Rust `nautilus_testkit::testers::ExecTesterConfig` builder (see
> [Current Rust ExecTesterConfig API](#current-rust-exectesterconfig-api) below). The Python
> `ExecTesterConfig` API documented next is retained for Python-only integration work and the
> AI/advisory lane, and as the reference matrix that the Rust path mirrors. New Rust adapter
> docs should lead with the Rust builder, not the Python examples.

### ExecTesterConfig API

```python
from nautilus_trader.testkit import ExecTesterConfig

# Basic execution test
config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.001"),
)

# With specific features
config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.01"),
    enable_limit_buys=True,
)

config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.01"),
    enable_limit_sells=True,
)

config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.01"),
    use_post_only=True,
)

# Current Python V2 execution-test coverage flag exposed by the generated stub
config = ExecTesterConfig(
    strategy_id=StrategyId("test-strat"),
    instrument_id=instrument_id,
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.01"),
    limit_aggressive=True,       # marketable limit paths crossing the spread
)

# `test_modify_rejected` and `test_reject_post_only` are Rust builder fields in
# the current source but are not exposed by the generated Python constructor.
```


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
