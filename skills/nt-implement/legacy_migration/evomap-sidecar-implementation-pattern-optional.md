# EvoMap Sidecar Implementation Pattern (Optional)

> **Migration/reference-only.** This non-AI Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-implement` skill. The only active Python lane is AI/advisory work
> routed through `nt-evomap-integration`.


If your Nautilus system integrates with EvoMap, LangChain, or LangGraph, implement it as a sidecar module, not as trading-loop logic:

- Create a dedicated local Proxy mailbox gateway client (for example, `EvoMapProxyMailboxClient`) and keep protocol concerns outside Strategy/Actor signal math.
- Map internal artifacts (feature deltas, design snapshots, decision outcomes) into explicit payload builders.
- Run Proxy mailbox submit/poll/search and optional LangGraph `StateGraph` review work on timers or background workers; handlers should only enqueue lightweight events.
- Enforce a policy layer: allowlisted payload fields, retry limits, and fail-closed behavior.
- Persist provenance (`event_id`, asset id, suggestion hash, graph checkpoint id, accept/reject reason) for auditability.

```python
from collections import deque

class RegimeActor(Actor):
    def __init__(self, config: RegimeActorConfig) -> None:
        super().__init__(config)
        self._evomap_queue: deque[dict] = deque(maxlen=10_000)

    def on_start(self) -> None:
        self._evomap = EvoMapProxyMailboxClient(proxy_url=self.config.evomap_proxy_url)
        self.set_timer("evomap-sync", interval=self.config.evomap_sync_interval_ns)

    def on_bar(self, bar: Bar) -> None:
        signal = self._compute_signal(bar)
        self._evomap_queue.append({"ts": bar.ts_event, "signal": signal})

    def on_timer(self, event: TimeEvent) -> None:
        if event.name != "evomap-sync" or not self._evomap_queue:
            return
        batch = [self._evomap_queue.popleft() for _ in range(min(50, len(self._evomap_queue)))]
        self._evomap.submit_assets([{"type": "EvolutionEvent", "events": batch}])
```
