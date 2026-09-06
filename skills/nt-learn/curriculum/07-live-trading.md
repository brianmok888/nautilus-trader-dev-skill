# Stage 07: Live Trading with Rust `LiveNode`

## Goal

Deploy the Rust strategy from the earlier stages with `LiveNode`, connect Rust
adapter clients, enable reconciliation, and understand production lifecycle and
risk boundaries.

Legacy Python live-node material is migration/reference-only. Use the
quarantined pointers in `skills/nt-live/migration_reference/python/` when
migrating an existing system; the active curriculum does not teach Python live
execution.

## Prerequisites

- Completed Stage 06 (Indicators & Actors)
- A Rust strategy tested in a backtest
- Understanding of event-driven architecture and async Rust

## Core concepts

### Same strategy, different runtime

The same Rust strategy logic can be registered with a backtest engine or a live
node. Live operation replaces simulated venues with adapter data and execution
clients while preserving strategy lifecycle and domain types.

### Build and run `LiveNode`

The current upstream pattern uses `LiveNode::builder`, venue client factories,
typed adapter configuration, strategy registration, and an async Tokio runtime.

```rust
use nautilus_common::enums::Environment;
use nautilus_live::node::LiveNode;
use nautilus_model::identifiers::TraderId;

let trader_id = TraderId::from("TRADER-001");

let mut node = LiveNode::builder(trader_id, Environment::Live)?
    .add_data_client(
        None,
        Box::new(data_client_factory),
        Box::new(data_client_config),
    )?
    .add_exec_client(
        None,
        Box::new(exec_client_factory),
        Box::new(exec_client_config),
    )?
    .with_reconciliation(true)
    .with_delay_post_stop_secs(5)
    .build()?;

node.add_strategy(strategy)?;
node.run().await?;
```

Use the concrete factory and config types from the selected adapter. The pinned
upstream baseline `6df237382eb1d8411906f9b1790fa06f8ba7aad4` includes runnable nodes under
`crates/adapters/<venue>/examples/` and the official
`docs/how_to/run_rust_live_trading.md` guide.

### Runtime constraints

1. Use one live runtime per process unless the adapter documentation proves a
   different supported topology.
2. Keep callbacks non-blocking; move heavy work behind bounded async channels.
3. Keep order placement, risk, adapter state, and liveness in Rust.

## Adapters

Each live adapter supplies typed configuration plus data and execution client
factories. Instrument discovery, market-data subscriptions, order routing,
account updates, and reconciliation remain adapter-owned Rust behavior.

Start from the nearest upstream example:

- Data-only validation: `crates/adapters/<venue>/examples/node_data_tester.rs`
- Execution validation: `crates/adapters/<venue>/examples/node_exec_tester.rs`
- Strategy wiring: a venue `node_*.rs` example or
  `docs/how_to/run_rust_live_trading.md`

## Reconciliation and persistence

Reconciliation aligns cached orders, positions, balances, and in-flight
commands with venue state at startup and while running. Production nodes keep
reconciliation enabled and test ambiguous submit, cancel, and modify outcomes
before deployment.

Persistence and external message-bus settings are deployment decisions. Verify
recovery ordering, stale-state handling, and shutdown durability against the
selected storage implementation rather than assuming configuration presence is
readiness evidence.

## Production considerations

- Load credentials from environment or a secrets manager; never hard-code them.
- Configure logging before build and preserve stable trader, node, account, and
  client identifiers in operational records.
- Treat Ctrl+C and programmatic shutdown as lifecycle events: stop accepting new
  work, reconcile in-flight commands, stop strategies, disconnect clients, and
  allow the configured post-stop delay.
- Keep risk fail-closed. Validate precision, quantity, notional, reduce-only,
  account, and venue constraints before orders reach the adapter.
- Use `Environment::Sandbox` or the venue's demo environment for paper checks;
  do not infer production readiness from connectivity alone.

## Exercises

1. Select one adapter and map its data config, execution config, factories, and
   environment enum from the upstream Rust example.
2. Port the Stage 05 Rust strategy registration from the backtest engine to
   `LiveNode` without changing strategy business logic.
3. Explain what reconciliation must recover after an unknown submit outcome.
4. Run the adapter data tester, then the execution tester, in a sandbox or demo
   environment and record the observed capability matrix.

## Checkpoint

You're ready for Stage 08 when:

- [ ] You can build a `LiveNode` with typed data and execution clients
- [ ] You can register a Rust strategy and run the async node
- [ ] You can explain startup and continuous reconciliation
- [ ] You can explain why Python has no live execution authority here
- [ ] You can demonstrate sandbox evidence without claiming production readiness
