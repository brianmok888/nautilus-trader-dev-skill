---
name: nt-live
description: "Use when working with live trading nodes, system boot, NautilusKernel, engine configuration, component lifecycle, or deployment in NautilusTrader."
---

# nt-live

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` material in this whole file is migration/reference-only; prefer current Rust v2/PyO3 and `LiveNode` guidance for new Rust-backed work.

## V2 callback and nightly migration hardening


- Python callback rule: no `Python::attach` from Tokio worker tasks. Worker tasks must not acquire the GIL directly to call Python strategy, actor, execution-algorithm, or adapter callbacks; route work onto live runner channels and let the live runner drain/dispatch those channels.
NT v2 compatibility note: Python live `TradingNode` examples are legacy/reference-only; use `LiveNode` for Rust v2/Rust-backed work.
- For Python-facing live V2 work, prefer `LiveNode`/PyO3 paths. Treat Python `TradingNode` examples as legacy/reference-only unless a guide explicitly labels them current Python-only integration guidance.
- `ExecutionEngineConfig.carry_replay_events_on_reopen` carries replay state across NETTING close/reopen cycles; keep reconciliation/restart tests for close/reopen sequences.
- `PortfolioConfig.use_mark_prices` defaults to `true`; set `false` only when a test or deployment intentionally excludes mark-price valuation.
- `RedisMessageBusBacking` is the current Python V2 Redis message-bus backing name.
- SQL/catalog migration: regenerate or migrate persisted SQL/catalog state before in-place V2 upgrades and smoke replay after migration.
- deferred V2 limits must be documented as explicit live-readiness gaps, not silently accepted.
- shared adapter task tracking, when upstream support exists for the adapter, must track spawned tasks through terminal events and abort outstanding tasks during stop/drop.
- Rust live crates that contain unsafe code must enable `#![deny(unsafe_op_in_unsafe_fn)]` at crate root and wrap each unsafe operation in an explicit `unsafe {}` block with a local safety reason.


## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Scope and ownership | Confirm the pinned developer-guide snapshot and record the current-develop overlay before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; `references/upstream-delta-review.json` records the reviewed current-develop delta. This gate does not certify every official-doc page or release tag. |
| G1 Legacy labelling | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 27 tests. |
| G2 Pinned V2 examples | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-live` passed the skill domain's scoped examples and owners against `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; schema-v2 provenance is recorded in `references/g2-evidence/nt-live.json`. |
| G3 Rust bindings/PyO3 | Validate the selected Rust/PyO3 ownership, registration, and callback boundaries exercised by the repository checks. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 selected ownership and callback boundary tests. |
| G4 Functional gates | Classify migration/reference-only Python, bounded PyO3 control-plane, source-pinned upstream snapshots, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 References and templates | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Operational and migration boundaries | Run selected repository policy checks for legacy labels, the NT-only repository boundary, and Rust-first lane guidance. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'` passed 26 selected repository policy checks; change-specific deterministic ordering, precision/overflow, secrets, async, FFI, and audit evidence remains required where applicable. |
| G7 Durable evidence | Report changed paths, validation commands, evidence, and unresolved gates. | Pass | Current per-skill evidence is recorded in `references/g2-evidence/nt-live.json`; repository closure is summarized in `docs/tracking/Findings.md`. |

AI and advisory work are outside this repository and must not be introduced into NautilusTrader production paths.

NT v2 compatibility note: Python live TradingNode material in the live gates is migration/reference-only; use LiveNode for Rust v2/Rust-backed work.

Live gates: `LiveNode` is the default for Rust-backed production live work; Python `TradingNode` material is migration/reference-only. Before `Pass`, prove startup/shutdown/reconnect/reconciliation behavior with `cargo nextest`, `cargo clippy`, `cargo deny`, config validation, and live safety dry-run evidence.

## Rust production lane

Build live systems around Rust `LiveNode`, Rust adapters, and Rust-owned execution, risk, reconciliation, and lifecycle state. Startup, shutdown, reconnect, task tracking, and fail-closed behavior must remain deterministic and must be proven with targeted live-runtime tests and the required cargo gates.

### Develop/nightly-only actor and strategy state persistence

Source: upstream develop commit `9a9e5fe7b762410229b380d5af92d32c13169c3a`.
This lifecycle is **develop/nightly only** and is not available in the pinned baseline or stable releases; do not present it as a stable configuration contract.

When `load_state` is enabled with a backing cache database, Rust loads actor
and strategy byte maps through `Cache::load_actor_state` and
`Cache::load_strategy_state`, then invokes the Rust `DataActor::on_load` and
`Strategy::on_load` callbacks before component startup. Empty or unavailable
state is skipped rather than synthesized.

When `save_state` is enabled, Rust invokes `DataActor::on_save` and
`Strategy::on_save`, persists the returned byte maps, and arms
`NautilusKernel::save_trader_state` for at-most-once saving. The live stop path
calls `NautilusKernel::finalize_stop` after residual event processing and saves
before cache teardown while still completing cleanup and reporting callback or
persistence errors.

The persistence hooks preserve the existing boundary: execution ownership remains in Rust. Persist component state only; do not move order flow, risk,
reconciliation, adapter liveness, or shutdown authority into Python callbacks.

### Current-develop cache backing and runner pressure

Sources: upstream develop commits `0caf26d216c4196d60cc35991492337b07568c22`,
`8181fee66fed42daeb9701b1b5b6eec5928aa1cf`,
`6c3c61c570eaf937ec6efe9b807f5501f77f1d91`, and
`42ff42b346ec42eeba4486f618f24e5cc15b2d02`.

For Python v2 live construction, register a typed cache database extractor and
pass its factory through `LiveNodeBuilder.with_cache_database_factory`. The
PyO3 method is `with_cache_database_factory`; unsupported Python factory types
fail with `NotImplementedError`. Keep persistence ownership in the Rust cache
backend rather than adding Python callbacks to the data path.

Monitor each runner channel by queue depth and `dispatch_busy_ns`.
`QueueStateChanged` publishes condition/state transitions together with
`queue_depth` and `mean_dispatch_ns`; treat critical pressure as a live safety
signal and prove its asserted/cleared transitions under load. Per-channel busy
time replaces a single aggregate dispatch-time assumption.

## PyO3 control-plane lane

Use PyO3 only for typed live configuration, Rust component registration, lifecycle commands, and read-only operational inspection. Python callbacks must not become authoritative for order flow, risk checks, adapter connectivity, reconciliation, or node liveness.

## Migration/reference lane

Python migration material is pointer-only here and physically quarantined under `migration_reference/python/` for `nt-live`.

## Source-pinned upstream lane

Source: [`references/developer_guide/rust.md`](../../references/developer_guide/rust.md) at immutable commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59`.

## What This Skill Covers

NautilusTrader **live infrastructure domain** — live trading nodes, system kernel, configuration, component lifecycle, and deployment.

**Python modules**: `live/`, `system/`, `config/`, `common/`, `core/`
**Rust crates**: `nautilus_system`, `nautilus_live`, `nautilus_common`, `nautilus_core`

## When To Use

NT v2 compatibility note: Python live/integration-specific `TradingNode`; use `LiveNode` for Rust v2/Rust-backed work.

- Configuring and launching live trading nodes
- `NautilusKernel` boot sequence and system setup
- Engine configuration (`TradingNodeConfig`)
- Component lifecycle management (INITIALIZED → RUNNING → STOPPED → DISPOSED)
- Logging setup and monitoring
- Clock configuration and timer management
- Deployment and production readiness
- Reconciliation and state recovery

## When NOT To Use

- **Adapter-specific configuration** → use `nt-adapters`
- **Strategy logic** → use `nt-trading`
- **Backtest setup** → use `nt-backtest`
- **Data persistence** → use `nt-data`

## Python Usage

Python production guidance is physically quarantined as migration/reference-only.
See [Python Usage migration reference](migration_reference/python/python-usage.md).
New production work follows the Rust or bounded PyO3 sections below. AI and advisory work is outside this repository.

## Live runtime contract

Python production guidance is physically quarantined as migration/reference-only.
See [Live runtime contract migration reference](migration_reference/python/live-runtime-contract.md).
New production work follows the Rust or bounded PyO3 sections below. AI and advisory work is outside this repository.

## Python Extension

Python production guidance is physically quarantined as migration/reference-only.
See [Python Extension migration reference](migration_reference/python/python-extension.md).
New production work follows the Rust or bounded PyO3 sections below. AI and advisory work is outside this repository.

## Rust Usage

The `LiveNode` connects to real venues through adapter clients. It uses a builder pattern and runs as a standalone Rust binary — no Python runtime needed.

### Dependencies

```toml
[dependencies]
nautilus-common = "0.61.0"
nautilus-live = "0.61.0"
nautilus-model = "0.61.0"
nautilus-okx = "0.61.0"          # or any venue adapter
nautilus-trading = { version = "0.61.0", features = ["examples"] }

anyhow = "1"
dotenvy = "0.15"
log = "0.4"
tokio = { version = "1", features = ["full"] }
```

### LiveNode Builder

```rust
use log::LevelFilter;
use nautilus_common::{
    enums::Environment,
    logging::{logger::LoggerConfig, writer::FileWriterConfig},
};
use nautilus_live::node::LiveNode;
use nautilus_model::identifiers::{AccountId, TraderId};
use nautilus_okx::{
    common::enums::OKXInstrumentType,
    config::{OKXDataClientConfig, OKXExecClientConfig},
    factories::{OKXDataClientFactory, OKXExecutionClientFactory},
};

let trader_id = TraderId::from("TESTER-001");
let account_id = AccountId::from("OKX-001");

let data_config = OKXDataClientConfig {
    instrument_types: vec![OKXInstrumentType::Swap],
    ..Default::default()
};

let exec_config = OKXExecClientConfig {
    trader_id,
    account_id,
    instrument_types: vec![OKXInstrumentType::Swap],
    ..Default::default()
};

let log_config = LoggerConfig {
    stdout_level: LevelFilter::Info,
    fileout_level: LevelFilter::Info,
    file_config: Some(FileWriterConfig {
        directory: Some("logs".into()),
        file_name: Some("live-node.log".into()),
        ..Default::default()
    }),
    clear_log_file: false,
    ..Default::default()
};

let mut node = LiveNode::builder(trader_id, Environment::Live)?
    .with_name("MY-NODE-001".to_string())
    .with_logging(log_config)
    .add_data_client(
        None,
        Box::new(OKXDataClientFactory::new()),
        Box::new(data_config),
    )?
    .add_exec_client(
        None,
        Box::new(OKXExecutionClientFactory::new()),
        Box::new(exec_config),
    )?
    .with_reconciliation(true)
    .with_delay_post_stop_secs(5)
    .build()?;
```

### Add Strategies and Run

```rust
use nautilus_model::{identifiers::InstrumentId, types::Quantity};
use nautilus_trading::examples::strategies::{GridMarketMaker, GridMarketMakerConfig};

let mut config = GridMarketMakerConfig::builder()
    .instrument_id(InstrumentId::from("ETH-USDT-SWAP.OKX"))
    .max_position(Quantity::from("0.10"))
    .num_levels(3)
    .grid_step_bps(100)
    .skew_factor(0.5)
    .requote_threshold_bps(10)
    .expire_time_secs(8)
    .on_cancel_resubmit(true)
    .build();

config.base.use_hyphens_in_client_order_ids = false; // OKX requirement

let strategy = GridMarketMaker::new(config);
node.add_strategy(strategy)?;
node.run().await?;
```

### Async Runtime

`LiveNode::run()` is async and requires a Tokio runtime:

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();
    // ... node setup ...
    node.run().await?;
    Ok(())
}
```

The node runs until interrupted (Ctrl+C) or shut down programmatically.

### Current v2 LiveNode deltas

- v2 `LiveNode` shutdown handles Unix SIGTERM in the Rust path.
- Rust live and sandbox node builders support `with_clock_factory` for
  deterministic clock injection.
- `LiveNode metrics` are available for Rust live runner observability.
- Python and PyO3 configs support WebSocket transport backend selection.
- The `event_store` format changed in v1.230.0; beta v1.227-v1.229 stores
  must be regenerated rather than migrated in-place.
- Current develop commit
  [`32bc6b680`](https://github.com/nautechsystems/nautilus_trader/commit/32bc6b680)
  hardens the evolving/alpha event store beyond the pinned baseline: capture
  avoids queue/execute duplication and preserves a message when encoding fails;
  reads reject a table key whose embedded `seq` differs; the verifier records an
  undecodable entry and continues; equal-start run listing and retention no
  longer depend on filesystem order; and writer halt fires exactly once and
  rejects post-halt submissions. Treat any backend, verifier, replay, or capture
  failure as fail-stop evidence, not as an event that may be silently skipped.
- Live reconciliation uses monotonic-time gates and `RecencyMap` tracking;
  review recency-sensitive checks for monotonic-clock use before deployment.

### v1.227.0 LiveNode config notes

- `LoggerConfig` can be constructed directly from Python and Rust; Rust `LiveNode` supports `file_config` and `clear_log_file`.
- `LiveNodeConfig` and adapter client configs implement serde `Deserialize`, so TOML-backed config loading is viable for Rust live nodes.
- Portfolio mark-to-market snapshots are emitted as `PortfolioSnapshot` events when `snapshot_interval_ms` is configured.

### Environment Variables

Adapters read API credentials from environment variables. Use `.env` + `dotenvy`:

```bash
export OKX_API_KEY="your_api_key"
export OKX_API_SECRET="your_api_secret"
export OKX_API_PASSPHRASE="your_passphrase"
```

Each adapter documents required variables in its integration guide.

### Adapter Examples

Most adapters include runnable `node_data_tester.rs` and `node_exec_tester.rs` examples:

| Adapter | Example directory |
|---|---|
| Architect AX | `crates/adapters/architect_ax/examples/` |
| Betfair | `crates/adapters/betfair/examples/` |
| Binance | `crates/adapters/binance/examples/` |
| BitMEX | `crates/adapters/bitmex/examples/` |
| Bybit | `crates/adapters/bybit/examples/` |
| Databento | `crates/adapters/databento/examples/` |
| Deribit | `crates/adapters/deribit/examples/` |
| dYdX | `crates/adapters/dydx/examples/` |
| Hyperliquid | `crates/adapters/hyperliquid/examples/` |
| Kraken | `crates/adapters/kraken/examples/` |
| OKX | `crates/adapters/okx/examples/` |
| Polymarket | `crates/adapters/polymarket/examples/` |
| Sandbox | `crates/adapters/sandbox/examples/` |
| Tardis | `crates/adapters/tardis/examples/` |

### Reconciliation

In production, enable reconciliation so the engine aligns cached state with the venue on startup:
- Keep `.with_reconciliation(true)` or the production default enabled unless an adapter limitation is documented and reviewed
- See `references/concepts/live.md` for reconciliation details

## Rust Extension (PyO3 Path)

### Infrastructure Components in Rust

```rust
use pyo3::prelude::*;

#[pyclass]
pub struct MyInfraComponent {
    // Component state
}

#[pymethods]
impl MyInfraComponent {
    #[new]
    fn new() -> Self { /* ... */ }
}
```

**PyO3 conventions:**
- Use `#[pyclass]` and `#[pymethods]` for Python-visible types
- Register in the owning crate’s `src/python/mod.rs`; `crates/pyo3/src/lib.rs` aggregates that crate submodule
- Python v2 live callback routing: never call `Python::attach()` from Tokio worker
  tasks. Send typed events through live runner channels; the runner dispatches
  callbacks on the host live event-loop thread.
- Tokio integration: use the Nautilus shared runtime and tracked tasks; do not
  construct an independent runtime inside live components.
- See `references/developer_guide/ffi.md` for FFI patterns
- See `references/developer_guide/rust.md` for Rust coding standards

## Key Conventions

### Component Lifecycle

Components follow strict state machine: `INITIALIZED → RUNNING → STOPPED → DISPOSED`. State transitions are enforced — calling `start()` on a `RUNNING` component raises an error. Always check state before operations.

### Logging Patterns

- Rust production components use the project `tracing`/`log` integration and structured fields.
- Migration/reference-only Python components may use `self.log.info()`,
  `self.log.warning()`, `self.log.error()`, and `self.log.debug()`.
- Log state transitions and significant events at appropriate levels.

### Config Validation

- Rust production configs use typed structs and builders; propagate `build()` validation errors.
- Migration/reference-only Python config classes use `frozen=True` and typed fields.
- Validate config before node creation.
- Secrets should be passed via environment variables, not config files.

### Production Readiness

- Enable reconciliation for live trading
- Configure appropriate rate limits
- Set up file logging for production
- Use health checks and monitoring
- Handle graceful shutdown properly

### Coding Standards

See `references/developer_guide/coding_standards.md` for project-wide conventions including:

### Production Readiness Checklist

- [ ] Rust configs pass typed builder validation; migration-only Python config validates in `__init__`
- [ ] Rust state hooks or migration-only Python `on_save`/`on_load` preserve required state
- [ ] Rust stop/finalization or migration-only Python `on_stop` cleans up timers
- [ ] Error handling covers all event handlers
- [ ] Logging configured for debugging and monitoring
- [ ] Adapter credentials via environment variables, not hardcoded
- [ ] Environment variables: `PYO3_PYTHON`, `PYTHONHOME`, and Linux
      `LD_LIBRARY_PATH` derived with `sysconfig.get_config_var("LIBDIR")`

- Python style (PEP 8, type hints, docstrings)
- Rust style (edition 2024, clippy lints)
- FFI patterns (GIL management, callback forwarding)

## References

NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.

- `references/concepts/` — architecture, cache, logging, live, overview, rust
- `references/api/` — system, core, common, config, live
- `references/developer_guide/` — coding standards, FFI, Python conventions, Rust conventions, environment setup
- `references/developer_guide/contracts/live_runtime_contract.md` — LiveNode versus TradingNode guidance
- `references/examples/legacy_migration/README.md` — migration pointer for removed Python `TradingNode` aliases; new live examples must be Rust `LiveNode`
