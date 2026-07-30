# Python Extension

> **Migration/reference-only.** This non-AI Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-backtest` skill. The only active Python lane is AI/advisory work
> routed through `nt-evomap-integration`.


### Custom FillModel

```python
from nautilus_trader.backtest.models import FillModel

class MyFillModel(FillModel):
    def __init__(self, ...):
        super().__init__()
        # TODO: Initialize model parameters

    # Override fill probability/slippage methods as needed
```

See `templates/legacy_migration/fill_model.py` for full template.

### Custom Fee Models

Configure fee structures per venue:

```python
from nautilus_trader.model.objects import Money

# Via BacktestVenueConfig
BacktestVenueConfig(
    ...,
    fee_model=MakerTakerFeeModel(
        maker_fee=Decimal("0.0002"),
        taker_fee=Decimal("0.0004"),
    ),
)
```
