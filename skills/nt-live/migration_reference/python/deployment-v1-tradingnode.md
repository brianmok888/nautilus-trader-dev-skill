NT v2 compatibility note: legacy v1 Python `TradingNode` references in this file are retained for migration/reference-only context; the whole file is migration reference. Prefer Rust v2 guidance and `LiveNode` for new Rust-backed live work.

# Deployment Patterns: v1 Python `TradingNode` (legacy)

> **Migration/reference-only.** This v1 Python `TradingNode` material is not a
> production default and does not exist at the pinned baseline
> (`nautilus_trader/live/` ships only `__init__.py`/`__init__.pyi`; there is no
> `live/node.py`, `live/cancellation.py`, or `TradingNodeBuilder`/`_is_built`).
> New production work uses the Rust `LiveNode` guidance in
> `deployment_patterns.md` (this skill's `references/guides` tree).
> NT v2 compatibility note: this legacy v1 `TradingNode` material is migration reference.

NT v2 compatibility note: legacy v1 deployment internals retained below; current: deploy with
`LiveNode` (builder wiring, `run`/`run_with_mode`/`run_async`, `LiveNodeHandle.stop()`,
`dispose()`), pinned `LiveNodeConfig` timeouts, and builder-factory cache/msgbus backing.

## TradingNode Lifecycle (v1)
NT v2 compatibility note: legacy v1 `TradingNode` lifecycle below is migration reference.

The v1 `TradingNode` class (historically `nautilus_trader/live/node.py`) was the top-level
entry point for live trading. Its lifecycle followed four phases.

### Phase 1: Build (v1)

NT v2 compatibility note: legacy v1 build flow; current: `LiveNode::builder(...)` /
`LiveNode.builder(...)` wires clients and engines before `build()`.

```python
node = TradingNode(config=config)
node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)
node.add_exec_client_factory("BINANCE", BinanceLiveExecClientFactory)
node.build()
```

NT v2 compatibility note: v1 build internals below are legacy migration reference.
During build (v1):
1. The `NautilusKernel` was created with all core engines (data, risk, execution).
2. A `TradingNodeBuilder` was instantiated, holding references to all engines.
3. Client factories were registered by name.
4. `build()` called `build_data_clients()` and `build_exec_clients()` on the builder,
   which instantiated each client from its factory and registered it with the
   corresponding engine. Venue routing was configured at this stage.
5. The `_is_built` flag was set to `True`. Calling `build()` again raised `RuntimeError`.

### Phase 2: Run (v1)

NT v2 compatibility note: legacy v1 run internals; current: `run()`/`run_async()` run the
pinned LiveNode event loop; queue processing is tracked by the live task lifecycle
(`TaskGroup`/`TaskSpawner`), not by ad-hoc `asyncio.gather` task sets.

The v1 `run()` method either created an async task (if the loop was already running) or
called `loop.run_until_complete(run_async())`. The async flow:

1. Validated that `build()` was called.
2. Called `kernel.start_async()`, which connected all clients, ran reconciliation,
   initialized portfolio, and started all strategies.
3. Created queue processing tasks for all engines:
   - DataEngine: cmd, req, res, data queues
   - RiskEngine: cmd, evt queues
   - ExecEngine: cmd, evt queues
4. If external message streaming was configured, started the streaming task.
5. Awaited `asyncio.gather(*tasks)` -- the node stayed alive as long as queues processed.

### Phase 3: Stop (v1)

```python
node.stop()
```

Called `kernel.stop_async()` which:
- Stopped all strategies (optionally saving state if `save_state=True`).
- Disconnected all data and execution clients.
- Waited for engine queues to drain.

### Phase 4: Dispose (v1)

```python
node.dispose()
```

Final cleanup:
1. Waited up to `timeout_disconnection` seconds for the kernel to stop running.
2. If timeout expired, logged disconnection status of DataEngine and ExecEngine.
3. Cancelled the streaming task if active.
4. Called `kernel.dispose()` to release all resources.
5. Shut down the thread pool executor.
6. Stopped or closed the event loop.
7. Logged final loop state (`is_running`, `is_closed`).

### Signal Handling (v1)

The node registered `_loop_sig_handler` as the signal callback. On receiving SIGINT
or SIGTERM, it logged a warning and called `stop()`, triggering graceful shutdown.

## TradingNodeConfig Options (v1)
NT v2 compatibility note: legacy v1 config surface; current: `LiveNodeConfig`
(pinned `crates/live/src/node/config.rs`) with `LiveDataEngineConfig`,
`LiveRiskEngineConfig`, `LiveExecutionEngineConfig`, `DataClientConfig`/
`ExecutionClientConfig`, builder-attached clients, and pinned timeout defaults.

`TradingNodeConfig` extended `NautilusKernelConfig` with live-specific defaults.

### Identity and Environment (v1)

| Field         | Type          | Default        | Description                           |
|---------------|---------------|----------------|---------------------------------------|
| `environment` | `Environment` | `LIVE`         | Context: `BACKTEST`, `SANDBOX`, `LIVE`|
| `trader_id`   | `TraderId`    | `"TRADER-001"` | Unique trader identity (NAME-TAG)     |
| `instance_id` | `UUID4`       | `None`         | Unique kernel instance ID (auto-gen)  |

### Engine Configurations (v1)

| Field          | Type                    | Description                         |
|----------------|-------------------------|-------------------------------------|
| `data_engine`  | `LiveDataEngineConfig`  | Queue sizes, shutdown behavior      |
| `risk_engine`  | `LiveRiskEngineConfig`  | Queue sizes, shutdown behavior      |
| `exec_engine`  | v1 `LiveExecEngineConfig` | Reconciliation, in-flight checks  |

NT v2 compatibility note: the v1 name `LiveExecEngineConfig` is historical; current:
`LiveExecutionEngineConfig`. Each v1 engine config had `qsize` (default 100,000) and
`graceful_shutdown_on_exception` (default `False`); current shutdown-on-error is the node-level
`LiveNodeConfig.shutdown_on_error`.

### Client Configuration (v1)

| Field          | Type                                           | Description                |
|----------------|------------------------------------------------|----------------------------|
| `data_clients` | `dict[str, LiveDataClientConfig]`              | Data client configs by name|
| `exec_clients` | `dict[str, LiveExecClientConfig]`              | Exec client configs by name|

NT v2 compatibility note: v1 names `LiveDataClientConfig`/`LiveExecClientConfig` are historical;
current: `DataClientConfig`/`ExecutionClientConfig`, attached via the node builder with a
`RoutingConfig` (`default: bool`, `venues: frozenset[str]`).

Client configs included:
- `instrument_provider`: `InstrumentProviderConfig` for instrument loading.
- `routing`: `RoutingConfig` with `default: bool` and `venues: frozenset[str]`.

### Infrastructure (v1)

| Field         | Type               | Description                                       |
|---------------|--------------------|---------------------------------------------------|
| `cache`       | `CacheConfig`      | Database backing for cache persistence             |
| `message_bus` | `MessageBusConfig` | External streams, database backing for message bus |
| `portfolio`   | `PortfolioConfig`  | Portfolio configuration                            |
| `emulator`    | `OrderEmulatorConfig` | Client-side order emulation                     |
| `streaming`   | `StreamingConfig`  | Feather file streaming for analysis                |
| `catalogs`    | `list[DataCatalogConfig]` | Data catalog sources                        |

NT v2 compatibility note: v1 wired persistence with `CacheConfig(database=DatabaseConfig(...))`
and `MessageBusConfig(database=DatabaseConfig(...))`; current: neither config carries a
`database` field. Attach backings via `LiveNodeBuilder.with_cache_database_factory`
(`RedisCacheConfig`/`PostgresCacheConfig`) and the external msgbus factory wiring.

### Strategy and Actor Loading (v1)

| Field             | Type                               | Description                       |
|-------------------|------------------------------------|-----------------------------------|
| `actors`          | `list[ImportableActorConfig]`      | Actor configurations              |
| `strategies`      | `list[ImportableStrategyConfig]`   | Strategy configurations           |
| `exec_algorithms` | `list[ImportableExecAlgorithmConfig]` | Execution algorithm configs    |
| `controller`      | `ImportableControllerConfig`       | Trader controller                 |

### State Management (v1)

| Field        | Type   | Default | Description                                 |
|--------------|--------|---------|---------------------------------------------|
| `load_state` | `bool` | `False` | Load strategy state from database on start  |
| `save_state` | `bool` | `False` | Save strategy state to database on stop     |
| `loop_debug` | `bool` | `False` | Enable asyncio event loop debug mode        |

### Timeouts (v1)

| Field                      | Default  | Description                                      |
|----------------------------|----------|--------------------------------------------------|
| `timeout_connection`       | `120.0`  | Max wait for all clients to connect/initialize   |
| `timeout_reconciliation`   | `30.0`   | Max wait for execution state reconciliation      |
| `timeout_portfolio`        | `10.0`   | Max wait for portfolio margin/PnL initialization |
| `timeout_disconnection`    | `10.0`   | Max wait for all clients to disconnect           |
| `timeout_post_stop`        | `10.0`   | Wait for residual events after stop              |
| `timeout_shutdown`         | `5.0`    | Wait for pending task cancellation               |

NT v2 compatibility note: v1 defaults and the field name `timeout_post_stop` are historical;
current: `LiveNodeConfig.timeout_connection` 60s, `timeout_reconciliation` 30s,
`timeout_portfolio` 10s, `timeout_disconnection` 10s, `delay_post_stop` 10s,
`timeout_shutdown` 5s.

### Logging (v1)

NT v2 compatibility note: the v1 `logging` field took a `LoggingConfig(log_level=...)`;
current: `LiveNodeConfig.logging` takes a `LoggerConfig` (`stdout_level`, `fileout_level`,
`component_levels`, `is_colored`, `file_config`). The node logs cache/msgbus backing status at
startup:

```
has_cache_backing=True
has_msgbus_backing=False
```

## Multi-Adapter Setup (v1)

NT v2 compatibility note: legacy v1 dict-key routing; current: attach each client through the
builder (`add_data_client`/`add_exec_client`, with `_with_routing` variants) and set
`RoutingConfig.default`/`venues` per client.

```python
config = TradingNodeConfig(
    data_clients={
        "BINANCE": BinanceLiveDataClientConfig(
            routing=RoutingConfig(venues=frozenset({"BINANCE"})),
        ),
        "BYBIT": BybitLiveDataClientConfig(
            routing=RoutingConfig(venues=frozenset({"BYBIT"})),
        ),
    },
    exec_clients={
        "BINANCE": BinanceLiveExecClientConfig(
            routing=RoutingConfig(venues=frozenset({"BINANCE"})),
        ),
        "BYBIT": BybitLiveExecClientConfig(
            routing=RoutingConfig(venues=frozenset({"BYBIT"})),
        ),
    },
)
```

The v1 builder extracted the factory name by splitting the `"NAME-suffix"` key on the first
hyphen: `parts.partition("-")[0]`.

## External Message Streaming (v1)

When `message_bus.external_streams` was configured, the node started a streaming task that
listened to external bus messages, deserialized them, processed them through any registered
stream processors, and published them on the internal message bus.

Custom stream processors were added via `node.add_stream_processor(callback)`.

NT v2 compatibility note: `add_stream_processor` does not exist at the pinned baseline;
current: external ingress/egress is wired at build time through the builder
(`with_external_msgbus_egress`, `with_external_msgbus_factory`, `with_external_ingress`).

## Task Cancellation and Retry Internals (v1)

NT v2 compatibility note: the v1 modules cited here do not exist at the pinned baseline;
current: the live crate tracks shutdown deterministically with `TaskGroup` generations,
`TaskSpawner`, `TaskSlot`, bounded by `timeout_shutdown` and `delay_post_stop`.

### Task Cancellation (v1)

The v1 cancellation module (`nautilus_trader/live/cancellation.py`) provided
`cancel_tasks_with_timeout`:

- Took a strong snapshot of tasks from a `WeakSet` to prevent GC during cancellation.
- Cancelled all pending tasks and awaited completion with configurable timeout.
- Default timeouts: 5s for tasks, 2s for futures (external connections).
- Logged warnings for any tasks that failed to complete within the timeout window.

### RetryManagerPool Shutdown (v1)

On component stop, `RetryManagerPool.shutdown()` cancelled all active retry managers
and cleared the active set, preventing orphaned retry loops.

## Health Check Patterns (v1)

NT v2 compatibility note: the v1 introspection points below do not exist at the pin
(`check_disconnected`, `_handle_run_task_result`, `_handle_streaming_exception`);
current: monitor through `LiveNodeHandle` (`is_running`, `is_stopping`, `state`,
`metrics_snapshot()`), `QueueStateChanged` pressure events, and node-level
`shutdown_on_error`.

### Engine Disconnection Checks (v1)

During shutdown, the node queried:

- `exec_engine.check_disconnected()` -- returned `True` if all exec clients were
  disconnected.

These were logged during timeout scenarios in `dispose()`.

### Continuous Reconciliation as Health Monitoring (v1)

NT v2 compatibility note: v1 configured continuous checks on the v1 `LiveExecEngineConfig`;
current: the pinned `LiveExecutionEngineConfig` carries the corresponding continuous-check
fields (`inflight_check_*`, `open_check_*`, `position_check_*`, `snapshot_*`).

- **In-flight order checks** (every 2s by default): detected stuck orders.
- **Open order checks** (configurable, recommended 5-10s): detected order state drift.
- **Position checks** (configurable, recommended 30-60s): detected fill loss.

### Own Book Auditing (v1)

Setting `own_books_audit_interval_secs` enabled periodic auditing of internal order
books against public order book data. Discrepancies were logged as errors.

### Queue Task Monitoring (v1)

The `run_async()` method monitored engine queue tasks. If any queue task completed
unexpectedly, the `_handle_run_task_result` callback logged the exception. The
streaming task had its own `_handle_streaming_exception` callback.

### Recommended Production Configuration (v1)

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
