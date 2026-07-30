# Python Extension

> **Migration/reference-only.** This non-AI Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-live` skill. The only active Python lane is AI/advisory work
> routed through `nt-evomap-integration`.


### Custom Component

```python
from nautilus_trader.common.component import Component

class MyComponent(Component):
    def __init__(self, ...):
        super().__init__(...)

    def _start(self):
        # Called during component start
        pass

    def _stop(self):
        # Called during component stop
        pass

    def _reset(self):
        # Called during component reset
        pass

    def _dispose(self):
        # Called during component disposal
        pass
```
