# Python Extension

> **Migration/reference-only.** This Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-signals` skill.


### Custom Indicator

Subclass `Indicator` and implement `handle_bar()`, `update_raw()`, `_reset()`:

```python
from nautilus_trader.indicators import Indicator

class MyIndicator(Indicator):
    def __init__(self, period: int):
        super().__init__(params=[period])
        self.period = period
        self.value = 0.0
        self.count = 0

    def handle_bar(self, bar):
        self.update_raw(bar.close.as_double())

    def update_raw(self, value: float):
        if not self.has_inputs:
            self._set_has_inputs(True)
        # TODO: Core calculation
        self.count += 1
        if not self.initialized and self.count >= self.period:
            self._set_initialized(True)

    def _reset(self):
        self.value = 0.0
        self.count = 0
```

See `templates/legacy_migration/indicator.py` for full template.

### Custom PortfolioStatistic

```python
from nautilus_trader.analysis.statistic import PortfolioStatistic

class MyStatistic(PortfolioStatistic):
    def calculate_from_returns(self, returns):
        if not self._check_valid_returns(returns):
            return None
        return float(returns.mean())
```

Return values must be JSON-serializable (float, int, str, bool, None).

See `templates/legacy_migration/portfolio_statistic.py` for full template.

### Custom Data Types

Use `@customdataclass` decorator — it auto-generates serialization methods (dict, bytes, Arrow). See `templates/legacy_migration/custom_data.py`.
