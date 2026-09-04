NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Deployment Patterns for NautilusTrader Live Trading

This guide covers deployment around the pinned `LiveNode` surface: lifecycle, run modes,
stop/dispose, `LiveNodeHandle`, task cancellation, configuration, backing stores, monitoring,
and production readiness. The legacy v1 Python `TradingNode` deployment internals moved to
[migration_reference/python/deployment-v1-tradingnode.md](../../migration_reference/python/deployment-v1-tradingnode.md);
NT v2 compatibility note: that legacy v1 material is migration reference only.

## LiveNode Lifecycle

Rust `LiveNode::run()` prepares cached and venue state before starting trader components, then
owns the event loop and coordinated shutdown. Startup order:

1. **Build**: configure and build the `LiveNode` (builder wiring; clients, engines, logging).
2. **Restore cached state** when a backing database is attached and cache loading is enabled
   (`LiveExecutionEngineConfig.load_cache = true` by default).
3. **Connect data clients** and cache instruments.
4. **Connect execution clients**.
5. **Startup reconciliation** (when enabled): fetch venue reports and align state.
6. **Start trader components** (actors, strategies).
7. **Run event loop and periodic checks** until a stop or shutdown request.
8. On stop: stop the trader and process residual events for the configured grace period, then
   disconnect clients and finalize.

Connection, reconciliation, or trader startup failures abort startup and follow the coordinated
cleanup path. The shutdown sequence is: signal received (SIGINT, SIGTERM, or handle stop);
trader components stopped (triggering order cancellations, etc.); the event loop continues
processing residual events for the configured grace period; the kernel is finalized, clients
disconnected, and remaining events drained.

## Run Modes

The same lifecycle runs in every mode; the mode decides only who owns signal handling.

- **Python `run()`**: the node owns the calling thread and installs its own `SIGINT`/`SIGTERM`
  handling. Use it for standalone processes.
- **Python `run_async()`**: the node runs on an event loop the host already owns (an ASGI server
  serving a dashboard beside the node, for example). A hosted node installs no signal handlers -
  the host owns them.
- **Rust `run()`**: equivalent to `run_with_mode(NodeRunMode::Owned)`.
- **Rust `run_with_mode(NodeRunMode::Hosted)`**: leaves signal handling to the host application.
  Every other responsibility, including maintenance, reconciliation, external ingress, and the
  shutdown sequence, is identical across modes so that hosted and owned nodes cannot diverge.

`run_async()` returns a coroutine and lends the node to it for the run's duration. Capture
`cache`, `portfolio`, and `handle()` before starting, because each stays usable while the node
runs, whereas reading state through the node itself raises until the run returns it. `handle()`
and `is_running` answer throughout. Calling `dispose()` during the run returns without doing
anything; call it after the run task finishes to release the node's resources.

### Hosted deployment sketch

```python
import asyncio

from nautilus_trader.live import LiveNode
from nautilus_trader.live import LiveNodeHandle

async def serve_with_node(node: LiveNode) -> None:
    cache, portfolio, handle = node.cache, node.portfolio, node.handle()
    run_task: asyncio.Task[None] | None = None
    service_task: asyncio.Task[None] | None = None
    try:
        # Start your dashboard/service task here.
        run_task = asyncio.create_task(node.run_async())
        await run_task
    finally:
        if service_task is not None and not service_task.done():
            service_task.cancel()
            await asyncio.gather(service_task, return_exceptions=True)
        try:
            if run_task is not None:
                handle.stop()
                await run_task
        finally:
            node.dispose()
```

Before an ASGI lifespan reports startup complete, wait until the handle reports `Running` while
checking whether the run task has failed; keep supervising the task after startup. Compatibility
is tested with the default asyncio loop and uvloop.

## Stop and Dispose

- `LiveNodeHandle.stop()` (Python handle, or Rust handle method) requests a graceful shutdown
  and returns immediately; the awaiting run task resolves once shutdown finishes. It is safe to
  call from any thread, including a signal handler.
- Rust `LiveNode::stop()` stops the trader, waits the configured grace period
  (`delay_post_stop`) to allow residual events to be processed, then finalizes the shutdown
  sequence: clients disconnect, remaining events drain, engines stop.
- Rust `LiveNode::start()` starts without entering the select loop; it is a building block for
  tests and embedding, not a lifecycle: use `run`/`run_with_mode` to run a node.
- `dispose()` releases the node's resources (Rust: closes external ingress, disposes the
  kernel, marks the handle stopped). Call it after the run finishes; during a run it returns
  without doing anything.

Cancelling the awaiting run task requests the same shutdown, waits for it, then re-raises the
cancellation, which keeps `asyncio.timeout` and task groups behaving as their callers expect.

## LiveNodeHandle

`LiveNodeHandle` is the thread-safe control surface for a running node:

- `is_running`, `is_stopping` - liveness predicates that answer throughout the run.
- `state` - the node's `NodeState`.
- `stop()` - request graceful shutdown from any thread.
- `metrics_snapshot()` (Rust handle) - primitive runner metrics; poll snapshots from another
  task and derive rates or utilization from `RunnerMetricsDelta::from_snapshots(prev, next)`.

Capture the handle from the node before calling `run()` (Python `node.handle()`, Rust
`node.handle()`), then poll or signal it from supervisor tasks.

## Task Cancellation

Live task tracking uses the structured primitives in `crates/live/src/task.rs` (see the task
lifecycle section in the skill `SKILL.md`): `TaskGroup` generations bound spawned tasks,
`begin_shutdown()` closes admission and cancels the current generation, `abort()` requests
immediate forced cancellation, and `drain()` awaits completion within graceful and forced
bounds. Pending task cancellation during shutdown is bounded by
`LiveNodeConfig.timeout_shutdown` (default 5s).

NT v2 compatibility note: legacy v1 used `nautilus_trader/live/cancellation.py`
`cancel_tasks_with_timeout` and `RetryManagerPool.shutdown()`; current: those modules do not
exist at the pinned baseline - shutdown cancellation is owned by the live task lifecycle.

## LiveNodeConfig Options

`LiveNodeConfig` (pinned `crates/live/src/node/config.rs:750`) is the node-level configuration
surface for both Rust and Python.

### Identity and Environment

| Field            | Type          | Default        | Description                            |
|------------------|---------------|----------------|----------------------------------------|
| `environment`    | `Environment` | `LIVE`         | Context: `BACKTEST`, `SANDBOX`, `LIVE` |
| `trader_id`      | `TraderId`    | `"TRADER-001"` | Unique trader identity (NAME-TAG)      |
| `instance_id`    | `UUID4`       | `None`         | Unique kernel instance ID (auto-gen)   |
| `load_state`     | `bool`        | `False`        | Load actor/strategy state from database on start |
| `save_state`     | `bool`        | `False`        | Save actor/strategy state to database on stop |
| `shutdown_on_error` | `bool`     | `False`        | Request shutdown when a Rust error log is emitted |
| `loop_debug`     | `bool`        | `False`        | Enable asyncio event loop debug mode   |

Python exposes the timeouts as `timeout_connection_secs`, `timeout_reconciliation_secs`,
`timeout_portfolio_secs`, `timeout_disconnection_secs`, `delay_post_stop_secs`, and
`timeout_shutdown_secs`; the builder equivalents are
`with_timeout_connection`/`with_timeout_reconciliation`/`with_timeout_portfolio`/
`with_timeout_disconnection_secs`/`with_delay_post_stop_secs`/`with_delay_shutdown_secs`.

### Timeouts

| Field (Rust)         | Default | Description                                      |
|----------------------|---------|--------------------------------------------------|
| `timeout_connection` | 60s     | Max wait for all clients to connect/initialize   |
| `timeout_reconciliation` | 30s | Max wait for startup reconciliation and each continuous report-collection task |
| `timeout_portfolio`  | 10s     | Max wait for portfolio margin/PnL initialization |
| `timeout_disconnection` | 10s  | Max wait for all engine clients to disconnect    |
| `delay_post_stop`    | 10s     | Delay after stopping the node to await residual events |
| `timeout_shutdown`   | 5s      | Max wait for pending task cancellation during shutdown |

NT v2 compatibility note: legacy v1 named the post-stop wait `timeout_post_stop` and defaulted
`timeout_connection` to 120s; current: `delay_post_stop` with a 60s connection timeout.

### Engine Configurations

| Field         | Type                       | Description                         |
|---------------|----------------------------|-------------------------------------|
| `data_engine` | `LiveDataEngineConfig`     | Data engine configuration           |
| `risk_engine` | `LiveRiskEngineConfig`     | Risk engine configuration           |
| `exec_engine` | `LiveExecutionEngineConfig` | Reconciliation, in-flight checks, snapshots |

NT v2 compatibility note: legacy v1 names `LiveExecEngineConfig`, `LiveDataClientConfig`, and
`LiveExecClientConfig`; current: `LiveExecutionEngineConfig`, `DataClientConfig`, and
`ExecutionClientConfig`.

`LiveExecutionEngineConfig` continuous consistency checks (pinned defaults): startup
`reconciliation` (true) with `reconciliation_lookback_mins`; in-flight checks
(`inflight_check_interval_ms` 2000, `inflight_check_threshold_ms` 5000,
`inflight_check_retries` 5); open order checks (`open_check_interval_secs`,
`open_check_missing_retries` 5, `open_check_threshold_ms` 5000); position checks
(`position_check_interval_secs`, `position_check_lookback_mins` 60); order/position snapshots
(`snapshot_orders`, `snapshot_positions`, `snapshot_positions_interval_secs`); own book auditing
(`own_books_audit_interval_secs`).

### Client Configuration (Rust config)

| Field          | Type                                        | Description                 |
|----------------|---------------------------------------------|-----------------------------|
| `data_clients` | `map[str, DataClientConfig]`                | Data client configs by name |
| `exec_clients` | `map[str, ExecutionClientConfig]`           | Exec client configs by name |

The Rust `LiveNodeConfig` accepts client config maps; the Python `LiveNodeConfig` does not -
Python attaches clients through `LiveNodeBuilder.add_data_client`/`add_exec_client`.
Each client config carries an `InstrumentProviderConfig` and a `RoutingConfig`
(`default: bool`, `venues`). Prefer attaching clients through the builder
(`add_data_client`/`add_exec_client`, or the `_with_routing` variants), which registers venue
routing explicitly: `default=True` registers the default client; each venue in
`RoutingConfig.venues` routes requests and commands for that venue to the client.

### Infrastructure

| Field          | Type                   | Description                                |
|----------------|------------------------|--------------------------------------------|
| `cache`        | `CacheConfig`          | Cache behavior and capacities              |
| `msgbus`       | `MessageBusConfig`     | External stream naming/encoding settings   |
| `portfolio`    | `PortfolioConfig`      | Portfolio configuration                    |
| `queue_monitor`| `QueueMonitorConfig`   | Queue depth monitoring thresholds          |
| `logging`      | `LoggerConfig`         | Logging configuration                      |
| `controller`   | `ImportableControllerConfig` | Trader controller                    |
| `plugins`      | `list[PluginConfig]`   | Plug-in configurations                     |

Rust-only `LiveNodeConfig` fields (no Python parameter): `emulator` (`OrderEmulatorConfig`),
`streaming` (`StreamingConfig`, also settable via `with_streaming_config`), and `event_store`
(`EventStoreConfig`).

## Cache and Message Bus Backing

NT v2 compatibility note: legacy v1 wired persistence with
`CacheConfig(database=DatabaseConfig(...))` and `MessageBusConfig(database=DatabaseConfig(...))`;
current: neither config carries a `database` field at the pinned baseline. Backings are
attached through the builder.

A backing is a recovery mechanism for supported cache records (general data, currencies,
instruments, accounts, orders, positions) - not a complete event archive or a synchronized
distributed cache. Connection settings belong to the concrete backing config
(`RedisCacheConfig`/`PostgresCacheConfig` from `nautilus_trader.infrastructure`):

```python
from nautilus_trader.common import Environment
from nautilus_trader.infrastructure import RedisCacheConfig
from nautilus_trader.live import LiveNode
from nautilus_trader.model import TraderId

node = (
    LiveNode.builder("LiveNode", TraderId("TRADER-001"), Environment.LIVE)
    .with_cache_database_factory(RedisCacheConfig(host="localhost", port=6379))
    .build()
)

try:
    node.run()
finally:
    node.dispose()
```

Pass `PostgresCacheConfig` to back cache data with Postgres; Postgres does not support actor or
strategy state persistence, so do not combine it with `load_state`/`save_state`. Rust callers
build the adapter through the `CacheDatabaseFactory` trait and attach it with
`node.set_cache_database(...)` before `run()`. External message bus egress/ingress is wired at
build time through `with_external_msgbus_egress`/`with_external_msgbus_factory`/
`with_external_ingress`; `MessageBusConfig.types_filter` is a `Sequence[str]` of type names,
not typed classes.

:::warning
Always dispose the node. `dispose()` closes the backing, which flushes writes still held in the
buffer when `CacheConfig.buffer_interval_ms` is set. Returning straight from `run()` can drop
them.
:::

## Shutdown on Error

Set `LiveNodeConfig.shutdown_on_error=True` so a Rust error log requests a live node shutdown.
The Rust logger records the first `log::error!` emitted after the kernel starts, including
error logs from other threads, and the kernel publishes a `ShutdownSystem` command when the
live event loop next checks for shutdown.

The shutdown request follows the normal live node stop path: the trader stops, the post-stop
delay is awaited, clients disconnect, and the engines stop. It does not abort the process.

```python
from nautilus_trader.config import LiveNodeConfig

config = LiveNodeConfig(shutdown_on_error=True)
```

Error logs suppressed by component filters or logging bypass mode still request shutdown. The
trigger is cleared and re-armed when a new kernel run starts, so a process can restart a node
without reinitializing the logging system. The per-engine `graceful_shutdown_on_error` option
has been removed; configure shutdown-on-error at the node/kernel level instead.
Shutdown-on-error observes Rust `log` records, not Python `logging.error(...)` calls.

## Monitoring and Health

- **Runner metrics**: poll `LiveNodeHandle::metrics_snapshot()` (Rust) from a supervisor task
  and derive event rates, staleness, dispatch/loop utilization, and queue depths from
  `RunnerMetricsDelta`. The snapshot covers channel dispatch after startup, including residual
  dispatch during the shutdown grace period.
- **Queue pressure**: `QueueStateChanged` events publish condition/state transitions together
  with `queue_depth` and `mean_dispatch_ns`; treat critical pressure as a live safety signal and
  prove asserted/cleared transitions under load. Configure thresholds with
  `QueueMonitorConfig`.
- **Continuous reconciliation as health monitoring**: the `LiveExecutionEngineConfig`
  continuous checks double as a health signal - in-flight checks detect stuck orders, open order
  checks detect state drift, position checks detect fill loss, and snapshots capture periodic
  order/position consistency records.
- **Own book auditing**: `own_books_audit_interval_secs` enables periodic auditing of internal
  order books against public order book data; discrepancies are logged as errors.

Recommended production `LiveExecutionEngineConfig` tuning:

```python
exec_engine = LiveExecutionEngineConfig(
    reconciliation=True,
    reconciliation_lookback_mins=120,
    open_check_interval_secs=10.0,
    open_check_missing_retries=5,
    position_check_interval_secs=30.0,
    position_check_retries=3,
    inflight_check_interval_ms=2_000,
    inflight_check_threshold_ms=5_000,
)
```

## Production Readiness Checklist

- [ ] Reconciliation enabled (or an adapter limitation documented and reviewed)
- [ ] `shutdown_on_error` decided explicitly for fail-closed behavior
- [ ] Timeouts sized for the venue (`timeout_connection`, `timeout_reconciliation`,
      `delay_post_stop`, `timeout_shutdown`)
- [ ] Cache backing attached via builder factory when state must survive restarts; node always
      disposed to flush buffered writes
- [ ] Log file configuration (`LoggerConfig` + `FileWriterConfig`) for production auditing
- [ ] Runner metrics/queue pressure monitoring in place
- [ ] Run mode chosen deliberately: `run()` for standalone processes, `run_async()`/
      `NodeRunMode::Hosted` when a host owns signals
- [ ] Adapter credentials via environment variables, not hardcoded

## v1 Migration

For the legacy v1 Python `TradingNode` deployment internals (build/run/stop/dispose phases,
`TradingNodeConfig` tables with v1 names and defaults, dict-key multi-adapter setup,
`add_stream_processor`, `cancel_tasks_with_timeout`, `RetryManagerPool`, and v1 health-check
internals), see
[migration_reference/python/deployment-v1-tradingnode.md](../../migration_reference/python/deployment-v1-tradingnode.md).
NT v2 compatibility note: that legacy v1 `TradingNode` material is migration reference only.
