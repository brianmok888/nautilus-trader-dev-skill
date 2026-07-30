# Python Extension

> **Migration/reference-only.** This non-AI Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-trading` skill. The only active Python lane is AI/advisory work
> routed through `nt-evomap-integration`.


### Custom ExecAlgorithm

Subclass `ExecAlgorithm` from `nautilus_trader.execution.algorithm`:

```python
from nautilus_trader.execution.algorithm import ExecAlgorithm

class MyExecAlgorithm(ExecAlgorithm):
    def on_start(self):
        pass

    def on_order(self, order):
        # Custom execution logic — split, time-slice, etc.
        self.submit_order(order)

    def on_stop(self):
        pass
```

Register in config:
```python
exec_algorithms=[MyExecAlgorithm.fully_qualified_name()]
```

### Custom Margin/Position Sizing

Extend risk calculations by subclassing margin models or implementing custom position sizing logic in your Strategy.
