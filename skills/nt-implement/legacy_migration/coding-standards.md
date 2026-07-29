# Coding Standards

> **Migration/reference-only.** This non-AI Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-implement` skill. The only active Python lane is AI/advisory work
> routed through `nt-evomap-integration`.


Follow these nautilus_trader conventions:

### Type Hints

All signatures must include comprehensive type annotations:
```python
def __init__(self, config: MyStrategyConfig) -> None:
def on_bar(self, bar: Bar) -> None:
def on_save(self) -> dict[str, bytes]:
```

### Docstrings

Use NumPy docstring format, imperative mood for Python:
```python
def calculate_signal(self, bar: Bar) -> float:
    """
    Calculate trading signal from bar data.

    Parameters
    ----------
    bar : Bar
        The bar to analyze.

    Returns
    -------
    float
        Signal value between -1 and 1.
    """
```

### Naming Conventions

- Config classes: `{Component}Config` (e.g., `TrendStrategyConfig`)
- Strategy IDs: `{StrategyClass}-{order_id_tag}` (e.g., `TrendStrategy-001`)
- Instrument IDs: `{symbol}.{venue}` (e.g., `BTCUSDT-PERP.BINANCE`)
- Bar types: `{instrument_id}-{step}-{aggregation}[{price_type}]-{source}` (price_type in square brackets)

### Formatting

- 100 character line limit
- Trailing commas for multi-line arguments
- Spaces only (no tabs)
